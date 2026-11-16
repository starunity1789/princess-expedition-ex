"""2.9：AI 建造上限、AI 禁杂交飞升、AI 物种改造冷却、减卡 defines

用法：python tools/gen_ai_limits.py [mod 目录，默认仓库 mod/]

改数字只改下面的 CAPS / 常量，再重跑本脚本。原版更新后也要重跑：本脚本从原版（环世界优先取
Real Space 的版本）复制定义块，再插入我们的判断，所以覆盖的永远是当前版本的原版内容。

设计：
- 只限 AI，玩家不受影响（判断里第一条就是 is_ai = no 直接放行）
- 只数「自己开工建造的」：捡到、修复废墟、俘获的都不算。
  做法是开工时（on_megastructure_build_start）给工地打标记并给国家计数 +1；
  完工时（on_megastructure_built）再查一次，漏掉的补记。终身计数：拆掉、被毁、被占都不退名额
- 原版居住站自带一条按星系大小与难度算的 AI 上限（ai_habitat_cap，连捡到的一起数），用我们的规则替换掉它
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOD = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "mod"
GAME = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Stellaris")
REAL_SPACE = Path(r"C:\Program Files (x86)\Steam\steamapps\workshop\content\281990\937289339")

# 巨构类型 -> AI 终身建造上限
CAPS = {
    "habitat_central_complex": 7,   # 居住站
    "ring_world_1": 1,              # 环世界（第一阶段框架；修复废弃环世界是另一种巨构，不算）
    "gateway_0": 2,                 # 星门（框架；修复废弃星门不算）
    "hyper_relay": 18,              # 超空间中继器
}
SPECIES_MOD_COOLDOWN_DAYS = 20 * 360
DEFINES = {"TRIGGERED_MODIFIER_UPDATE_DELAY": 15, "POP_ETHOS_DIVERGENCE_INTERVAL": 30}

HEADER = "# 由 tools/gen_ai_limits.py 生成，不要手改\n"


def strip_comments(text):
    out = []
    for line in text.split("\n"):
        buf, q = [], False
        for ch in line:
            if ch == '"':
                q = not q
            if ch == "#" and not q:
                break
            buf.append(ch)
        out.append("".join(buf))
    return "\n".join(out)


def match_brace(text, open_idx):
    """text[open_idx] == '{'，返回配对 '}' 的下标（跳过注释与字符串）"""
    d, q, i = 0, False, open_idx
    while i < len(text):
        ch = text[i]
        if ch == '"':
            q = not q
        elif not q and ch == "#":
            i = text.index("\n", i) if "\n" in text[i:] else len(text)
            continue
        elif not q and ch == "{":
            d += 1
        elif not q and ch == "}":
            d -= 1
            if d == 0:
                return i
        i += 1
    raise ValueError("括号不配对")


def top_block(text, key):
    m = re.search(r"(?m)^" + re.escape(key) + r"\s*=\s*\{", text)
    if not m:
        raise SystemExit(f"找不到顶层定义 {key}")
    end = match_brace(text, m.end() - 1)
    return text[m.start():end + 1]


def child_span(block, key):
    """块内第一层子块 key = { ... } 的 (起点, '{' 下标, '}' 下标)"""
    body_start = block.index("{") + 1
    d, q, i = 0, False, body_start
    while i < len(block):
        ch = block[i]
        if ch == '"':
            q = not q
        elif not q and ch == "#":
            i = block.index("\n", i)
            continue
        elif not q and ch == "{":
            d += 1
        elif not q and ch == "}":
            d -= 1
        elif not q and d == 0 and block.startswith(key, i) and not (block[i - 1].isalnum() or block[i - 1] == "_"):
            m = re.match(re.escape(key) + r"\s*=\s*\{", block[i:])
            if m:
                ob = i + m.end() - 1
                return i, ob, match_brace(block, ob)
        i += 1
    raise SystemExit(f"块里找不到 {key} = {{")


def file_vars(text, block):
    """块里用到、在源文件顶部定义的 @变量"""
    used = set(re.findall(r"@([A-Za-z0-9_]+)", strip_comments(block)))
    defs = dict(re.findall(r"(?m)^@([A-Za-z0-9_]+)\s*=\s*(\S+)", text))
    return [f"@{k} = {defs[k]}" for k in sorted(used) if k in defs]


def insert_before_close(block, key, lines):
    _, _, close = child_span(block, key)
    nl = block.rindex("\n", 0, close) + 1
    return block[:nl] + "".join(f"\t\t{l}\n" for l in lines) + block[nl:]


def remove_vanilla_habitat_cap(block):
    m = re.search(r"\n[ \t]*# The AI has a hard cap on number of habitats[^\n]*\n[ \t]*hidden_trigger\s*=\s*\{", block)
    if not m:
        raise SystemExit("原版居住站的 AI 上限位置变了，检查 habitats.txt")
    close = match_brace(block, m.end() - 1)
    cut = block[m.start():close + 1]
    if "value:ai_habitat_cap" not in cut:
        raise SystemExit("原版居住站的 AI 上限位置变了，检查 habitats.txt")
    return block[:m.start()] + block[close + 1:]


def write(rel, text, bom=False):
    p = MOD / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    data = text.replace("\r\n", "\n").encode("utf-8")
    p.write_bytes((b"\xef\xbb\xbf" if bom else b"") + data)
    print("写出", rel)


def cap_line(t):
    return f"hidden_trigger = {{ from = {{ atb_ex_ai_mega_under_cap = {{ TYPE = {t} CAP = {CAPS[t]} }} }} }}"


# ---------------------------------------------------------------- 巨构
SOURCES = {
    "habitat_central_complex": [GAME / "common/megastructures/habitats.txt"],
    "ring_world_1": [REAL_SPACE / "common/megastructures/00_ring_world.txt", GAME / "common/megastructures/00_ring_world.txt"],
    "gateway_0": [GAME / "common/megastructures/05_gateways.txt"],
    "hyper_relay": [GAME / "common/megastructures/14_hyper_relay.txt"],
}
parts, varlines = [], []
for t, cands in SOURCES.items():
    src = next(p for p in cands if p.exists())
    text = src.read_text(encoding="utf-8-sig")
    blk = top_block(text, t)
    if t == "habitat_central_complex":
        blk = remove_vanilla_habitat_cap(blk)
    blk = insert_before_close(blk, "possible", ["# 皇女的远征军EX：AI 建造上限（只数自己开工的）", cap_line(t)])
    varlines += [v for v in file_vars(text, blk) if v not in varlines]
    origin = "Real Space" if REAL_SPACE in src.parents else "原版"
    parts.append(f"# 来源：{origin} {src.name}\n{blk}\n")
mega = HEADER + "# 文件名以 zz_ 开头，排在原版与 Real Space 之后，同名定义以这里为准\n\n" + \
    "".join(v + "\n" for v in varlines) + "\n" + "\n".join(parts)
write("common/megastructures/zz_atb_ex_ai_limits.txt", mega)

# ---------------------------------------------------------------- 跨物种杂交：AI 不能选
text = (GAME / "common/ascension_perks/00_ascension_perks.txt").read_text(encoding="utf-8-sig")
blk = top_block(text, "ap_xeno_compatibility")
blk = insert_before_close(blk, "potential", ["# 皇女的远征军EX：AI 不选（大量杂交亚种拖慢后期，效果也弱）", "is_ai = no"])
write("common/ascension_perks/zz_atb_ex_ai_limits.txt",
      HEADER + "# 来源：原版 00_ascension_perks.txt\n" + "".join(v + "\n" for v in file_vars(text, blk)) + "\n" + blk + "\n")

# ---------------------------------------------------------------- 物种改造：AI 冷却
text = (GAME / "common/game_rules/00_rules.txt").read_text(encoding="utf-8-sig")
blk = top_block(text, "can_modify_species")
ob = blk.index("{")
blk = blk[:ob + 1] + (
    "\n\t# 皇女的远征军EX：AI 每完成一次物种改造，20 年内不能再改（频繁改造会拖住科研）\n"
    "\thidden_trigger = {\n\t\tROOT = {\n\t\t\tOR = {\n\t\t\t\tis_ai = no\n"
    "\t\t\t\tNOT = { has_country_flag = atb_ex_species_mod_cooldown }\n\t\t\t}\n\t\t}\n\t}\n") + blk[ob + 1:]
write("common/game_rules/zz_atb_ex_ai_limits.txt",
      HEADER + "# 来源：原版 00_rules.txt\n" + "".join(v + "\n" for v in file_vars(text, blk)) + "\n" + blk + "\n")

# ---------------------------------------------------------------- 触发器 / 效果 / 事件 / on_actions
types_or = "\n".join(f"\t\tis_megastructure_type = {t}" for t in CAPS)
count_ifs = "\n".join(
    f"\t{'if' if i == 0 else 'else_if'} = {{\n\t\tlimit = {{ is_megastructure_type = {t} }}\n"
    f"\t\troot = {{ change_variable = {{ which = atb_ex_built_{t} value = 1 }} }}\n\t}}"
    for i, t in enumerate(CAPS))
write("common/scripted_triggers/atb_ex_ai_limits_triggers.txt", HEADER + f"""
# 国家作用域：这个国家还能不能再开工一座 $TYPE$
atb_ex_ai_mega_under_cap = {{
	OR = {{
		is_ai = no
		NOT = {{ is_variable_set = atb_ex_built_$TYPE$ }}
		check_variable = {{ which = atb_ex_built_$TYPE$ value < $CAP$ }}
	}}
}}

