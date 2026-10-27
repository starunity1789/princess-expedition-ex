"""皇女的远征军EX：改动后的静态自检。只读，不改任何文件。"""
import re
import sys
from pathlib import Path

MOD = Path(r"C:\Users\sol3u\Documents\GitHub\princess-expedition-ex\mod")
GAME = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Stellaris")

problems: list[str] = []
notes: list[str] = []


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8-sig", errors="replace")


def strip_noise(text: str) -> str:
    """去掉注释和字符串，只留结构字符。"""
    out, in_str = [], False
    for line in text.splitlines():
        buf = []
        i = 0
        while i < len(line):
            c = line[i]
            if in_str:
                if c == '"':
                    in_str = False
                i += 1
                continue
            if c == '"':
                in_str = True
                i += 1
                continue
            if c == "#":
                break
            buf.append(c)
            i += 1
        out.append("".join(buf))
        in_str = False  # 群星的字符串不跨行
    return "\n".join(out)


# ---------------------------------------------------------------- 1. 括号配对
txts = sorted(p for p in MOD.rglob("*.txt"))
gfxs = sorted(p for p in MOD.rglob("*.gfx"))
for p in txts + gfxs:
    s = strip_noise(read(p))
    depth, bad = 0, False
    for ch in s:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth < 0:
                bad = True
                break
    if bad or depth != 0:
        problems.append(f"括号不配对：{p.relative_to(MOD)}（收尾 depth={depth}）")
notes.append(f"括号检查：{len(txts)} 个 .txt + {len(gfxs)} 个 .gfx 全部配对" if not problems else "")

# ---------------------------------------------------------------- 2. 本地化 yml
for p in sorted(MOD.rglob("*.yml")):
    lines = read(p).splitlines()
    if not lines or not lines[0].strip().startswith("l_"):
        problems.append(f"本地化首行不是 l_xxx：{p.relative_to(MOD)}")
    keys = {}
    for i, line in enumerate(lines[1:], 2):
        if not line.strip() or line.strip().startswith("#"):
            continue
        m = re.match(r'^\s*([A-Za-z0-9_.]+):\d*\s+"', line)
        if not m:
            problems.append(f"本地化行格式可疑：{p.relative_to(MOD)}:{i}: {line[:60]}")
            continue
        if line.count('"') % 2:
            problems.append(f"本地化引号不成对：{p.relative_to(MOD)}:{i}")
        keys.setdefault(m.group(1), []).append(i)
    dup = {k: v for k, v in keys.items() if len(v) > 1}
    if dup:
        problems.append(f"本地化重复键：{p.relative_to(MOD)} -> {list(dup)[:5]}")

# ---------------------------------------------------------------- 3. 纹理文件存在
tex = re.compile(r'(?:texturefile|character_textures\s*=\s*\{)?\s*"((?:gfx|flags)/[^"]+\.dds)"')
missing = set()
for p in txts + gfxs:
    for rel in tex.findall(strip_noise(read(p))):
        if not (MOD / rel).exists() and not (GAME / rel).exists():
            missing.add(f"{p.relative_to(MOD)} -> {rel}")
if missing:
    problems += [f"引用的贴图不存在：{m}" for m in sorted(missing)[:20]]
else:
    notes.append("贴图引用：全部存在")

# ---------------------------------------------------------------- 4. 本 MOD 自己的效果/触发器调用
defined = set()
for sub in ("common/scripted_effects", "common/scripted_triggers"):
    for p in (MOD / sub).glob("*.txt"):
        defined |= set(re.findall(r"^([a-z_][a-z0-9_]*)\s*=\s*\{", read(p), re.M))
called = set()
for p in txts:
    for name in re.findall(r"\b(at[a-z0-9_]*)\s*=\s*(?:yes|\{)", read(p)):
        called.add(name)
# 只检查本 MOD 前缀里「被调用但没定义」的
unknown = {c for c in called if c.startswith(("atb_", "atbgp_")) and c not in defined}
# 事件 / 初始化器 / 效果名以外的 ID 会混进来，用白名单过滤掉明显不是效果的
unknown = {c for c in unknown if not re.match(r"atbgp_(sys|home|planet|country|species|d_|leader|ruler|cluster|power|btc|crisis)", c)}
unknown = {c for c in unknown if not re.match(r"atb_(system|planet|rl_sys|ex_galaxy|expedition|princess|leader|origin)", c)}
for c in sorted(unknown):
    hits = [str(p.relative_to(MOD)) for p in txts if re.search(rf"\b{c}\s*=\s*yes", read(p))]
    if hits:
        problems.append(f"调用了未定义的效果/触发器 {c}（出现在 {hits[0]}）")
notes.append(f"本 MOD 定义的 scripted effect/trigger：{len(defined)} 个")

# ---------------------------------------------------------------- 5. 本次改动点
init = read(MOD / "common/solar_system_initializers/atbgp_initializers.txt")
eff = read(MOD / "common/scripted_effects/atbgp_effects.txt")
ev = read(MOD / "events/atbgp_events.txt")
rl = read(MOD / "common/solar_system_initializers/atb_rl_initializers.txt")
exeff = read(MOD / "common/scripted_effects/atb_ex_effects.txt")
dep = read(MOD / "common/deposits/atbgp_deposits.txt")

