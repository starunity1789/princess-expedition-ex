"""3.26：生成本 MOD 的「星体缩小」部分（直接写进 mod/，覆盖原版与几个 MOD 的同路径文件）。

用法：python gen_celestial_scale.py <群星安装目录> <创意工坊 281990 目录> <本 MOD 目录>

起初做成附属 MOD，用户决定整合进本体。代价：本 MOD 从此需要 Real Space 4.0——这里整份覆盖了
common/planet_classes/00_planet_classes.txt（Real Space 的版本，原版恒星已移到 realspace_planet_classes.txt，
用的是 Real Space 的模型），没装 Real Space 时恒星会显示不出来。
本脚本只读原版与创意工坊里的 MOD，不读本 MOD 自己生成的文件，所以重复运行不会叠加缩放。
逆熵行星护盾的缩放直接在 tools/gen_entropy_shield.py 里算好（× BODY），这里不再处理。

思路：不放大星系空间（那样舰船、射程会一起显得变小），只缩小星体（BODY = 1/8）与人造设施
（恒星基地、防御平台、离子炮等军用站 STATION = 1/4，其余 ART = 1/6）。
星体与星系的比例和「Real Space - System Scale」接近，舰船、武器、战斗都保持原版大小。

本 MOD 要排在下列 MOD 之后（同路径文件靠加载顺序覆盖）：
Real Space 4.0、Planetary Diversity、More Events Mod、! Reworked Advanced Ascension。

星体（× BODY）：
1. Real Space 的星体大小变量（行星、卫星、气态巨行星、小行星、6 档恒星）：整份覆盖
   common/scripted_variables/00_realspace_scripted_variables.txt，只改这 9 个变量
2. 写死了数字大小的星体类别（原版 DLC、Real Space、Planetary Diversity 的部分文件）：整份覆盖这些文件，
   只改非固定大小（没有 fixed_entity_scale = yes）星体的 entity_scale
3. Real Space 的星球环（环境物体）：缩小并重新算高度，保持和星球对齐
4. 包住恒星的巨构：戴森球（含危机球）、戴森云、物质解压器、量子弹射器、炼狱熔炉、戴森炮
5. More Events Mod 的行星护盾（按星球大小摆的环境物体）
6. 小行星带碎石的最大尺寸，舰船 / 空间站 / 恒星基地停靠的距离（defines）

人造设施（× ART）：
7. 恒星基地、防御平台、离子炮等军用站（× STATION）；采矿站、研究站、观测站（× ART）。改舰船尺寸的 hull_scale，
   原版与 RAA、More Events Mod 的定义都改
8. 星门、超空间中继器、L 星门、巨型船坞、战略协调中心、艺术品、星际议会、智库、监视球、大档案馆、
   迷雾封印、巨构施工平台、栖息地（模型；栖息地的星球类别 entity_scale 也一起改）

模型的缩放只改带网格（pdxmesh）的实体：只挂别的实体、自己没有网格的「容器」实体（如戴森球各阶段）不改，
从容器往下找到第一层带网格的实体为止，保证同一个零件只缩一次（3.26 初版把容器和零件都缩了，戴森球缩成 1/64）。

不缩：舰船、方舟、轨道环与电弧熔炉（原版本来就跟星球大小走）、环形世界（各段是轨道上的固定大小星球）；
星云、尘埃盘等星系级特效。群星或上述 MOD 更新后重新运行。
"""
import re
import sys
from pathlib import Path

GAME = Path(sys.argv[1])
WS = Path(sys.argv[2])
OUT = Path(sys.argv[3])  # 本 MOD 目录

BODY = 1 / 8  # 星体
ART = 1 / 6   # 人造设施
STATION = 1 / 4  # 恒星基地、防御平台、离子炮等军用站（用户测试后定：比其余人造设施大一些）

RS = WS / "937289339"     # Real Space 4.0
PD = WS / "819148835"     # Planetary Diversity
MEM = WS / "727000451"    # More Events Mod
RAA = WS / "1199002146"   # ! Reworked Advanced Ascension

SOURCES = []  # (输出路径, 来源说明)
WARN = []


def fmt(v: float) -> str:
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return s if s else "0"


