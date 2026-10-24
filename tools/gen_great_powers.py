"""生成「皇女的远征军EX」中保底列强部分（atbgp_ 前缀）的全部脚本和本地化。

用法：python gen_great_powers.py <MOD 根目录>
元首肖像由 make_portraits.py 转换。
改方位、距离、收入、星系配置都改这里，然后重新运行；不要手改生成出来的 .txt/.yml。
"""
import sys
from pathlib import Path

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
               "volatile_motes": 22, "exotic_gases": 22, "rare_crystals": 22}
CRISIS_RESEARCH_EXTRA = 550

# ---------------------------------------------------------------- 三个列强
# 星系 kind：planet（一颗指定星球）、tomb3（三颗死寂星球）、blackhole、neutron、shattered、ring
EMPIRES = [
    dict(
        n=1, clock=11, research=45, pops=52,
        name="燃烧白鹿军团", adj="白鹿", en="Burning White Stag Legion", en_adj="White Stag",
        species=("白鹿机兵", "白鹿机兵", "白鹿"), species_en=("Stag Unit", "Stag Units", "Stag"),
        species_class="MACHINE", species_traits="random",
        authority="auth_machine_intelligence",
        ethics=["ethic_gestalt_consciousness"],
        civics=["civic_machine_replication", "civic_machine_ota_updates"],
        ruler=dict(id="rongxin", name="融心演算", en="Fused-Heart Calculus", cls="MACHINE",
                   species=("演算核心", "Calculus Core")),
        home=dict(sys="俳句", en="Haiku", star="sc_g", pc="pc_gaia", size=22),
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
        authority="auth_corporate",
        ethics=["ethic_egalitarian", "ethic_materialist", "ethic_militarist"],
        civics=["civic_worker_coop", "civic_corporate_dark_consortium"],
        ruler=dict(id="taiaria", name="泰阿瑞亚-星之心", en="Taiaria Starheart", cls="HUM",
                   species=("星之心", "Starheart")),
        home=dict(sys="救赎", en="Redemption", star="sc_f", pc="pc_relic", size=22),
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
        n=3, clock=9, research=56, pops=48,
        name="大君主同盟领地", adj="大君主", en="Grand Suzerain Allied Fief", en_adj="Suzerain",
        species=("君主裔", "君主裔", "君主裔"), species_en=("Suzerainite", "Suzerainites", "Suzerainite"),
        species_class="NECROID", species_traits="random",
        authority="auth_imperial",
        ethics=["ethic_fanatic_authoritarian", "ethic_xenophobe"],
        civics=["civic_philosopher_king", "civic_feudal_realm"],
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
]


def angle(clock: int) -> int:
    return (ANGLE_AT_12 + ANGLE_STEP * clock) % 360


def window(a: int, half: int) -> tuple[int, int]:
    return (a - half) % 360, (a + half) % 360


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


def home_initializer(e):
    n, h = e["n"], e["home"]
    country = f"event_target:atbgp_country_{n}"
    civics = " ".join(f"civic = {c}" for c in e["civics"])
    ethics = " ".join(f"ethic = {x}" for x in e["ethics"])
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
		}}
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
			create_species = {{
				name = atbgp_species_{n}
				plural = atbgp_species_{n}_plural
				adjective = atbgp_species_{n}_adj
				class = {e['species_class']}
				portrait = random
				traits = {e['species_traits']}
				homeworld = this
				effect = {{ save_global_event_target_as = atbgp_species_{n} }}
			}}
			create_country = {{
				name = "atbgp_country_{n}"
				adjective = "atbgp_country_{n}_adj"
				authority = {e['authority']}
				civics = {{ {civics} }}
				ethos = {{ {ethics} }}
				species = event_target:atbgp_species_{n}
				origin = "origin_default"
				flag = random
				ignore_initial_colony_error = yes
				effect = {{
					save_global_event_target_as = atbgp_country_{n}
					set_country_flag = atbgp_great_power
					set_country_flag = atbgp_power_{n}
					advanced_empire_base_init_effect = yes
				}}
			}}
			set_owner = {country}
			set_controller = {country}
			set_capital = yes
			while = {{
				count = {e['pops']}
				create_pop_group = {{ species = event_target:atbgp_species_{n} }}
			}}
			colony = {{ generate_start_buildings_and_districts = yes }}
			add_deposit = atbgp_d_income_{n}
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
        body = star_block() + "\n\tchange_orbit = 35\n" + "".join(f"""
	planet = {{
		class = "pc_nuked"
		orbit_distance = {0 if i == 0 else 22}
		orbit_angle = {{ min = 60 max = 300 }}
		size = {{ min = 14 max = 18 }}
		has_ring = no
		deposit_blockers = none
		modifiers = none
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
    lines = [f"\t\t# {e['name']}：{e['clock']} 点方位（角度 {a}）"]
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
    lines.append(f"\t\t# {e['name']}：母星接入银河")
    for _ in range(LINK_COUNT):
        lines.append(f"\t\tatbgp_link_to_galaxy = {{ SYSTEM = atbgp_sys_{n}_0 }}")
    return "\n".join(lines)


events = [f"""# 由 _tools/gen_great_powers.py 生成，请勿手改
namespace = atbgp

# 开局：在银河边缘外现造三个列强的星团（on_game_start）
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
events.append("""	}
}

# 开局次日：初始舰船、替换元首
country_event = {
	id = atbgp.2
	hide_window = yes
	is_triggered_only = yes

	immediate = {
		atbgp_spawn_start_fleets = yes
		if = {
			limit = { has_country_flag = atbgp_power_1 }
			atbgp_install_named_ruler = { ID = rongxin CLASS = MACHINE }
		}
		else_if = {
			limit = { has_country_flag = atbgp_power_2 }
			atbgp_install_named_ruler = { ID = taiaria CLASS = HUM }
		}
		else_if = {
			limit = { has_country_flag = atbgp_power_3 }
			atbgp_install_random_ruler = yes
		}
	}
}

# 每月：危机检测、补给特征跟随首都、星海天罚
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
		if = {
			limit = { has_country_flag = atbgp_power_1 }
			atbgp_maintain_income = { N = 1 }
		}
		else_if = {
			limit = { has_country_flag = atbgp_power_2 }
			atbgp_maintain_income = { N = 2 }
		}
		else_if = {
			limit = { has_country_flag = atbgp_power_3 }
			atbgp_maintain_income = { N = 3 }
			atbgp_check_become_the_crisis = yes
		}
	}
}

# 选飞升时：大君主同盟领地的第 12 个飞升必定是星海天罚（on_ascension_perk_picked）
country_event = {
	id = atbgp.12
	hide_window = yes
	is_triggered_only = yes

	trigger = {
		has_country_flag = atbgp_power_3
	}

	immediate = {
		atbgp_check_become_the_crisis = yes
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
""")
out["events/atbgp_events.txt"] = "".join(events)

# ---------------------------------------------------------------- 脚本效果 / 触发器
clear_parts = []
has_parts = []
for e in EMPIRES:
    n = e["n"]
    has_parts.append(f"\t\thas_deposit = atbgp_d_income_{n}\n\t\thas_deposit = atbgp_d_income_crisis_{n}")
    clear_parts.append(f"""	if = {{
		limit = {{
			OR = {{
				has_deposit = atbgp_d_income_{n}
				has_deposit = atbgp_d_income_crisis_{n}
			}}
			NAND = {{
				exists = owner
				owner = {{ has_country_flag = atbgp_power_{n} }}
				is_capital = yes
			}}
		}}
		remove_deposit = atbgp_d_income_{n}
		remove_deposit = atbgp_d_income_crisis_{n}
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

# 可以接入列强星团的银河星系
atbgp_link_candidate = {{
	NOT = {{ has_star_flag = atbgp_cluster }}
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

out["common/scripted_effects/atbgp_effects.txt"] = f"""# 由 _tools/gen_great_powers.py 生成，请勿手改

# 给星团母星接一条通往银河的航道：由近到远找还没连上的星系
atbgp_link_to_galaxy = {{
{chr(10).join(link_tiers)}
}}

# 国家作用域：普通开局的初始舰船（建造舰、科研舰带科学家、3 艘护卫舰）
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
				count = 3
				create_ship = {{
					name = random
					random_existing_design = corvette
				}}
			}}
			set_location = root.capital_star
		}}
	}}
}}

