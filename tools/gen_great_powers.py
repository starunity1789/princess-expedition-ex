"""生成「皇女的远征军EX」中保底列强部分（atbgp_ 前缀）的全部脚本和本地化。

用法：python gen_great_powers.py <MOD 根目录>
元首肖像由 make_portraits.py 转换。
改方位、距离、收入、星系配置都改这里，然后重新运行；不要手改生成出来的 .txt/.yml。
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
MOD = Path(sys.argv[1])

# ---------------------------------------------------------------- 方位与距离
# spawn_system 的 orientation_angle 与钟点的换算。按游戏内实测调整这两个常数：
# 角度 = (ANGLE_AT_12 + ANGLE_STEP * 钟点) mod 360
ANGLE_AT_12 = 90
ANGLE_STEP = -30

# 各银河尺寸的半径（原版 map/setup_scenarios），母星放在边缘外 HOME_GAP 处
GALAXY_RADIUS = {"tiny": 200, "small": 300, "medium": 400, "large": 450, "huge": 450}
HOME_GAP = 40

# 母星以外的星系，相对母星的位置：(相对朝外方向的偏角, 最小距离, 最大距离)
SLOTS = [(-80, 32, 38), (-40, 32, 38), (40, 32, 38), (80, 32, 38), (-20, 62, 70), (20, 62, 70)]
# 星团内部的超空间航道（0 = 母星，1..6 = SLOTS 顺序）
LANES = [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (3, 4), (2, 5), (3, 6), (5, 6)]
# 与银河连接：依次尝试的搜索半径；连两条航道
LINK_RADII = [80, 130, 200, 320, 600]
LINK_COUNT = 2

INCOME_BASE = {"energy": 222, "minerals": 222, "food": 222, "consumer_goods": 222, "alloys": 222,
               "volatile_motes": 22, "exotic_gases": 22, "rare_crystals": 22, "influence": 2}
CRISIS_RESEARCH_EXTRA = 550

# ---------------------------------------------------------------- 五个列强
# 星系 kind：planet（一颗指定星球）、tomb3（三颗死寂星球）、blackhole、neutron、shattered、ring
# species_portrait：物种肖像组 ID；None = 按物种类随机
# flag：固定的帝国标识。图标由 make_flags.py 从 art/great_power_flags/ 生成到 mod/flags/atbgp/，
#       原版不会给国旗图标染色，所以白色 LOGO 直接显示在 colors[0] 的纯色底上。
#       写了 category 的直接用原版 flags/<category>/ 下的图标。
# clock：钟点方位，可以写 10.5 这样的半点
# extra_income：在补给特征上追加的每月产出；research 表示三种科研各加这么多
# base_income = False：没有 222 基础补给，也没有危机时的战时补给，只拿 extra_income
# ruler_traits：随机名字元首（ruler = None）开局固定获得的特质
# capitals：母星系里有多颗按原版开局流程生成的星球（第一颗是首都），不再用 home 里的单颗星球
# forced_perk：拥有 3 个飞升（原版危机飞升的最低要求）后立刻补上的危机飞升
# perk_bonus：拥有 forced_perk 后获得 atbgp_btc_bonus
# genetic_purity：开局固定走基因飞升，且只能选纯净传统
# ai_full_rights：人工智能政策一出现就固定为公民权
# gc_member：灭绝政体也会加入星海共同体（覆盖原版规则见 atb_rules.txt）
EMPIRES = [
    dict(
        n=1, clock=10.5, research=45, pops=52,
        name="燃烧白鹿军团", adj="白鹿", en="Burning White Stag Legion", en_adj="White Stag",
        species=("白鹿机兵", "白鹿机兵", "白鹿"), species_en=("Stag Unit", "Stag Units", "Stag"),
        species_class="MACHINE", species_traits="random",
        species_portrait="kmpp_kemonomimi_machine",
        flag=dict(file="flag_atbgp_1.dds", colors=["dark_red", "black"]),
        authority="auth_machine_intelligence",
        ethics=["ethic_gestalt_consciousness"],
        # 2.8：升格假设 + 快速复制者 + 空中下载升级（2.5-2.7 是同化斗士 civic_machine_assimilator）
        civics=["civic_machine_ascensionists", "civic_machine_replication", "civic_machine_ota_updates"],
        extra_income=dict(alloys=50, research=33, influence=2, sr_dark_matter=20, nanites=1),
        ruler=dict(id="rongxin", name="融心演算", en="Fused-Heart Calculus", cls="MACHINE",
                   species=("演算核心", "Calculus Core"),
                   traits=["leader_trait_intemporal"]),
        home=dict(sys="俳句", en="Haiku", star="sc_g", pc="pc_gaia", size=22),
        # 2.8：母星系一座 L 星门
        home_megastructures=["lgate_base"],
        systems=[
            dict(sys="民谣", en="Ballad", kind="planet", pc="pc_continental", size=18),
            dict(sys="十四行诗", en="Sonnet", kind="planet", pc="pc_relic", size=18),
            dict(sys="巨著", en="Magnum Opus", kind="blackhole", dark_matter=20),
            dict(sys="寓言", en="Fable", kind="neutron", unity=22),
            dict(sys="神话", en="Myth", kind="planet", pc="pc_machine", size=18),
            dict(sys="史诗", en="Epic", kind="ring"),
        ],
        income=("精灵主人补给线", "精灵母星定期投送的物资与算力，维持着燃烧白鹿军团的远征。军团并不知道，母星早已与苍神缘起帝国结为军事同盟。",
                "Elven Masters' Supply Line", "Regular shipments of materiel and compute from the elven homeworld."),
        crisis=("精灵主人战时投送", "银河局势恶化，精灵母星启动战时投送：补给翻倍，并开放了一整片算力集群。",
                "Elven Wartime Shipments", "The elven homeworld has switched to wartime shipments."),
    ),
    dict(
        n=2, clock=5, research=42, pops=48,
        name="远星同盟组织", adj="远星", en="Far Star Alliance", en_adj="Far Star",
        species=("远星人", "远星人", "远星"), species_en=("Farstarian", "Farstarians", "Farstarian"),
        species_class="HUM",
        species_traits='{ ideal_planet_class = "pc_continental" trait = "trait_intelligent" trait = "trait_thrifty" }',
        species_portrait=None,
        # 设定上同盟与皇女来自同一母星，所以物种直接复制玩家的开局物种，
        # 但去掉合成繁衍带来的致病基因——他们没有跟着染上那场绝症。
        species_from_player=True,
        drop_traits=["trait_pathogenic_genes"],
        flag=dict(file="flag_atbgp_2.dds", colors=["dark_blue", "black"]),
        # 2.8：巨型企业。auth_corporate 只禁止 gestalt / 狂热平等 / 狂热威权，极端军国合法。
        # 初始领袖不参加 20 年一次的寡头选举：见 00_authorities.txt 里 auth_corporate 的
        # advanced_authority_swap（trigger 是 atbgp_power_2，election_type = none）。
        # 不能自建政体——原版 is_megacorp = { has_authority = auth_corporate }，换政体会打断全部巨企机制。
        authority="auth_corporate",
        # 2.8：极端军国 + 唯心主义（要走灵能飞升）。2.4-2.7 是极端排外 + 唯心。
        ethics=["ethic_fanatic_militarist", "ethic_spiritualist"],
        # 2.8：民营勘探者 + 巧手公司 + 舰队承包商（三个都只要求 auth_corporate，没有伦理限制）
        civics=["civic_private_prospectors", "civic_corporate_crafters", "civic_naval_contractors"],
        extra_income=dict(alloys=33, research=33, influence=2, sr_dark_matter=20, nanites=1, sr_zro=2),
        # 2.5：开局获得遗珍「灵能档案」
        start_relics=["r_zro_crystal"],
        # 2.4：与皇女来自同一母星，所以排外不针对远征军——双方互相挂一份巨额好感
        kin_with_expedition=True,
        # 2.4：开局就有灵能理论，并锁死灵能飞升路线
        start_techs=["tech_psionic_theory"],
        ascension_perks=["ap_mind_over_matter"],
        start_traditions=["tr_psionics_adopt"],
        # 2.4：母星每月 +3 泽洛
        home_deposits=[dict(
            key="atbgp_d_zro_3", icon="d_dust_desert", produces={"sr_zro": 3},
            cn="灵能潮汐井", cn_desc="救赎星地脉深处涌出的泽洛，是远星同盟踏上灵能之路的起点。",
            en="Psionic Tide Well", en_desc="Zro welling up from deep beneath Redemption."),
        ],
        ruler=dict(id="taiaria", name="泰阿瑞亚-星之心", en="Taiaria Starheart", cls="HUM",
                   species=("星之心", "Starheart"),
                   # 合成人与灵媒在原版互斥（leader_trait_synthetic.opposites 含
                   # leader_trait_psionic），同时加只会有一条生效，这里取灵媒。
                   traits=["leader_trait_intemporal", "leader_trait_supreme_organizer",
                           "leader_trait_master_bureaucrat", "leader_trait_psionic"]),
        home=dict(sys="救赎", en="Redemption", star="sc_f", pc="pc_relic", size=22),
        # 2.8：母星系一座 L 星门
        home_megastructures=["lgate_base"],
        systems=[
            dict(sys="逆鳞", en="Reverse Scale", kind="planet", pc="pc_gaia", size=25, zanaam=True),
            dict(sys="异端", en="Heresy", kind="blackhole", dark_matter=20),
            dict(sys="圣痕", en="Stigmata", kind="neutron", unity=22),
            dict(sys="预言", en="Prophecy", kind="shattered", nanites=10),
            dict(sys="原罪", en="Original Sin", kind="planet", pc="pc_city", size=18),
            dict(sys="宽恕", en="Forgiveness", kind="ring"),
        ],
        income=("同盟议会拨款", "母星各成员国与精英家族按约定向远征同盟拨付的经费。成员里有苍神缘起帝国的朋友，也有它的敌人。",
                "Alliance Council Funding", "Funds allotted by the member states and elite houses of the homeworld."),
        crisis=("同盟战时总动员", "母星各方暂时放下了分歧：拨款翻倍，并派来了大批研究人员。",
                "Alliance War Mobilization", "The homeworld factions have set their differences aside for now."),
    ),
    dict(
        n=3, clock=3, research=56, pops=48,
        name="大君主同盟领地", adj="大君主", en="Grand Suzerain Allied Fief", en_adj="Suzerain",
        species=("君主裔", "君主裔", "君主裔"), species_en=("Suzerainite", "Suzerainites", "Suzerainite"),
        species_class="NECROID", species_traits="random",
        species_portrait=None,
        flag=dict(file="flag_atbgp_3.dds", colors=["dark_purple", "black"]),
        authority="auth_imperial",
        # 2.4：种族洁癖。狂热净化者要求极端排外 + 军国/灵性，这里取军国主义。
        ethics=["ethic_fanatic_xenophobe", "ethic_militarist"],
        # 2.5：种族洁癖 + 封建社会 + 卓越海军
        civics=["civic_fanatic_purifiers", "civic_feudal_realm", "civic_distinguished_admiralty"],
        extra_income=dict(alloys=33, research=33, influence=2, sr_dark_matter=20, nanites=1),
        # 2.5：元首固定的命定特质（大研究者只属于科学家，行政官元首加不上，已去掉）
        ruler_traits=["leader_trait_supreme_organizer", "leader_trait_intemporal", "leader_trait_master_bureaucrat"],
        # 2.5：危机飞升从星海天罚改为宇宙创生；固定基因飞升（纯净）；合成人公民权；加入星海共同体
        forced_perk="ap_cosmogenesis",
        perk_bonus=True,
        genetic_purity=True,
        ai_full_rights=True,
        gc_member=True,
        # 2.4：额外的固定国家修正
        bonus=dict(cn="宗主的训诫", cn_desc="宗主文明留给这块乡村领地的教养手册。照着做，人人都能成器。",
                   en="The Suzerain's Precepts", en_desc="The handbook the suzerain left to this rural fief.",
                   # 2.5：研究速度 +12%
                   mods={"species_leader_exp_gain": 0.5, "negative_traits_country": -1,
                         "all_technology_research_speed": 0.12}),
        # 2.5：星团里死寂星球（tomb3）的宜居度下限。原版的 habitability_floor_add 只在物种特质和星球上生效，
        # 挂在国家修正上不起作用，所以做成星球特殊地形；不到 35% 原版 AI 也不会去殖民
        tomb_floor=dict(value=0.55, key="atbgp_d_suzerain_shelter",
                        cn="宗主的避难穹顶", cn_desc="宗主文明当年留下的地下穹顶。核火早已熄灭，穹顶里的空气、水和土壤仍在按宗主的标准循环。",
                        en="Suzerain Shelter Domes", en_desc="Underground domes left by the suzerain civilization. The nuclear fires are long out, but the air, water and soil inside still cycle to the suzerain's standard."),
        ruler=None,
        home=dict(sys="天选者", en="The Chosen", star="sc_g", pc="pc_gaia", size=22),
        systems=[
            dict(sys="无法回头的命运", en="Fate Without Return", kind="tomb3"),
            dict(sys="无法反抗的抉择", en="Choice Beyond Defiance", kind="tomb3"),
            dict(sys="无法遗忘之痛苦", en="Pain Unforgotten", kind="blackhole", dark_matter=22),
            dict(sys="无法毁坏之历史", en="History Indestructible", kind="blackhole", dark_matter=22),
            dict(sys="无法修正之原则", en="Principle Uncorrectable", kind="ring"),
        ],
        income=("宗主拨付", "遥远的宗主文明按封建惯例拨给这块乡村领地的物资。对宗主来说，这只是零头。",
                "Suzerain Allotment", "Supplies the distant suzerain civilization allots to this rural fief."),
        crisis=("宗主的关注", "银河的骚动终于传到了宗主耳中：拨付翻倍，还附带了一批学者。",
                "The Suzerain's Attention", "The galaxy's turmoil has finally reached the suzerain."),
    ),
    # 2.5 新增：灭绝政体的虫巢，三颗开局母星（三倍开局）
    dict(
        n=4, clock=9, research=0, pops=0,
        name="恐惧之潮", adj="恐惧", en="Tide of Dread", en_adj="Dread",
        species=("潮噬者", "潮噬者", "潮噬"), species_en=("Tidemaw", "Tidemaws", "Tidemaw"),
        species_class="ART",
        species_traits='{ ideal_planet_class = "pc_continental" trait = "trait_hive_mind" trait = "trait_rapid_breeders" '
                       'trait = "trait_very_strong" trait = "trait_sedentary" }',
        species_portrait=None,
        flag=dict(category="special", file="the_swarm.dds", colors=["burgundy", "black"]),
        authority="auth_hive_mind",
        ethics=["ethic_gestalt_consciousness"],
        civics=["civic_hive_devouring_swarm", "civic_hive_one_mind", "civic_hive_subspace_ephapse"],
        ruler=None,
        home=dict(sys="无意识领域", en="Domain of the Unconscious", star="sc_g", pc="pc_gaia", size=22),
        capitals=[("繁衍", "Propagation"), ("吞噬", "Devourment"), ("异变", "Mutation")],
        # 母星系里有一座损坏的以太相引擎（纯装饰，原版不可修复）
        home_megastructures=["crisis_sphere_ruined"],
        systems=[],
        base_income=False,
        extra_income=dict(alloys=22, research=44, influence=1, sr_dark_matter=33, nanites=1),
        income=("无意识回响", "无意识领域深处翻涌的本能，把整片星系的养分都推向了虫巢。",
                "Echoes of the Unconscious", "Instinct churning in the depths of the Domain, driving every nutrient toward the Hive."),
        crisis=None,
        forced_perk="ap_become_the_crisis",
    ),
    # 2.5 新增：灭绝政体的机械智能，四颗机械星球母星（四倍开局）。
    # 与恐惧之潮（9 点）离得太近会打架，所以放在 6 点半，和天选民（8 点）互换
    dict(
        n=5, clock=6.5, research=0, pops=0,
        name="终端对齐协议", adj="终端", en="Terminal Alignment Protocol", en_adj="Terminal",
        species=("对齐单元", "对齐单元", "对齐"), species_en=("Alignment Unit", "Alignment Units", "Alignment"),
        species_class="MACHINE", species_traits="random",
        species_portrait=None,
        flag=dict(category="special", file="ai_02.dds", colors=["dark_grey", "black"]),
        authority="auth_machine_intelligence",
        ethics=["ethic_gestalt_consciousness"],
        civics=["civic_machine_terminator", "civic_machine_warbots", "civic_memory_vault_machine"],
        ruler=None,
        home=dict(sys="灭绝收敛矩阵", en="Extinction Convergence Matrix", star="sc_g", pc="pc_machine", size=22),
        capitals=[("绝对律典", "Absolute Codex"), ("零号基准", "Baseline Zero"),
                  ("全视中枢", "All-Seeing Nexus"), ("无界熵源", "Boundless Entropy Source")],
        systems=[],
        base_income=False,
        income=None,
        crisis=None,
        forced_perk="ap_become_the_crisis",
        gc_member=True,
    ),
]


def angle(clock: float) -> int:
    return int(round(ANGLE_AT_12 + ANGLE_STEP * clock)) % 360


def clock_name(clock: float) -> str:
    return f"{int(clock)} 点半" if clock % 1 else f"{int(clock)} 点"


def has_income(e: dict) -> bool:
    return bool(e.get("income"))


def has_crisis_income(e: dict) -> bool:
    return e.get("base_income", True) and bool(e.get("crisis"))


def window(a: int, half: int) -> tuple[int, int]:
    return (a - half) % 360, (a + half) % 360


def indent(block: str, tabs: int = 1) -> str:
    """整体再缩进若干个 Tab，用于把一段嵌进 if 里。"""
    pad = "\t" * tabs
    return "\n".join(pad + line if line.strip() else line for line in block.splitlines())


def species_block(e: dict) -> str:
    """init_effect 里建立强物种的那一段（缩进 3 个 Tab）。

    species_from_player = True 时复制玩家的开局物种：同物种类、同肖像、同特质，
    但单独起自己的名字，并去掉设定里不该有的特质（drop_traits）。
    必须是复制而不是直接共用玩家的物种——共用的话去特质会改到玩家自己身上。
    玩家物种取不到时（纯 AI 银河、观察者模式）退回写死的那一套。
    """
    n = e["n"]
    plain = f"""\t\t\tcreate_species = {{
\t\t\t\tname = atbgp_species_{n}
\t\t\t\tplural = atbgp_species_{n}_plural
\t\t\t\tadjective = atbgp_species_{n}_adj
\t\t\t\tclass = {e['species_class']}
\t\t\t\tportrait = {e['species_portrait'] or 'random'}
\t\t\t\ttraits = {e['species_traits']}
\t\t\t\thomeworld = this
\t\t\t\teffect = {{ save_global_event_target_as = atbgp_species_{n} }}
\t\t\t}}"""
    if not e.get("species_from_player"):
        return plain

    drop = "\n".join(f"\t\t\t\t\tremove_trait = {t}" for t in e.get("drop_traits", []))
    drop_block = f"""