def read(p: Path) -> str:
    return p.read_bytes().decode("utf-8-sig").replace("\r\n", "\n")


def write(rel: str, text: str, src: str) -> None:
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(text.encode("utf-8"))
    SOURCES.append((rel, src))
    print("generated", rel)


def header(src: str, what: str) -> str:
    return (f"# 皇女的远征军EX · 星体缩小：覆盖 {src}。\n"
            f"# 由 tools/gen_celestial_scale.py 生成，请勿手改；{what}\n\n")


def blocks(text: str, head: str):
    """顶层块：返回 (起点, 终点, 键名)。head 是块开头的正则（行首）。"""
    for m in re.finditer(head, text, re.M):
        d = 0
        j = text.index("{", m.start())
        while j < len(text):
            c = text[j]
            if c == "#":
                nl = text.find("\n", j)
                j = len(text) if nl < 0 else nl
                continue
            if c == "{":
                d += 1
            elif c == "}":
                d -= 1
                if d == 0:
                    break
            j += 1
        yield m.start(), j + 1, m.group(1) if m.groups() else ""


def file_vars(text: str) -> dict:
    return {m.group(1): float(m.group(2)) for m in re.finditer(r"^@(\w+)\s*=\s*(-?[\d.]+)", text, re.M)}


def top_level(block: str) -> str:
    """块内第一层的文字（去掉更深的嵌套与注释）。"""
    out, depth = [], 0
    for line in block.split("\n")[1:]:
        code = line.split("#", 1)[0]
        if depth == 0:
            out.append(code)
        depth += code.count("{") - code.count("}")
    return "\n".join(out)


def scale_top_level(block: str, vars_: dict, factor: float) -> str:
    """把实体块第一层的 scale 乘以 factor；没有 scale 就补一行。"""
    lines = block.split("\n")
    depth = 0
    for i, line in enumerate(lines):
        code = line.split("#", 1)[0]
        if depth == 1:
            m = re.match(r"^(\s*)scale\s*=\s*(@?[\w.\-]+)(.*)$", line)
            if m:
                raw = m.group(2)
                val = vars_[raw[1:]] if raw.startswith("@") else float(raw)
                lines[i] = f"{m.group(1)}scale = {fmt(val * factor)}\t# 原 {raw}，×{fmt(factor)}"
                return "\n".join(lines)
        depth += code.count("{") - code.count("}")
    k = block.rindex("}")
    return block[:k] + f"\tscale = {fmt(factor)}\t# 原版没写（1.0），×{fmt(factor)}\n" + block[k:]


def scale_models(root: Path, rel: str, roots_pat, factor: float, tag: str, what: str) -> None:
    """缩放模型文件里的实体。roots_pat 为 None 时，文件里没被别的实体挂载的实体都算根。
    从根往下：带网格的实体缩放后不再往下（子实体随它一起缩）；没有网格的容器不缩，继续往下找。"""
    text = read(root / rel)
    vars_ = file_vars(text)
    ents = {}
    for s, e, _ in blocks(text, r"^[ \t]*entity\s*=\s*\{"):
        b = text[s:e]
        n = re.search(r'name\s*=\s*"([^"]+)"', b)
        if not n:
            continue
        tl = top_level(b)
        ents[n.group(1)] = dict(span=(s, e), mesh=bool(re.search(r"^\s*pdxmesh\s*=", tl, re.M)),
                                kids=re.findall(r'attach\s*=\s*\{[^}]*?"([\w]+)"\s*\}', tl))
    attached = {k for e in ents.values() for k in e["kids"]}
    if roots_pat is None:
        roots = [n for n in ents if n not in attached]
    else:
        roots = [n for n in ents if re.search(roots_pat + "$", n)]
    if not roots:
        sys.exit(f"{rel} 里一个目标实体都没找到，原版可能改了写法")
    scaled, blocked = set(), set()

    def visit(n, under_scaled):
        if n not in ents:
            if not under_scaled:
                WARN.append(f"{rel}: {n} 定义在别的文件里，没缩到")
            return
        e = ents[n]
        if under_scaled:
            blocked.add(n)
            for k in e["kids"]:
                visit(k, True)
            return
        if e["mesh"]:
            scaled.add(n)
            for k in e["kids"]:
                visit(k, True)
        else:
            for k in e["kids"]:
                visit(k, False)

    for r in roots:
        visit(r, False)
    both = scaled & blocked
    if both:
        WARN.append(f"{rel}: {sorted(both)[:3]} 既单独显示又挂在已缩放的实体下，会缩两次")
    out, last = [], 0
    for n in sorted(scaled, key=lambda n: ents[n]["span"][0]):
        s, e = ents[n]["span"]
        out.append(text[last:s] + scale_top_level(text[s:e], vars_, factor))
        last = e
    out.append(text[last:])
    write(rel, header(f"{tag}的 {rel}", f"{what}：{len(scaled)} 个带网格的实体 ×{fmt(factor)}。") + "".join(out), tag)


