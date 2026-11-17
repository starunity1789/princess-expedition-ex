"""3.5：把 Guilli's Planet Modifiers（GPM）的遗珍整合进本 MOD，GPM 其余内容一概不要。

用法（在仓库根目录，GPM 需要还在订阅目录里）：
    python tools/gen_gpm_relics.py

起因：单独启用 GPM 的几局 AI 几乎不打仗（系列 7、21、23、28、29），没开或只并入遗珍的几局都正常；
代码里没找到 GPM 直接压制宣战的地方，用户决定只留遗珍、退订 GPM。
GPM 的遗珍战争目标与宣战理由（每个遗珍一个）**不搬**——它们是嫌疑最大的部分。

搬进来的（遗珍 ID、修正名、特质名都不改，这样旧存档里已经拿到的 GPM 遗珍在退订后照样有效）：
- common/relics/        GPM 的两份遗珍定义原样照搬（29 个）
- common/static_modifiers/  遗珍用到的修正：gpm_static_modifiers_relics.txt 全部 + 机械世界核心的方舟加成
- common/armies/        外星卵、古老无畏舰召唤的两种陆军（只用原版图标，不牵扯模型）
- common/traits/        共享之魂、隐形战术家、陨落者纹章三个领袖特质
- common/opinion_modifiers/  opinion_intellectual_promise（一个前驱者遗珍使用）
- events/ 与 on_actions：隐形装置、陨落者旗帜给海军将领发特质的四个事件（gpm_relics.1/2/20/21）；
  原版 leader_class = admiral 已改名 commander，这里顺手改掉
- common/decisions/     三个遗珍决议**改写**：原版依赖 GPM 的行星分类触发器、矿藏、行星修正和环境物体，
  全部换成原版触发器与本 MOD 自己的两个行星修正（护盾阵列、浮岛住房），效果按 GPM 的矿藏/修正数值折算
- interface/ 与 gfx/：上面用到的图标（遗珍、特质、决议、行星修正）
- localisation/：从 GPM 各语言的本地化里只抽上面用到的键（含 $引用$ 的键）

生成后不再依赖 GPM；GPM 更新后想同步就再跑一次。
"""
import re
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parent.parent
MOD = ROOT / "mod"
GPM = Path(r"C:\Program Files (x86)\Steam\steamapps\workshop\content\281990\865040033")
GAME = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Stellaris")
if not (GPM / "common" / "relics").exists():
    raise SystemExit(f"找不到 GPM：{GPM}")

HEAD = "# 由 tools/gen_gpm_relics.py 从 Guilli's Planet Modifiers 抽取生成，请勿手改\n"


def read(rel: str) -> str:
    return (GPM / rel).read_text(encoding="utf-8-sig", errors="replace")


def block(text: str, key: str) -> str:
    """取顶层（行首）key = { ... } 整块"""
    m = re.search(rf"(?m)^{re.escape(key)}\s*=\s*\{{", text)
    if not m:
        raise SystemExit(f"GPM 里找不到 {key}")
    i, depth = m.end(), 1
    while depth:
        c = text[i]
        if c == "#":
            i = text.index("\n", i)
            continue
        depth += {"{": 1, "}": -1}.get(c, 0)
        i += 1
    return text[m.start():i]


def event_block(text: str, eid: str) -> str:
    m = re.search(rf"(?m)^\s*id\s*=\s*{re.escape(eid)}\s*$", text)
    start = text.rfind("\ncountry_event", 0, m.start()) + 1
    i, depth = text.index("{", start) + 1, 1
    while depth:
        depth += {"{": 1, "}": -1}.get(text[i], 0)
        i += 1
    return text[start:i]


written = []


def write(rel: str, text: str, bom: bool = False):
    p = MOD / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes((b"\xef\xbb\xbf" if bom else b"") + text.replace("\r\n", "\n").encode("utf-8"))
    written.append(rel)


# ---------------------------------------------------------------- 遗珍定义：原样照搬
relic_src = {"gpm_relics.txt": "atb_gpm_relics.txt", "gpm_relics_precursors.txt": "atb_gpm_relics_precursors.txt"}
relic_ids = []
for src, dst in relic_src.items():
    text = read(f"common/relics/{src}")
    relic_ids += re.findall(r"(?m)^(gpm_r_\w+)\s*=\s*\{", re.sub(r"#[^\n]*", "", text))
    write(f"common/relics/{dst}", HEAD + f"# 来源：GPM common/relics/{src}\n\n" + text)