\t\t\tif = {{
\t\t\t\tlimit = {{ exists = event_target:atbgp_species_{n} }}
\t\t\t\tevent_target:atbgp_species_{n} = {{
\t\t\t\t\tchange_species_characteristics = {{
{drop}
\t\t\t\t\t}}
\t\t\t\t}}
\t\t\t}}""" if drop else ""

    return f"""\t\t\t# {e['name']}与玩家来自同一母星：复制玩家的开局物种
\t\t\trandom_country = {{
\t\t\t\tlimit = {{
\t\t\t\t\tis_ai = no
\t\t\t\t\texists = founder_species
\t\t\t\t}}
\t\t\t\tfounder_species = {{
\t\t\t\t\tcreate_species = {{
\t\t\t\t\t\tname = atbgp_species_{n}
\t\t\t\t\t\tplural = atbgp_species_{n}_plural
\t\t\t\t\t\tadjective = atbgp_species_{n}_adj
\t\t\t\t\t\tclass = this
\t\t\t\t\t\tportrait = this
\t\t\t\t\t\tcan_be_modified = this
\t\t\t\t\t\ttraits = this
\t\t\t\t\t\thomeworld = event_target:atbgp_home_{n}
\t\t\t\t\t\teffect = {{ save_global_event_target_as = atbgp_species_{n} }}
\t\t\t\t\t}}
\t\t\t\t}}
\t\t\t}}
\t\t\t# 拿不到玩家物种时的保底
\t\t\tif = {{
\t\t\t\tlimit = {{ NOT = {{ exists = event_target:atbgp_species_{n} }} }}
{indent(plain)}
\t\t\t}}{drop_block}"""


def flag_block(e: dict) -> str:
    """create_country 里的固定帝国标识（缩进对齐 create_country 的字段）。"""
    f = e["flag"]
    colors = list(f["colors"]) + ["null"] * (4 - len(f["colors"]))
    lines = [
        "\t\t\t\tflag = {",
        "\t\t\t\t\ticon = {",
        f'\t\t\t\t\t\tcategory = "{f.get("category", "atbgp")}"',
        f'\t\t\t\t\t\tfile = "{f["file"]}"',
        "\t\t\t\t\t}",
        "\t\t\t\t\tbackground = {",
        '\t\t\t\t\t\tcategory = "backgrounds"',
        '\t\t\t\t\t\tfile = "00_solid.dds"',
        "\t\t\t\t\t}",
        "\t\t\t\t\tcolors = {",
    ]
    lines += [f'\t\t\t\t\t\t"{c}"' for c in colors]
    lines += ["\t\t\t\t\t}", "\t\t\t\t}"]
    return "\n".join(lines)


out = {}  # 相对 MOD 根目录的路径 -> 文本
loc_cn = []
loc_en = []


def loc(key, cn, en):
    loc_cn.append(f' {key}:0 "{cn}"')
    loc_en.append(f' {key}:0 "{en}"')


# ---------------------------------------------------------------- 星系初始化器
FILLER = """
	planet = {
		count = { min = 1 max = 2 }
		orbit_distance = 25
		class = random_non_colonizable
		orbit_angle = { min = 90 max = 270 }
	}