# 巨构作用域：受 AI 上限管的类型
atb_ex_ai_capped_megastructure = {{
	OR = {{
{types_or}
	}}
}}
""")
write("common/scripted_effects/atb_ex_ai_limits_effects.txt", HEADER + f"""
# 巨构作用域，root = 建造它的国家：打标记并给 root 计数 +1
atb_ex_count_megastructure = {{
	set_megastructure_flag = atb_ex_counted
{count_ifs}
}}
""")
write("events/atb_ex_ai_limits_events.txt", HEADER + f"""
namespace = atb_ex_lim

# 开工：root = 国家，from = 星系。给本国在这个星系里新出现、还没记过的工地计数
# 3.4：原版偶尔传一个空星系（id 4294967295），先判断存在；这种情况在完工（atb_ex_lim.2）时补记
country_event = {{
	id = atb_ex_lim.1
	hide_window = yes
	is_triggered_only = yes

	trigger = {{
		exists = from
	}}

	immediate = {{
		from = {{
			every_system_megastructure = {{
				limit = {{
					atb_ex_ai_capped_megastructure = yes
					NOT = {{ has_megastructure_flag = atb_ex_counted }}
					exists = owner
					owner = {{ is_same_value = root }}
				}}
				atb_ex_count_megastructure = yes
			}}
		}}
	}}
}}