# 国家作用域：用专属立绘的元首替换开局元首（时间永驻，10 级）
# 元首是单独的物种，原版改造/飞升换肖像不会作用到她身上
atbgp_install_named_ruler = {{
	if = {{
		limit = {{ exists = ruler }}
		ruler = {{ set_leader_flag = atbgp_replaced_ruler }}
	}}
	create_species = {{
		name = atbgp_ruler_species_$ID$
		plural = atbgp_ruler_species_$ID$
		adjective = atbgp_ruler_species_$ID$
		class = $CLASS$
		portrait = atbgp_$ID$
		traits = random
		allow_negative_traits = no
		effect = {{ save_event_target_as = atbgp_ruler_species_tmp }}
	}}
	create_leader = {{
		class = official
		species = event_target:atbgp_ruler_species_tmp
		name = atbgp_leader_$ID$
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
			add_trait = {{
				trait = leader_trait_intemporal
				show_message = no
			}}
			change_leader_portrait = atbgp_$ID$
			save_event_target_as = atbgp_new_ruler
		}}
	}}
	set_leader = event_target:atbgp_new_ruler
	atbgp_remove_replaced_ruler = yes
}}

# 国家作用域：随机名字的 10 级元首（大君主同盟领地）
atbgp_install_random_ruler = {{
	if = {{
		limit = {{ exists = ruler }}
		ruler = {{ set_leader_flag = atbgp_replaced_ruler }}
	}}
	create_leader = {{
		class = official
		species = root.species
		name = random
		skill = 10
		effect = {{ save_event_target_as = atbgp_new_ruler }}
	}}
	set_leader = event_target:atbgp_new_ruler
	atbgp_remove_replaced_ruler = yes
}}

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

