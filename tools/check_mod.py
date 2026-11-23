"""皇女的远征军EX：改动后的静态自检。只读，不改任何文件。"""
import re
import sys
from pathlib import Path

# Windows 控制台默认 cp1252，打印中文会报 UnicodeEncodeError
sys.stdout.reconfigure(encoding="utf-8")

MOD = Path(__file__).resolve().parent.parent / "mod"   # 相对脚本位置：任何 clone / worktree 都对
GAME = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Stellaris")

problems: list[str] = []
notes: list[str] = []


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8-sig", errors="replace")


def strip_noise(text: str, multiline: bool = False) -> str:
    """去掉注释和字符串，只留结构字符。
    本 MOD 自己的文件不用跨行字符串，按行重置能让单行内的引号笔误直接暴露；
    上游文件（含原版拷贝）会把 inline_script 参数写成跨行字符串，要 multiline=True。"""
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
        if not multiline:
            in_str = False
    return "\n".join(out)


# 3.0 起不再内置任何上游 MOD，MOD 里全部是本 MOD 自己的文件（含少量整文件覆盖的原版文件）
UPSTREAM: set[str] = set()


def is_upstream(p: Path) -> bool:
    return False


# ---------------------------------------------------------------- 1. 括号配对（含上游文件）
all_txts = sorted(p for p in MOD.rglob("*.txt"))
all_gfxs = sorted(p for p in MOD.rglob("*.gfx"))
txts = [p for p in all_txts if not is_upstream(p)]
gfxs = [p for p in all_gfxs if not is_upstream(p)]
def is_vanilla_copy(p: Path) -> bool:
    """gen_vanilla_patches.py 从原版生成的整文件覆盖：原版里有跨行字符串，括号检查要按跨行处理"""
    return "gen_vanilla_patches.py" in read(p)[:800]


for p in all_txts + all_gfxs:
    s = strip_noise(read(p), multiline=is_upstream(p) or is_vanilla_copy(p))
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
notes.append(f"括号检查：{len(all_txts)} 个 .txt + {len(all_gfxs)} 个 .gfx 全部配对"
             f"（其中上游 {len(all_txts) - len(txts) + len(all_gfxs) - len(gfxs)} 个）" if not problems else "")

# ---------------------------------------------------------------- 2. 本地化 yml（只查本 MOD 自己的）
for p in sorted(p for p in MOD.rglob("*.yml") if not is_upstream(p)):
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
opin = read(MOD / "common/opinion_modifiers/atbgp_opinion_modifiers.txt")
gpmod = read(MOD / "common/static_modifiers/atbgp_static_modifiers.txt")
atbmod = read(MOD / "common/static_modifiers/atb_static_modifiers.txt")
trt = read(MOD / "common/traits/atb_leader_traits.txt")
atbdep = read(MOD / "common/deposits/atb_deposits.txt")
rules = read(MOD / "common/game_rules/atb_rules.txt")
exev = read(MOD / "events/atb_ex_events.txt")
mega = read(MOD / "common/megastructures/11_mega_shipyard.txt")
arcsite = read(MOD / "events/ancient_relics_arcsite_events_2.txt")

