"""3.7：把「东方project领袖」（创意工坊 2983419228，作者已停更）的一部分内容整合进皇女的远征军。

用法（在仓库根目录，原 MOD 需要还在订阅目录里）：
    python tools/gen_touhou.py

搬进来的（ID 不改；生成的文件都以 atb_th_ 开头）：
- 13 个东方国策与 13 个对应议员（AI 不会选：原作者就把 AI 权重设成 0）
- 34 位东方角色：创建效果、特质组、他们用到的全部领袖特质（以及红魔眷族国策的物种特质、河童的物种特质）
- 选了国策时开局给对应角色（原作的 touhou_paragon.1 改写为 atb_th.1：只给角色、命定特质和原版科技）
- 首都决议「招募幻想乡来客」：花 2000 食物随机招募一位还没有的角色（国策之外唯一的获得途径）
- 两件武器 Master Spark（X 槽）/ Final Spark（T 槽）：改成普通科技，接在粒子光矛之后，所有国家都能研究
- 河童飞地（河童轨道开发集团）：固定生成在大传承者旁边，一条航道相连；保留技术移民、科学家派遣、
  建造援助、机器人生产线，去掉扩展船坞、非想天则、雇佣河城荷取、被摧毁后重建
- 用到的全部美术（肖像、特质/国策/科技/部件图标、武器特效与音效、河童肖像）和中文本地化

不搬的：符卡系统、建筑/岗位/区划/特殊地形、事件链、局势、议程、领袖抽奖与来访事件、特殊舰船、陆军、
其余科技、对原版规则/事件/条件的覆盖。被保留内容里引用到它们的地方一律删掉（单行修正、背景岗位等），
引用到被删事件的选项整个删掉。

生成后不再依赖原 MOD。
"""
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
MOD = ROOT / "mod"
TH = Path(r"C:\Program Files (x86)\Steam\steamapps\workshop\content\281990\2983419228")
GAME = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Stellaris")
if not (TH / "common").exists():
    raise SystemExit(f"找不到东方project领袖：{TH}")
HEAD = "# 由 tools/gen_touhou.py 从「东方project领袖」（创意工坊 2983419228）抽取改写，请勿手改\n"
RECRUIT_COST = {"scientist": 500, "commander": 1000, "official": 2000}   # 招募决议的食物花费
CLASS_ZH = {"scientist": "科学家", "commander": "指挥官", "official": "行政官"}


# ---------------------------------------------------------------- 解析工具
def strip_comments(t: str) -> str:
    out = []
    for line in t.split("\n"):
        q = False
        for i, c in enumerate(line):
            if c == '"':
                q = not q
            elif c == "#" and not q:
                line = line[:i]
                break
        out.append(line.rstrip())
    return "\n".join(out)


def match_end(t: str, open_idx: int) -> int:
    """t[open_idx] == '{'，返回匹配的 '}' 之后的位置"""
    d, i, q = 0, open_idx, False
    while i < len(t):
        c = t[i]
        if c == '"':
            q = not q
        elif not q:
            if c == "{":
                d += 1
            elif c == "}":
                d -= 1
                if d == 0:
                    return i + 1
        i += 1
    raise ValueError("括号不配对")


def top_blocks(t: str):
    """[(key, start, end)]，只取行首的 key = { ... }"""
    out = []
    for m in re.finditer(r"(?m)^([A-Za-z_@][\w.:@-]*)\s*=\s*\{", t):
        if out and m.start() < out[-1][2]:
            continue
        out.append((m.group(1), m.start(), match_end(t, m.end() - 1)))
    return out


def read(p: Path) -> str:
    return strip_comments(p.read_text(encoding="utf-8-sig", errors="replace"))


# 原 MOD 的所有顶层定义
DEFS = {}           # key -> (相对路径, 文本)
for p in sorted((TH / "common").rglob("*.txt")):
    t = read(p)
    for k, s, e in top_blocks(t):
        DEFS.setdefault(k, (p.relative_to(TH).as_posix(), t[s:e]))
EVENTS = {}         # id -> 文本
for p in sorted((TH / "events").glob("*.txt")):
    t = read(p)
    for k, s, e in top_blocks(t):
        b = t[s:e]
        m = re.search(r"\bid\s*=\s*([\w.]+)", b)
        if m:
            EVENTS.setdefault(m.group(1), b)
VANILLA = set()
for p in (GAME / "common").rglob("*.txt"):
    VANILLA |= set(re.findall(r"(?m)^([A-Za-z_@][\w.:@-]*)\s*=", read(p)))
for p in (GAME / "events").glob("*.txt"):
    VANILLA |= set(re.findall(r"(?m)^\s*id\s*=\s*([\w.]+)", read(p)))


def keyed_block(folder: str, kind: str, key: str) -> str:
    """component_template / component_set 这类靠内部 key 区分的块"""
    for p in sorted((TH / "common" / folder).rglob("*.txt")):
        t = read(p)
        for k, s, e in top_blocks(t):
            b = t[s:e]
            if k == kind and re.search(rf'\bkey\s*=\s*"?{re.escape(key)}"?\s', b):
                return b
    raise SystemExit(f"找不到 {kind} {key}")