# 星球作用域：补给特征不在对应列强的首都上就移除
atbgp_clear_foreign_income = {{
{chr(10).join(clear_parts)}
}}

# 国家作用域：已选 11 个飞升时直接补上星海天罚；拥有星海天罚就加舰队加成
atbgp_check_become_the_crisis = {{
	if = {{
		limit = {{
			num_ascension_perks >= 11
			NOT = {{ has_ascension_perk = ap_become_the_crisis }}
		}}
		add_ascension_perk = ap_become_the_crisis
	}}
	if = {{
		limit = {{
			has_ascension_perk = ap_become_the_crisis
			NOT = {{ has_modifier = atbgp_btc_bonus }}
		}}
		add_modifier = {{
			modifier = atbgp_btc_bonus
			days = -1
		}}
	}}
}}
"""

# ---------------------------------------------------------------- 特征（资源点）
dep = ["# 由 _tools/gen_great_powers.py 生成，请勿手改\n"]


def produces(e, crisis):
    lines = [f"\t\t\t{k} = {v}" for k, v in INCOME_BASE.items()]
    r = e["research"] + (CRISIS_RESEARCH_EXTRA if crisis else 0)
    lines += [f"\t\t\t{k} = {r}" for k in ("physics_research", "society_research", "engineering_research")]
    return "\n".join(lines)


for e in EMPIRES:
    n = e["n"]
    for crisis, key in ((False, f"atbgp_d_income_{n}"), (True, f"atbgp_d_income_crisis_{n}")):
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
out["common/deposits/atbgp_deposits.txt"] = "".join(dep)

out["common/static_modifiers/atbgp_static_modifiers.txt"] = """# 由 _tools/gen_great_powers.py 生成，请勿手改

# 大君主同盟领地选择星海天罚后
atbgp_btc_bonus = {
	country_naval_cap_add = 1000
	shipclass_military_build_speed_mult = 1.0
}
"""
loc("atbgp_btc_bonus", "天罚舰队编制", "Retribution Fleet Charter")
loc("atbgp_btc_bonus_desc", "宗主终于允许这块乡村领地扩编舰队。对银河其他文明来说，这意味着灾难。",
    "The suzerain has finally allowed this rural fief to expand its fleet.")

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