checks = [
    ("白鹿物种肖像 = 兽耳机械", "portrait = kmpp_kemonomimi_machine" in init),
    ("白鹿方位 = 135°（10 点半）", "10 点半方位（角度 135）" in ev),
    ("白鹿国民 = 升格假设 + 快速复制者 + 空中下载升级",
     "civic = civic_machine_ascensionists civic = civic_machine_replication civic = civic_machine_ota_updates" in init),
    ("白鹿母星系有 L 星门", init.count("type = lgate_base") == 2),
    ("远星政体 = 巨型企业", "authority = auth_corporate" in init),
    ("远星国民 = 群众福音 + 巧手公司 + 舰队承包商",
     "civic = civic_gospel_of_the_masses civic = civic_corporate_crafters civic = civic_naval_contractors" in init),
    ("专属立绘元首永不下台", "id = atbgp.14" in ev and "on_ruler_set = {" in read(MOD / "common/on_actions/atbgp_on_actions.txt")),
    ("远星开局获得灵能档案", "add_relic = r_zro_crystal" in ev),
    ("远星思潮 = 极端军国 + 唯心", "ethic = ethic_fanatic_militarist ethic = ethic_spiritualist" in init),
    ("远星开局灵能理论", "give_technology = { tech = tech_psionic_theory message = no }" in ev),
    ("远星锁定灵能飞升", "add_ascension_perk = ap_mind_over_matter" in ev and "add_tradition = tr_psionics_adopt" in ev),
    ("远星母星每月 +3 泽洛", "add_deposit = atbgp_d_zro_3" in init and "sr_zro = 3" in dep),
    ("远星与远征军认同族", "atbgp_kin_with_expedition = yes" in ev
     and "atbgp_kin_with_expedition = {" in eff and "atbgp_same_homeworld = {" in opin),
    ("大君主方位 = 0°（3 点）", "3 点方位（角度 0）" in ev),
    ("大君主国民 = 种族洁癖 + 封建社会 + 卓越海军",
     "civic = civic_fanatic_purifiers civic = civic_feudal_realm civic = civic_distinguished_admiralty" in init),
    ("大君主元首 3 条特质（不含大研究者）", all(t in eff.split("atbgp_install_random_ruler_3")[1].split("atbgp_install_random_ruler_4")[0]
        for t in ("leader_trait_supreme_organizer", "leader_trait_intemporal", "leader_trait_master_bureaucrat"))
        and "leader_trait_great_researcher" not in eff),
    ("大君主研究速度 +12%（国家修正里不再挂不生效的宜居度下限）",
     "all_technology_research_speed = 0.12" in gpmod and "habitability_floor_add" not in gpmod),
    ("大君主 6 颗死寂星球带宜居度下限 +55% 的特殊地形",
     init.count("add_deposit = atbgp_d_suzerain_shelter") == 6 and "habitability_floor_add = 0.55" in dep),
    ("大君主固定宇宙创生", "atbgp_force_crisis_perk = { PERK = ap_cosmogenesis }" in ev),
    ("大君主固定基因纯净飞升", "atbgp_start_purity_ascension = yes" in ev and "atbgp_purity_lock = yes" in ev),
    ("大君主合成人公民权", "atbgp_force_ai_full_rights = yes" in ev and "option = ai_full_rights" in eff),
    ("恐惧之潮方位 = 195°（8 点半，3.10）", "8 点半方位（角度 195）" in ev),
    ("恐惧之潮国民 = 噬杀蜂群 + 唯一意志 + 亚空间突触",
     "civic = civic_hive_devouring_swarm civic = civic_hive_one_mind civic = civic_hive_subspace_ephapse" in init),
    ("恐惧之潮三颗开局母星", init.count("atbgp_planet_4_home_") == 3 and "atbgp_planet_4_home_4" not in init),
    ("恐惧之潮母星系有损坏的以太相引擎", 'type = "crisis_sphere_ruined"' in init),
    ("恐惧之潮固定星海天罚", "atbgp_force_crisis_perk = { PERK = ap_become_the_crisis }" in ev.split("limit = { has_country_flag = atbgp_power_4 }")[2]),
    ("终端对齐协议方位 = 255°（6 点半）", "6 点半方位（角度 255）" in ev),
    ("终端对齐协议国民 = 铁心灭绝者 + 战争机器 + 经验缓存器",
     "civic = civic_machine_terminator civic = civic_machine_warbots civic = civic_memory_vault_machine" in init),
    ("终端对齐协议四颗机械星球母星", init.count("atbgp_planet_5_home_") == 4 and init.count('class = "pc_machine"') >= 4),
    ("多母星都走原版开局流程", init.count("generate_start_pops = yes") == 7),
    ("大君主与终端对齐协议加入星海共同体", init.count("set_country_flag = atbgp_gc_member") == 2
     and "has_country_flag = atbgp_gc_member" in rules and "can_be_part_of_galactic_community = {" in rules),
    ("五个列强开局海军容量 +300（3.1）；恒星基地上限 +10 除大君主外（3.10）", init.count("modifier = atbgp_power_base") == 5
     and "atbgp_power_base = {\n\tcountry_naval_cap_add = 300\n}" in gpmod
     and "atbgp_starbase_bonus = {\n\tcountry_starbase_capacity_add = 10\n}" in gpmod),
    ("3.0.3：AI 超容造舰预算 ×0.1、天灾邻国 ×5 只到 100%", (lambda b: "factor = 0.1\n\t\t\tused_naval_capacity_percent >= 1.0" in b
     and "used_naval_capacity_percent < 1.0\t# 皇女的远征军EX：原版 1.5" in b)(
        read(MOD / "common/ai_budget/01_alloys_budget.txt") if (MOD / "common/ai_budget/01_alloys_budget.txt").exists() else "")),
    ("2.7：10 颗开局母星人口增长翻倍 20 年", init.count("modifier = atbgp_growth_boost") == 10
     and "days = 7200" in init and "logistic_growth_mult = 1.0" in gpmod and "planet_pop_assembly_mult = 1.0" in gpmod),
    ("2.7：开局舰队带 10 级永生舰队司令", "class = commander" in eff and "skill = 10" in eff
     and "assign_leader = event_target:atbgp_start_admiral" in eff),
    ("2.7：10 颗列强开局母星都先放开局特征（决定乡村区划上限）再建区划",
     init.count("generate_start_deposits_and_blockers = yes") == 10
     and init.count("generate_start_buildings_and_districts = yes") == 10),
    ("2.7：6 颗标准区划集开局母星加农业/发电/采矿区划各 10 个（机械星球不加）",
     init.count("modifier = atbgp_homeworld_districts") == 6
     and init.count("add_district = { district_type = district_farming ignore_cap = yes }") == 6
     and "planet_max_districts_add = 30" in gpmod),
    ("2.7：舰船不再用编号命名", "CGEN_SEQ_SHIP" not in read(MOD / "common/name_lists/00_cgen_azure_genesis.txt")),
    ("列强星团不连到天选民", "has_star_flag = chosen_system" in read(MOD / "common/scripted_triggers/atbgp_triggers.txt")),
    ("大君主额外国家修正已挂上",
     "modifier = atbgp_bonus_3" in init and "atbgp_bonus_3 = {" in gpmod
     and "species_leader_exp_gain = 0.5" in gpmod and "negative_traits_country = -1" in gpmod),
    ("远征军星团方位 = 12 点（88~92；3.10 起遥远之约定另有一处，在 L 星群正上方）",
     exeff.count("min_orientation_angle = 88") == 7 and "min_orientation_angle = 267" in exeff),
    ("远征军母星系有毁坏的巨型船坞与 L 星门", 'type = "mega_shipyard_ruined"' in rl
     and rl.split("atb_rl_home = {")[1].split("atb_rl_lgate = {")[0].count("lgate_base") == 1),
    ("高位元素秘封研究院", "d_atb_elemental_seal_institute = {" in atbdep and "country_resource_max_add = 1000000" in atbdep
     and "minor_artifacts = 2" in atbdep and "add_deposit = d_atb_elemental_seal_institute" in exeff),
    ("星海共同体议程/休会时间减半", all(x in read(MOD / "common/defines/atb_ex_defines.txt") for x in (
        "RESOLUTION_VOTE_TIMER = 720", "RESOLUTION_VOTE_PREMATURE_TIMER = 360", "SENATE_RECESS_TIMER = 360"))),
    ("内置名称集「苍神缘起帝国」与 10 种语言本地化",
     (MOD / "common/name_lists/00_cgen_azure_genesis.txt").exists()
     and len(list((MOD / "localisation").glob("*/cgen_names_l_*.yml"))) == 10
     and read(MOD / "common/name_lists/00_cgen_azure_genesis.txt").count("full_names = {") == 24
     # 群星 4.6 起名称集不能带 BOM（4.5 反而要求带），带了整份读不出来
     and not (MOD / "common/name_lists/00_cgen_azure_genesis.txt").read_bytes().startswith(b"\xef\xbb\xbf")
     and not (MOD / "common/name_lists/atb_th_NITORI.txt").read_bytes().startswith(b"\xef\xbb\xbf")),
    ("3.15：L 星群特殊星系副本的 trigger id 加 atb_lc. 前缀（不与原版重名）",
     "id = \"atb_lc.dragon.home.1\"" in read(MOD / "common/solar_system_initializers/atb_lc_initializers.txt")
     and "id = scav.1\n" not in read(MOD / "common/solar_system_initializers/atb_lc_initializers.txt")),
    ("3.15：融合黄金世代的学院与培养领袖（标记、触发器、原版文件替换、意识形态与失去起源的例外、搬家）",
     "atb_has_golden_generation = {" in read(MOD / "common/scripted_triggers/atb_triggers.txt")
     and "set_country_flag = atb_golden_generation\n" in read(MOD / "common/scripted_effects/atb_effects.txt")
     and read(MOD / "events/origin_events_forceofwill.txt").count("atb_has_golden_generation = yes") == 72
     and read(MOD / "events/origin_events_forceofwill.txt").count("remove_country_flag = atb_golden_generation") == 2
     and "has_origin = origin_golden_generation\t# 皇女的远征军：意识形态部分" in read(MOD / "events/origin_events_forceofwill.txt")
     and read(MOD / "common/buildings/25_forceofwill_buildings.txt").count("atb_has_golden_generation = yes") == 7  # 6 处 + 文件头说明
     and "set_carrier_flag = golden_academy_built" in read(MOD / "common/scripted_effects/atb_ex_effects.txt")
     and "remove_carrier_flag = golden_academy_built" in read(MOD / "common/scripted_effects/atb_ex_effects.txt")
     and not (MOD / "common/ideologies").exists()),
    ("3.15：适配群星 4.6（supported_version）", 'supported_version="v4.6.*"' in read(MOD / "descriptor.mod")),
    ("预设帝国「苍神缘起帝国」：皇女起源 + 内置名称集", all(x in read(MOD / "prescripted_countries/atb_prescripted_countries.txt") for x in (
        'origin = "origin_atb_princess_expedition"', 'name_list = "CGEN_AZURE_GENESIS"', "playable = atb_preset_playable",
        'authority = "auth_dictatorial"', 'government = "gov_technocratic_dictatorship"', 'planet_class = "pc_continental"'))
     and "atb_preset_playable = {" in read(MOD / "common/scripted_triggers/atb_triggers.txt")),
    ("巨型船坞 50 个船坞", mega.count("starbase_shipyard_capacity_add = 50") == 2 and "capacity_add = 20" not in mega),
    ("天选民固定 7 点半（3.10）", "atb_ex_spawn_chosen_fixed = yes" in exev and exeff.count("min_orientation_angle = 223") == 4
     and "# random_rim_system = {" in arcsite
     and not re.search(r"^\s*system_event = \{ id = fircon\.3500 \}", arcsite, re.M)),
    ("二皇女带舰船加成", "ship_weapon_damage = 1.0" in trt and "ship_shield_hardening_add = 1.0" in trt),
    ("三皇女带物种修饰点（有机/机械/智械三个原型）",
     all(f"{a}_species_trait_points_add = 16" in trt for a in ("BIOLOGICAL", "ROBOT", "MACHINE"))),
    ("四皇女带大使上限", "envoys_add = 2" in trt),
    ("远征军同化速度 +9000%", "auto_mod_monthly_add = 4725" in atbmod),
    ("三面自制帝国标识都写进了 create_country", init.count('category = "atbgp"') == 3),
    ("旧的 atbgp_install_named_ruler 已清除", "atbgp_install_named_ruler" not in eff + ev),
    ("两个具名元首安装效果已定义", "atbgp_install_ruler_rongxin = {" in eff and "atbgp_install_ruler_taiaria = {" in eff),
    ("两个具名元首安装效果被调用", "atbgp_install_ruler_rongxin = yes" in ev and "atbgp_install_ruler_taiaria = yes" in ev),
    # 合成人与灵媒在原版互斥，只保留灵媒
    ("泰阿瑞亚 4 条特质齐全", all(t in eff.split("atbgp_install_ruler_taiaria")[1] for t in (
        "leader_trait_intemporal", "leader_trait_supreme_organizer", "leader_trait_master_bureaucrat",
        "leader_trait_psionic"))),
    ("泰阿瑞亚不带互斥的合成人", "leader_trait_synthetic" not in eff),
    ("融心演算只有时间永驻", eff.split("atbgp_install_ruler_rongxin")[1].split("atbgp_install_ruler_taiaria")[0].count("add_trait") == 1),
    ("三个老列强的战时补给仍是影响力 +2、平时 +4", dep.count("influence = 2") == 3 and dep.count("influence = 4") == 3),
    ("各列强追加的每月资源", "alloys = 272" in dep and "physics_research = 78" in dep and "sr_zro = 2" in dep
     and "atbgp_d_income_5" not in dep and "atbgp_d_income_crisis_4" not in dep),
    ("远星物种复制玩家开局物种", "is_ai = no" in init and "founder_species = {" in init),
    ("远星物种去掉致病基因", "remove_trait = trait_pathogenic_genes" in init),
    ("无形链接生成龙族土著", "atb_ex_generate_dragonkin_preftl = yes" in rl),
    ("龙族土著效果已定义", "atb_ex_generate_dragonkin_preftl = {" in exeff),
    # 2.8
    ("居住站科技开局给所有帝国", "atb_ex_grant_habitat_techs = {" in exeff and "atb_ex_give_habitat_techs = {" in exeff
     and exev.count("atb_ex_grant_habitat_techs = yes") == 2 and "atb_ex_give_habitat_techs = yes" in exev
     and all(f"give_technology = {{ tech = tech_habitat_{i} message = no }}" in exeff for i in (1, 2, 3))),
    ("atb_ex 不再挂月脉冲：年兜底 + 新国家事件钩子", (lambda oa: "on_monthly_pulse" not in oa
     and "on_yearly_pulse = {" in oa and "on_country_created = {" in oa and "on_country_type_changed = {" in oa)(
         read(MOD / "common/on_actions/atb_ex_on_actions.txt")) and "id = atb_ex.3" in exev),
    ("初始护卫舰 x10 = 30 艘，建造舰/科研舰各 1 艘",
     (lambda f: "count = 30" in f and "count = 10" not in f and "while" not in f.split("random_existing_design = corvette")[0].split("create_leader")[0]
      and f.count("random_existing_design = constructor") == 1 and f.count("random_existing_design = science") == 1)(
         eff.split("atbgp_spawn_start_fleets = {")[1].split("atbgp_install_ruler_")[0])),
    ("白鹿与远星母星系各一座 L 星门", init.count("type = lgate_base") == 2
     and init.count("lgate_enabled = yes") == 2),
]