# ---------------------------------------------------------------- 修正
mods = read("common/static_modifiers/gpm_static_modifiers_relics.txt")
ark = block(read("common/static_modifiers/gpm_static_modifiers_events.txt"), "gpm_machine_world_core_ark_bonus")
own_mods = """
# ---- 本 MOD 新增：改写后的遗珍决议用（原来是 GPM 的矿藏 + 行星修正，数值照搬）----
# 护盾阵列（神秘护盾发生器）：GPM 的 gpm_precursor_planetary_shield_on，另把矿藏的 +10 物理改成研究员产出 +5%
atb_gpm_planetary_shield_array = {
	planet_orbital_bombardment_damage = -0.50
	pop_happiness = 0.05
	planet_resettlement_unemployed_destination_mult = 0.40
	planet_researchers_produces_mult = 0.05
	icon = "gfx/interface/icons/planet_modifiers/gpm_planet_shield.dds"
	icon_frame = 11
}

# 浮岛住房（重力引擎）：GPM 矿藏 gpm_d_floating_islands_housing 的效果
atb_gpm_floating_islands_housing = {
	planet_max_districts_add = 4
	planet_housing_add = 4000
	icon = "gfx/interface/icons/planet_modifiers/gpm_floating_islands.dds"
	icon_frame = 11
}
"""
write("common/static_modifiers/atb_gpm_relic_modifiers.txt",
      HEAD + "# 来源：GPM gpm_static_modifiers_relics.txt（全部）、gpm_static_modifiers_events.txt（方舟加成）\n\n"
      + mods + "\n\n" + ark + "\n" + own_mods)

# ---------------------------------------------------------------- 陆军、特质、好感
armies = read("common/armies/gpm_armies.txt")
write("common/armies/atb_gpm_relic_armies.txt", HEAD + "# 外星卵、古老无畏舰两个遗珍召唤的陆军（只用原版图标）\n\n"
      + block(armies, "gpm_xenomorph_army_no_upkeep") + "\n\n" + block(armies, "gpm_venerable_dreadnaught_army") + "\n")

traits = read("common/traits/gpm_traits_leaders.txt")
trait_ids = ["leader_trait_gpm_shared_soul", "leader_trait_gpm_stealth_tactician", "leader_trait_gpm_fallen_heraldry"]
write("common/traits/atb_gpm_relic_traits.txt", HEAD + "# 灵魂宝石、隐形装置、陨落者旗帜三个遗珍给的领袖特质\n\n"
      + "\n\n".join(block(traits, t) for t in trait_ids) + "\n")

write("common/opinion_modifiers/atb_gpm_relic_opinions.txt", HEAD + "\n"
      + block(read("common/opinion_modifiers/gpm_opinions.txt"), "opinion_intellectual_promise") + "\n")

# ---------------------------------------------------------------- 事件与钩子
ev = read("events/gpm_relic_events.txt")
events = "\n\n".join(event_block(ev, e) for e in ("gpm_relics.1", "gpm_relics.2", "gpm_relics.20", "gpm_relics.21"))
events = events.replace("leader_class = admiral", "leader_class = commander")
write("events/atb_gpm_relic_events.txt", HEAD + """# 隐形装置（gpm_r_cloaking_device）→ 海军将领「隐形战术家」；陨落者旗帜 → 「陨落者纹章」
# gpm_relics.1 / .20 在拿到遗珍时触发（atb_grant_quest_relic），.2 / .21 在新领袖出现时补发
# 原版 leader_class = admiral 在 4.x 叫 commander，已改

namespace = gpm_relics

""" + events + "\n")
write("common/on_actions/atb_gpm_relic_on_actions.txt", HEAD + """
# 新领袖出现（scope: country, from: leader）
on_leader_spawned = {
	events = {
		gpm_relics.2	# 有隐形装置：新海军将领 25% 获得隐形战术家
		gpm_relics.21	# 有陨落者旗帜：新海军将领获得陨落者纹章
	}
}
""")