checks = [
    ("白鹿物种肖像 = 兽耳机械", "portrait = kmpp_kemonomimi_machine" in init),
    ("白鹿方位 = 90°（12 点）", "12 点方位（角度 90）" in ev),
    ("远星政体 = 独裁制", "authority = auth_dictatorial" in init),
    ("远星国民 = 技术官僚 + 暗影财团", "civic = civic_technocracy civic = civic_dark_consortium" in init),
    ("远星思潮含威权主义", "ethic = ethic_authoritarian ethic = ethic_materialist" in init),
    ("三面帝国标识都写进了 create_country", init.count('category = "atbgp"') == 3),
    ("旧的 atbgp_install_named_ruler 已清除", "atbgp_install_named_ruler" not in eff + ev),
    ("两个具名元首安装效果已定义", "atbgp_install_ruler_rongxin = {" in eff and "atbgp_install_ruler_taiaria = {" in eff),
    ("两个具名元首安装效果被调用", "atbgp_install_ruler_rongxin = yes" in ev and "atbgp_install_ruler_taiaria = yes" in ev),
    ("泰阿瑞亚 5 条特质齐全", all(t in eff.split("atbgp_install_ruler_taiaria")[1] for t in (
        "leader_trait_intemporal", "leader_trait_supreme_organizer", "leader_trait_master_bureaucrat",
        "leader_trait_synthetic", "leader_trait_psionic"))),
    ("融心演算只有时间永驻", eff.split("atbgp_install_ruler_rongxin")[1].split("atbgp_install_ruler_taiaria")[0].count("add_trait") == 1),
    ("六份补给特征都有影响力 +2", dep.count("influence = 2") == 6),
    ("远星物种复制玩家开局物种", "is_ai = no" in init and "founder_species = {" in init),
    ("远星物种去掉致病基因", "remove_trait = trait_pathogenic_genes" in init),
    ("无形链接生成龙族土著", "atb_ex_generate_dragonkin_preftl = yes" in rl),
    ("龙族土著效果已定义", "atb_ex_generate_dragonkin_preftl = {" in exeff),
]
for label, ok in checks:
    if not ok:
        problems.append(f"改动点未生效：{label}")
notes.append(f"改动点检查：{sum(1 for _, ok in checks if ok)}/{len(checks)} 通过")

# ---------------------------------------------------------------- 6. 引用的原版 ID 是否存在
def game_has(pattern: str, *globs: str) -> bool:
    for g in globs:
        for p in GAME.glob(g):
            if re.search(pattern, read(p), re.M):
                return True
    return False


vanilla = [
    ("leader_trait_intemporal", r"^leader_trait_intemporal\s*=\s*\{", "common/traits/*.txt"),
    ("leader_trait_supreme_organizer", r"^leader_trait_supreme_organizer\s*=\s*\{", "common/traits/*.txt"),
    ("leader_trait_master_bureaucrat", r"^leader_trait_master_bureaucrat\s*=\s*\{", "common/traits/*.txt"),
    ("leader_trait_synthetic", r"^leader_trait_synthetic\s*=\s*\{", "common/traits/*.txt"),
    ("leader_trait_psionic", r"^leader_trait_psionic\s*=\s*\{", "common/traits/*.txt"),
    ("auth_dictatorial", r"^auth_dictatorial\s*=\s*\{", "common/governments/authorities/*.txt"),
    ("civic_technocracy", r"^civic_technocracy\s*=\s*\{", "common/governments/civics/*.txt"),
    ("civic_dark_consortium", r"^civic_dark_consortium\s*=\s*\{", "common/governments/civics/*.txt"),
    ("ethic_authoritarian", r"^ethic_authoritarian\s*=\s*\{", "common/ethics/*.txt"),
    ("00_solid.dds 背景", r".", "flags/backgrounds/00_solid.dds"),
    ("generate_pre_ftls_on_planet", r"^generate_pre_ftls_on_planet\s*=\s*\{", "common/scripted_effects/*.txt"),
    ("change_species_characteristics 用法存在", r"change_species_characteristics\s*=\s*\{\s*portrait", "common/scripted_effects/*.txt"),
]
for label, pat, glob in vanilla:
    if glob.endswith(".dds"):
        ok = (GAME / glob).exists()
    else:
        ok = game_has(pat, glob)
    if not ok:
        problems.append(f"原版里找不到：{label}")
notes.append(f"原版 ID 检查：{len(vanilla)} 项")

# 两个肖像组是否在 MOD 里定义
for group in ("kmpp_kemonomimi_machine", "adpp_ancient_dragonkin"):
    found = any(re.search(rf"^\s*{group}\s*=\s*\{{", read(p), re.M) for p in (MOD / "gfx/portraits/portraits").glob("*.txt"))
    if not found:
        problems.append(f"肖像组未定义：{group}")

# ---------------------------------------------------------------- 7. 护盾装甲翻倍
src = GAME / "common/scripted_variables/02_scripted_variables_component_cost.txt"
dst = MOD / "common/scripted_variables/02_scripted_variables_component_cost.txt"
if not dst.exists():
    problems.append("缺少翻倍后的 02_scripted_variables_component_cost.txt")
else:
    S = read(src).splitlines()
    M = read(dst).splitlines()[6:]
    if len(S) != len(M):
        problems.append(f"翻倍文件行数与原版不一致：{len(S)} vs {len(M)}")
    else:
        diff = [(s, m) for s, m in zip(S, M) if s != m]
        bad = [d for d in diff if not d[0].lstrip().startswith("@")]
        if bad:
            problems.append(f"翻倍文件改到了非变量行：{bad[:3]}")
        notes.append(f"护盾装甲翻倍：改动 {len(diff)} 行，全部是 @ 变量")

print("=" * 60)
for n in notes:
    if n:
        print("·", n)
print("=" * 60)
if problems:
    print(f"发现 {len(problems)} 个问题：")
    for p in problems:
        print("  ✗", p)
    sys.exit(1)
print("全部检查通过")