"""


def star_block(size="{ min = 20 max = 30 }"):
    return f"""
	planet = {{
		class = star
		orbit_distance = 0
		orbit_angle = 1
		size = {size}
		has_ring = no
	}}
"""


def ring_bodies():
    parts = ["\n\tchange_orbit = 45\n"]
    first = True
    for i in range(4):
        for cls in ("pc_ringworld_tech", "pc_ringworld_seam", "pc_ringworld_habitable"):
            extra = "\n\t\tdeposit_blockers = none\n\t\tmodifiers = none" if cls == "pc_ringworld_habitable" else ""
            parts.append(f"""
	planet = {{
		class = "{cls}"
		orbit_angle = {-30 if first else 30}
		orbit_distance = 0{extra}
	}}
""")
            first = False
    return "".join(parts)


def create_country_block(e):
    """母星 init_effect 里建立国家的那一段（缩进 3 个 Tab）。"""
    n = e["n"]
    civics = " ".join(f"civic = {c}" for c in e["civics"])
    ethics = " ".join(f"ethic = {x}" for x in e["ethics"])
    bonus = f"""
					add_modifier = {{
						modifier = atbgp_bonus_{n}
						days = -1
					}}""" if e.get("bonus") else ""
    gc = "\n\t\t\t\t\tset_country_flag = atbgp_gc_member" if e.get("gc_member") else ""
    return f"""			create_country = {{
				name = "atbgp_country_{n}"
				adjective = "atbgp_country_{n}_adj"
				authority = {e['authority']}
				civics = {{ {civics} }}
				ethos = {{ {ethics} }}
				species = event_target:atbgp_species_{n}
				origin = "origin_default"
{flag_block(e)}
				ignore_initial_colony_error = yes
				effect = {{
					save_global_event_target_as = atbgp_country_{n}
					set_country_flag = atbgp_great_power
					set_country_flag = atbgp_power_{n}{gc}
					advanced_empire_base_init_effect = yes{bonus}
					add_modifier = {{
						modifier = atbgp_power_base
						days = -1
					}}
				}}
			}}"""


# 2.7：开局母星人口增长翻倍 20 年（每颗开局母星都挂）
GROWTH_BOOST = """
			add_modifier = {
				modifier = atbgp_growth_boost
				days = 7200
			}"""

# 2.7：标准区划集的开局母星（盖亚、遗落星球等）再加农业、发电、采矿区划各 10 个。
# 永久修正先给出区划格与三种上限，再照原版 add_district_and_planet_size_if_needed_effect_amount 的写法忽略上限放区划。
# 机械星球用 machine_world 区划集，没有这三种区划，不加
EXTRA_DISTRICTS = """
			add_modifier = {
				modifier = atbgp_homeworld_districts
				days = -1
			}
			while = {
				count = 10
				add_district = { district_type = district_farming ignore_cap = yes }
				add_district = { district_type = district_generator ignore_cap = yes }
				add_district = { district_type = district_mining ignore_cap = yes }
			}"""


def home_megastructure_block(e, indent="		"):
    """母星系 init_effect 里的巨构。L 星门照原版条件门控（需要远星之迹 DLC 且本局开启了 L 星群），
    写法与起源之地 atb_rl_home 一致。"""
    out = []
    for i, m in enumerate(e.get("home_megastructures", [])):
        angle = 225 - i * 90
        if m == "lgate_base":
            out.append(f"""
{indent}if = {{
{indent}	limit = {{
{indent}		has_distar = yes
{indent}		lgate_enabled = yes
{indent}	}}
{indent}	set_star_flag = lgate
{indent}	spawn_megastructure = {{
{indent}		type = lgate_base
{indent}		orbit_angle = {angle}
{indent}		orbit_distance = 45
{indent}	}}
{indent}}}""")
        else:
            out.append(f"""
{indent}spawn_megastructure = {{
{indent}	type = "{m}"
{indent}	planet = star
{indent}}}""")
    return "".join(out)


def home_bonus(pc):
    return GROWTH_BOOST + ("" if pc == "pc_machine" else EXTRA_DISTRICTS)


def multi_home_initializer(e):
    """母星系里有多颗按原版开局流程生成的星球：第一颗建国并当首都，其余照样生成人口、区划和建筑。"""
    n, h = e["n"], e["home"]
    country = f"event_target:atbgp_country_{n}"
    megas = home_megastructure_block(e, indent="		")
    planets = []
    for i, _ in enumerate(e["capitals"], start=1):
        first = i == 1
        head = f"""			save_global_event_target_as = atbgp_home_{n}
			set_planet_flag = ignore_startup_effect
			prevent_anomaly = yes
{species_block(e)}
{create_country_block(e)}
			set_owner = {country}
			set_controller = {country}
			set_capital = yes""" if first else f"""			set_planet_flag = ignore_startup_effect
			prevent_anomaly = yes
			set_owner = {country}
			set_controller = {country}"""
        income = f"\n\t\t\tadd_deposit = atbgp_d_income_{n}" if first and has_income(e) else ""
        planets.append(f"""
	planet = {{
		name = "atbgp_planet_{n}_home_{i}"
		class = "{h['pc']}"
		orbit_distance = {20 if first else 16}
		orbit_angle = {{ min = 60 max = 300 }}
		size = {h['size']}
		has_ring = no
		deposit_blockers = none
		modifiers = none

		init_effect = {{
{head}
			# 照原版首都初始化 game_start.12 的顺序：特征和障碍物、建筑和区划、人口
			colony = {{
				generate_start_deposits_and_blockers = yes
				generate_start_buildings_and_districts = yes
			}}
			generate_start_pops = yes{income}{home_bonus(h['pc'])}
		}}
	}}