# ---------------------------------------------------------------- 2.9：AI 限制与减卡（tools/gen_ai_limits.py）
lim_mega = read(MOD / "common/megastructures/zz_atb_ex_ai_limits.txt") if (MOD / "common/megastructures/zz_atb_ex_ai_limits.txt").exists() else ""
lim_oa = read(MOD / "common/on_actions/atb_ex_ai_limits_on_actions.txt") if (MOD / "common/on_actions/atb_ex_ai_limits_on_actions.txt").exists() else ""
checks += [
    ("AI 巨构上限：居住站 7 / 环世界 1 / 星门 2 / 中继器 18", all(
        re.search(r"^%s\s*=\s*\{" % t, lim_mega, re.M) and f"TYPE = {t} CAP = {c} " in lim_mega
        for t, c in (("habitat_central_complex", 7), ("ring_world_1", 1), ("gateway_0", 2), ("hyper_relay", 18)))
     and "value:ai_habitat_cap" not in lim_mega),
    ("AI 巨构计数挂在开工与完工上", "on_megastructure_build_start = {" in lim_oa
     and "on_megastructure_built = {" in lim_oa and "on_monthly_pulse" not in lim_oa),
    ("AI 不选跨物种杂交", "is_ai = no" in read(MOD / "common/ascension_perks/zz_atb_ex_ai_limits.txt").split("modifier = {")[0]),
    ("AI 物种改造 20 年冷却", "has_country_flag = atb_ex_species_mod_cooldown" in read(MOD / "common/game_rules/zz_atb_ex_ai_limits.txt")
     and "days = 7200" in read(MOD / "events/atb_ex_ai_limits_events.txt")
     and "on_modification_completion = {" in lim_oa),
    ("减卡 defines：触发修正 15 天、思潮偏移 30 天", (lambda d: "TRIGGERED_MODIFIER_UPDATE_DELAY = 15" in d
     and "POP_ETHOS_DIVERGENCE_INTERVAL = 30" in d)(read(MOD / "common/defines/zz_atb_ex_performance_defines.txt"))),
]