# ---------------------------------------------------------------- 保留清单
creator_txt = DEFS["thl_leader_creator_core"][1] and read(TH / "common/scripted_effects/touhou_paragon_leader_creator_effects.txt")
CREATE = re.findall(r"(?m)^(create_\w+_leader)\s*=", creator_txt)
TRAITSETS = re.findall(r"(?m)^(add_\w+_traits)\s*=", creator_txt)
CIVICS = [k for k, (f, _) in DEFS.items() if f.startswith("common/governments/civics")]
COUNCILORS = [k for k, (f, _) in DEFS.items() if f.startswith("common/governments/councilors")]

KEEP = set(CREATE) | set(TRAITSETS) | set(CIVICS) | set(COUNCILORS) | {"thl_leader_creator_core"}
KEEP |= {"trait_kappa_aquatic", "kappa_enclave", "kappa_enclave_init", "kappa_enclave_stage_1", "kappa_enclave_stage_2",
         "modifier_kappa_construction", "modifier_kappa_robot", "touhou_value_reimu_excessive_amount", "tech_master_spark",
         "tech_final_spark", "thl_leader_trait_destined", "NITORI"}
ENCLAVE_EVENTS = ["300", "301", "302", "303", "305", "310", "320", "340", "341", "350", "351"]
KEEP |= {f"touhou_paragon_enclave.{e}" for e in ENCLAVE_EVENTS}
KEEP.discard("thl_ethic_leader_creator")
CREATE = [c for c in CREATE if c != "thl_ethic_leader_creator"]
# 特质闭包
todo = list(KEEP)
while todo:
    k = todo.pop()
    body = DEFS.get(k, ("", EVENTS.get(k, "")))[1]
    for tok in set(re.findall(r"[A-Za-z_][\w]*", body)):
        if tok in DEFS and DEFS[tok][0].startswith("common/traits") and tok not in KEEP:
            KEEP.add(tok)
            todo.append(tok)
# 闭包会顺着河童星系初始化走到非想天则机器人工人的物种特质；那个物种属于不搬的早苗科技线，整块删
KEEP.discard("trait_sanae_robot_worker")
# 原作重定义了几个原版特质（同名）；不搬，角色直接用原版的
KEEP -= VANILLA
TRAITS = sorted(k for k in KEEP if k in DEFS and DEFS[k][0].startswith("common/traits"))

JOBS = {k for k, (f, _) in DEFS.items() if f.startswith("common/pop_jobs")}
SCRIPTED_MODS = {k for k, (f, _) in DEFS.items() if f.startswith("common/scripted_modifiers")}
RES = re.compile(r"thl_(mana|bomb|spirit)")


def is_bad(tok: str, line: str) -> bool:
    if tok in KEEP or tok in VANILLA:
        return False
    if re.search(rf"_flag\s*=\s*{re.escape(tok)}\b", line) or re.search(rf"\bflag\s*=\s*{re.escape(tok)}\b", line):
        return False
    if tok in DEFS or tok in EVENTS or tok in SCRIPTED_MODS:
        return True
    if RES.search(tok):
        return True
    if tok.startswith(("job_", "pop_", "planet_")):
        return any(re.search(rf"(^|_){re.escape(j)}(_|$)", tok) for j in JOBS)
    return False


def enclosing(t: str, pos: int, keys) -> tuple | None:
    """包含 pos 的、键名在 keys 里的最近一层块的 (start, end)"""
    best = None
    for m in re.finditer(r"([A-Za-z_][\w.]*)\s*=\s*\{", t[:pos]):
        if m.group(1) in keys:
            e = match_end(t, m.end() - 1)
            if e > pos:
                ls = t.rfind("\n", 0, m.start()) + 1
                best = (ls, e)
    return best


REMOVED = defaultdict(int)


def clean(t: str) -> str:
    """删掉引用了被丢弃内容的行；事件跳转所在的 option、被丢弃特质所在的 create_species 整块删"""
    changed = True
    while changed:
        changed = False
        for m in re.finditer(r"[A-Za-z_][\w.]*", t):
            tok = m.group(0)
            ls = t.rfind("\n", 0, m.start()) + 1
            le = t.find("\n", m.end())
            le = len(t) if le < 0 else le
            line = t[ls:le]
            if not is_bad(tok, line):
                continue
            span = None
            if tok in EVENTS:
                span = enclosing(t, m.start(), {"option"})
            elif tok in DEFS and DEFS[tok][0].startswith("common/traits"):
                span = enclosing(t, m.start(), {"create_species"})
            if span is None:
                if line.count("{") != line.count("}"):
                    s = t.find("{", ls)
                    span = (ls, match_end(t, s))
                else:
                    span = (ls, le)
            end = span[1] + 1 if span[1] < len(t) and t[span[1]] == "\n" else span[1]
            REMOVED[tok] += 1
            t = t[:span[0]] + t[end:]
            changed = True
            break
    return t


written = []


def write(rel: str, text: str, bom: bool = False):
    p = MOD / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes((b"\xef\xbb\xbf" if bom else b"") + text.replace("\r\n", "\n").encode("utf-8"))
    written.append(rel)