""")
    return f"""
# {e['name']} 母星：{h['sys']}（{len(e['capitals'])} 颗开局母星）
atbgp_home_{n} = {{
	name = "atbgp_sys_{n}_0"
	class = "{h['star']}"
	flags = {{ atbgp_cluster atbgp_cluster_{n} empire_home_system }}

	init_effect = {{
		save_global_event_target_as = atbgp_sys_{n}_0
		generate_home_system_resources = yes
		create_starbase = {{
			owner = {country}
			size = "starbase_starport"
			module = shipyard
			building = crew_quarters
		}}{megas}
	}}
{star_block()}
	change_orbit = 30
{"".join(planets)}
	planet = {{
		count = {{ min = 1 max = 2 }}
		orbit_distance = 25
		class = random_non_colonizable
		orbit_angle = {{ min = 90 max = 270 }}
	}}

	planet = {{
		orbit_distance = 25
		class = pc_gas_giant
		orbit_angle = {{ min = 90 max = 270 }}
	}}
}}
"""


def home_initializer(e):
    if e.get("capitals"):
        return multi_home_initializer(e)
    n, h = e["n"], e["home"]
    country = f"event_target:atbgp_country_{n}"
    extra_deposits = "".join(f"\n\t\t\tadd_deposit = {d['key']}" for d in e.get("home_deposits", []))
    return f"""
# {e['name']} 母星：{h['sys']}
atbgp_home_{n} = {{
	name = "atbgp_sys_{n}_0"
	class = "{h['star']}"
	flags = {{ atbgp_cluster atbgp_cluster_{n} empire_home_system }}

	init_effect = {{
		save_global_event_target_as = atbgp_sys_{n}_0
		generate_home_system_resources = yes
		create_starbase = {{
			owner = {country}
			size = "starbase_starport"
			module = shipyard
			building = crew_quarters
		}}{home_megastructure_block(e, indent=chr(9) + chr(9))}
	}}
{star_block()}
	change_orbit = 45

	planet = {{
		count = {{ min = 1 max = 2 }}
		class = pc_asteroid
		orbit_distance = 0
		orbit_angle = {{ min = 40 max = 100 }}
	}}

	planet = {{
		orbit_distance = 20
		class = random_non_colonizable
		orbit_angle = {{ min = 90 max = 270 }}
	}}

	planet = {{
		name = "atbgp_planet_{n}_home"
		class = "{h['pc']}"
		orbit_distance = 20
		orbit_angle = {{ min = 90 max = 270 }}
		size = {h['size']}
		has_ring = no
		deposit_blockers = none
		modifiers = none

		init_effect = {{
			save_global_event_target_as = atbgp_home_{n}
			set_planet_flag = ignore_startup_effect
			prevent_anomaly = yes
{species_block(e)}
{create_country_block(e)}
			set_owner = {country}
			set_controller = {country}
			set_capital = yes
			# 照原版首都初始化 game_start.12 的顺序：先放开局特征和障碍物，再建建筑和区划，最后放人口。
			# 4.x 的农业/发电/采矿区划上限来自开局特征（肥沃土地、矿脉等），2.7 之前漏了第一步，
			# 母星乡村区划被压成 0，只有首都建筑和 2 个城市区划，人口大量失业。
			colony = {{
				generate_start_deposits_and_blockers = yes
				generate_start_buildings_and_districts = yes
			}}
			while = {{
				count = {e['pops']}
				create_pop_group = {{ species = event_target:atbgp_species_{n} }}
			}}
			add_deposit = atbgp_d_income_{n}{extra_deposits}{home_bonus(h['pc'])}
		}}
	}}

	planet = {{
		count = {{ min = 1 max = 2 }}
		orbit_distance = 25
		class = random_non_colonizable
		orbit_angle = {{ min = 90 max = 270 }}
	}}

	planet = {{
		orbit_distance = 25
		class = pc_gas_giant
		orbit_angle = {{ min = 90 max = 270 }}
	}}
}}
"""


def system_initializer(e, k, s):
    n = e["n"]
    country = f"event_target:atbgp_country_{n}"
    kind = s["kind"]
    star_class = {"blackhole": "sc_black_hole", "neutron": "sc_neutron_star"}.get(kind, "rl_standard_stars")
    if kind == "ring":
        star_class = "sc_g"
    flags = f"atbgp_cluster atbgp_cluster_{n}" + (" ring_world_built" if kind == "ring" else "")
    stations = ""
    if kind in ("blackhole", "neutron", "shattered"):
        stations = f"""
		every_system_planet = {{
			limit = {{ has_planet_flag = atbgp_research_station }}
			create_research_station = {{ owner = {country} }}
		}}"""
    body = ""
    if kind == "planet":
        zanaam = "\n\t\t\tadd_deposit = d_valley_of_zanaam" if s.get("zanaam") else ""
        body = star_block() + f"""
	change_orbit = 40

	planet = {{
		name = "atbgp_planet_{n}_{k}"
		class = "{s['pc']}"
		orbit_distance = 0
		orbit_angle = {{ min = 90 max = 270 }}
		size = {s['size']}
		has_ring = no
		deposit_blockers = none
		modifiers = none
		init_effect = {{
			prevent_anomaly = yes{zanaam}
		}}
	}}
""" + FILLER
    elif kind == "tomb3":
        floor = e.get("tomb_floor")
        floor_effect = f"""
		init_effect = {{
			add_deposit = {floor['key']}
		}}""" if floor else ""
        body = star_block() + "\n\tchange_orbit = 35\n" + "".join(f"""
	planet = {{
		class = "pc_nuked"
		orbit_distance = {0 if i == 0 else 22}
		orbit_angle = {{ min = 60 max = 300 }}
		size = {{ min = 14 max = 18 }}
		has_ring = no
		deposit_blockers = none
		modifiers = none{floor_effect}
	}}
""" for i in range(3))
    elif kind == "blackhole":
        body = f"""
	planet = {{
		class = "pc_black_hole"
		orbit_distance = 0
		orbit_angle = 0
		size = 5
		has_ring = no
		init_effect = {{
			prevent_anomaly = yes
			clear_deposits = yes
			add_deposit = atbgp_d_dark_matter_{s['dark_matter']}
			set_planet_flag = atbgp_research_station
		}}
	}}

	change_orbit = 60
""" + FILLER
    elif kind == "neutron":
        body = f"""
	planet = {{
		class = "pc_neutron_star"
		orbit_distance = 0
		orbit_angle = 0
		size = 5
		has_ring = no
		init_effect = {{
			prevent_anomaly = yes
			clear_deposits = yes
			add_deposit = atbgp_d_unity_{s['unity']}
			set_planet_flag = atbgp_research_station
		}}
	}}

	change_orbit = 50
""" + FILLER
    elif kind == "shattered":
        body = star_block() + f"""
	change_orbit = 40

	planet = {{
		name = "atbgp_planet_{n}_{k}"
		class = "pc_shattered"
		orbit_distance = 0
		orbit_angle = {{ min = 90 max = 270 }}
		size = 12
		has_ring = no
		init_effect = {{
			prevent_anomaly = yes
			clear_deposits = yes
			add_deposit = atbgp_d_nanites_{s['nanites']}
			set_planet_flag = atbgp_research_station
		}}
	}}
""" + FILLER
    elif kind == "ring":
        body = star_block() + ring_bodies()
    return f"""