# ================================================================ 星体（× BODY）
# ---------------------------------------------------------------- 1. Real Space 星体大小变量
VARS = ["planet_standard_scale", "asteroid_standard_scale", "giant_standard_scale",
        "star_dwarf_scale", "star_browndwarf_scale", "star_standard_scale",
        "star_giant_scale", "star_super_scale", "star_hyper_scale"]
rel = "common/scripted_variables/00_realspace_scripted_variables.txt"
text = read(RS / rel)
for v in VARS:
    pat = re.compile(rf"^@{v}\s*=\s*([\d.]+)[^\n]*$", re.M)
    m = pat.search(text)
    if not m:
        sys.exit(f"Real Space 的变量文件里找不到 @{v}，请手动核对")
    text = pat.sub(f"@{v} = {fmt(float(m.group(1)) * BODY)}\t# Real Space 原值 {m.group(1)}，×{fmt(BODY)}", text, count=1)
write(rel, header("Real Space 4.0 的 " + rel, f"只改 {len(VARS)} 个星体大小变量（×{fmt(BODY)}），其余照抄。") + text,
      "Real Space 4.0")

# ---------------------------------------------------------------- 2. 写死数字大小的星体类别（栖息地类 × ART）
HABITAT_CLASSES = {"pc_habitat", "pc_habitat_shielded", "pc_crystal_habitat"}
paths = {}
for root, tag in ((GAME, "原版"), (PD, "Planetary Diversity"), (RS, "Real Space 4.0")):  # 后者覆盖前者
    for p in sorted((root / "common/planet_classes").glob("*.txt")):
        paths[p.name] = (p, tag)
for name, (p, tag) in sorted(paths.items()):
    text = read(p)
    changed = []
    out, last = [], 0
    for s, e, k in blocks(text, r"^([a-z][\w]*)\s*=\s*\{"):
        b = text[s:e]
        fixed = "fixed_entity_scale = yes" in re.sub(r"#[^\n]*", "", b)
        if k in HABITAT_CLASSES:
            factor = ART
        elif fixed:
            continue
        else:
            factor = BODY
        m = re.search(r"^(\s*)entity_scale\s*=\s*([\d.]+)[ \t]*$", b, re.M)
        if not m:
            continue
        old = m.group(2)
        nb = b[:m.start()] + f"{m.group(1)}entity_scale = {fmt(float(old) * factor)}\t# 原 {old}，×{fmt(factor)}" + b[m.end():]
        out.append(text[last:s] + nb)
        last = e
        changed.append(f"{k} {old}×{fmt(factor)}")
    if changed:
        out.append(text[last:])
        rel = f"common/planet_classes/{name}"
        write(rel, header(f"{tag}的 {rel}", "只改这些写死了数字大小的星体：" + "、".join(changed) + "。") + "".join(out), tag)

# ---------------------------------------------------------------- 3. Real Space 星球环
rel = "gfx/models/planets/rs_rings_entities.asset"
text = read(RS / rel)
v = file_vars(text)
rs, rh = v["rings_scale"], v["rings_height"]
plane = rs * rh  # 环的根在轨道平面上，靠 locator 往下挪到星球所在高度（≈ -150）
nrs = rs * BODY
text = re.sub(r"^@rings_scale\s*=.*$", f"@rings_scale = {fmt(nrs)}\t# Real Space 原值 {fmt(rs)}，×{fmt(BODY)}",
              text, count=1, flags=re.M)