def defs_text(keys) -> str:
    return "\n\n".join(clean(DEFS[k][1]) for k in keys) + "\n"


# ---------------------------------------------------------------- 国策、议员、特质、角色
write("common/governments/civics/atb_th_civics.txt", HEAD + "# 13 个东方国策（AI 权重为 0，只有玩家会选）\n\n" + defs_text(CIVICS))
write("common/governments/councilors/atb_th_councilors.txt", HEAD + "\n" + defs_text(COUNCILORS))
# 特质说明（custom_tooltip）描述的机制如果实现在不搬的内容里（原作别处的事件/法令/建筑/决议引用了这个特质），
# 机制已不存在，说明也删掉，特质只剩它本身的修正（变白板）。再生特质例外：改用原版旗标 leader_death_events_blocked
# 实现「不会死于意外」，说明改写（见本地化 own）。
KEPT_FILES = {"common/traits/", "common/governments/", "common/scripted_effects/touhou_paragon_leader_creator_effects.txt"}
elsewhere = set()
for p in list((TH / "common").rglob("*.txt")) + list((TH / "events").glob("*.txt")):
    rel = p.relative_to(TH).as_posix()
    if any(rel.startswith(k) for k in KEPT_FILES):
        continue
    elsewhere |= set(re.findall(r"\b(?:thl_leader_trait|leader_trait|thl_thl_leader_trait|trait)_\w+", read(p))) & set(TRAITS)
REGEN = {t for t in TRAITS if t.startswith("thl_leader_trait_regeneration")}
dead_tooltips = sorted(elsewhere - REGEN)


# 原作里 4.x 已失效的修正：能换成现行写法的换掉，没有对应物的删掉
MODIFIER_FIX = {
    "district_farming_max": "district_farming_max_add",
    "planet_jobs_specialist_upkeep_mult": "planet_jobs_upkeep_mult",
    "pop_demotion_time_mult": None,
    "piracy_suppression_mult": None,
}


def modernize(b):
    for old, new in MODIFIER_FIX.items():
        if new:
            b = re.sub(rf"(?m)^(\s*){old}(\s*=)", rf"\1{new}\2", b)
        else:
            b = re.sub(rf"(?m)^\s*{old}\s*=.*\n", "", b)
    return b


def trait_text(k):
    b = modernize(clean(DEFS[k][1]))
    if k in dead_tooltips:
        b = re.sub(r"(?m)^\s*custom_tooltip(?:_with_modifiers)?\s*=\s*\"?[\w.]+\"?\s*\n", "", b)
    return b


write("common/traits/atb_th_traits.txt", HEAD + f"""# 东方角色与河童用到的特质（{len(TRAITS)} 个）
# 机制在原作别处实现、这里已不存在的特质，去掉了说明文字：{' '.join(dead_tooltips)}

""" + "\n\n".join(trait_text(k) for k in TRAITS) + "\n")


def core_text():
    """所有东方角色都是英杰典范（leader_tier_renowned，紫色底框）"""
    b = clean(DEFS["thl_leader_creator_core"][1])
    a = "\t\tclass = $CLASS$\n"
    assert b.count(a) == 1
    return b.replace(a, a + "\t\ttier = leader_tier_renowned\n")


# 原作给的原版特质在 4.5 里加不上（职业不符或与同角色另一特质互斥），换成同职业里效果相近的，没有对应物的删掉
TRAIT_FIX = {
    ("yuka", "leader_trait_arbiter"): "leader_trait_pop_focused_2",            # 总督特质 4.5 只给指挥官 → 工人产出
    ("yuka", "leader_trait_farming_focus"): None,                              # 她已有农业出身（食物产出），不重复
    ("rin", "leader_trait_enlister"): "leader_trait_army_veteran",              # 陆军建造与花费
    ("rin", "leader_trait_generator_focus_3"): "leader_trait_forge_focus_3",    # 灼热地狱的熔炉：合金产出
    ("onoduka", "trait_ruler_deep_connections"): None,                         # 只限官员，指挥官没有对应
    ("tewi", "leader_trait_insider_trading"): None,                            # 与贸易专精互斥，原本就加不上
}


def traitset_text(k):
    b = clean(DEFS[k][1])
    g = re.match(r"add_(\w+)_traits$", k).group(1)
    for (grp, old), new in TRAIT_FIX.items():
        if grp != g:
            continue
        pat = rf"(?m)^(\s*add_trait = \{{ trait = ){old}( .*)\n"
        assert re.search(pat, b), (k, old)
        b = re.sub(pat, (rf"\g<1>{new}\g<2>" + "\n") if new else "", b)
    return b


def stem(c):
    return re.match(r"create_(\w+)_leader$", c).group(1)


def create_text(c):
    """每位东方领袖：标记（重生、不计入领袖上限用）、免疫原版意外死亡事件；国策版另带命定特质"""
    b = clean(DEFS[c][1]).rstrip()[:-1].rstrip()
    destined = "\n\t\tadd_trait = { trait = thl_leader_trait_destined }" if stem(c).startswith("civic_") else ""
    return b + f"""
	last_created_leader = {{
		set_leader_flag = atb_th_leader
		set_leader_flag = atb_th_rc_{stem(c)}
		set_leader_flag = leader_death_events_blocked{destined}
	}}
}}"""