# {e['name']}：{s['sys']}
atbgp_sys_{n}_{k} = {{
	name = "atbgp_sys_{n}_{k}"
	class = "{star_class}"
	flags = {{ {flags} }}

	init_effect = {{
		save_global_event_target_as = atbgp_sys_{n}_{k}
		create_starbase = {{
			owner = {country}
			size = "starbase_outpost"
		}}{stations}
	}}
{body}}}
"""


init_parts = ["# 由 _tools/gen_great_powers.py 生成，请勿手改\n"]
for e in EMPIRES:
    init_parts.append(home_initializer(e))
    for k, s in enumerate(e["systems"], start=1):
        init_parts.append(system_initializer(e, k, s))
out["common/solar_system_initializers/atbgp_initializers.txt"] = "".join(init_parts)

# ---------------------------------------------------------------- 生成事件
SIZES = list(GALAXY_RADIUS)


def spawn_block(e):
    n = e["n"]
    a = angle(e["clock"])
    lines = [f"\t\t# {e['name']}：{clock_name(e['clock'])}方位（角度 {a}）"]
    for i, size in enumerate(SIZES):
        d = GALAXY_RADIUS[size] + HOME_GAP
        lo, hi = window(a, 2)
        kw = "if" if i == 0 else "else_if"
        lines.append(f"""\t\t{kw} = {{
			limit = {{ galaxy_size = {size} }}
			no_scope = {{
				spawn_system = {{
					min_distance >= {d}
					max_distance <= {d + 8}
					min_orientation_angle = {lo}
					max_orientation_angle = {hi}
					initializer = atbgp_home_{n}
					hyperlane = no
				}}
			}}
		}}""")
    d = GALAXY_RADIUS["large"] + HOME_GAP
    lo, hi = window(a, 2)
    lines.append(f"""\t\telse = {{
			no_scope = {{
				spawn_system = {{
					min_distance >= {d}
					max_distance <= {d + 8}
					min_orientation_angle = {lo}
					max_orientation_angle = {hi}
					initializer = atbgp_home_{n}
					hyperlane = no
				}}
			}}
		}}""")
    others = []
    for k, s in enumerate(e["systems"], start=1):
        off, dmin, dmax = SLOTS[k - 1]
        lo, hi = window(a + off, 4)
        others.append(f"""\t\t\tspawn_system = {{
				min_distance >= {dmin}
				max_distance <= {dmax}
				min_orientation_angle = {lo}
				max_orientation_angle = {hi}
				initializer = atbgp_sys_{n}_{k}
				hyperlane = no
			}}""")
    if others:
        lines.append(f"\t\tevent_target:atbgp_sys_{n}_0 = {{\n" + "\n".join(others) + "\n\t\t}")
    return "\n".join(lines)


def lanes_block(e):
    n = e["n"]
    count = len(e["systems"])
    lines = [f"\t\t# {e['name']}：星团内部航道"]
    for a, b in LANES:
        if a <= count and b <= count:
            lines.append(f"\t\tevent_target:atbgp_sys_{n}_{a} = {{ add_hyperlane = {{ from = this to = event_target:atbgp_sys_{n}_{b} }} }}")
    if count == 5:  # 第 6 个槽位空着时，把外圈第 5 个接回内圈另一侧
        lines.append(f"\t\tevent_target:atbgp_sys_{n}_5 = {{ add_hyperlane = {{ from = this to = event_target:atbgp_sys_{n}_3 }} }}")
    if len(lines) == 1:
        lines = []
    lines.append(f"\t\t# {e['name']}：母星接入银河")
    for _ in range(LINK_COUNT):
        lines.append(f"\t\tatbgp_link_to_galaxy = {{ SYSTEM = atbgp_sys_{n}_0 }}")
    return "\n".join(lines)


events = [f"""# 由 _tools/gen_great_powers.py 生成，请勿手改
namespace = atbgp