# 完工：root = 国家，from = 巨构。开工时没记上的在这里补记
country_event = {{
	id = atb_ex_lim.2
	hide_window = yes
	is_triggered_only = yes

	trigger = {{
		from = {{
			atb_ex_ai_capped_megastructure = yes
			NOT = {{ has_megastructure_flag = atb_ex_counted }}
		}}
	}}

	immediate = {{
		from = {{ atb_ex_count_megastructure = yes }}
	}}
}}

# 物种改造完成：this = 国家。AI 进入 {SPECIES_MOD_COOLDOWN_DAYS // 360} 年冷却
country_event = {{
	id = atb_ex_lim.3
	hide_window = yes
	is_triggered_only = yes

	trigger = {{ is_ai = yes }}

	immediate = {{
		set_timed_country_flag = {{ flag = atb_ex_species_mod_cooldown days = {SPECIES_MOD_COOLDOWN_DAYS} }}
	}}
}}
""")
write("common/on_actions/atb_ex_ai_limits_on_actions.txt", HEADER + """
on_megastructure_build_start = {
	events = {
		atb_ex_lim.1
	}
}

on_megastructure_built = {
	events = {
		atb_ex_lim.2
	}
}

on_modification_completion = {
	events = {
		atb_ex_lim.3
	}
}
""")

# ---------------------------------------------------------------- defines
write("common/defines/zz_atb_ex_performance_defines.txt", HEADER + "# 减轻后期卡顿：原版 5 天 / 18 天\nNGameplay = {\n" +
      "".join(f"\t{k} = {v}\n" for k, v in DEFINES.items()) + "}\n")
print("完成")