write("common/scripted_effects/atb_th_leader_effects.txt", HEAD + """
# 东方角色：thl_leader_creator_core 建一个专属物种和一位领袖，add_<角色>_traits 加特质组。
# 原作的领袖抽奖（thl_ethic_leader_creator）不搬；角色只能由国策开局获得，或用首都决议招募。
# 每位东方领袖都带原版旗标 leader_death_events_blocked（不会死于意外事件）；
# 仍会因寿命、舰队覆灭等死亡，死后由 atb_th.2 按初始等级和状态重新生成同一角色。
# 东方领袖不计入领袖上限：游戏规则 should_count_towards_leader_cap 认 atb_th_leader 旗标（atb_th_rules.txt）。

""" + "\n\n".join([core_text()] + [create_text(c) for c in CREATE]) + "\n\n"
      + "\n\n".join(traitset_text(k) for k in TRAITSETS) + "\n")
vals = [k for k in KEEP if k in DEFS and DEFS[k][0].startswith("common/script_values")]
write("common/script_values/atb_th_values.txt", HEAD + "\n" + defs_text(sorted(vals)))
mods = [k for k in KEEP if k in DEFS and DEFS[k][0].startswith("common/static_modifiers")]
write("common/static_modifiers/atb_th_modifiers.txt", HEAD + "\n" + defs_text(sorted(mods)))

# 角色清单：同一角色的国策版（create_civic_*）与两种诹访子只算一个
CHARS = sorted({re.match(r"create_(?:civic_)?(\w+?)(?:_commander)?_leader", c).group(1) for c in CREATE})
RECRUIT = {ch: f"create_{ch}_leader" for ch in CHARS if f"create_{ch}_leader" in CREATE}

# ---------------------------------------------------------------- 国策开局给角色
CIVIC_GRANTS = [
    ("hakurei_shinto", ["reimu"], []),
    ("moriya_shinto", ["sanae"], ["tech_storm_prediction_1"]),
    ("kirisame_magic", ["marisa"], []),
    ("scarlet_allience", ["sakuya"], []),
    ("nether_world", ["youmu"], []),
    ("penglai_medcine", ["reisen"], ["tech_genome_mapping", "tech_gene_tailoring", "tech_frontier_health"]),
    ("hifuu", ["merry", "renko"], []),
]
grants = []
for civic, chars, techs in CIVIC_GRANTS:
    has = f"has_civic = civic_{civic}" + (f"\n\t\t\t\t\thas_civic = civic_{civic}_corp" if f"civic_{civic}_corp" in CIVICS else "")
    body = "".join(f"""
			create_civic_{ch}_leader = yes
			set_country_flag = atb_th_got_{ch}""" for ch in chars)
    body += "".join(f"""
			give_technology = {{ tech = {t} message = no }}""" for t in techs)
    grants.append(f"""		if = {{
			limit = {{
				OR = {{
					{has}
				}}
			}}{body}
		}}""")
RESPAWN = "\n".join(f"""		{"if" if i == 0 else "else_if"} = {{
			limit = {{ from = {{ has_leader_flag = atb_th_rc_{stem(c)} }} }}
			{c} = yes
		}}""" for i, c in enumerate(CREATE))
EVENTS_OUT = HEAD + f"""
namespace = atb_th

# 开局（on_game_start_country）：选了东方国策的国家得到对应角色（原作的 touhou_paragon.1，
# 只保留角色、命定特质与原版科技；神社、舰船、幽灵人口等依赖已删内容的部分去掉）
country_event = {{
	id = atb_th.1
	hide_window = yes
	is_triggered_only = yes

	immediate = {{
{chr(10).join(grants)}
	}}
}}

# 东方领袖死亡（on_leader_death，From = 死去的领袖）：按初始等级和状态重新生成同一角色
country_event = {{
	id = atb_th.2
	hide_window = yes
	is_triggered_only = yes

	trigger = {{
		from = {{ has_leader_flag = atb_th_leader }}
	}}

	immediate = {{
{RESPAWN}
	}}
}}
"""
# ---------------------------------------------------------------- 河童飞地事件
enc = []
for e in ENCLAVE_EVENTS:
    enc.append(clean(EVENTS[f"touhou_paragon_enclave.{e}"]))
EVENTS_OUT += """
# ---------------------------------------------------------------- 河童飞地（原作 touhou_paragon_enclave.*）
# 菜单里的扩展船坞、非想天则、雇佣河城荷取三项与被摧毁后重建不搬
namespace = touhou_paragon_enclave

""" + "\n\n".join(enc) + "\n"
write("events/atb_th_events.txt", EVENTS_OUT)