text = re.sub(r"^@rings_height\s*=.*$",
              f"@rings_height = {fmt(plane / nrs)}\t# 原 {fmt(rh)}；locator 会随实体一起缩放，所以要放大回去，保持实际高度 {fmt(plane)}",
              text, count=1, flags=re.M)
write(rel, header("Real Space 4.0 的 " + rel, "环缩小，高度换算后不变。") + text, "Real Space 4.0")

# ---------------------------------------------------------------- 4. 包住恒星的巨构
STAR_MEGA = {
    "gfx/models/ships/megastructures/dyson_sphere/_dyson_sphere_entities.asset":
        r"dyson_sphere_(phase_0\d|part_\d|frame|destroyed)_entity",
    "gfx/models/ships/superstructures/dyson_swarm/dyson_swarm.asset": r"dyson_swarm_phase_\d_entity",
    "gfx/models/ships/megastructures/matter_decompressor/matter_decompressor_01.asset":
        r"matter_decompressor_(stage_\d(_construction)?|destroyed_01)_entity",
    "gfx/models/ships/megastructures/quantum_catapult/quantum_catapult_01.asset":
        r"quantum_catapult_(stage_\d|01_destroyed)_entity",
    "gfx/models/ships/megastructures/galactic_crucible/_infernal_01_galactic_crucible.asset":
        r"galactic_crucible_(phase_0\d|part_\d|construction_frame|destroyed)_entity",
    "gfx/models/ships/megastructures/dyson_gun/dyson_gun_01.asset": r"dyson_gun_01_(stage_\d|destroyed)_entity",
}
for rel, pat in STAR_MEGA.items():
    scale_models(GAME, rel, pat, BODY, "原版", "包住恒星的巨构，跟恒星一起缩小")

# ---------------------------------------------------------------- 5. 按星球大小摆放的护盾（环境物体）
SHIELDS = [(MEM, f"gfx/models/planets/{f}", "More Events Mod") for f in (
    "mem_malthus_planet_shield_ambient_scaling.asset",
    "mem_malthus_planet_shield_alt_ambient_scaling.asset",
    "mem_malthus_planet_shield_orila_ambient_scaling.asset",
)]
for root, rel, tag in SHIELDS:
    if (root / rel).exists():
        scale_models(root, rel, None, BODY, tag, "护盾随星球一起缩小")
    else:
        print("skip (not found)", rel)

# ---------------------------------------------------------------- 6. defines
write("common/defines/zz_atb_celestial_scale_defines.txt", header("原版 defines 的几项", "") + f"""NGraphics = {{
	ASTEROID_MAX_SCALE = {fmt(4.0 * BODY)}	# 原版 4.0：小行星带碎石的最大尺寸，×{fmt(BODY)}
}}

# 星球、恒星变小以后，舰船和空间站原版的停靠距离显得离得很远。取 Real Space - System Scale 的值：
# 它把空间放大 6 倍、星体基本不动，看上去的比例和这里（空间不动、星体缩小）相近
NGameplay = {{
	PLANET_SHIP_ORBIT_DISTANCE = 4.0	# 原版 10：舰队在星球旁停靠的距离
	PLANET_STATION_ORBIT_DISTANCE = 3.5	# 原版 6：采矿站、研究站离星球的距离
	STARBASE_ORBIT_DISTANCE = 7.0		# 原版 15：恒星基地离恒星的距离
}}
""", "原版")

# ================================================================ 人造设施（× ART）
# ---------------------------------------------------------------- 7. 恒星基地、空间站（舰船尺寸 hull_scale）
STATION_CLASSES = {"shipclass_starbase": STATION, "shipclass_military_station": STATION,
                   "shipclass_mining_station": ART, "shipclass_research_station": ART,
                   "shipclass_observation_station": ART, "shipclass_habitat_station": ART}