# ---------------------------------------------------------------- 遗珍决议（改写，去掉 GPM 依赖）
decisions = """
# 3 个遗珍决议，按 GPM 的 gpm_relic_decisions.txt 改写：
# GPM 的行星分类触发器换成原版行星类型；矿藏、行星修正、环境物体、GPM 修正清理全部去掉，
# 效果换成本 MOD 的两个行星修正（atb_gpm_relic_modifiers.txt）

# 机械世界核心激活后：把一颗不宜居星球改造成机械世界
decision_gpm_machine_world_core_relic = {
	important = yes
	owned_planets_only = no
	sound = event_administrative_work
	icon = gpm_decision_machine_world_core_relic

	potential = {
		from = {
			has_country_flag = relic_machine_world_core_activated
		}
		OR = {
			is_planet_class = pc_barren
			is_planet_class = pc_barren_cold
			is_planet_class = pc_molten
			is_planet_class = pc_toxic
			is_planet_class = pc_frozen
			is_planet_class = pc_gas_giant
			is_planet_class = pc_broken
		}
	}

	allow = {
		custom_tooltip = decision_gpm_machine_world_core_relic_tt
	}

	effect = {
		hidden_effect = { from = { remove_country_flag = relic_machine_world_core_activated } }
		custom_tooltip = decision_gpm_machine_world_core_relic_tt
		change_pc = pc_machine
		hidden_effect = {
			reset_planet = yes
			clear_deposits = yes
			remove_modifier = terraforming_candidate
		}
		change_planet_size = 5
	}

	ai_weight = {
		weight = 0
		modifier = {
			weight = 1000
			planet_size >= 20
		}
	}
}

# 神秘护盾发生器激活后（次数存在国家变量 gpm_shield_generator_decision_count）：给一颗殖民地加护盾阵列
decision_gpm_shield_generator_arrays = {
	important = yes
	owned_planets_only = yes
	sound = event_administrative_work
	icon = gpm_decision_gpm_shield_generator_arrays

	resources = {
		category = decisions
		cost = {
			alloys = 1000
			exotic_gases = 500
		}
	}

	potential = {
		from = {
			check_variable = {
				which = "gpm_shield_generator_decision_count"
				value > 0
			}
		}
		is_colony = yes
		NOT = { has_modifier = atb_gpm_planetary_shield_array }
	}

	allow = {
	}

	effect = {
		custom_tooltip = decision_gpm_shield_generator_arrays_tt
		hidden_effect = {
			owner = {
				change_variable = {
					which = "gpm_shield_generator_decision_count"
					value = -1
				}
			}
		}
		add_modifier = { modifier = atb_gpm_planetary_shield_array }
	}

	ai_weight = {
		weight = 500
		modifier = {
			factor = 10
			is_capital = yes
		}
	}
}

# 重力引擎激活后（次数存在国家变量 gpm_r_gravity_engine_decision_count）：给一颗殖民地建浮岛
decision_gpm_Floating_Island_Housing = {
	important = yes
	owned_planets_only = yes
	sound = event_administrative_work
	icon = gpm_decision_floating_islands

	potential = {
		exists = from
		from = {
			check_variable = {
				which = "gpm_r_gravity_engine_decision_count"
				value > 0
			}
		}
		is_colony = yes
		NOT = { has_modifier = atb_gpm_floating_islands_housing }
	}

	allow = {
	}

	effect = {
		add_modifier = { modifier = atb_gpm_floating_islands_housing }
		hidden_effect = {
			owner = {
				change_variable = {
					which = "gpm_r_gravity_engine_decision_count"
					value = -1
				}
			}
		}
	}

	ai_weight = {
		weight = 100
		modifier = {
			factor = 100
			is_capital = yes
		}
	}
}
"""
write("common/decisions/atb_gpm_relic_decisions.txt", HEAD + decisions)

# ---------------------------------------------------------------- 图标
gfx_text = "\n".join(p.read_text(encoding="utf-8-sig", errors="replace") for p in GPM.rglob("*.gfx"))
sprites = {}
for m in re.finditer(r"spriteType\s*=\s*\{", gfx_text, re.I):
    i, depth = m.end(), 1
    while depth:
        depth += {"{": 1, "}": -1}.get(gfx_text[i], 0)
        i += 1
    b = gfx_text[m.start():i]
    n = re.search(r'name\s*=\s*"([^"]+)"', b)
    if n:
        sprites[n.group(1)] = b

script_text = "\n".join((MOD / r).read_text(encoding="utf-8") for r in written)
used_sprites = sorted(s for s in set(re.findall(r"GFX_\w+", script_text)) if s in sprites)
gfx_out = "spriteTypes = {\n" + "\n".join("\t" + sprites[s].strip() for s in used_sprites) + "\n}\n"
write("interface/atb_gpm_relics.gfx", HEAD + gfx_out)