write("common/on_actions/atb_th_on_actions.txt", HEAD + """
on_game_start_country = {
	events = {
		atb_th.1
	}
}

# 东方领袖死后重生
on_leader_death = {
	events = {
		atb_th.2
	}
}

# 河童飞地的外交界面
on_custom_diplomacy = {
	events = {
		touhou_paragon_enclave.300
	}
}

# 河童飞地的首次接触
on_first_contact_stage_1_no_path = {
	events = {
		touhou_paragon_enclave.301
	}
}
""")

# ---------------------------------------------------------------- 不计入领袖上限
# 原版的写法：游戏规则 should_count_towards_leader_cap（传奇典范、裂隙扭曲者等都走这里），
# 从原版 00_rules.txt 照抄，NOR 里加一条东方领袖旗标
rules = read(GAME / "common/game_rules/00_rules.txt")
s = rules.index("should_count_towards_leader_cap = {")
rule = rules[s:match_end(rules, rules.index("{", s)) + 1]
assert "\tNOR = {\n" in rule
rule = rule.replace("\tNOR = {\n", "\tNOR = {\n\t\thas_leader_flag = atb_th_leader\t# 东方领袖\n", 1)
write("common/game_rules/atb_th_rules.txt", HEAD + """
# 覆盖原版 should_count_towards_leader_cap（common/game_rules/00_rules.txt）：东方领袖不计入领袖上限。
# This = leader
""" + rule + "\n")

# ---------------------------------------------------------------- 招募决议（按职业分三个）
def char_class(fn):
    blk = clean(DEFS[fn][1])
    return re.search(r"(?<!\w)CLASS\s*=\s*(\w+)", blk).group(1)


RCLASS = {ch: char_class(fn) for ch, fn in RECRUIT.items()}
trig, effs, decs = [], [], []
for cls, cost in RECRUIT_COST.items():
    chars = [ch for ch in RECRUIT if RCLASS[ch] == cls]
    assert chars, cls
    nand = "\n".join(f"\t\thas_country_flag = atb_th_got_{ch}" for ch in chars)
    entries = "\n".join(f"""		10 = {{
			modifier = {{ factor = 0 has_country_flag = atb_th_got_{ch} }}
			{RECRUIT[ch]} = yes
			set_country_flag = atb_th_got_{ch}
		}}""" for ch in chars)
    trig.append(f"""# 国家作用域：还有没招募到的东方{CLASS_ZH[cls]}（{len(chars)} 位：{' '.join(chars)}）
atb_th_has_unrecruited_{cls} = {{
	NAND = {{
{nand}
	}}
}}""")
    effs.append(f"""# 国家作用域：随机招募一位还没有的东方{CLASS_ZH[cls]}
atb_th_recruit_{cls} = {{
	random_list = {{
{entries}
	}}
}}""")
    decs.append(f"""# {cost} 食物：随机招募一位还没有的东方{CLASS_ZH[cls]}（{len(chars)} 位）
decision_atb_th_recruit_{cls} = {{
	owned_planets_only = yes
	sound = event_administrative_work
	icon = decision_luxuries

	resources = {{
		category = decisions
		cost = {{
			food = {cost}
		}}
	}}

	potential = {{
		is_capital = yes
		owner = {{
			is_ai = no
			atb_th_has_unrecruited_{cls} = yes
		}}
	}}

	effect = {{
		custom_tooltip = decision_atb_th_recruit_{cls}_tt
		hidden_effect = {{
			owner = {{
				atb_th_recruit_{cls} = yes
			}}
		}}
	}}

	ai_weight = {{
		weight = 0
	}}
}}""")
write("common/scripted_triggers/atb_th_triggers.txt", HEAD + "\n" + "\n\n".join(trig) + "\n")
write("common/scripted_effects/atb_th_recruit_effects.txt", HEAD + "\n" + "\n\n".join(effs) + "\n")
write("common/decisions/atb_th_decisions.txt", HEAD + """
# 招募幻想乡来客：玩家首都决议，按职业分三个，花食物随机招募一位还没有的该职业东方角色，直到招完。
# 这是东方国策之外唯一的获得途径；AI 看不到。

""" + "\n\n".join(decs) + "\n")

# ---------------------------------------------------------------- 武器：普通科技
sets = "\n\n".join(keyed_block("component_sets", "component_set", k) for k in ("MASTER_SPARK", "FINAL_SPARK"))
comps = "\n\n".join(clean(keyed_block("component_templates", "weapon_component_template", k)) for k in ("MASTER_SPARK", "FINAL_SPARK"))
write("common/component_sets/atb_th_component_sets.txt", HEAD + "\n" + sets + "\n")
write("common/component_templates/atb_th_weapons.txt", HEAD + "# 数值沿用原作（直接写在模板里，不在原版武器 CSV 里，所以不受本 MOD 的 X 槽位加强影响）\n\n" + comps + "\n")
WEAPON_AI = """	weight_modifier = {
		modifier = {
			factor = 1.25
			has_ethic = ethic_militarist
		}
		modifier = {
			factor = 1.5
			has_ethic = ethic_fanatic_militarist
		}
	}

	ai_weight = {
		modifier = {
			factor = 1.25
			has_ethic = ethic_militarist
		}
		modifier = {
			factor = 1.5
			has_ethic = ethic_fanatic_militarist
		}
		inline_script = {
			script = ai/weapon_preference_weight
			WEAPON_TYPE = weapon_type_energy
		}
	}"""
