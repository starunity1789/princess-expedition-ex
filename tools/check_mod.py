"""皇女的远征军EX：改动后的静态自检。只读，不改任何文件。"""
import re
import sys
from pathlib import Path

# Windows 控制台默认 cp1252，打印中文会报 UnicodeEncodeError
sys.stdout.reconfigure(encoding="utf-8")

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
    ("远星国民 = 民营勘探者 + 巧手公司 + 舰队承包商",
     "civic = civic_private_prospectors civic = civic_corporate_crafters civic = civic_naval_contractors" in init),
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
    ("恐惧之潮方位 = 180°（9 点）", "9 点方位（角度 180）" in ev),
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
    ("2.7：五个列强开局海军容量 +1000、恒星基地上限 +10", init.count("modifier = atbgp_power_base") == 5
     and "country_naval_cap_add = 1000\n\tcountry_starbase_capacity_add = 10" in gpmod),
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
    ("远征军星团方位 = 12 点（88~92）",
     exeff.count("min_orientation_angle = 88") == 6 and "min_orientation_angle = 267" in exeff),
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
     and (MOD / "common/name_lists/00_cgen_azure_genesis.txt").read_bytes().startswith(b"\xef\xbb\xbf")),
    ("预设帝国「苍神缘起帝国」：皇女起源 + 内置名称集", all(x in read(MOD / "prescripted_countries/atb_prescripted_countries.txt") for x in (
        'origin = "origin_atb_princess_expedition"', 'name_list = "CGEN_AZURE_GENESIS"', "playable = atb_preset_playable",
        'authority = "auth_dictatorial"', 'government = "gov_technocratic_dictatorship"', 'planet_class = "pc_continental"'))
     and "atb_preset_playable = {" in read(MOD / "common/scripted_triggers/atb_triggers.txt")),
    ("巨型船坞 50 个船坞", mega.count("starbase_shipyard_capacity_add = 50") == 2 and "capacity_add = 20" not in mega),
    ("天选民固定 8 点", "atb_ex_spawn_chosen = yes" in exev and exeff.count("min_orientation_angle = 208") == 4
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
        "civic_private_prospectors", "civic_corporate_crafters", "civic_naval_contractors")],
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