# ---------------------------------------------------------------- 3.0：AI 自动星球、去掉三方内置
def exists(rel):
    return (MOD / rel).exists()


auto_eff = read(MOD / "common/scripted_effects/atb_ai_auto_effects.txt") if exists("common/scripted_effects/atb_ai_auto_effects.txt") else ""
auto_bld = read(MOD / "common/buildings/atb_ai_auto_buildings.txt") if exists("common/buildings/atb_ai_auto_buildings.txt") else ""
auto_ev = read(MOD / "events/atb_ai_auto_events.txt") if exists("events/atb_ai_auto_events.txt") else ""
auto_oa = read(MOD / "common/on_actions/atb_ai_auto_on_actions.txt") if exists("common/on_actions/atb_ai_auto_on_actions.txt") else ""
auto_var = read(MOD / "common/scripted_variables/atb_ai_auto_variables.txt") if exists("common/scripted_variables/atb_ai_auto_variables.txt") else ""
quest = read(MOD / "common/scripted_effects/atb_relic_quest_effects.txt") if exists("common/scripted_effects/atb_relic_quest_effects.txt") else ""
checks += [
    # 3.5：GPM 的遗珍整合回来了（脚本文件都叫 atb_gpm_*，图标沿用 GPM 原名 gpm_*.dds），其余 GPM 内容仍不要
    ("PD / GPM / Stellar AI 已移出（GPM 只留遗珍）", not any(p for p in MOD.rglob("gpm_*") if p.suffix != ".dds")
     and not any(MOD.rglob("pd_*")) and not any(MOD.rglob("*stellarai*"))
     and not (MOD.parent / "tools/upstream_manifest.json").exists()
     and not any(MOD.rglob("*wargoal*")) and not any(MOD.rglob("*casus_belli*"))),
    ("3.5：GPM 遗珍内置（28 个，不带遗珍战争目标）", sum(len(re.findall(r"(?m)^gpm_r_\w+ = \{", read(p))) for p in (MOD / "common/relics").glob("atb_gpm_*.txt")) >= 28
     and exists("common/armies/atb_gpm_relic_armies.txt") and exists("common/traits/atb_gpm_relic_traits.txt")
     and exists("interface/atb_gpm_relics.gfx") and exists("localisation/simp_chinese/atb_gpm_relics_l_simp_chinese.yml")
     and not any("gpm" in f.name.lower() or "relic" in f.name.lower() for f in (MOD / "common/war_goals").glob("*"))
     and not exists("common/casus_belli")),
    ("自动星球 6 座建筑都定义了", all(f"{b} = {{" in auto_bld for b in (
        "building_atb_ai_core", "building_atb_ai_foundry", "building_atb_ai_power",
        "building_atb_ai_admin", "building_atb_ai_industry", "building_atb_ai_supply"))
     and auto_bld.count("multiplier = value:atb_ai_auto_output") == 9
     and "atb_ai_auto_output = {" in read(MOD / "common/script_values/atb_ai_auto_values.txt")),
    ("自治中枢带护盾、FTL 抑制器、10 支防御陆军、海军容量", "planetary_ftl_inhibitor = yes" in auto_bld
     and "planet_orbital_bombardment_damage = -0.5" in auto_bld and "planet_defense_armies_add = 10" in auto_bld
     and "country_naval_cap_add = @atb_ai_auto_naval_cap" in auto_bld),
    ("自动星球的转换、还原、增长、易手都接上了", all(x in auto_eff for x in (
        "atb_ai_auto_convert = {", "atb_ai_auto_revert = {", "atb_ai_auto_grow = {", "atb_ai_auto_refresh = {"))
     and all(f"atb_ai.{i}" in auto_oa for i in (1, 3, 4, 5, 10))
     and all(f"on_{h} = {{" in auto_oa for h in ("game_start", "colonized", "colony_transfer", "yearly_pulse_country"))),
    ("3.6：自动星球数值列强与普通相同（+3/年、起点 10、上限 300）", "@atb_ai_auto_growth = 3" in auto_var and "@atb_ai_auto_growth_gp = 3" in auto_var
     and "@atb_ai_auto_start_gp = 10" in auto_var and "@atb_ai_auto_cap_gp = 300" in auto_var),
    ("3.14：自动星球产出为 3.10 的 ×1.6（3.13 的 ×2.1 下调），海军容量仍 0.1", "@atb_ai_auto_out_consumer_goods = 2.0779" in auto_var
     and "@atb_ai_auto_out_energy = 3.1170" in auto_var
     and "@atb_ai_auto_naval_cap = 0.1" in auto_var and auto_bld.count("@atb_ai_auto_out_") >= 17),
    ("3.14：自动星球合金 0.7363、科研 1.5534；列强倍率（大君主 ×1.1982，恐惧之潮/终端 ×1.1081）",
     "@atb_ai_auto_out_alloys = 0.7363" in auto_var and "@atb_ai_auto_out_research = 1.5534" in auto_var
     and "factor = 1.1982" in read(MOD / "common/script_values/atb_ai_auto_values.txt")
     and "factor = 1.1081" in read(MOD / "common/script_values/atb_ai_auto_values.txt")),
    ("3.10：大君主同盟领地没有恒星基地上限 +10", "country_starbase_capacity_add" not in read(MOD / "common/static_modifiers/atbgp_static_modifiers.txt").split("atbgp_power_base = {", 1)[1].split("}", 1)[0]
     and read(MOD / "common/solar_system_initializers/atbgp_initializers.txt").count("modifier = atbgp_starbase_bonus") == 4),
    ("3.6：无形链接↔逆鳞、极限边缘↔神话两个虫洞，白鹿与远星互相 +200 好感", "id = atb_ex.6" in read(MOD / "events/atb_ex_events.txt")
     and re.sub(r"#.*", "", read(MOD / "events/atb_ex_events.txt")).count("link_wormholes = prev") == 2
     and "base = 200" in read(MOD / "common/opinion_modifiers/atb_ex_opinion_modifiers.txt")),
    ("3.6：无形链接土著固定为龙族（Nivlac/Robust/Psionic/Stargazer）", all(x in read(MOD / "common/scripted_effects/atb_ex_effects.txt")
     for x in ("name = atb_species_rl_dragonkin", "trait = trait_nivlac", "trait = trait_robust", "trait = trait_psionic", "trait = trait_stargazer"))),
    ("3.6：三皇女异常发现 +50%、要塞工程学 +30", "ship_anomaly_generation_chance_mult = 0.5" in read(MOD / "common/traits/atb_leader_traits.txt")
     and "engineering_research = 60" in read(MOD / "common/deposits/atb_deposits.txt")),
    ("3.8：星海纪念碑凝聚力 +66", "unity = 66" in read(MOD / "common/deposits/atb_deposits.txt")),
    ("3.10：可编入舰队的主宰（20 万舰体、T 槽、没有船坞、限 1 艘），原版主宰停建",
     "atb_juggernaut = {" in read(MOD / "common/ship_sizes/atb_ship_sizes.txt")
     and "max_hitpoints = 200000" in read(MOD / "common/ship_sizes/atb_ship_sizes.txt")
     and "class = shipclass_military" in read(MOD / "common/ship_sizes/atb_ship_sizes.txt").split("atb_juggernaut = {", 1)[1]
     and "starbase_shipyard_capacity_add" not in read(MOD / "common/ship_sizes/atb_ship_sizes.txt")
     and read(MOD / "common/section_templates/atb_juggernaut.txt").count("invisible_titanic_fixed") == 2
     and read(MOD / "common/section_templates/atb_juggernaut.txt").count("large_strike_craft") == 6
     and read(MOD / "common/scripted_triggers/07_scripted_triggers_ships.txt").count("is_ship_size = atb_juggernaut") == 6
     and "juggernaut_potential_construction = {\n\talways = no\n}" in read(MOD / "common/scripted_triggers/07_scripted_triggers_ships.txt")
     and "atb_juggernaut_ships_limit" in read(MOD / "common/country_limits/ownership_limits/atb_ownership_limits.txt")),
    ("3.10：起源「遥远之约定」：开局生成 L 星群、星团只连 L 星群、空星群结局、小灰异常现象",
     "origin_atb_distant_promise = {" in read(MOD / "common/governments/civics/atb_origins.txt")
     and "set_country_flag = atb_distant_promise" in read(MOD / "common/scripted_effects/atb_effects.txt")
     and "country_event = { id = distar.11000 }" in read(MOD / "common/scripted_effects/atb_ex_effects.txt")
     and "to = event_target:lcluster4b" in read(MOD / "common/scripted_effects/atb_ex_effects.txt")
     and "category = disco_gray_cat" in read(MOD / "common/scripted_effects/atb_ex_effects.txt")
     and "has_origin = origin_atb_distant_promise" in read(MOD / "events/atb_events.txt")
     and "origin_atb_distant_promise:0" in read(MOD / "localisation/simp_chinese/atb_princess_expedition_l_simp_chinese.yml")
     and "origin_atb_distant_promise:0" in read(MOD / "localisation/english/atb_princess_expedition_l_english.yml")),
    ("3.11：遥远之约定的 L 星群纳米星球可环境改造（开局与每年补）",
     read(MOD / "common/scripted_effects/atb_ex_effects.txt").count("atb_ex_lcluster_terraformable") == 2
     and "atb_ex_lcluster_terraformable = yes" in read(MOD / "events/atb_ex_events.txt")
     and "modifier = terraforming_candidate" in read(MOD / "common/scripted_effects/atb_ex_effects.txt")),
    ("3.11：遥远之约定把原版 11 个特殊星系搬进 L 星群（并清掉银河里的那份）",
     (lambda e: "INIT = hyacinth_system" in e and all(f"INIT = atb_lc_{k}" in e and f"\natb_lc_{k} = {{" in read(MOD / "common/solar_system_initializers/atb_lc_initializers.txt") for k in (
         "time_loop_world_system", "living_planet_system", "scavenger_system", "guardians_init_dragon",
         "guardians_artist_init_01", "guardians_curator_init_01", "great_wound_system", "elderly_tiyanki_system",
         "locust_system_initializer_01", "voidworms_spawn_system_medium"))
      and "\tmax_instances" not in read(MOD / "common/solar_system_initializers/atb_lc_initializers.txt")
      and e.count("atb_ex_lc_link = { A = ") == 12 and "atb_ex_lc_strip_galaxy_copies = yes" in e
      and "atb_ex_lcluster_extra_systems = yes" in e and "hyperlane = no" in e)(
         read(MOD / "common/scripted_effects/atb_ex_effects.txt"))),
    ("3.14：二皇女海军容量 +500、舰队指挥上限 +1000",
     "country_naval_cap_add = 500\t# 3.14" in read(MOD / "common/traits/atb_leader_traits.txt")
     and "command_limit_add = 1000\t# 3.14" in read(MOD / "common/traits/atb_leader_traits.txt")),
    ("3.14：开局科技农业生产聚合体、集中工业产线枢纽（照抄巴奥有机工厂、伊拉斯人海军船坞）",
     read(MOD / "common/technology/atb_precursor_copy_tech.txt").count("start_tech = yes") == 2
     and "prerequisites = {\n\t\t\"tech_atb_agri_aggregate\"" in read(MOD / "common/buildings/atb_precursor_copy_buildings.txt")
     and read(MOD / "common/starbase_buildings/atb_precursor_copy_starbase_buildings.txt").count("has_technology = tech_atb_industrial_hub") == 2
     and all(f" {k}:0" in read(MOD / f"localisation/{lang}/atb_ex_l_{lang}.yml") for lang in ("simp_chinese", "english")
             for k in ("tech_atb_agri_aggregate", "building_atb_agri_aggregate", "tech_atb_industrial_hub", "sm_atb_industrial_hub", "sm_atb_arkship_industrial_hub"))),
    ("3.10：去掉必定生成凯德斯坠毁点", not exists("common/solar_system_initializers/atb_ex_initializers.txt")
     and "legendary_leader" not in read(MOD / "events/atb_ex_events.txt")),
    ("3.14：星堡舰体 +1000%、交战范围翻倍、花费减半、建造与升级时间 -80%、平台上限 +24；防御平台与离子炮时间 -80%、花费/维护减半、舰体 +1000%",
     (lambda m: m.count("_hull_mult = 10\n") == 9 and "starbase_upgrade_time_mult = -0.8" in m
      and "shipclass_starbase_build_speed_mult = 4" in m and m.count("_engagement_range_mult = 1") == 8
      and "starbase_upgrade_cost_mult = -0.5" in m and "starbase_outpost_cost_mult = -0.5" in m
      and "starbase_defense_platform_capacity_add = 24" in m and "shipclass_military_station_build_cost_mult = -0.5" in m
      and "shipclass_military_station_build_speed_mult = 4" in m and "ship_ion_cannon_upkeep_mult = -0.5" in m
      and "ship_military_station_small_upkeep_mult = -0.5" in m)(read(MOD / "common/static_modifiers/atb_ex_static_modifiers.txt"))),
    ("3.14：L 星门线索 7 → 5，银河里至少 7 座 L 星门",
     "max = 5\t# 皇女的远征军EX：原版 7" in read(MOD / "common/event_chains/00_event_chains_distant_stars.txt")
     and "atb_ex_ensure_lgates = {" in read(MOD / "common/scripted_effects/atb_ex_effects.txt")
     and "atb_ex_ensure_lgates = yes" in read(MOD / "events/atb_ex_events.txt")),
    ("3.10：天选民虫洞出口在大君主母星、同种族、开门后结盟；天选民 7 点半、恐惧之潮 8 点半",
     "atb_ex_spawn_chosen_fixed = {" in read(MOD / "common/scripted_effects/atb_ex_effects.txt")
     and "change_dominant_species" in read(MOD / "common/scripted_effects/atb_ex_effects.txt")
     and "min_orientation_angle = 223" in read(MOD / "common/scripted_effects/atb_ex_effects.txt")
     and "id = atb_ex.8" in read(MOD / "events/atb_ex_events.txt")
     and "atb_ex.8" in read(MOD / "common/on_actions/atb_ex_on_actions.txt")
     and "min_orientation_angle = 193" in read(MOD / "events/atbgp_events.txt")),
    ("3.9：首席调停者、开局 3 个国策、第一皇女领袖维护费 -33%",
     read(MOD / "common/governments/councilors/atb_th_councilors.txt").count("empire_size_colonies_mult = -0.01") == 2
     and "GOVERNMENT_CIVIC_POINTS_BASE = 3" in read(MOD / "common/defines/atb_ex_defines.txt")
     and "leaders_upkeep_mult = -0.33" in read(MOD / "common/traits/atb_leader_traits.txt")
     and 'councilor_nether_world:0 "首席调停者"' in read(MOD / "localisation/simp_chinese/atb_th_l_simp_chinese.yml")),
    ("3.6：灵能之路（二皇女事件 + 四处原版条件开例外）", "id = atb.50" in read(MOD / "events/atb_events.txt")
     and all(exists(f) and "atb_psionic_path_open" in read(MOD / f) for f in (
         "common/ascension_perks/00_ascension_paths.txt", "common/tradition_categories/01_psionics_shroud.txt",
         "common/council_agendas/02_council_agendas_ascensions.txt"))
     and re.sub(r"#.*", "", read(MOD / "common/council_agendas/02_council_agendas_ascensions.txt")).count("atb_psionic_path_open") == 2),
    ("3.2：X 槽位武器伤害 ×2、射程 ×1.33", exists("common/component_templates/weapon_components.csv")
     and exists("common/component_templates/mutation_weapon_components.csv")
     and "MASS_ACCELERATOR_1;250.00;-200.00;1400.00;4000.00" in read(MOD / "common/component_templates/weapon_components.csv")
     and ";199.50;" in read(MOD / "common/component_templates/weapon_components.csv")),
    ("3.2：战列舰舰体值 ×2", "shipsize_battleship_hull_mult = 1.0" in read(MOD / "common/static_modifiers/atb_ex_static_modifiers.txt")),
    ("3.3：所有国家亚光速 ×1.2（不看其它 MOD）", "ship_speed_mult = 0.2" in read(MOD / "common/static_modifiers/atb_ex_static_modifiers.txt")
     and "has_shipsinscaling" not in read(MOD / "common/scripted_effects/atb_ex_effects.txt")
     and "modifier = atb_ex_sublight_rs" in read(MOD / "common/scripted_effects/atb_ex_effects.txt")
     and "id = atb_ex.5" in read(MOD / "events/atb_ex_events.txt")),
    ("AI 外交权重 ×3", "diplo_weight_mult = 2" in read(MOD / "common/static_modifiers/atb_ex_static_modifiers.txt")),
    ("3.16：整合 Stellar AI 的性格与行为（性格以原版为底、26 个扩张期性格、实力门槛、好感、附庸偏好、间谍、行为参数），不取岗位与经济",
     (lambda p: p.count("\nexpansionists_") == 26 and "adopt_ideology_acceptance" in p and "utopian_missionaries = {" in p
      and "# Stellar AI，原版" in p)(read(MOD / "common/personalities/00_personalities.txt"))
     and read(MOD / "common/war_goals/~atb_sai_war_goals.txt").count('inline_script = "atb_sai/war_goal_strength_gate"') >= 7
     and (MOD / "common/inline_scripts/atb_sai/war_goal_strength_gate.txt").exists()
     and "triggered_opinion_stellarai_we_can_win = {" in read(MOD / "common/opinion_modifiers/atb_sai_odds_opinion.txt")
     and "stellarai_conquest_identity = {" in read(MOD / "common/scripted_triggers/atb_sai_triggers.txt")
     and "Keep native operations" in read(MOD / "common/ai_espionage/spynetworks/00_base_strategies.txt")
     and "OFFENSE_VS_DEFENSE_STRATEGY_ALLOTMENT = 1.6" in read(MOD / "common/defines/atb_sai_defines.txt")
     and "\tUNDERDEVELOPED_PLANET_LIMIT" not in read(MOD / "common/defines/atb_sai_defines.txt")
     and not any((MOD / "common/pop_jobs" / f).exists() for f in ("01_ruler_jobs.txt", "02_specialist_jobs.txt", "04_gestalt_jobs.txt"))
     and not (MOD / "common/zones").exists()
     and not (MOD / "common/economic_plans").exists()),
    ("3.4：AI 宣战基础概率（3.16 起 ×3，之前 ×4）、殖民宜居度门槛回原版", (lambda d: "AI_AGGRESSIVENESS_BASE = 75" in d
     and "AI_MIN_HABITABILITY_TO_COLONIZE" not in d and "UNDERDEVELOPED_PLANET_LIMIT = 999" in d)(
        read(MOD / "common/defines/atb_ex_defines.txt"))),
    ("3.4：自动星球每年自检（缺中枢重建、特殊区划集放回普通星球）", "atb_ai_auto_release = {" in auto_eff
     and "atb_ai_auto_supported_planet = no" in auto_eff and "atb_ai_auto_refresh = yes" in auto_ev),
    ("3.4：巨构开工计数事件先判断星系存在", "exists = from" in read(MOD / "events/atb_ex_ai_limits_events.txt")),
    ("3.7：船坞模块恢复原版（不再覆盖 00_starbase_modules.txt）", not exists("common/starbase_modules/00_starbase_modules.txt")),
    ("3.7：东方project领袖——13 国策、13 议员、34 位角色、招募决议、两件武器、河童飞地",
     len(re.findall(r"(?m)^civic_\w+ = \{", read(MOD / "common/governments/civics/atb_th_civics.txt"))) == 13
     and read(MOD / "common/scripted_effects/atb_th_recruit_effects.txt").count("set_country_flag = atb_th_got_") == 34
     and all(f"food = {c}" in read(MOD / "common/decisions/atb_th_decisions.txt") for c in (500, 1000, 2000))
     and all(f"decision_atb_th_recruit_{c} = {{" in read(MOD / "common/decisions/atb_th_decisions.txt") for c in ("scientist", "commander", "official"))
     and all(x in read(MOD / "common/technology/atb_th_tech.txt") for x in ('"tech_energy_lance_2"', '"tech_master_spark" "tech_titans"'))
     and "marisa_leader" not in read(MOD / "common/technology/atb_th_tech.txt")
     and "initializer = kappa_enclave_init" in read(MOD / "common/scripted_effects/atb_ex_effects.txt")
     and "to = event_target:atb_th_kappa_sys" in read(MOD / "common/scripted_effects/atb_ex_effects.txt")
     and "usage_odds" not in read(MOD / "common/solar_system_initializers/atb_th_kappa.txt")
     and all(f"touhou_paragon_enclave.{e}" not in read(MOD / "events/atb_th_events.txt") for e in ("330", "360", "370"))),
    ("3.7：东方领袖不占领袖上限、免疫意外死亡、死后按初始状态重生",
     read(MOD / "common/scripted_effects/atb_th_leader_effects.txt").count("set_leader_flag = leader_death_events_blocked") >= 40
     and read(MOD / "events/atb_th_events.txt").count("has_leader_flag = atb_th_rc_") >= 40
     and "atb_th.2" in read(MOD / "common/on_actions/atb_th_on_actions.txt")
     and "has_leader_flag = atb_th_leader\t# 东方领袖" in read(MOD / "common/game_rules/atb_th_rules.txt")
     and "is_leader_tier = leader_tier_legendary" in read(MOD / "common/game_rules/atb_th_rules.txt")),
    ("3.7：四位皇女是传奇典范，东方角色是英杰典范，原作加不上的原版特质已替换",
     "tier = leader_tier_legendary" in read(MOD / "common/scripted_effects/atb_effects.txt").split("atb_create_princess = {", 1)[1].split("\n}", 1)[0]
     and "tier = leader_tier_renowned" in read(MOD / "common/scripted_effects/atb_th_leader_effects.txt")
     and not any(x in read(MOD / "common/scripted_effects/atb_th_leader_effects.txt") for x in (
         "leader_trait_farming_focus ", "leader_trait_enlister ", "leader_trait_generator_focus_3 ",
         "trait_ruler_deep_connections ", "leader_trait_insider_trading "))),
    ("星系贸易中心：远征军帝国市场评分拉满", "value = 1000000" in auto_ev and "ongoing_market_nomination" in auto_ev),
    ("3.5：探寻遗珍只抽内置的 GPM 遗珍，并补发隐形装置、陨落者旗帜的将领特质", "has_guillis_planet_modifiers_mod" not in quest
     and quest.count("add_relic = gpm_r_") >= 28 and "add_relic = r_" not in quest
     and "id = gpm_relics.1 }" in quest and "id = gpm_relics.20 }" in quest),
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
    ("civic_exalted_priesthood", r"^civic_exalted_priesthood\s*=\s*\{", "common/governments/civics/*.txt"),
    ("civic_dark_consortium", r"^civic_dark_consortium\s*=\s*\{", "common/governments/civics/*.txt"),
    ("ethic_spiritualist", r"^ethic_spiritualist\s*=\s*\{", "common/ethics/*.txt"),
    ("ethic_fanatic_xenophobe", r"^ethic_fanatic_xenophobe\s*=\s*\{", "common/ethics/*.txt"),
    ("civic_machine_ascensionists", r"^civic_machine_ascensionists\s*=\s*\{", "common/governments/civics/*.txt"),
    ("auth_corporate", r"^auth_corporate\s*=\s*\{", "common/governments/authorities/*.txt"),
    ("ethic_fanatic_militarist", r"^ethic_fanatic_militarist\s*=\s*\{", "common/ethics/*.txt"),
    ("lgate_base", r"^lgate_base\s*=\s*\{", "common/megastructures/*.txt"),
    *[(c, rf"^{c}\s*=\s*\{{", "common/governments/civics/*.txt") for c in (
        "civic_gospel_of_the_masses", "civic_corporate_crafters", "civic_naval_contractors")],
    *[(t, rf"^{t}\s*=\s*\{{", "common/technology/*.txt") for t in (
        "tech_habitat_1", "tech_habitat_2", "tech_habitat_3")],
    ("civic_machine_ota_updates", r"^civic_machine_ota_updates\s*=\s*\{", "common/governments/civics/*.txt"),
    ("civic_fanatic_purifiers", r"^civic_fanatic_purifiers\s*=\s*\{", "common/governments/civics/*.txt"),
    *[(c, rf"^{c}\s*=\s*\{{", "common/governments/civics/*.txt") for c in (
        "civic_machine_replication", "civic_selective_kinship", "civic_functional_architecture",
        "civic_feudal_realm", "civic_distinguished_admiralty", "civic_hive_devouring_swarm", "civic_hive_one_mind",
        "civic_hive_subspace_ephapse", "civic_machine_terminator", "civic_machine_warbots", "civic_memory_vault_machine")],
    ("r_zro_crystal", r"^r_zro_crystal\s*=\s*\{", "common/relics/*.txt"),
    ("ap_cosmogenesis", r"^ap_cosmogenesis\s*=\s*\{", "common/ascension_perks/*.txt"),
    ("ap_become_the_crisis", r"^ap_become_the_crisis\s*=\s*\{", "common/ascension_perks/*.txt"),
    ("ap_engineered_evolution", r"^ap_engineered_evolution\s*=\s*\{", "common/ascension_perks/*.txt"),
    ("give_purity_unlocks_effect", r"^give_purity_unlocks_effect\s*=\s*\{", "common/scripted_effects/*.txt"),
    ("can_set_ai_policy", r"^can_set_ai_policy\s*=\s*\{", "common/scripted_triggers/*.txt"),
    ("mega_shipyard_ruined", r"^mega_shipyard_ruined\s*=\s*\{", "common/megastructures/*.txt"),
    ("crisis_sphere_ruined", r"^crisis_sphere_ruined\s*=\s*\{", "common/megastructures/*.txt"),
    ("the_chosen_home_initializer", r"^the_chosen_home_initializer\s*=\s*\{", "common/solar_system_initializers/*.txt"),
    ("generate_start_pops", r"^generate_start_pops\s*=\s*\{", "common/scripted_effects/*.txt"),
    ("special/the_swarm.dds", r".", "flags/special/the_swarm.dds"),
    # 预设帝国「苍神缘起帝国」用到的原版内容
    *[(x, rf"^{x}\s*=\s*\{{", "common/governments/civics/*.txt") for x in ("civic_philosopher_king", "civic_technocracy")],
    *[(x, rf"^{x}\s*=\s*\{{", "common/ethics/*.txt") for x in ("ethic_fanatic_authoritarian", "ethic_materialist")],
    *[(x, rf"^{x}\s*=\s*\{{", "common/traits/*.txt") for x in ("trait_intelligent", "trait_natural_engineers", "trait_pathogenic_genes")],
    ("human_female_05 肖像", r"^\s*human_female_05\s*=", "gfx/portraits/portraits/*.txt"),
    ("imperial/imperial_01.dds", r".", "flags/imperial/imperial_01.dds"),
    ("special/ai_02.dds", r".", "flags/special/ai_02.dds"),
    ("tech_psionic_theory", r"^tech_psionic_theory\s*=\s*\{", "common/technology/*.txt"),
    ("ap_mind_over_matter", r"^ap_mind_over_matter\s*=\s*\{", "common/ascension_perks/*.txt"),
    ("tr_psionics_adopt", r"^tr_psionics_adopt\s*=\s*\{", "common/traditions/*.txt"),
    # 同化速度靠这两个修正进 assimilation_counter，原版 set_assimilation_counter_variable 里读
    ("auto_mod_monthly_add 用于同化计数", r"modifier\s*=\s*auto_mod_monthly_add", "common/scripted_effects/*.txt"),
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