write("common/technology/atb_th_tech.txt", HEAD + f"""
# 原作只有拥有魔理沙的国家才能研究；改成普通科技，接在粒子光矛之后，所有国家（含 AI）都能研究

# Master Spark：X 槽能量武器，粒子光矛 II 之后
tech_master_spark = {{
	area = physics
	cost = @tier4cost3
	tier = 4
	category = {{ particles }}
	prerequisites = {{ "tech_energy_lance_2" }}
	weight = @tier4weight3

{WEAPON_AI}
}}

# Final Spark：泰坦级（T 槽）能量武器，Master Spark 与泰坦之后
tech_final_spark = {{
	area = physics
	cost = @tier5cost3
	tier = 5
	category = {{ particles }}
	prerequisites = {{ "tech_master_spark" "tech_titans" }}
	weight = @tier5weight3

{WEAPON_AI}
}}
""")

# ---------------------------------------------------------------- 河童飞地：国家类型、星系、首次接触、空间站设计、名字表
init = DEFS["kappa_enclave_init"][1]
init = re.sub(r"(?ms)^\tusage_odds\s*=\s*\{.*?\n\t\}\n", "", init)
init = re.sub(r"(?m)^\s*(usage|max_instances|spawn_chance)\s*=.*\n", "", init)
init = init.replace("\tflags = { kappa_enclave_system enclave }",
                    "\tflags = { kappa_enclave_system enclave }\n\n\tinit_effect = {\n\t\tsave_global_event_target_as = atb_th_kappa_sys\n\t}")
init = init.replace('"ne_flag_machine.dds"', '"enclaves_flag_trader.dds"')   # 原作引用的旗帜贴图 4.5 原版没有
write("common/solar_system_initializers/atb_th_kappa.txt", HEAD + """
# 河童飞地星系：不再随机生成，由 atb_ex_spawn_cluster 固定放在大传承者旁边（一条航道相连）

""" + clean(init) + "\n")
write("common/country_types/atb_th_country_types.txt", HEAD + "\n" + clean(DEFS["kappa_enclave"][1]) + "\n")
write("common/first_contact/atb_th_first_contact.txt", HEAD + "\n" + defs_text(["kappa_enclave_stage_1", "kappa_enclave_stage_2"]))
station = None
for p in (TH / "common/global_ship_designs").glob("*.txt"):
    t = read(p)
    for k, s, e in top_blocks(t):
        if 'name = "NAME_Kappa_Enclave_Station"' in t[s:e]:
            station = t[s:e]
write("common/global_ship_designs/atb_th_designs.txt", HEAD + "\n" + station + "\n")
shutil.copyfile(TH / "common/name_lists/NITORI.txt", MOD / "common/name_lists/atb_th_NITORI.txt")
written.append("common/name_lists/atb_th_NITORI.txt")

# ---------------------------------------------------------------- 残留检查
out_text = "\n".join((MOD / r).read_text(encoding="utf-8") for r in written if r.endswith(".txt"))
resid = sorted({t for t in re.findall(r"[A-Za-z_][\w.]*", out_text)
                if (t in DEFS or t in EVENTS) and t not in KEEP and t not in VANILLA
                and t not in ("namespace",)})
print("被删引用：", dict(sorted(REMOVED.items(), key=lambda x: -x[1])))
print("残留的原 MOD 引用：", resid)
print(f"角色 {len(RECRUIT)} 位：{', '.join(RECRUIT)}")
print(f"国策 {len(CIVICS)}、议员 {len(COUNCILORS)}、特质 {len(TRAITS)}")

# ---------------------------------------------------------------- 美术
# 1) 原作所有图形定义（.gfx 的 spriteType / pdxmesh、.asset 的 entity / particle / sound / soundeffect、
#    projectiles 的 beam 等），按 name 建索引；从保留内容里出现的名字出发递归收集，并拷贝引用到的文件
NAME_RE = re.compile(r'\bname\s*=\s*"?([\w.\-]+)"?')


def index_blocks(root, paths, into, skip=()):
    for p in paths:
        if p.suffix not in (".gfx", ".asset", ".txt") or p.name in skip:
            continue
        t = read(p)
        try:
            blocks = top_blocks(t)
        except ValueError:   # 原版个别美术文件括号不配对，跳过
            continue
        srcdir = p.parent.relative_to(root).as_posix()
        for k, s, e in blocks:
            b = t[s:e]
            if k == "category":
                continue
            if k.lower() in ("spritetypes", "objecttypes"):
                body = b[b.index("{") + 1:-1].replace("\n\t", "\n")
                for ik, s2, e2 in top_blocks(body):
                    m = NAME_RE.search(body[s2:e2])
                    if m:
                        into.setdefault(m.group(1), (p.suffix, k, ik, body[s2:e2], srcdir))
            else:
                m = NAME_RE.search(b)
                if m:
                    into.setdefault(m.group(1), (p.suffix, None, k, b, srcdir))


