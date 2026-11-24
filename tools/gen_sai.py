"""把 Stellar AI（创意工坊 3610149307，0.14.4，见 tools/sai_source/descriptor.mod）的「AI 性格与行为」部分整合进本 MOD（3.16）。

用法：python tools/gen_sai.py [MOD 根目录，默认仓库 mod/]
源数据是 tools/sai_source/（从 Stellar AI 0.14.4 复制的子集，退订原 MOD 后也能重新生成），原版取群星安装目录。
群星更新后重新运行即可；每处替换都会核对，原版改了写法就直接报错。

只取性格与行为，不取岗位、区划、建筑、殖民地类型、经济计划、预算、战略资源、市场、援助与它的按月调度系统
（本 MOD 的普通 AI 用自动星球，那些本来也用不上）。生成：
- common/personalities/00_personalities.txt：以【原版】性格文件为底（保留 4.6 新增的意识形态接受度、战争贩子权重、
  纯粹思潮判断），每个性格的数值（侵略性、勇气、军费、外交接受度等）换成 Stellar AI 的；另加 Stellar AI 的 26 个
  「扩张期」性格 expansionists_*（前 40 年、未在战争中使用），出现条件取原版对应性格的条件再加上这两条
- common/war_goals/~atb_sai_war_goals.txt：原版进攻性战争目标，ai_weight 里加 Stellar AI 的实力门槛
  （不对舰队更强的国家开战，偏好孤立目标）
- common/inline_scripts/atb_sai/war_goal_strength_gate.txt：实力门槛本身
- common/opinion_modifiers/atb_sai_odds_opinion.txt：「实力决定态度」的好感（照抄）
- common/agreement_presets/zz_atb_sai_fair_protection.txt：附庸协议偏好（照抄）
- common/ai_espionage/spynetworks/00_base_strategies.txt：原版间谍策略 + Stellar AI 的目标选择
- common/scripted_triggers/atb_sai_triggers.txt：上面用到的两个触发器
- common/defines/atb_sai_defines.txt：战争、舰队、外交行为参数（殖民与人口迁移的几项不取，会打乱自动星球）
- localisation：三个好感修正的名字（中英）
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
MOD = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "mod"
GAME = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Stellaris")
SRC = ROOT / "tools/sai_source"
HEAD = "# 皇女的远征军 3.16：整合 Stellar AI 0.14.4 的 AI 性格与行为部分。由 tools/gen_sai.py 生成，请勿手改。\n"


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8-sig", errors="replace").replace("\r\n", "\n")


def write(rel: str, text: str, bom: bool = False):
    p = MOD / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes((b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8"))
    print("写出", rel)


def block_end(text: str, start: int) -> int:
    """start 指向 '{'，返回配对 '}' 的下标（跳过注释与字符串）"""
    depth, j, n, in_str = 0, start, len(text), False
    while j < n:
        c = text[j]
        if in_str:
            if c == '"':
                in_str = False
        elif c == '"':
            in_str = True
        elif c == "#":
            j = text.find("\n", j)
            j = n if j < 0 else j
            continue
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return j
        j += 1
    raise ValueError("括号不配对")


def blocks(text: str):
    """顶层 key = { ... } 块：(key, 起点, 终点+1)"""
    i = 0
    for m in re.finditer(r"(?m)^([A-Za-z_0-9@]+)\s*=\s*\{", text):
        if m.start() < i:
            continue
        e = block_end(text, m.end() - 1)
        yield m.group(1), m.start(), e + 1
        i = e + 1


def top_fields(block: str):
    """块第一层的字段：[(名字, 起点, 终点, 是否为块)]，坐标相对 block"""
    out, k, n = [], block.index("{") + 1, len(block) - 1
    while k < n:
        c = block[k]
        if c == "#":
            k = block.find("\n", k)
            continue
        m = re.match(r"([A-Za-z_0-9]+)\s*=\s*", block[k:])
        if m and (k == 0 or not (block[k - 1].isalnum() or block[k - 1] == "_")):
            name, vs = m.group(1), k + m.end()
            if block[vs] == "{":
                e = block_end(block, vs)
                out.append((name, k, e + 1, True))
                k = e + 1
            else:
                m2 = re.match(r'"[^"]*"|[^\s{}#]+', block[vs:])
                out.append((name, k, vs + m2.end(), False))
                k = vs + m2.end()
            continue
        k += 1
    return out


def field_value(block: str, name: str):
    for f, s, e, is_block in top_fields(block):
        if f == name:
            return block[s:e], is_block
    return None, None


# ---------------------------------------------------------------- 脚本变量（性格数值用 @ 写法）
sai_vars = {}
for src in (SRC / "common/scripted_variables/stellarai_scripted_variables.txt",):
    for m in re.finditer(r"(?m)^(@[A-Za-z_0-9]+)\s*=\s*([-\d.]+)", read(src)):
        sai_vars[m.group(1)] = m.group(2)


def resolve(text: str) -> str:
    def sub(m):
        if m.group(0) not in sai_vars:
            sys.exit(f"Stellar AI 变量 {m.group(0)} 找不到定义")
        return sai_vars[m.group(0)]
    return re.sub(r"@[A-Za-z_0-9]+", sub, text)


# ---------------------------------------------------------------- 1. 性格
van = read(GAME / "common/personalities/00_personalities.txt")
sai = read(SRC / "common/personalities/00_personalities.txt")
sai_blocks = {k: sai[s:e] for k, s, e in blocks(sai)}
van_blocks = [(k, s, e) for k, s, e in blocks(van)]
van_map = {k: van[s:e] for k, s, e in van_blocks}

SKIP_FIELDS = {"allow", "weight_modifier"}	# 出现条件与权重保留原版（4.6 的纯粹思潮、战争贩子）
out, last, changed = [], 0, 0
for k, s, e in van_blocks:
    out.append(van[last:s])
    blk = van[s:e]
    if k in sai_blocks:
        sb = resolve(sai_blocks[k])
        new = blk
        for f, fs, fe, is_block in sorted(top_fields(sb), key=lambda x: -x[1]):
            if f in SKIP_FIELDS or is_block:
                continue
            sval = sb[fs:fe]
            vval, vblock = field_value(new, f)
            if vval is None:
                # 原版没有的字段：插在第一行之后
                first = new.index("\n") + 1
                new = new[:first] + "\t" + sval + "\t# Stellar AI\n" + new[first:]
                changed += 1
            elif re.sub(r"\s+", " ", vval) != re.sub(r"\s+", " ", sval):
                new = new.replace(vval, sval + "\t# Stellar AI，原版 " + vval.split("=", 1)[1].strip(), 1)
                changed += 1
        blk = new
    out.append(blk)
    last = e
out.append(van[last:])
pers = "".join(out)

# 扩张期性格：Stellar AI 的块（数值、行为、权重 2000），出现条件 = 原版对应性格的条件 + 前 40 年 + 未在战争中
exp_out = ["\n\n# ======== Stellar AI：扩张期性格（前 40 年、未在战争中；之后回到上面的正常性格） ========\n"]
n_exp = 0
for k, sb in sai_blocks.items():
    if not k.startswith("expansionists_"):
        continue
    base = k[len("expansionists_"):]
    if base not in van_map:
        sys.exit(f"{k} 对应的原版性格 {base} 不存在了，请手动核对")
    sb = resolve(sb)
    sa, _ = field_value(sb, "allow")
    va, _ = field_value(van_map[base], "allow")
    if sa is None or va is None:
        sys.exit(f"{k}：找不到 allow")
    vbody = va[va.index("{") + 1:va.rindex("}")].strip("\n")
    new_allow = ("allow = {\n\t\tis_country_type = default\n\t\tyears_passed < 41\n\t\tis_at_war = no\n"
                 "\t\t# 以下取原版 " + base + " 的条件（含 4.6 的纯粹思潮）\n" + vbody + "\n\t}")
    sb = sb.replace(sa, new_allow, 1)
    # 4.6 新增、Stellar AI（4.5）没有的标量字段，从原版对应性格补上（如 adopt_ideology_acceptance）
    for f, fs, fe, is_block in top_fields(van_map[base]):
        if is_block or field_value(sb, f)[0] is not None:
            continue
        first = sb.index("\n") + 1
        sb = sb[:first] + "\t" + van_map[base][fs:fe] + "\t# 原版 4.6 " + base + "\n" + sb[first:]
    exp_out.append(sb + "\n\n")
    n_exp += 1
pers = pers.rstrip("\n") + "".join(exp_out)

# 3.20：恐惧之潮存活期间，终端对齐协议（atbgp_power_5）的性格 = 灭绝者（含扩张期）侵略性减半。
# 恐惧之潮灭亡后（全局旗标 atbgp_tide_fallen）出现条件不再满足，原版重新评估时回到正常的灭绝者。
restrained = ["\n# ======== 皇女的远征军 3.20：恐惧之潮存活期间的终端对齐协议（侵略性减半） ========\n"]
for base, new_key in (("exterminators", "atb_terminal_restrained"),
                      ("expansionists_exterminators", "atb_terminal_restrained_exp")):
    src_blk = next(pers[s:e] for k, s, e in blocks(pers) if k == base)
    blk = src_blk.replace(base + " = {", new_key + " = {", 1)
    m = re.search(r"(?m)^\taggressiveness = ([0-9.]+)[^\n]*$", blk)
    if not m:
        sys.exit(f"{base}：找不到 aggressiveness")
    half = float(m.group(1)) / 2
    blk = blk.replace(m.group(0), f"\taggressiveness = {half:g}\t# 3.20：{base} 的 {m.group(1)} 减半", 1)
    a, _ = field_value(blk, "allow")
    # 两份权重相同，正常期那份要避开扩张期（前 40 年且未在战争中）
    phase = "" if base.startswith("expansionists_") else "\t\tOR = { years_passed > 40 is_at_war = yes }\n"
    blk = blk.replace(a, a[:a.rindex("}")].rstrip() + "\n\t\thas_country_flag = atbgp_power_5\n"
                      "\t\tNOT = { has_global_flag = atbgp_tide_fallen }\n" + phase + "\t}", 1)
    w, _ = field_value(blk, "weight_modifier")
    blk = blk.replace(w, "weight_modifier = {\n\t\tweight = 100000\n\t}", 1)
    restrained.append(blk + "\n\n")
pers = pers.rstrip("\n") + "\n" + "".join(restrained)
write("common/personalities/00_personalities.txt",
      HEAD + "# 覆盖原版 common/personalities/00_personalities.txt：以原版为底，数值换成 Stellar AI 的，另加扩张期性格。\n\n" + pers)
print(f"  性格：改了 {changed} 处数值，加了 {n_exp} 个扩张期性格")

# ---------------------------------------------------------------- 2. 战争目标的实力门槛
GATE = '\t\tinline_script = "atb_sai/war_goal_strength_gate"\t# Stellar AI：实力门槛\n'
gate_src = read(SRC / "common/inline_scripts/stellarai/war_goal_strength_gate.txt")
write("common/inline_scripts/atb_sai/war_goal_strength_gate.txt", HEAD + gate_src)
sai_wg = read(SRC / "common/war_goals/~stellarai_war_goals.txt")
wg_keys = [k for k, s, e in blocks(sai_wg) if not k.startswith("@")]
van_wg = {}
for f in sorted((GAME / "common/war_goals").glob("*.txt")):
    t = read(f)
    for k, s, e in blocks(t):
        van_wg[k] = (f.name, t[s:e])
wg_out = [HEAD, "# 原版进攻性战争目标（取当前原版），只在 ai_weight 里加 Stellar AI 的实力门槛：不对舰队更强的国家开战，偏好孤立目标。\n",
          "# 文件名以 ~ 开头，排在原版之后覆盖同名战争目标。\n\n"]
# 原版战争目标文件里的局部变量（如 @protectorate_tech_threshold）要一起带上
used_vars = set()
for k in wg_keys:
    if k not in van_wg:
        sys.exit(f"原版没有战争目标 {k} 了，请手动核对")
    fname, blk = van_wg[k]
    a, _ = field_value(blk, "ai_weight")
    if a is None:
        sys.exit(f"{k} 没有 ai_weight")
    new_a = a[:a.rindex("}")].rstrip("\t") + GATE + "\t}"
    blk = blk.replace(a, new_a, 1)
    used_vars |= set(re.findall(r"@[A-Za-z_0-9]+", blk))
    wg_out.append(f"# 原版 {fname}\n{blk}\n\n")
for v in sorted(used_vars):
    m = None
    for f in sorted((GAME / "common/war_goals").glob("*.txt")):
        m = re.search(rf"(?m)^{re.escape(v)}\s*=\s*\S+", read(f))
        if m:
            break
    if m:
        wg_out.insert(3, m.group(0) + "\t# 原版战争目标文件里的局部变量\n")
write("common/war_goals/~atb_sai_war_goals.txt", "".join(wg_out))

# ---------------------------------------------------------------- 3. 好感、附庸协议、触发器
write("common/opinion_modifiers/atb_sai_odds_opinion.txt",
      HEAD + read(SRC / "common/opinion_modifiers/stellarai_odds_opinion.txt"))
write("common/agreement_presets/zz_atb_sai_fair_protection.txt",
      HEAD + "@stellarai_diplomatic_fallback_bonus = " + sai_vars["@stellarai_diplomatic_fallback_bonus"] + "\n"
      + read(SRC / "common/agreement_presets/zz_stellarai_fair_protection.txt"))
trig_src = read(SRC / "common/scripted_triggers/stellarai_strategy_triggers.txt")
trig = {k: trig_src[s:e] for k, s, e in blocks(trig_src)}
write("common/scripted_triggers/atb_sai_triggers.txt",
      HEAD + "\n".join(trig[k] + "\n" for k in ("stellarai_conquest_identity", "stellarai_fair_protection_preference")))

# ---------------------------------------------------------------- 4. 间谍策略：原版 + Stellar AI 的目标选择
van_esp = read(GAME / "common/ai_espionage/spynetworks/00_base_strategies.txt")
sai_esp = read(SRC / "common/ai_espionage/spynetworks/00_base_strategies.txt")
ins = re.search(r"\n\t\t# Keep native operations\..*?\t\t\tfactor = 0\n\t\t}\n", sai_esp, re.S)
if not ins:
    sys.exit("Stellar AI 间谍策略的插入段找不到了")
# 插入点：Stellar AI 文件里插入段之前的 200 个字符，在原版里也应唯一出现
anchor = sai_esp[:ins.start()][-200:]
if van_esp.count(anchor) != 1:
    sys.exit("原版间谍策略的插入点变了，请手动核对")
van_esp = van_esp.replace(anchor, anchor + ins.group(0), 1)
write("common/ai_espionage/spynetworks/00_base_strategies.txt",
      HEAD + "# 覆盖原版 common/ai_espionage/spynetworks/00_base_strategies.txt：原版 + Stellar AI 的目标选择（不刺探联邦成员，优先战争对象、宿敌、缺少军事/科技情报的国家）。\n\n" + van_esp)

# ---------------------------------------------------------------- 5. 行为参数
SKIP_DEFINES = {"UNDERDEVELOPED_PLANET_LIMIT", "AI_FEW_PLANETS_COLONIZATION_BOOST", "RESETTLE_UNEMPLOYED_BASE_RATE"}
d = read(SRC / "common/defines/9999_stellarai_defines.txt")
nai = re.search(r"NAI\s*=\s*\{(.*?)\n\t\}", d, re.S)
lines = []
for line in nai.group(1).split("\n"):
    m = re.match(r"\s*([A-Z_0-9]+)\s*=", line)
    if m and m.group(1) in SKIP_DEFINES:
        lines.append("\t# " + line.strip() + "\t# 皇女的远征军：不取（会打乱自动星球的殖民）")
    elif line.strip():
        lines.append("\t" + line.strip())
write("common/defines/atb_sai_defines.txt",
      HEAD + "# Stellar AI 的战争、舰队、外交行为参数。殖民与人口迁移的几项不取，本 MOD 自己的值在 atb_ex_defines.txt。\n"
      "NAI = {\n" + "\n".join(lines) + "\n}\n")

# ---------------------------------------------------------------- 6. 本地化
LOC = {
    "english": [("triggered_opinion_stellarai_we_can_win", "We Can Win"),
                ("triggered_opinion_stellarai_we_can_win_peaceful", "We Can Win"),
                ("triggered_opinion_stellarai_not_to_be_provoked", "Not to Be Provoked"),
                ("personality_atb_terminal_restrained", "Dormant Exterminators"),
                ("personality_atb_terminal_restrained_desc", "While the Tide of Dread still lives, the Protocol holds its blade and waits."),
                ("personality_atb_terminal_restrained_exp", "Dormant Exterminators"),
                ("personality_atb_terminal_restrained_exp_desc", "While the Tide of Dread still lives, the Protocol holds its blade and waits.")],
    "simp_chinese": [("triggered_opinion_stellarai_we_can_win", "我们打得过"),
                     ("triggered_opinion_stellarai_we_can_win_peaceful", "我们打得过"),
                     ("triggered_opinion_stellarai_not_to_be_provoked", "不可招惹"),
                     ("personality_atb_terminal_restrained", "蛰伏灭绝者"),
                     ("personality_atb_terminal_restrained_desc", "恐惧之潮尚在，协议按住了刀锋，静候时机。"),
                     ("personality_atb_terminal_restrained_exp", "蛰伏灭绝者"),
                     ("personality_atb_terminal_restrained_exp_desc", "恐惧之潮尚在，协议按住了刀锋，静候时机。")],
}
for lang, items in LOC.items():
    body = f"l_{lang}:\n # 皇女的远征军 3.16：Stellar AI「实力决定态度」的好感修正。由 tools/gen_sai.py 生成\n" + "".join(
        f' {k}:0 "{v}"\n' for k, v in items)
    write(f"localisation/{lang}/atb_sai_l_{lang}.yml", body, bom=True)
print("完成")