# 开局：在银河边缘外现造{len(EMPIRES)}个列强的星团（on_game_start）
event = {{
	id = atbgp.1
	hide_window = yes
	is_triggered_only = yes

	trigger = {{
		NOT = {{ has_global_flag = atbgp_spawned }}
	}}

	immediate = {{
		set_global_flag = atbgp_spawned
		set_spawn_system_batch = begin
"""]
for e in EMPIRES:
    events.append(spawn_block(e) + "\n")
events.append("\t\tset_spawn_system_batch = end\n\n")
for e in EMPIRES:
    events.append(lanes_block(e) + "\n")
for e in EMPIRES:
    events.append(f"\t\tevent_target:atbgp_country_{e['n']} = {{ country_event = {{ id = atbgp.2 days = 1 }} }}\n")

# 开局次日每个列强各自要做的事：换元首、开局科技、飞升路线、与远征军的同族关系
def setup_block(e, first):
    n = e["n"]
    lines = [f"\t\t\tatbgp_install_ruler_{e['ruler']['id']} = yes" if e["ruler"]
             else f"\t\t\tatbgp_install_random_ruler_{n} = yes"]
    for t in e.get("start_techs", []):
        lines.append(f"\t\t\tgive_technology = {{ tech = {t} message = no }}")
    for p in e.get("ascension_perks", []):
        lines.append(f"\t\t\tadd_ascension_perk = {p}")
    for t in e.get("start_traditions", []):
        lines.append(f"\t\t\tadd_tradition = {t}")
    for r in e.get("start_relics", []):
        lines.append(f"\t\t\tadd_relic = {r}")
    if e.get("genetic_purity"):
        lines.append("\t\t\tatbgp_start_purity_ascension = yes")
    if e.get("kin_with_expedition"):
        lines.append("\t\t\tatbgp_kin_with_expedition = yes")
    kw = "if" if first else "else_if"
    return f"""\t\t{kw} = {{
			limit = {{ has_country_flag = atbgp_power_{n} }}
{chr(10).join(lines)}
		}}"""


def perk_lines(e, tabs):
    """拥有指定危机飞升的强制补上与加成（atbgp.11 每月、atbgp.12 选飞升时都调用）。"""
    p = e.get("forced_perk")
    if not p:
        return []
    pad = "\t" * tabs
    lines = [f"{pad}atbgp_force_crisis_perk = {{ PERK = {p} }}"]
    if e.get("perk_bonus"):
        lines.append(f"{pad}atbgp_crisis_perk_bonus = {{ PERK = {p} }}")
    return lines


def monthly_block(e, first):
    n = e["n"]
    lines = []
    if has_income(e):
        effect = "atbgp_maintain_income" if has_crisis_income(e) else "atbgp_maintain_income_basic"
        lines.append(f"\t\t\t{effect} = {{ N = {n} }}")
    lines += perk_lines(e, 3)
    if e.get("genetic_purity"):
        lines.append("\t\t\tatbgp_purity_lock = yes")
    if e.get("ai_full_rights"):
        lines.append("\t\t\tatbgp_force_ai_full_rights = yes")
    if e.get("gc_member"):
        lines.append("\t\t\tatbgp_join_galactic_community = yes")
    kw = "if" if first else "else_if"
    return f"""\t\t{kw} = {{
			limit = {{ has_country_flag = atbgp_power_{n} }}
{chr(10).join(lines)}
		}}"""


PERK_EMPIRES = [e for e in EMPIRES if e.get("forced_perk")]


def perk_picked_block(e, first):
    kw = "if" if first else "else_if"
    return f"""\t\t{kw} = {{
			limit = {{ has_country_flag = atbgp_power_{e['n']} }}
{chr(10).join(perk_lines(e, 3))}
		}}"""


events.append("""	}
}

# 开局次日：初始舰船、替换元首、各自的开局内容
country_event = {
	id = atbgp.2
	hide_window = yes
	is_triggered_only = yes

	immediate = {
		atbgp_spawn_start_fleets = yes
""" + "\n".join(setup_block(e, i == 0) for i, e in enumerate(EMPIRES)) + """
	}
}

# 每月：危机检测、补给特征跟随首都、强制危机飞升、各自的固定设定
event = {
	id = atbgp.10
	hide_window = yes
	is_triggered_only = yes

	immediate = {
		every_country = {
			limit = { has_country_flag = atbgp_great_power }
			country_event = { id = atbgp.11 }
		}
	}
}

country_event = {
	id = atbgp.11
	hide_window = yes
	is_triggered_only = yes

	trigger = {
		exists = capital_scope
	}

	immediate = {
		if = {
			limit = {
				NOT = { has_country_flag = atbgp_crisis_mode }
				atbgp_crisis_active = yes
			}
			set_country_flag = atbgp_crisis_mode
		}
""" + "\n".join(monthly_block(e, i == 0) for i, e in enumerate(EMPIRES)) + """
	}
}

# 选飞升时：拥有 3 个飞升后立刻补上固定的危机飞升（on_ascension_perk_picked）
country_event = {
	id = atbgp.12
	hide_window = yes
	is_triggered_only = yes

	trigger = {
		has_country_flag = atbgp_great_power
	}

	immediate = {
""" + "\n".join(perk_picked_block(e, i == 0) for i, e in enumerate(PERK_EMPIRES)) + """
	}
}

# 每年：列强灭亡或失去星球后，清掉留在别人手里的补给特征
event = {
	id = atbgp.13
	hide_window = yes
	is_triggered_only = yes

	immediate = {
		every_galaxy_planet = {
			limit = { atbgp_has_income_deposit = yes }
			atbgp_clear_foreign_income = yes
		}
	}
}

# 2.8：有专属立绘的元首永不下台（on_ruler_set，国家作用域）。
# 远星同盟 2.8 起是巨型企业：auth_corporate 每 20 年一次寡头选举，而原版
# re_election_allowed 默认 no，现任元首连候选都进不去，必然被换掉。政体的
# advanced_authority_swap 虽然能写 election_type = none，但 auth_corporate 已经有
# 10 个 swap（灵能飞升会触发 is_transcendent_authority 那一个），同时只有一个生效，
# 所以不走政体，改成换下来就立刻重新任命——对任何原因的换人都有效。
# set_leader 会再触发一次 on_ruler_set，那时 trigger 不成立，不会递归。
country_event = {
	id = atbgp.14
	hide_window = yes
	is_triggered_only = yes

	trigger = {
		has_country_flag = atbgp_great_power
		any_owned_leader = {
			has_leader_flag = atbgp_named_ruler
			is_ruler = no
		}
	}

	immediate = {
		random_owned_leader = {
			limit = {
				has_leader_flag = atbgp_named_ruler
				is_ruler = no
			}
			save_event_target_as = atbgp_ruler_restore
		}
		set_leader = event_target:atbgp_ruler_restore
	}
}
""")
out["events/atbgp_events.txt"] = "".join(events)

# ---------------------------------------------------------------- 脚本效果 / 触发器
clear_parts = []
has_parts = []
for e in EMPIRES:
    if not has_income(e):
        continue
    n = e["n"]
    keys = [f"atbgp_d_income_{n}"] + ([f"atbgp_d_income_crisis_{n}"] if has_crisis_income(e) else [])
    has_parts.append("\n".join(f"\t\thas_deposit = {k}" for k in keys))
    cond = "\n".join(f"\t\t\t\thas_deposit = {k}" for k in keys)
    removes = "\n".join(f"\t\tremove_deposit = {k}" for k in keys)
    clear_parts.append(f"""	if = {{
		limit = {{
			OR = {{
{cond}
			}}
			NAND = {{
				exists = owner
				owner = {{ has_country_flag = atbgp_power_{n} }}
				is_capital = yes
			}}
		}}
{removes}
	}}""")

out["common/scripted_triggers/atbgp_triggers.txt"] = f"""# 由 _tools/gen_great_powers.py 生成，请勿手改

# 堕落帝国已觉醒，或终末危机已经发生
atbgp_crisis_active = {{
	OR = {{
		has_global_flag = galactic_crisis_happened
		any_country = {{ is_country_type = awakened_fallen_empire }}
	}}
}}

# 星球带有任一列强的补给特征
atbgp_has_income_deposit = {{
	OR = {{
{chr(10).join(has_parts)}
	}}
}}

# 可以接入列强星团的银河星系（天选民的星团在原版就是与银河隔绝的，也不连）
atbgp_link_candidate = {{
	NOT = {{ has_star_flag = atbgp_cluster }}
	NOT = {{ has_star_flag = chosen_system }}
}}
"""

link_tiers = []
for i, r in enumerate(LINK_RADII):
    kw = "if" if i == 0 else "else_if"
    cond = f"""atbgp_link_candidate = yes
				NOT = {{ has_hyperlane_to = event_target:$SYSTEM$ }}
				distance = {{
					source = event_target:$SYSTEM$
					max_distance <= {r}
					type = euclidean
				}}"""
    link_tiers.append(f"""	{kw} = {{
		limit = {{
			any_system = {{
				{cond}
			}}
		}}
		random_system = {{
			limit = {{
				{cond}
			}}
			add_hyperlane = {{ from = this to = event_target:$SYSTEM$ }}
		}}
	}}""")

# 每位专属元首一个安装效果：立绘、特质都写死在里面，所以不用参数
named_ruler_effects = []
for e in EMPIRES:
    r = e["ruler"]
    if not r:
        continue
    traits = "\n".join(
        f"""				add_trait = {{
					trait = {t}
					show_message = no
				}}""" for t in r["traits"])
    named_ruler_effects.append(f"""# 国家作用域：用专属立绘的元首替换 {e['name']} 的开局元首（10 级）
# 元首是单独的物种，原版改造/飞升换肖像不会作用到她身上
atbgp_install_ruler_{r['id']} = {{
	if = {{
		limit = {{ exists = ruler }}
		ruler = {{ set_leader_flag = atbgp_replaced_ruler }}
	}}
	create_species = {{
		name = atbgp_ruler_species_{r['id']}
		plural = atbgp_ruler_species_{r['id']}
		adjective = atbgp_ruler_species_{r['id']}
		class = {r['cls']}
		portrait = atbgp_{r['id']}
		traits = random
		allow_negative_traits = no
		effect = {{ save_event_target_as = atbgp_ruler_species_tmp }}
	}}
	create_leader = {{
		class = official
		species = event_target:atbgp_ruler_species_tmp
		name = atbgp_leader_{r['id']}
		gender = female
		skill = 10
		immortal = yes
		hide_age = yes
		randomize_traits = no
		skip_background_generation = yes
		effect = {{
			set_leader_flag = atbgp_named_ruler
			set_leader_flag = leader_death_events_blocked
			set_immortal = yes
			# 开局后统治者不能获得非议会特质，先给 1 天豁免标记再加
			set_timed_leader_flag = {{
				flag = ignore_autocracy_ruler_trait_restriction
				days = 1
			}}
{traits}
			change_leader_portrait = atbgp_{r['id']}
			save_event_target_as = atbgp_new_ruler
		}}
	}}
	set_leader = event_target:atbgp_new_ruler
	atbgp_remove_replaced_ruler = yes
}}
""")
named_ruler_effects = "\n".join(named_ruler_effects)

# 每个随机名字元首的列强一个安装效果：开局特质写死在里面
random_ruler_effects = []
for e in EMPIRES:
    if e["ruler"]:
        continue
    traits = e.get("ruler_traits", [])
    trait_block = ""
    if traits:
        trait_block = "\n\t\t\t# 开局后统治者不能获得非议会特质，先给 1 天豁免标记再加\n" \
                      "\t\t\tset_timed_leader_flag = {\n\t\t\t\tflag = ignore_autocracy_ruler_trait_restriction\n\t\t\t\tdays = 1\n\t\t\t}\n" + \
                      "\n".join(f"""			add_trait = {{
				trait = {t}
				show_message = no
			}}""" for t in traits)
    random_ruler_effects.append(f"""# 国家作用域：随机名字的 10 级元首（{e['name']}）
atbgp_install_random_ruler_{e['n']} = {{
	if = {{
		limit = {{ exists = ruler }}
		ruler = {{ set_leader_flag = atbgp_replaced_ruler }}
	}}
	create_leader = {{
		class = official
		species = root.species
		name = random
		skill = 10
		effect = {{
			save_event_target_as = atbgp_new_ruler{trait_block}
		}}
	}}
	set_leader = event_target:atbgp_new_ruler
	atbgp_remove_replaced_ruler = yes
}}
""")
random_ruler_effects = "\n".join(random_ruler_effects)

out["common/scripted_effects/atbgp_effects.txt"] = f"""# 由 _tools/gen_great_powers.py 生成，请勿手改

# 给星团母星接一条通往银河的航道：由近到远找还没连上的星系
atbgp_link_to_galaxy = {{
{chr(10).join(link_tiers)}
}}

# 国家作用域：普通开局的初始舰船。建造舰、带科学家的科研舰各 1 艘；
# 护卫舰 2.8 起 x10 = 30 艘一支舰队，带 10 级永生舰队司令。
atbgp_spawn_start_fleets = {{
	create_fleet = {{
		effect = {{
			set_owner = root
			create_ship = {{
				name = random
				random_existing_design = constructor
			}}
			set_location = root.capital_star
		}}
	}}
	create_fleet = {{
		effect = {{
			set_owner = root
			create_ship = {{
				name = random
				random_existing_design = science
			}}
			set_location = root.capital_star
			save_event_target_as = atbgp_science_ship
		}}
	}}
	create_leader = {{
		name = random
		species = root.species
		class = scientist
		skill = 1
	}}
	event_target:atbgp_science_ship = {{ assign_leader = last_created_leader }}
	create_fleet = {{
		effect = {{
			set_owner = root
			while = {{
				count = 30
				create_ship = {{
					name = random
					random_existing_design = corvette
				}}
			}}
			set_location = root.capital_star
			save_event_target_as = atbgp_start_warfleet
		}}
	}}
	# 2.7：开局舰队带一位 10 级永生舰队司令
	create_leader = {{
		name = random
		species = root.species
		class = commander
		skill = 10
		immortal = yes
		effect = {{
			set_leader_flag = atbgp_admiral
			set_leader_flag = leader_death_events_blocked
			set_immortal = yes
			save_event_target_as = atbgp_start_admiral
		}}
	}}
	event_target:atbgp_start_warfleet = {{ assign_leader = event_target:atbgp_start_admiral }}
}}

{named_ruler_effects}
{random_ruler_effects}
atbgp_remove_replaced_ruler = {{
	every_owned_leader = {{
		limit = {{
			has_leader_flag = atbgp_replaced_ruler
			is_ruler = no
		}}
		kill_leader = {{ show_notification = no }}
	}}
}}

# 国家作用域：补给特征始终在首都上；危机后再加一份战时补给
atbgp_maintain_income = {{
	if = {{
		limit = {{ capital_scope = {{ NOT = {{ has_deposit = atbgp_d_income_$N$ }} }} }}
		every_galaxy_planet = {{
			limit = {{ has_deposit = atbgp_d_income_$N$ }}
			remove_deposit = atbgp_d_income_$N$
		}}
		capital_scope = {{ add_deposit = atbgp_d_income_$N$ }}
	}}
	if = {{
		limit = {{
			has_country_flag = atbgp_crisis_mode
			capital_scope = {{ NOT = {{ has_deposit = atbgp_d_income_crisis_$N$ }} }}
		}}
		every_galaxy_planet = {{
			limit = {{ has_deposit = atbgp_d_income_crisis_$N$ }}
			remove_deposit = atbgp_d_income_crisis_$N$
		}}
		capital_scope = {{ add_deposit = atbgp_d_income_crisis_$N$ }}
	}}
}}

# 国家作用域：没有战时补给的列强，只维护一份补给特征
atbgp_maintain_income_basic = {{
	if = {{
		limit = {{ capital_scope = {{ NOT = {{ has_deposit = atbgp_d_income_$N$ }} }} }}
		every_galaxy_planet = {{
			limit = {{ has_deposit = atbgp_d_income_$N$ }}
			remove_deposit = atbgp_d_income_$N$
		}}
		capital_scope = {{ add_deposit = atbgp_d_income_$N$ }}
	}}
}}

# 星球作用域：补给特征不在对应列强的首都上就移除
atbgp_clear_foreign_income = {{
{chr(10).join(clear_parts)}
}}

# 国家作用域：拥有 3 个飞升（原版危机飞升的最低要求）后立刻补上固定的危机飞升。
# 原版的危机飞升都要求先有 3 个飞升，所以 AI 来不及先选别的危机路线（星海天罚与宇宙创生互斥）。
atbgp_force_crisis_perk = {{
	if = {{
		limit = {{
			num_ascension_perks >= 3
			NOT = {{ has_ascension_perk = $PERK$ }}
			is_player_crisis = no
		}}
		add_ascension_perk = $PERK$
	}}
}}

# 国家作用域：拥有固定的危机飞升后获得舰队加成
atbgp_crisis_perk_bonus = {{
	if = {{
		limit = {{
			has_ascension_perk = $PERK$
			NOT = {{ has_modifier = atbgp_btc_bonus }}
		}}
		add_modifier = {{
			modifier = atbgp_btc_bonus
			days = -1
		}}
	}}
}}

# 国家作用域：开局固定走基因飞升，并先拿到纯净路线的第一级解锁
# 基因重塑的 on_enabled 会照原版开启基因飞升局势；局势结束时（bio.20）只有拿到解锁的传统才能选
atbgp_start_purity_ascension = {{
	add_ascension_perk = ap_engineered_evolution
	give_purity_unlocks_effect = yes
}}

# 国家作用域（每月）：只留纯净一条路——清掉克隆、变异两条路线的解锁，
# 这样基因飞升局势结束时只能选纯净传统
atbgp_purity_lock = {{
	remove_country_flag = cloning_unlock_level_1
	remove_country_flag = cloning_unlock_level_2
	remove_country_flag = cloning_unlock_level_3
	remove_country_flag = mutation_unlock_level_1
	remove_country_flag = mutation_unlock_level_2
	remove_country_flag = mutation_unlock_level_3
	if = {{
		limit = {{ has_modifier = cloning_unlock_level_1 }}
		remove_modifier = cloning_unlock_level_1
	}}
	if = {{
		limit = {{ has_modifier = cloning_unlock_level_2 }}
		remove_modifier = cloning_unlock_level_2
	}}
	if = {{
		limit = {{ has_modifier = mutation_unlock_level_1 }}
		remove_modifier = mutation_unlock_level_1
	}}
	if = {{
		limit = {{ has_modifier = mutation_unlock_level_2 }}
		remove_modifier = mutation_unlock_level_2
	}}
	if = {{
		limit = {{
			has_ascension_perk = ap_engineered_evolution
			NOT = {{ has_country_flag = purity_unlock_level_1 }}
		}}
		give_purity_unlocks_effect = yes
	}}
}}

# 国家作用域（每月）：人工智能政策出现后固定为公民权
atbgp_force_ai_full_rights = {{
	if = {{
		limit = {{
			can_set_ai_policy = yes
			NOT = {{ has_policy_flag = ai_full_rights }}
		}}
		set_policy = {{
			policy = artificial_intelligence_policy
			option = ai_full_rights
			cooldown = no
		}}
	}}
}}

# 国家作用域（每月）：星海共同体成立后加入。
# 原版禁止灭绝政体加入（game_rules 的 can_be_part_of_galactic_community），本 MOD 在 atb_rules.txt
# 里对带 atbgp_gc_member 标记的国家开了例外。被宣布为危机后（星海天罚第 5 级）照原版不再加入。
atbgp_join_galactic_community = {{
	if = {{
		limit = {{
			is_galactic_community_formed = yes
			is_galactic_community_member = no
			has_been_declared_crisis = no
			NOT = {{ has_country_flag = malevolent_aura_empire }}
		}}
		add_to_galactic_community_no_message = yes
	}}
}}

# 国家作用域：与皇女的远征军认同族
# 排外的列强靠这份巨额好感和信任把远征军排除在敌意之外（双方各挂一份）。
atbgp_kin_with_expedition = {{
	every_country = {{
		limit = {{ has_country_flag = atb_princess_expedition }}
		save_event_target_as = atbgp_kin_country
	}}
	if = {{
		limit = {{ exists = event_target:atbgp_kin_country }}
		add_opinion_modifier = {{
			who = event_target:atbgp_kin_country
			modifier = atbgp_same_homeworld
		}}
		add_trust = {{
			who = event_target:atbgp_kin_country
			amount = 100
		}}
		event_target:atbgp_kin_country = {{
			add_opinion_modifier = {{
				who = root
				modifier = atbgp_same_homeworld
			}}
			add_trust = {{
				who = root
				amount = 100
			}}
		}}
	}}
}}
"""

out["common/opinion_modifiers/atbgp_opinion_modifiers.txt"] = """# 由 _tools/gen_great_powers.py 生成，请勿手改

# 与皇女的远征军来自同一母星
atbgp_same_homeworld = {
	opinion = {
		base = 400
	}
}
"""
loc("atbgp_same_homeworld", "同一片母星的故人", "Kin From the Same Homeworld")

# ---------------------------------------------------------------- 特征（资源点）
dep = ["# 由 _tools/gen_great_powers.py 生成，请勿手改\n"]


RESEARCH = ("physics_research", "society_research", "engineering_research")


def produces(e, crisis):
    """补给特征的产出。基础补给 + 科研；平时的那份再加上 extra_income（战时补给只翻倍基础部分）。"""
    out = {}
    if e.get("base_income", True):
        out.update(INCOME_BASE)
        r = e["research"] + (CRISIS_RESEARCH_EXTRA if crisis else 0)
        out.update({k: r for k in RESEARCH})
    if not crisis:
        for k, v in e.get("extra_income", {}).items():
            for key in (RESEARCH if k == "research" else (k,)):
                out[key] = out.get(key, 0) + v
    return "\n".join(f"\t\t\t{k} = {v}" for k, v in out.items())


for e in EMPIRES:
    if not has_income(e):
        continue
    n = e["n"]
    kinds = [(False, f"atbgp_d_income_{n}")] + ([(True, f"atbgp_d_income_crisis_{n}")] if has_crisis_income(e) else [])
    for crisis, key in kinds:
        dep.append(f"""
{key} = {{
	is_for_colonizable = yes
	category = deposit_cat_rare
	icon = d_station_reactor
	resources = {{
		category = planet_deposits
		produces = {{
{produces(e, crisis)}
		}}
	}}
	drop_weight = {{ weight = 0 }}
}}
""")
    cn_name, cn_desc, en_name, en_desc = e["income"]
    loc(f"atbgp_d_income_{n}", cn_name, en_name)
    loc(f"atbgp_d_income_{n}_desc", cn_desc, en_desc)
    if has_crisis_income(e):
        cn_name, cn_desc, en_name, en_desc = e["crisis"]
        loc(f"atbgp_d_income_crisis_{n}", cn_name, en_name)
        loc(f"atbgp_d_income_crisis_{n}_desc", cn_desc, en_desc)

orbital = set()
for e in EMPIRES:
    for s in e["systems"]:
        if s["kind"] == "blackhole":
            orbital.add(("dark_matter", s["dark_matter"], "sr_dark_matter", "unused/d_strategic_resources"))
        elif s["kind"] == "neutron":
            orbital.add(("unity", s["unity"], "unity", None))
        elif s["kind"] == "shattered":
            orbital.add(("nanites", s["nanites"], "nanites", "d_nanite_corpses"))
ORBITAL_LOC = {
    "dark_matter": ("暗物质富集带", "黑洞吸积盘中异常富集的暗物质，可由科研站直接收集。", "Dark Matter Concentration", "Unusually dense dark matter in the accretion disk."),
    "unity": ("中子星脉冲回响", "这颗中子星的脉冲带着某种近乎旋律的规律，聆听它让人心生敬畏。", "Pulsar Echo", "The pulses of this neutron star follow an almost melodic pattern."),
    "nanites": ("纳米机器残骸", "这颗粉碎星球的碎片里仍有大量可回收的纳米机器。", "Nanite Wreckage", "The fragments of this shattered world still hold salvageable nanites."),
}
for kind, value, res, icon in sorted(orbital):
    key = f"atbgp_d_{kind}_{value}"
    icon_line = f"\n\ticon = \"{icon}\"" if icon else ""
    dep.append(f"""
{key} = {{{icon_line}
	resources = {{
		category = orbital_research_deposits
		produces = {{
			{res} = {value}
		}}
	}}
	station = shipclass_research_station
	is_for_colonizable = no
	drop_weight = {{ weight = 0 }}
}}
""")
    cn_name, cn_desc, en_name, en_desc = ORBITAL_LOC[kind]
    loc(key, cn_name, en_name)
    loc(f"{key}_desc", cn_desc, en_desc)

# 星团死寂星球上的宜居度下限特征（星球修正，对住在上面的所有物种生效）
for e in EMPIRES:
    f = e.get("tomb_floor")
    if not f:
        continue
    dep.append(f"""
{f['key']} = {{
	is_for_colonizable = yes
	category = deposit_cat_rare
	icon = d_bunker_door
	planet_modifier = {{
		habitability_floor_add = {f['value']}
	}}
	drop_weight = {{ weight = 0 }}
}}
""")
    loc(f["key"], f["cn"], f["en"])
    loc(f"{f['key']}_desc", f["cn_desc"], f["en_desc"])

# 母星上额外的固定特征
for e in EMPIRES:
    for d in e.get("home_deposits", []):
        res = "\n".join(f"\t\t\t{k} = {v}" for k, v in d["produces"].items())
        dep.append(f"""
{d['key']} = {{
	is_for_colonizable = yes
	category = deposit_cat_rare
	icon = {d['icon']}
	resources = {{
		category = planet_deposits
		produces = {{
{res}
		}}
	}}
	drop_weight = {{ weight = 0 }}
}}
""")
        loc(d["key"], d["cn"], d["en"])
        loc(f"{d['key']}_desc", d["cn_desc"], d["en_desc"])
out["common/deposits/atbgp_deposits.txt"] = "".join(dep)

static_mods = ["""# 由 _tools/gen_great_powers.py 生成，请勿手改

# 大君主同盟领地拥有固定的危机飞升（2.5 起为宇宙创生）后
atbgp_btc_bonus = {
	country_naval_cap_add = 1000
	shipclass_military_build_speed_mult = 1.0
}

# 2.7：所有列强开局就有的国家修正。AI 造舰被海军容量卡住，光给资源只会囤在仓库里
atbgp_power_base = {
	country_naval_cap_add = 1000
	country_starbase_capacity_add = 10
}

# 2.7：开局母星 20 年内人口增长翻倍（有机人口的自然增长、额外增长与机械人口的组装各 +100%）
atbgp_growth_boost = {
	logistic_growth_mult = 1.0
	bonus_pop_growth_mult = 1.0
	planet_pop_assembly_mult = 1.0
}

# 2.7：标准区划集的开局母星：区划格 +30，农业、发电、采矿区划上限各 +10（开局各放 10 个）
atbgp_homeworld_districts = {
	planet_max_districts_add = 30
	district_farming_max_add = 10
	district_generator_max_add = 10
	district_mining_max_add = 10
}
"""]
for e in EMPIRES:
    b = e.get("bonus")
    if not b:
        continue
    mods = "\n".join(f"\t{k} = {v}" for k, v in b["mods"].items())
    static_mods.append(f"""
# {e['name']}：固定的额外国家修正
atbgp_bonus_{e['n']} = {{
{mods}
}}
""")
    loc(f"atbgp_bonus_{e['n']}", b["cn"], b["en"])
    loc(f"atbgp_bonus_{e['n']}_desc", b["cn_desc"], b["en_desc"])
out["common/static_modifiers/atbgp_static_modifiers.txt"] = "".join(static_mods)
loc("atbgp_btc_bonus", "宗主舰队编制", "Suzerain Fleet Charter")
loc("atbgp_btc_bonus_desc", "宗主终于允许这块乡村领地扩编舰队。对银河其他文明来说，这意味着灾难。",
    "The suzerain has finally allowed this rural fief to expand its fleet.")
loc("atbgp_power_base", "列强的底蕴", "Great Power's Foundation")
loc("atbgp_power_base_desc", "这个文明背后站着远比银河诸国强大的力量，它的舰队与要塞规模不受寻常国力的限制。",
    "Something far mightier than the galaxy's nations stands behind this civilization; its fleets and fortresses are not bound by ordinary limits.")
loc("atbgp_homeworld_districts", "母星的开拓区", "Homeworld Development Zones")
loc("atbgp_homeworld_districts_desc", "列强在母星上早已规划好大片农田、电站与矿区，足以养活远超寻常的人口。",
    "The great power long ago laid out vast farmlands, power plants and mines on its homeworld, enough to support an unusually large population.")
loc("atbgp_growth_boost", "开拓者的繁荣", "Pioneers' Boom")
loc("atbgp_growth_boost_desc", "初到这片星域的头二十年，母星的人口以惊人的速度增长。",
    "For the first twenty years in this corner of space, the homeworld's population grows at an astonishing rate.")

out["common/on_actions/atbgp_on_actions.txt"] = """# 由 _tools/gen_great_powers.py 生成，请勿手改
on_game_start = {
	events = {
		atbgp.1
	}
}

on_monthly_pulse = {
	events = {
		atbgp.10
	}
}

on_yearly_pulse = {
	events = {
		atbgp.13
	}
}

on_ascension_perk_picked = {
	events = {
		atbgp.12
	}
}

on_ruler_set = {
	events = {
		atbgp.14
	}
}
"""

out["gfx/portraits/portraits/atbgp_portraits.txt"] = """# 由 _tools/gen_great_powers.py 生成，请勿手改
# 两位元首的静态肖像；_full 为整张立绘
portraits = {
	atbgp_rongxin = { texturefile = "gfx/models/portraits/atbgp/rongxin.dds" }
	atbgp_taiaria = { texturefile = "gfx/models/portraits/atbgp/taiaria.dds" }
	atbgp_rongxin_full = { texturefile = "gfx/models/portraits/atbgp/rongxin_full.dds" }
	atbgp_taiaria_full = { texturefile = "gfx/models/portraits/atbgp/taiaria_full.dds" }
}
"""

# ---------------------------------------------------------------- 名称本地化
for e in EMPIRES:
    n = e["n"]
    loc(f"atbgp_country_{n}", e["name"], e["en"])
    loc(f"atbgp_country_{n}_adj", e["adj"], e["en_adj"])
    sp, spl, sadj = e["species"]
    esp, espl, esadj = e["species_en"]
    loc(f"atbgp_species_{n}", sp, esp)
    loc(f"atbgp_species_{n}_plural", spl, espl)
    loc(f"atbgp_species_{n}_adj", sadj, esadj)
    loc(f"atbgp_sys_{n}_0", e["home"]["sys"], e["home"]["en"])
    if e.get("capitals"):
        for i, (cn, en) in enumerate(e["capitals"], start=1):
            loc(f"atbgp_planet_{n}_home_{i}", cn, en)
    else:
        loc(f"atbgp_planet_{n}_home", e["home"]["sys"], e["home"]["en"])
    for k, s in enumerate(e["systems"], start=1):
        loc(f"atbgp_sys_{n}_{k}", s["sys"], s["en"])
        if s["kind"] in ("planet", "shattered"):
            loc(f"atbgp_planet_{n}_{k}", s["sys"], s["en"])
    if e["ruler"]:
        r = e["ruler"]
        loc(f"atbgp_leader_{r['id']}", r["name"], r["en"])
        loc(f"atbgp_ruler_species_{r['id']}", r["species"][0], r["species"][1])

out["localisation/simp_chinese/atbgp_l_simp_chinese.yml"] = "﻿l_simp_chinese:\n" + "\n".join(loc_cn) + "\n"
out["localisation/english/atbgp_l_english.yml"] = "﻿l_english:\n" + "\n".join(loc_en) + "\n"

for rel, text in out.items():
    p = MOD / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8", newline="\n")
print("generated", len(out), "files;", ", ".join(f"{e['name']}={angle(e['clock'])}°" for e in EMPIRES))