ART = lambda root: list((root / "gfx").rglob("*")) + list((root / "interface").rglob("*.gfx")) + list((root / "sound").rglob("*.asset"))
INDEX = {}   # name -> (后缀, 外层键或 None, 块键, 块文本, 所在目录)
index_blocks(TH, ART(TH), INDEX, skip=("zri_portraits.txt",))
VANILLA_ART = {}
index_blocks(GAME, ART(GAME), VANILLA_ART)   # 和原版同名的图形/音效定义不搬，免得改掉原版的样子

loc_files = sorted((TH / "localisation").rglob("*.yml"))
need, files = set(), set()


def mesh_textures(rel: str):
    """.mesh 是二进制，里面按文件名（不带路径）引用贴图，贴图和 .mesh 在同一目录"""
    p = TH / rel
    if p.exists():
        d = p.parent.relative_to(TH).as_posix()
        for n in set(re.findall(rb"[\w.\-]+\.(?:dds|tga)", p.read_bytes())):
            files.add(f"{d}/{n.decode()}")


def crawl(text, srcdir=None):
    for name in set(re.findall(r"[\w.\-]+", text)):
        if name in INDEX and name not in VANILLA_ART and name not in need:
            need.add(name)
            suffix, wrapper, k, b, d = INDEX[name]
            crawl(b, d)
            if k == "sound":   # 音效文件路径相对 sound/
                files.update("sound/" + f for f in re.findall(r'\bfile\s*=\s*"([^"]+)"', b))
    for f in re.findall(r'"((?:gfx|sound|music)/[^"]+\.(?:dds|tga|png|mesh|anim|wav|ogg|shader|fxh))"', text, re.I):
        files.add(f)
        if f.endswith(".mesh"):
            mesh_textures(f)
    if srcdir:   # 不带路径的文件名（动画、贴图）相对定义所在目录
        for f in re.findall(r'"([\w.\-]+\.(?:dds|tga|anim|mesh))"', text, re.I):
            files.add(f"{srcdir}/{f}")
            if f.endswith(".mesh"):
                mesh_textures(f"{srcdir}/{f}")


crawl(out_text)
# 2) 隐式图标：国策、科技（按键名找文件）
for k in CIVICS:
    files.add(f"gfx/interface/icons/governments/civics/{k}.dds")
for k in ("tech_master_spark", "tech_final_spark"):
    files.add(f"gfx/interface/icons/technologies/{k}.dds")
# 3) 肖像：只拷保留角色与河童用到的
portraits_used = set(re.findall(r"\bportrait\s*=\s*\"?(\w+)", out_text)) | set(re.findall(r"LEADER_PORTRAIT\s*=\s*(\w+)", out_text))
# 原作的肖像文件里有 portraits（单张）和 portrait_groups（如河童 kappa，内含若干单张）两个块
pt = read(TH / "gfx/portraits/portraits/zri_portraits.txt")
pdefs = {}   # (外层块, 名字) -> 文本
for outer, s, e in top_blocks(pt):
    inner = pt[pt.index("{", s) + 1:e - 1]
    pos = 0
    for m in re.finditer(r"(?m)^\s*(\w+)\s*=\s*\{", inner):
        if m.start() < pos:
            continue
        end = match_end(inner, m.end() - 1)
        pdefs[(outer, m.group(1))] = inner[m.start():end].strip()
        pos = end
groups_used = {n for (o, n) in pdefs if o == "portrait_groups" and n in portraits_used}
for n in groups_used:
    portraits_used |= set(re.findall(r"\b(\w+)\b", pdefs[("portrait_groups", n)]))
out_p = defaultdict(list)
for (o, n), b in pdefs.items():
    if (o == "portraits" and n in portraits_used) or (o == "portrait_groups" and n in groups_used):
        out_p[o].append(b)
        files.update(re.findall(r'"(gfx/[^"]+\.dds)"', b))
plines = out_p["portraits"]
write("gfx/portraits/portraits/atb_th_portraits.txt",
      "\n".join(f"{o} = {{\n\t" + "\n\t".join(bl) + "\n}" for o, bl in out_p.items()) + "\n")
missing_portraits = sorted(n for n in portraits_used if ("portraits", n) not in pdefs and ("portrait_groups", n) not in pdefs
                           and re.match(r"^(x|tpop)\d+$", n))

# 输出图形定义：图标（spriteType）放 interface/；网格（pdxmesh）、实体、粒子放回原来的目录（里面的相对路径才对得上）；
# 音效放 sound/ 并登记到 Weapons 音量类别
by_out = defaultdict(lambda: defaultdict(list))
for name in sorted(need):
    suffix, wrapper, k, b, d = INDEX[name]
    if suffix == ".asset" and k in ("sound", "soundeffect"):
        key = ("sound", "sound/atb_th_sounds.asset", None)
    elif suffix == ".asset":
        key = ("asset", f"{d}/atb_th_entities.asset", None)
    elif wrapper and wrapper.lower() == "spritetypes":
        key = ("gfx", "interface/atb_th_sprites.gfx", wrapper)
    elif wrapper:
        key = ("gfx", f"{d}/atb_th_meshes.gfx", wrapper)
    else:
        key = ("txt", f"{d}/atb_th_{k}.txt", None)
    by_out[key][k].append(b)