SKIP_SIZES = re.compile(r"^(juggernaut|\w*arkship\w*)$")  # 主宰（本 MOD 改成了战舰）、游牧方舟（会飞，按舰船算）
for root, tag in ((GAME, "原版"), (RAA, "! Reworked Advanced Ascension"), (MEM, "More Events Mod")):
    for p in sorted((root / "common/ship_sizes").glob("*.txt")):
        text = read(p)
        changed, out, last = [], [], 0
        for s, e, k in blocks(text, r"^([A-Za-z][\w]*)\s*=\s*\{"):
            b = text[s:e]
            tl = top_level(b)
            cl = re.search(r'^\s*class\s*=\s*"?(\w+)', tl, re.M)
            if not cl or cl.group(1) not in STATION_CLASSES or SKIP_SIZES.match(k):
                continue
            if re.search(r"^\s*scales_with_planet\s*=\s*yes", tl, re.M):
                continue  # 轨道环：原版本来就跟星球大小走
            f = STATION_CLASSES[cl.group(1)]
            m = re.search(r"^(\s*)hull_scale\s*=\s*([\d.]+)[^\n]*$", b, re.M)
            if m and m.group(0).split("#")[0].strip() and top_level(b).count("hull_scale"):
                old = float(m.group(2))
                nb = b[:m.start()] + f"{m.group(1)}hull_scale = {fmt(old * f)}\t# 原 {m.group(2)}，×{fmt(f)}" + b[m.end():]
            else:
                first = b.index("\n") + 1
                nb = b[:first] + f"\thull_scale = {fmt(f)}\t# 原版没写（1.0），×{fmt(f)}\n" + b[first:]
            out.append(text[last:s] + nb)
            last = e
            changed.append(f"{k}×{fmt(f)}")
        if changed:
            out.append(text[last:])
            rel = f"common/ship_sizes/{p.name}"
            write(rel, header(f"{tag}的 {rel}", f"只给 {len(changed)} 种恒星基地 / 空间站 / 防御平台加 hull_scale："
                              + "、".join(changed[:12]) + ("等" if len(changed) > 12 else "") + "。") + "".join(out), tag)

# ---------------------------------------------------------------- 8. 人造巨构与栖息地（模型）
ART_MODELS = [
    "gfx/models/ships/megastructures/gateway/gateway.asset",
    "gfx/models/ships/megastructures/gateway/gateway_portal.asset",
    "gfx/models/ships/megastructures/hyper_relay/hyper_relay_01.asset",
    "gfx/models/ships/megastructures/mega_shipyard/mega_shipyard_01.asset",
    "gfx/models/ships/megastructures/strategic_coordination_center/strategic_coordination_center_01.asset",
    "gfx/models/ships/megastructures/mega_art_institution/mega_art_institution_01.asset",
    "gfx/models/ships/megastructures/interstellar_assembly/interstellar_assembly_01.asset",
    "gfx/models/ships/megastructures/think_tank/think_tank_01.asset",
    "gfx/models/ships/megastructures/spy_orb/_spyorb_entities.asset",
    "gfx/models/ships/megastructures/grand_archive/_grand_archive_entities.asset",
    "gfx/models/ships/megastructures/construction_platform/construction_platform_01.asset",
    "gfx/models/ships/superstructures/shroud_seal/shroud_seal.asset",
]
for rel in ART_MODELS:
    scale_models(GAME, rel, None, ART, "原版", "人造巨构")
# L 星门在 gatebuilder 画风文件里（同文件还有该画风的舰船，只改星门）
scale_models(GAME, "gfx/models/ships/gatebuilder_01/_gatebuilder_entities.asset", r"gatebuilder_01_gateway(_portal)?_entity", ART, "原版", "L 星门")
# 栖息地：各画风的舰船模型文件里（只改栖息地），毁坏的栖息地在 _other_entities.asset
for p in sorted((GAME / "gfx/models/ships").glob("*/_*_ships_entities.asset")):
    rel = p.relative_to(GAME).as_posix()
    if re.search(r'name\s*=\s*"\w*habitat_phase_0\d_entity"', read(p)):
        scale_models(GAME, rel, r"\w*habitat_phase_0\d_entity", ART, "原版", "栖息地")
scale_models(GAME, "gfx/models/ships/other/_other_entities.asset", r"habitat_destroyed_01_entity", ART, "原版", "毁坏的栖息地")

print(f"{len(SOURCES)} files, BODY = {fmt(BODY)}, STATION = {fmt(STATION)}, ART = {fmt(ART)}")
for w in WARN:
    print("WARN", w)