files = set(re.findall(r'(gfx/[\w/.-]+\.dds)', gfx_out + script_text))
for d in ("gpm_decision_machine_world_core_relic", "gpm_decision_gpm_shield_generator_arrays", "gpm_decision_floating_islands"):
    files.add(f"gfx/interface/icons/decisions/{d}.dds")
copied = 0
for f in sorted(files):
    src = GPM / f
    if not src.exists():
        if not (GAME / f).exists():
            print("  缺图标：", f)
        continue
    dst = MOD / f
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    copied += 1

# ---------------------------------------------------------------- 本地化
tokens = set(re.findall(r"[A-Za-z_][\w.]*", script_text))
prefixes = tuple(relic_ids + trait_ids + ["gpm_xenomorph_army_no_upkeep", "gpm_venerable_dreadnaught_army",
                                          "opinion_intellectual_promise", "decision_gpm_", "gpm_relic_",
                                          "gpm_machine_world_core_ark_bonus", "gpm_time_displacer_relic_bonus"])
mod_ids = set(re.findall(r"(?m)^(\w+)\s*=\s*\{", re.sub(r"#[^\n]*", "", mods + ark)))
LINE = re.compile(r'^\s*([\w.\-]+):\d*\s*"(.*)"\s*(#.*)?$')
# 本 MOD 新增的两个行星修正（改写后的遗珍决议用）；中文以外的语言用英文
OWN_LOC = {
    "simp_chinese": {
        "atb_gpm_planetary_shield_array": "先驱护盾阵列",
        "atb_gpm_planetary_shield_array_desc": "分布在这颗星球上的护盾阵列撑起了一层几乎无法击穿的屏障。",
        "atb_gpm_floating_islands_housing": "浮岛住房",
        "atb_gpm_floating_islands_housing_desc": "重力引擎托起的巨大浮岛，为这颗星球提供了大量新的建设空间与住房。",
    },
    "english": {
        "atb_gpm_planetary_shield_array": "Precursor Shield Arrays",
        "atb_gpm_planetary_shield_array_desc": "Shield arrays spread across this world project a near-impenetrable barrier.",
        "atb_gpm_floating_islands_housing": "Floating Island Housing",
        "atb_gpm_floating_islands_housing_desc": "Vast islands held aloft by the Gravity Engine give this world much more room to build and live.",
    },
}


def load_lang(langdir: Path):
    entries, header = {}, None
    for p in sorted(langdir.glob("*.yml")):
        for line in p.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            if header is None and re.match(r"^l_\w+:", line):
                header = line.split(":")[0]
            m = LINE.match(line)
            if m:
                entries.setdefault(m.group(1), m.group(2))
    return header or "l_" + langdir.name, entries


_, english = load_lang(GPM / "localisation" / "english")
langs = 0
for langdir in sorted((GPM / "localisation").iterdir()):
    if not langdir.is_dir() or langdir.name == "replace" or not (MOD / "localisation" / langdir.name).exists():
        continue
    header, entries = load_lang(langdir)
    for k, v in english.items():  # 这个语言缺的键用英文补
        entries.setdefault(k, v)
    for k, v in OWN_LOC.get(langdir.name, OWN_LOC["english"]).items():
        entries[k] = v
        tokens.add(k)

    def wanted(k: str) -> bool:
        base = k[4:] if k.startswith("mod_") else k
        return k in tokens or base in mod_ids or k.startswith(prefixes)

    keep = {k for k in entries if wanted(k)}
    todo = list(keep)
    while todo:  # $引用$ 的键也带上
        for ref in re.findall(r"\$([\w.\-]+)\$", entries[todo.pop()]):
            if ref in entries and ref not in keep:
                keep.add(ref)
                todo.append(ref)
    body = "\n".join(f' {k}:0 "{entries[k]}"' for k in sorted(keep))
    write(f"localisation/{langdir.name}/atb_gpm_relics_l_{langdir.name}.yml",
          f"{header}:\n # 由 tools/gen_gpm_relics.py 从 GPM 抽取生成，请勿手改\n{body}\n", bom=True)
    langs += 1

print(f"GPM 遗珍：{len(relic_ids)} 个；精灵 {len(used_sprites)} 个，图标文件 {copied} 个；本地化 {langs} 种语言")
for r in written:
    print("  写出", r)