for (kind, rel, wrapper), groups in by_out.items():
    body = "\n".join("\n".join(bl) for bl in groups.values())
    if wrapper:
        body = f"{wrapper} = {{\n" + "\n".join("\t" + l for l in body.splitlines()) + "\n}"
    if kind == "sound":
        effects = [NAME_RE.search(b).group(1) for b in groups.get("soundeffect", [])]
        body += '\n\ncategory = {\n\tname = "Weapons"\n\tsoundeffects = {\n' + "".join(f"\t\t{e}\n" for e in effects) + "\t}\n}"
    if kind == "asset":   # 炮口特效是静态网格，原作给它挂了 idle 动画，引擎会报错
        body = body.replace('state_time = 5.0 animation = "idle" animation_blend_time = 0 looping = no',
                            "state_time = 5.0 looping = no")
    write(rel, "# 由 tools/gen_touhou.py 从「东方project领袖」抽取\n" + body + "\n")
copied, miss = 0, []
for f in sorted(files):
    src = TH / f
    if src.exists():
        dst = MOD / f
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        copied += 1
    elif not (GAME / f).exists():
        miss.append(f)
print(f"图形定义 {len(need)} 个，文件 {copied} 个；肖像 {len(plines)} 个，缺肖像定义 {missing_portraits}；缺文件 {miss[:20]}")

# ---------------------------------------------------------------- 本地化（原作只有中文；英文目录放同样的中文，免得显示键名）
LINE = re.compile(r'^\s*([\w.\-]+):\d*\s*"(.*)"\s*$')
entries = {}
for p in loc_files:
    for l in p.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        m = LINE.match(l)
        if m:
            entries.setdefault(m.group(1), m.group(2))
tokens = set(re.findall(r"[\w.\-]+", out_text))
prefixes = tuple(sorted(KEEP | set(CIVICS) | set(COUNCILORS) | {"MASTER_SPARK", "FINAL_SPARK", "kappa_", "touhou_paragon_enclave."}))
keep_loc = {k for k in entries if k in tokens or k.startswith(prefixes)
            or any(k == f"{t}_desc" or k == f"{t}_effects" for t in tokens)}
todo = list(keep_loc)
while todo:
    for ref in re.findall(r"\$([\w.\-]+)\$", entries[todo.pop()]):
        if ref in entries and ref not in keep_loc:
            keep_loc.add(ref)
            todo.append(ref)
own = {
    "decision_atb_th_recruit_scientist": "招募幻想乡来客：科学家",
    "decision_atb_th_recruit_scientist_desc": "据说银河的某处连着一片被结界隔开的土地。只要备足宴席所需的食物，那里的少女们或许愿意前来做客，甚至留下来。",
    "decision_atb_th_recruit_scientist_tt": "随机招募一位尚未加入的§Y东方科学家§!，直到全部招到。",
    "decision_atb_th_recruit_commander": "招募幻想乡来客：指挥官",
    "decision_atb_th_recruit_commander_desc": "据说银河的某处连着一片被结界隔开的土地。只要备足宴席所需的食物，那里的少女们或许愿意前来做客，甚至留下来。",
    "decision_atb_th_recruit_commander_tt": "随机招募一位尚未加入的§Y东方指挥官§!，直到全部招到。",
    "decision_atb_th_recruit_official": "招募幻想乡来客：行政官",
    "decision_atb_th_recruit_official_desc": "据说银河的某处连着一片被结界隔开的土地。只要备足宴席所需的食物，那里的少女们或许愿意前来做客，甚至留下来。",
    "decision_atb_th_recruit_official_tt": "随机招募一位尚未加入的§Y东方行政官§!，直到全部招到。",
    "thl_leader_trait_regeneration_effect": "遭遇§R致命事故§!时不会死亡；超出预期寿命时仍会自然死亡。",
}
# 原作缺本地化的 II / III 级特质：名字用「基础名 II/III」，说明沿用基础特质
for t in TRAITS:
    m = re.match(r"(.+)_([23])$", t)
    if m and t not in entries:
        base = m.group(1)
        own[t] = f"${base}$ {'II' if m.group(2) == '2' else 'III'}"
        if f"{t}_desc" not in entries:
            own[f"{t}_desc"] = f"${base}_desc$"
    elif t not in entries and t not in own:
        print("  特质缺本地化（原作也没有）：", t)
for lang, header in (("simp_chinese", "l_simp_chinese"), ("english", "l_english")):
    body = "\n".join(f' {k}:0 "{entries[k]}"' for k in sorted(keep_loc - set(own))) + "\n" + "\n".join(f' {k}:0 "{v}"' for k, v in own.items())
    write(f"localisation/{lang}/atb_th_l_{lang}.yml", f"{header}:\n # 由 tools/gen_touhou.py 从「东方project领袖」抽取，请勿手改\n{body}\n", bom=True)
print(f"本地化 {len(keep_loc)} 条")
for r in written:
    print("  写出", r)
