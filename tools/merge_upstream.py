"""把 Planetary Diversity / Guilli's Planet Modifiers and Features / Stellar AI 按保留清单合并进 mod/。

用法（在仓库根目录）：
    python tools/merge_upstream.py "C:/Program Files (x86)/Steam/steamapps/workshop/content/281990" mod

做的事：
  1. 按 KEEP 清单挑出三个上游 MOD 里要保留的文本文件（脚本、本地化、界面定义）
  2. 对其中一部分套 PATCHES（删块、掏空函数、剥离语句、裁剪 on_actions 事件表、替换条件）
  3. 按引用关系拷贝需要的贴图/模型/音频（二进制不进 git，路径写进 .gitignore 的生成段）
  4. 校验：保留下来的上游文件里，不允许出现只在被删上游文件里才有定义的符号（事件、巨构、
     环境物件、科技、陆军……）。有就报错退出，不写任何东西

设计取舍与每一处删改的理由见 docs/整合方案.md。上游更新后重跑本脚本；上游改了文件名或
结构时校验会失败，按报错调整 KEEP / PATCHES 即可。

上次写入的文件记录在 tools/upstream_manifest.json，重跑时先按它清理，绝不碰本 MOD 自己的文件。
"""
import hashlib
import json
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "tools" / "upstream_manifest.json"
GITIGNORE = REPO / ".gitignore"
GI_BEGIN = "# >>> merge_upstream.py 生成：上游 MOD 的二进制资源（不进 git，重跑脚本即可恢复）"
GI_END = "# <<< merge_upstream.py 生成结束"

UPSTREAM = {"gpm": "865040033", "pd": "819148835", "sai": "3610149307"}
NAMES = {"gpm": "Guilli's Planet Modifiers and Features", "pd": "Planetary Diversity", "sai": "Stellar AI"}
TEXT_EXT = {".txt", ".yml", ".gfx", ".gui", ".asset", ".shader", ".fxh", ".settings", ".sfx"}
BINARY_EXT = {".dds", ".tga", ".png", ".mesh", ".anim", ".wav", ".ogg", ".bank", ".fnt", ".psd"}

# =====================================================================================
# 保留清单：相对路径全匹配正则。先 include 再 exclude。
# 二进制资源不在这里列，见 ASSETS。
# =====================================================================================
KEEP = {
    # ---------------------------------------------------------------- GPM
    # 只留行星修正与遗珍。定义类（静态修正、沉积物、触发器、变量）是惰性的——没人引用就零开销，
    # 全留，保留引擎里那些 has_modifier = gpm_precursor_xxx 之类的条件就不用改逻辑。
    # 沉积物 216 个全部 drop_weight = 0（只由脚本放置），不会被原版生成器随机撒出来。
    "gpm": dict(include=[
        r"common/static_modifiers/.*",
        r"common/deposits/.*", r"common/deposit_categories/.*",
        r"common/scripted_triggers/.*", r"common/scripted_variables/.*",
        r"common/script_values/.*", r"common/scripted_loc/.*",
        # 经济类别不是「入口」而是基础设施：planet_<岗位>_<资源>_produces_mult 这类修正键由它自动生成，
        # GPM 的行星修正里用到了（例如 planet_engineers_engineering_research_produces_mult）。
        # 删掉它们会让 20 多个修正条目变成 Invalid modifier（游戏实测确认）。你原来的 PD+GPM+SAI 组合里它们一直在生效。
        r"common/economic_categories/.*",
        # 引擎会调用到的脚本效果（由可达性分析得出，见 docs/整合方案.md）
        r"common/scripted_effects/gpm_spawn_.*",
        r"common/scripted_effects/gpm_scripted_effects\.txt",
        r"common/scripted_effects/gpm_scripted_effects_wondrous_worlds\.txt",
        r"common/scripted_effects/gpm_terraform_scripted_effects\.txt",
        r"common/scripted_effects/gpm_remove_modifiers\.txt",
        r"common/scripted_effects/gpm_remove_planetary_features\.txt",
        r"common/scripted_effects/gpm_remove_ambient_objects\.txt",
        r"common/scripted_effects/gpm_planet_destruction_modifiers\.txt",
        r"common/scripted_effects/gpm_set_ambient_objects\.txt",
        r"common/scripted_effects/gpm_rings_resource_sites\.txt",
        r"common/scripted_effects/gpm_space_deposits\.txt",
        r"common/scripted_effects/gpm_rewards_deposits\.txt",
        # 行星修正调度
        r"common/on_actions/gpm_on_actions\.txt",
        r"common/on_actions/gpm_planet_destruction\.txt",
        r"common/on_actions/zz_on_planet_class_changed_actions\.txt",
        r"events/gpm_engine\.txt", r"events/gpm_game_start\.txt",
        r"events/gpm_on_planet_class_changed_events\.txt", r"events/gpm_terraform_events\.txt",
        r"events/gpm_planet_destruction\.txt", r"events/gpm_flag\.txt",
        # 遗珍与它的支撑
        r"common/relics/.*", r"common/decisions/gpm_relic_decisions\.txt",
        r"common/traits/gpm_traits_leaders\.txt", r"events/gpm_relic_events\.txt",
        r"common/opinion_modifiers/gpm_opinions\.txt",
        # 障碍物 gpm_deposits_blockers 要靠这三个科技清除；改造政策决定改造后重掷还是保留修正
        r"common/technology/gpm_tech\.txt",
        r"common/policies/gpm_policies\.txt",
        r"common/game_concepts/gpm_game_concepts\.txt",   # 唯一的概念，只被改造政策的说明引用
        # 界面与本地化
        r"interface/gpm_icons\.gfx", r"interface/gpm_relics\.gfx", r"interface/gpm_eventpictures\.gfx",
        r"interface/icons/traits/gpm_leader_traits\.gfx",
        r"interface/zzzzzz_gpm_icon_border_override\.gfx",   # 行星修正图标的 12 帧边框（原版只有更少的帧）
        r"common/message_types/gpm_message_types\.txt",     # 遗珍事件的 create_message 要用这里的消息类型
        r"localisation/.*",
        r"gfx/portraits/asset_selectors/gpm_room_textures\.txt",
    ], exclude=[
        # 只服务被删系统的定义（游牧民族）
        r"common/static_modifiers/gpm_NOMADS_static_modifiers\.txt",
        r"common/scripted_triggers/!!_0_gpm_NOMADS_temp_overwrites\.txt",   # 覆盖原版触发器，不惰性
        r"common/scripted_triggers/gpm_NOMADS_scripted_triggers\.txt",
        r"common/scripted_variables/gpm_NOMADS_scripted_variables\.txt",
    ]),
    # ---------------------------------------------------------------- PD
    # 保留全部行星类型体系；删岗位、区域及一切非行星类型内容。
    # events/!vanilla_*_fix.txt 是新行星类型的必需兼容垫片（否则 PD 罕见星球会出现永远完不成的
    # 废弃改造项目 colony.100），保留。政策 pd_terraforming / pd_gaia_modifier 决定改造能否落到
    # PD 类型（pdengine.20/23 读它的 policy_flag），保留。
    "pd": dict(include=[r".*"], exclude=[
        r"descriptor\.mod", r"thumbnail\.png",
        r"common/pop_jobs/.*", r"common/zones/.*",
        r"common/inline_scripts/jobs/.*", r"common/inline_scripts/buildings/.*",
        r"common/inline_scripts/zones/.*",
        # 这三个是原版文件的覆盖，按 PD 区域给区划改名；区域删了，回落到原版
        r"common/inline_scripts/districts/district_triggered_name_(farming|generator|mining)\.txt",
        r"common/buildings/.*",          # 含盖亚播种者覆盖：以 Stellar AI 为准
        r"common/megastructures/.*", r"common/ascension_perks/.*", r"common/governments/.*",
        r"common/technology/.*", r"common/pop_faction_types/.*",
        r"common/decisions/(?!pd_replace_decisions\.txt).*",
        r"common/solar_system_initializers/pd_habitat_start\.txt",
        r"common/scripted_effects/pd_ascension_world_effects\.txt",
        r"common/scripted_effects/pd_domed_colonies_effects\.txt",
        r"common/scripted_effects/pd_ma_overwrite_effects\.txt",
        r"common/deposits/pd_ascension_deposits\.txt",
        r"common/deposits/pd_domed_colony_deposits\.txt",      # 9 个会随机生成，只落在穹顶殖民地上
        r"common/deposits/pd_domed_habitat_deposits\.txt",     # 星系网络枢纽（穹顶基地），用到已删的岗位 inline_script
        r"events/pd_ascension_world_checks\.txt", r"events/pd_dome_bases_events\.txt",
        r"events/pd_planetary_infesters_events\.txt", r"events/pd_tree_of_life_origin_events\.txt",
        r"events/pd_lithoid_planet_events\.txt",   # 岩石飞升世界选颜色，飞升世界已删
    ]),
    # ---------------------------------------------------------------- Stellar AI：原样
    "sai": dict(include=[r".*"], exclude=[r"descriptor\.mod", r"thumbnail\.png"]),
}

# =====================================================================================
# 二进制资源
#   copy_all：整目录拷（PD 的行星贴图几乎全要；GPM 的界面图标、事件图、星球背景体积小）
#   其余二进制只在被保留文本引用时拷（GPM 的模型只用到一个 gpm_molten_planet_blue_2_entity）
# =====================================================================================
ASSETS = {
    "gpm": dict(copy_all=[r"gfx/interface/.*", r"gfx/portraits/.*", r"gfx/event_pictures/.*"]),
    "pd": dict(copy_all=[r"gfx/.*", r"sound/.*"]),
    "sai": dict(copy_all=[]),
}

# =====================================================================================
# 补丁
# =====================================================================================
GPM_DROP_RELICS = [
    # 依赖已删内容、会变空壳的 7 个遗珍（docs/整合方案.md §2.2）
    "gpm_r_alien_eggs", "gpm_r_venerable_dreadnaught", "gpm_r_machine_world_core",
    "gpm_r_self_repairing_obelisk", "gpm_r_time_displacer", "gpm_r_mysterious_shield_generator",
    "gpm_r_soul_gem",
]

GAME_START = """namespace = gpm_game_start

# 皇女的远征军EX：GPM 原来在这里弹出设置菜单（gpm_start_menu.1），由菜单里的「开始游戏」选项
# 启动引擎 gpm_engine.0。菜单已删，这里固定用默认设置直接启动。
# 同时打开 GPM 自带的两个子系统关闭开关——迷你巨构、前驱者修正已经整个删掉，走作者自己设计的关闭路径最稳。
# 起源相关的分支（死亡世界、前驱者世界、陨落帝国殖民地、后裔）与詹姆斯·韦伯彩蛋一并删除。
event = {
	id = gpm_game_start.0
	hide_window = yes
	is_triggered_only = yes

	trigger = {
		NOT = { has_global_flag = gpm_initialisation_menu }
		is_ai = no
	}

	immediate = {
		set_global_flag = gpm_initialisation_menu
		# 默认设置（原菜单的初始值）
		set_global_flag = gpm_modifier_amount_normal
		set_global_flag = gpm_galaxy_age_default
		set_global_flag = gpm_scaling_base_modifier_option
		# 已删子系统的关闭开关
		set_global_flag = gpm_mini_megas_disabled
		set_global_flag = gpm_modifiers_precursor_disabled
		# 不要设 gpm_planetary_rings_disabled：它不只关行星环装饰，还会关掉金属环/冰环这两个
		# 挂在真实星球上的行星修正（gpm_spawn_planet_ring_modifier）。装饰函数 gpm_set_planetary_rings
		# 与资源开采站 gpm_spawn_RES 已经掏空，所以不设它的结果是：修正照挂、不生成环形装饰和开采站
		# 原菜单「开始游戏」选项
		country_event = { id = gpm_engine.0 days = 1 }
	}
}
"""

# (src, rel) -> [(op, arg)]
PATCHES = {
    ("gpm", "events/gpm_game_start.txt"): [("replace_file", GAME_START)],
    ("gpm", "common/on_actions/gpm_on_actions.txt"): [("trim_events", None)],
    # 7 个遗珍分散在两个文件里，各自只找到一部分；最后统一核对 7 个都删到了
    ("gpm", "common/relics/gpm_relics.txt"): [("drop_any", GPM_DROP_RELICS)],
    ("gpm", "common/relics/gpm_relics_precursors.txt"): [("drop_any", GPM_DROP_RELICS)],
    ("gpm", "common/decisions/gpm_relic_decisions.txt"): [
        ("drop", ["decision_gpm_machine_world_core_relic", "decision_gpm_shield_generator_arrays"])],
    # 「遗珍被窃」好感按要求删；opinion_respected_species 依赖已删的物种特质 trait_gpm_high_status；
    # 留下的 opinion_intellectual_promise 被一个前驱者遗珍使用
    ("gpm", "common/opinion_modifiers/gpm_opinions.txt"): [
        ("drop", ["opinion_gpm_stolen_relic", "opinion_respected_species"])],
    ("gpm", "common/policies/gpm_policies.txt"): [("drop", ["gpm_exploration_policy"])],
    ("gpm", "common/technology/gpm_tech.txt"): [("drop", ["gpm_tech_arcane_research"])],
    # 整个函数都在生成已删内容：掏空函数体，保留名字，调用方不用动
    ("gpm", "common/scripted_effects/gpm_rings_resource_sites.txt"): [("stub", ["gpm_spawn_RES"])],
    ("gpm", "common/scripted_effects/gpm_scripted_effects.txt"): [("stub", [
        "gpm_spawn_ruined_mining_facility", "gpm_spawn_ruined_observation_station",
        "gpm_spawn_ruined_refinery", "gpm_spawn_ruined_silo", "gpm_precursor_star_shipyards",
        "gpm_spawn_xandar_gaia_world"])],   # 「赞达尔」彩蛋星球，带守护者 gpm_ego
    ("gpm", "common/scripted_effects/gpm_set_ambient_objects.txt"): [("stub", [
        "gpm_precursor_ambient_object_generator", "gpm_set_fallen_empire_planetary_shields",
        "gpm_set_planetary_rings", "gpm_set_precursor_planetary_shields",
        "gpm_set_precursor_planetary_shields_machines", "gpm_set_shipyards_objects",
        "gpm_set_precursor_energy_grid"])],   # 前驱者能源网格的星球外观（16 个实体、约 260 MB 贴图）
    ("gpm", "common/scripted_effects/gpm_spawn_precursor_modifiers.txt"): [("stub", ["gpm_spawn_precursor_modifier"])],
    # 函数里修正和装饰混在一起：只剥掉生成环境物件的语句
    ("gpm", "common/scripted_effects/gpm_spawn_city_planet_modifiers.txt"): [("strip_ambient", None)],
    ("pd", "common/on_actions/pd_on_actions.txt"): [("trim_events", None)],
    # 巴奥尔的生命之种：GPM 和 PD 都重定义了它，采用 PD 版（PD 的新行星类型会影响改造目标判定；
    # GPM 版加的掷修正已经由 on_planet_class_changed 钩子覆盖）。GPM 那份 zz_gpm_boal_overwrite.txt 不在保留清单里
    ("pd", "common/decisions/pd_replace_decisions.txt"): [
        ("drop", ["decision_tidal_lock_planet", "decision_cultivated_worldscaping"])],
    ("pd", "common/game_concepts/01_pd_concepts.txt"): [
        ("drop", ["concept_pd_moonbase", "concept_pd_domed_colony", "concept_tech_pd_domed_colonies",
                  "concept_pd_network_hub"])],
    # 星系网络枢纽属于已删的穹顶基地，永远不会出现：计数恒为 0
    ("pd", "common/script_values/pd_script_values.txt"): [
        ("sub", (r"has_deposit\s*=\s*d_pd_solar_system_network_hub", "always = no"))],
    # PD 整个覆盖了原版的赛博特质文件，但那份比 4.5.3 旧，缺火山气候赛博适应（地狱 DLC 加的）。
    # 原版的断开连接局势（unplugged_effects.txt）与同化事件（assimilation_events.txt）都引用它。
    # 从原版同名文件把这个块补回来，并把它加进另外三个气候适应特质的互斥列表（与原版一致）。
    # 顺序不能反：先补互斥（只命中 PD 原有的 3 个），再追加原版块（它自己的互斥列表已经是对的）
    ("pd", "common/traits/10_species_traits_cyborg.txt"): [
        ("sub", (r'(opposites\s*=\s*\{(?:\s*"trait_cyborg_climate_adjustment_(?:wet|dry|cold)")+)',
                 '\\1\n\t\t"trait_cyborg_climate_adjustment_volcanic"', 3)),
        ("append_vanilla", ["trait_cyborg_climate_adjustment_volcanic"])],
}

# 从被排除的上游文件里只抽出指定的顶层块，单独成一个新文件。
# 新文件路径 -> (src, 来源相对路径, [块名])
EXTRACT = {
    # 遗珍激活奖励（gpm_relic_events.txt）要用这两个函数；它们只依赖原版（has_ancrel、add_resource），
    # 但所在的 gpm_rewards.txt 其余部分全是勘探奖励，引用大量已删的科技与标本
    "common/scripted_effects/gpm_rewards_relic_subset.txt": (
        "gpm", "common/scripted_effects/gpm_rewards.txt",
        ["gpm_random_minor_artifacts_precursor", "gpm_random_minor_artifacts_precursor_big"]),
}

# 对保留的 GPM/PD 脚本统一做的条件替换。本来就没有国家能拥有已删的起源，逻辑等价。
GLOBAL_SUBS = [
    (re.compile(r"\bhas_origin\s*=\s*\"?origin_(?:gpm|pd)_\w+\"?"), "always = no"),
    # 同理：没人能拥有已删的遗珍（gpm_relics_scripted_triggers.txt 的「拥有任一 GPM 遗珍」里列着它们）
    (re.compile(r"\bhas_relic\s*=\s*\"?(?:" + "|".join(GPM_DROP_RELICS) + r")\b\"?"), "always = no"),
]

# =====================================================================================
# 文本工具
# =====================================================================================
COMMENT = re.compile(r"#[^\n]*")


def decode(raw: bytes):
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig", errors="strict") if bom else raw.decode("utf-8", errors="replace")
    crlf = "\r\n" in text
    return text.replace("\r\n", "\n"), bom, crlf


def encode(text, bom, crlf):
    if crlf:
        text = text.replace("\n", "\r\n")
    return (b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8")


def code_mask(text):
    """注释与字符串位置换成空格的副本（长度不变），用来找括号与关键字。"""
    out = list(text)
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == "#":
            while i < n and text[i] != "\n":
                out[i] = " "; i += 1
            continue
        if c == '"':
            out[i] = " "; i += 1
            while i < n and text[i] != '"':
                if text[i] != "\n":
                    out[i] = " "
                i += 1
            if i < n:
                out[i] = " "; i += 1
            continue
        i += 1
    return "".join(out)


def match_brace(mask, open_idx):
    d = 0
    for j in range(open_idx, len(mask)):
        if mask[j] == "{":
            d += 1
        elif mask[j] == "}":
            d -= 1
            if d == 0:
                return j
    raise ValueError("括号不配对")


def top_blocks(text):
    """[(name, line_start, brace_open, brace_close)]，只认行首无缩进的 name = {"""
    mask = code_mask(text)
    out = []
    for m in re.finditer(r"^([A-Za-z0-9_@.\-]+)[ \t]*=[ \t]*\{", mask, re.M):
        o = m.end() - 1
        c = match_brace(mask, o)
        out.append((m.group(1), m.start(), o, c))
    return out


def op_drop(text, names, label, strict=True):
    want = set(names)
    blocks = [b for b in top_blocks(text) if b[0] in want]
    found = {b[0] for b in blocks}
    if strict and want - found:
        raise SystemExit(f"[补丁失败] {label}：找不到要删除的块 {sorted(want - found)}（上游结构变了？）")
    for name, start, _o, close in sorted(blocks, key=lambda b: -b[1]):
        end = close + 1
        if end < len(text) and text[end] == "\n":
            end += 1
        text = text[:start] + f"# [merge_upstream] 已删除 {name}\n" + text[end:]
    return text, found


def op_stub(text, names, label):
    want = set(names)
    blocks = [b for b in top_blocks(text) if b[0] in want]
    found = {b[0] for b in blocks}
    miss = want - found
    if miss:
        raise SystemExit(f"[补丁失败] {label}：找不到要掏空的函数 {sorted(miss)}（上游结构变了？）")
    for name, _s, o, close in sorted(blocks, key=lambda b: -b[2]):
        text = text[:o + 1] + f"\n\t# [merge_upstream] 函数体已掏空：只生成已删除的内容\n" + text[close:]
    return text


def op_strip_ambient(text, label):
    """删掉所有 create_ambient_object = { ... } 及紧随其后的 last_created_ambient_object = { ... }。"""
    count = 0
    while True:
        mask = code_mask(text)
        m = re.search(r"create_ambient_object\s*=\s*\{", mask)
        if not m:
            break
        o = m.end() - 1
        c = match_brace(mask, o)
        end = c + 1
        tail = re.match(r"\s*last_created_ambient_object\s*=\s*\{", mask[end:])
        if tail:
            o2 = end + tail.end() - 1
            end = match_brace(mask, o2) + 1
        line_start = text.rfind("\n", 0, m.start()) + 1
        indent = text[line_start:m.start()]
        text = text[:m.start()] + "# [merge_upstream] 已剥离环境物件（装饰）" + text[end:]
        count += 1
    if not count:
        raise SystemExit(f"[补丁失败] {label}：没有找到 create_ambient_object（上游结构变了？）")
    return text, count


def op_trim_events(text, deleted_ids, label):
    """on_actions：events = { ... } 里删掉已删事件；random_events = { N = id } 里整对删掉。"""
    removed = []
    out_parts, pos = [], 0
    mask = code_mask(text)
    for m in re.finditer(r"\b(events|random_events)\s*=\s*\{", mask):
        o = m.end() - 1
        c = match_brace(mask, o)
        body = text[o + 1:c]
        lines = body.split("\n")
        new_lines = []
        for ln in lines:
            code, sep, comment = ln.partition("#")
            if m.group(1) == "random_events":
                def kill_pair(mm):
                    if mm.group(2) in deleted_ids:
                        removed.append(mm.group(2)); return ""
                    return mm.group(0)
                code2 = re.sub(r"(\b[0-9.]+\s*=\s*)([A-Za-z0-9_]+\.[0-9]+)\b", kill_pair, code)
            else:
                def kill(mm):
                    if mm.group(0) in deleted_ids:
                        removed.append(mm.group(0)); return ""
                    return mm.group(0)
                code2 = re.sub(r"\b[A-Za-z0-9_]+\.[0-9]+\b", kill, code)
            if code2 != code and not code2.strip():
                # 整行只剩被删的事件：连注释一起去掉，避免留下误导性的说明
                continue
            new_lines.append(code2 + sep + comment)
        out_parts.append(text[pos:o + 1])
        out_parts.append("\n".join(new_lines))
        pos = c
    out_parts.append(text[pos:])
    return "".join(out_parts), removed


# =====================================================================================
# 符号表（用于事件裁剪与最终校验）
# =====================================================================================
NONINERT = {  # 删了会让引用方出错/失效的定义类型
    "megastructures", "global_ship_designs", "ship_sizes", "armies", "special_projects", "ambient_objects",
    "decisions", "technology", "buildings", "edicts", "policies", "war_goals", "casus_belli",
    "tradable_actions", "espionage_operation_types", "archaeological_site_types", "specimens",
    "starbase_buildings", "zones", "pop_jobs", "solar_system_initializers", "anomalies", "event_chains",
    "relics", "traits", "planet_classes", "component_templates", "governments", "opinion_modifiers",
    "artifact_actions", "ascension_perks", "section_templates", "static_modifiers", "deposits",
    "scripted_effects", "scripted_triggers", "script_values", "event",
}
INNER_KEY = {"special_projects": "key", "ambient_objects": "name", "global_ship_designs": "name",
             "component_templates": "key", "section_templates": "key", "message_types": "key"}
SKIP_DEF = {"on_actions", "random_names", "economic_categories", "game_concepts",
            "start_screen_messages", "defines", "map_modes", "inline_scripts", "scripted_variables"}
NONINERT.add("message_types")
INLINE_REF = re.compile(r"\binline_script\s*=\s*(?:\{[^}]*?\bscript\s*=\s*)?\"?([A-Za-z0-9_/\-]+)\"?")


def event_ids(text):
    """事件文件里定义的事件 ID：每个顶层 *_event = { ... } 块里的第一个 id。
    GPM 有不少写成一行的事件（carrier_event = { id = gpm_colony.1 hide_window = yes ...），
    不能按「行首 id =」找；也不能找全部 id =，那会把 country_event = { id = X } 这类调用算进来。"""
    out = []
    for name, _s, o, c in top_blocks(text):
        if name.endswith("event"):
            m = re.search(r"\bid\s*=\s*([A-Za-z0-9_]+\.[0-9]+)", code_mask(text[o + 1:c]))
            if m:
                out.append(m.group(1))
    return out
FLAG_STMT = re.compile(r"\b(?:has|set|remove|set_timed)_\w*_flag\s*=\s*(?:\{[^}]*\}|\"?[A-Za-z0-9_@\[\].]+\"?)")
PATH_STR = re.compile(r"\"[^\"\n]*/[^\"\n]*\"")   # 文件路径字符串（图标等），里面的名字不是符号引用
TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(?:\.[0-9]+)?")


def definitions(rel, text):
    parts = rel.split("/")
    if parts[0] == "events":
        return [("event", i) for i in event_ids(text)]
    text = COMMENT.sub("", text)
    if parts[0] != "common" or len(parts) < 3:
        return []
    folder = parts[1]
    if folder in SKIP_DEF:
        return []
    if folder in INNER_KEY:
        k = INNER_KEY[folder]
        return [(folder, n) for n in re.findall(rf"^\s+{k}\s*=\s*\"?([A-Za-z0-9_]+)\"?", text, re.M)]
    return [(folder, m) for m in re.findall(r"^([A-Za-z0-9_\-]+)\s*=\s*\{", text, re.M)]


def scan_tree(root: Path, only=None):
    """{name: set(kind)}；only 是相对路径集合（None = 全部 common/ 与 events/ 下的 .txt）"""
    defs = defaultdict(set)
    for p in list(root.glob("common/**/*.txt")) + list(root.glob("events/*.txt")):
        rel = p.relative_to(root).as_posix()
        if only is not None and rel not in only:
            continue
        for k, n in definitions(rel, p.read_text(encoding="utf-8-sig", errors="replace")):
            defs[n].add(k)
    return defs


# =====================================================================================
# 主流程
# =====================================================================================
def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    ws = Path(sys.argv[1])
    mod = Path(sys.argv[2]).resolve()
    game = ws.parents[2] / "common" / "Stellaris"
    for s, mid in UPSTREAM.items():
        if not (ws / mid).is_dir():
            raise SystemExit(f"找不到 {NAMES[s]}：{ws / mid}（没订阅？）")
    if not (game / "common").is_dir():
        raise SystemExit(f"找不到原版目录：{game}")

    # ---------- 1. 挑文件 ----------
    keep = {}
    every = {}
    for s, mid in UPSTREAM.items():
        root = ws / mid
        allf = sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())
        every[s] = allf
        inc = [re.compile(x) for x in KEEP[s]["include"]]
        exc = [re.compile(x) for x in KEEP[s]["exclude"]]
        keep[s] = [r for r in allf if Path(r).suffix.lower() in TEXT_EXT
                   and any(p.fullmatch(r) for p in inc) and not any(p.fullmatch(r) for p in exc)
                   and "/" in r]   # 根目录下的说明文档不要
    for (s, rel) in PATCHES:
        if rel not in keep[s]:
            raise SystemExit(f"[配置错误] 补丁目标 {s}:{rel} 不在保留清单里（或上游已改名）")

    # 被删事件 ID（用于裁剪 on_actions）
    deleted_events = set()
    kept_events = set()
    for s, mid in UPSTREAM.items():
        root = ws / mid
        for r in every[s]:
            if r.startswith("events/") and r.endswith(".txt"):
                ids = event_ids((root / r).read_text(encoding="utf-8-sig", errors="replace"))
                (kept_events if r in keep[s] else deleted_events).update(ids)
    deleted_events -= kept_events

    # ---------- 2. 生成文本（先全部在内存里做完，校验通过才落盘） ----------
    out_text = {}   # mod 相对路径 -> bytes
    origin = {}     # mod 相对路径 -> "src:rel"
    report = defaultdict(list)
    dropped_defs = defaultdict(set)   # 被「删块」删掉的定义：校验时与被删文件里的定义同等对待
    for s, mid in UPSTREAM.items():
        root = ws / mid
        for rel in keep[s]:
            raw = (root / rel).read_bytes()
            ops = PATCHES.get((s, rel), [])
            is_script = rel.startswith("common/") or rel.startswith("events/")
            if not ops and not (is_script and s in ("gpm", "pd")):
                out_text[rel] = raw
                origin[rel] = f"{s}:{rel}"
                continue
            text, bom, crlf = decode(raw)
            for op, arg in ops:
                if op == "replace_file":
                    text = arg
                    report[s].append(f"{rel}：整文件改写")
                elif op in ("drop", "drop_any"):
                    text, found = op_drop(text, arg, rel, strict=(op == "drop"))
                    report[s].append(f"{rel}：删除 {len(found)} 块 {sorted(found)}")
                    folder = rel.split("/")[1] if rel.startswith("common/") else "event"
                    for n in found:
                        dropped_defs[n].add(folder)
                elif op == "stub":
                    text = op_stub(text, arg, rel)
                    report[s].append(f"{rel}：掏空 {len(arg)} 个函数")
                elif op == "strip_ambient":
                    text, n = op_strip_ambient(text, rel)
                    report[s].append(f"{rel}：剥离 {n} 处环境物件")
                elif op == "trim_events":
                    text, removed = op_trim_events(text, deleted_events, rel)
                    report[s].append(f"{rel}：裁掉 {len(removed)} 个已删事件的钩子")
                elif op == "sub":
                    text, n = re.subn(arg[0], arg[1], text)
                    want = arg[2] if len(arg) > 2 else None
                    if not n or (want is not None and n != want):
                        raise SystemExit(f"[补丁失败] {rel}：正则 {arg[0]} 命中 {n} 处"
                                         f"{f'（应为 {want}）' if want else ''}（上游结构变了？）")
                    report[s].append(f"{rel}：替换 {n} 处 {arg[0][:50]}")
                elif op == "append_vanilla":
                    vtext, _b, _c = decode((game / rel).read_bytes())
                    vblocks = {b[0]: b for b in top_blocks(vtext)}
                    have = {b[0] for b in top_blocks(text)}
                    for n in arg:
                        if n in have:
                            raise SystemExit(f"[补丁失败] {rel}：{n} 上游已经有了，不需要从原版补（上游更新了？）")
                        if n not in vblocks:
                            raise SystemExit(f"[补丁失败] {rel}：原版同名文件里找不到 {n}")
                        b = vblocks[n]
                        text = text.rstrip("\n") + f"\n\n# [merge_upstream] 从原版 4.5.3 同名文件补回（上游缺）\n" \
                                                   f"{vtext[b[1]:b[3] + 1]}\n"
                    report[s].append(f"{rel}：从原版补回 {len(arg)} 块 {arg}")
            if is_script and s in ("gpm", "pd"):
                for rx, rep in GLOBAL_SUBS:
                    text, n = rx.subn(rep, text)
                    if n:
                        report[s].append(f"{rel}：{n} 处已删起源/遗珍条件 -> always = no")
            # drop 的块如果分散在两个遗珍文件里，各自只找到一部分是正常的；最后统一核对
            out_text[rel] = encode(text, bom, crlf)
            origin[rel] = f"{s}:{rel}"

    for new_rel, (s, src_rel, names) in EXTRACT.items():
        if src_rel in keep[s]:
            raise SystemExit(f"[配置错误] {src_rel} 已在保留清单里，不需要 EXTRACT")
        text, bom, crlf = decode((ws / UPSTREAM[s] / src_rel).read_bytes())
        blocks = {b[0]: b for b in top_blocks(text)}
        miss = [n for n in names if n not in blocks]
        if miss:
            raise SystemExit(f"[补丁失败] {s}:{src_rel} 里找不到要抽取的块 {miss}（上游结构变了？）")
        body = "".join(text[blocks[n][1]:blocks[n][3] + 1] + "\n\n" for n in names)
        head = (f"# 由 tools/merge_upstream.py 从 {NAMES[s]} 的 {src_rel} 抽出，请勿手改\n"
                f"# 只保留 {len(names)} 个块：{', '.join(names)}\n\n")
        out_text[new_rel] = encode(head + body, bom, crlf)
        origin[new_rel] = f"{s}:{src_rel}（抽取）"
        report[s].append(f"{new_rel}：从 {src_rel} 抽出 {len(names)} 个函数")

    dropped_relics = set()
    for rel in ("common/relics/gpm_relics.txt", "common/relics/gpm_relics_precursors.txt"):
        for n in GPM_DROP_RELICS:
            if f"# [merge_upstream] 已删除 {n}\n" in out_text[rel].decode("utf-8-sig", errors="replace").replace("\r\n", "\n"):
                dropped_relics.add(n)
    if dropped_relics != set(GPM_DROP_RELICS):
        raise SystemExit(f"[补丁失败] 没删到的遗珍：{sorted(set(GPM_DROP_RELICS) - dropped_relics)}")

    # 与本 MOD 自己的文件撞路径？
    prev = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {"files": {}}
    prev_files = set(prev["files"])
    for rel in out_text:
        if (mod / rel).exists() and rel not in prev_files:
            raise SystemExit(f"[冲突] {rel} 已经是本 MOD 自己的文件，上游也有同路径文件——需要手工处理")

    # ---------- 3. 校验：保留的上游脚本里不得引用只在被删上游文件里定义的符号 ----------
    ok_defs = scan_tree(game)
    own_files = {p.relative_to(mod).as_posix() for p in mod.rglob("*.txt")} - prev_files
    for n, k in scan_tree(mod, own_files).items():
        ok_defs[n] |= k
    for rel, raw in out_text.items():
        if rel.endswith(".txt"):
            for k, n in definitions(rel, raw.decode("utf-8-sig", errors="replace")):
                ok_defs[n].add(k)
    del_defs = defaultdict(set)
    for s, mid in UPSTREAM.items():
        root = ws / mid
        kept = set(keep[s])
        for r in every[s]:
            if r.endswith(".txt") and r not in kept and (r.startswith("common/") or r.startswith("events/")):
                for k, n in definitions(r, (root / r).read_text(encoding="utf-8-sig", errors="replace")):
                    if k in NONINERT:
                        del_defs[n].add(k)
    for n, kinds in dropped_defs.items():
        del_defs[n] |= kinds
    problems = defaultdict(set)
    for rel, raw in out_text.items():
        if not (rel.endswith(".txt") and (rel.startswith("common/") or rel.startswith("events/"))):
            continue
        text = PATH_STR.sub(" ", FLAG_STMT.sub(" ", COMMENT.sub("", raw.decode("utf-8-sig", errors="replace"))))
        for tok in set(TOKEN.findall(text)):
            if tok in del_defs and tok not in ok_defs:
                problems[origin[rel]].add(f"{tok} ({'/'.join(sorted(del_defs[tok]))})")
    # inline_script 引用的脚本必须存在（合并结果、本 MOD 自己、原版三者之一）
    inline_ok = {r[len("common/inline_scripts/"):-4] for r in out_text if r.startswith("common/inline_scripts/")}
    inline_ok |= {p.relative_to(mod / "common/inline_scripts").as_posix()[:-4]
                  for p in (mod / "common/inline_scripts").rglob("*.txt")
                  if p.relative_to(mod).as_posix() not in prev_files} if (mod / "common/inline_scripts").exists() else set()
    inline_ok |= {p.relative_to(game / "common/inline_scripts").as_posix()[:-4]
                  for p in (game / "common/inline_scripts").rglob("*.txt")}
    for rel, raw in out_text.items():
        if rel.endswith(".txt") and (rel.startswith("common/") or rel.startswith("events/")):
            for ref in INLINE_REF.findall(COMMENT.sub("", raw.decode("utf-8-sig", errors="replace"))):
                if ref not in inline_ok:
                    problems[origin[rel]].add(f"inline_script {ref}（不存在）")
    if problems:
        print("\n[校验失败] 保留的上游文件引用了已删除的定义：\n")
        for where, toks in sorted(problems.items()):
            print(f"  {where}")
            for t in sorted(toks):
                print(f"      {t}")
        raise SystemExit(1)

    # ---------- 4. 二进制资源 ----------
    out_bin = {}   # mod 相对路径 -> 源文件 Path
    entity_need = set()
    path_need = set()
    for rel, raw in out_text.items():
        t = raw.decode("utf-8-sig", errors="replace")
        if origin[rel].startswith("gpm:"):
            entity_need |= set(re.findall(r"\bentity\s*=\s*\"([A-Za-z0-9_]+)\"", t))
        path_need |= {x.replace("\\", "/").lower() for x in
                      re.findall(r"\"((?:gfx|sound|music)/[^\"]+\.(?:dds|tga|png|mesh|anim|wav|ogg))\"", t, re.I)}
    # GPM 脚本用到的实体：只抽取需要的 entity 块（GPM 一个 .asset 里几十个实体，原样拷会让其余实体
    # 引用一堆没拷的贴图，启动时刷缺贴图错误）。实体里的贴图写的是裸文件名，相对 .asset 所在目录。
    groot = ws / UPSTREAM["gpm"]
    extracted = defaultdict(list)
    for ap in sorted(groot.glob("gfx/models/**/*.asset")):
        at, _bom, _crlf = decode(ap.read_bytes())
        d = ap.relative_to(groot).parent.as_posix()
        for name, start, _o, close in top_blocks(at):
            if name != "entity":
                continue
            block = at[start:close + 1]
            m = re.search(r"\bname\s*=\s*\"([A-Za-z0-9_]+)\"", block)
            if m and m.group(1) in entity_need:
                extracted[d].append((ap.relative_to(groot).as_posix(), m.group(1), block))
                path_need |= {f"{d}/{x}".lower() for x in re.findall(r"\"([A-Za-z0-9_\-]+\.dds)\"", block)}
                path_need |= {x.lower() for x in re.findall(r"\"((?:gfx)/[^\"]+\.(?:mesh|anim|dds))\"", block, re.I)}
    for d, items in extracted.items():
        rel = f"{d}/gpm_merged_entities.asset"
        head = "# 由 tools/merge_upstream.py 从 Guilli's Planet Modifiers 抽出被保留脚本用到的实体，请勿手改\n\n"
        body = "".join(f"# 来自 {src}\n{blk}\n\n" for src, _n, blk in items)
        out_text[rel] = (head + body).encode("utf-8")
        origin[rel] = "gpm:gfx/models（抽取）"
        report["gpm"].append(f"{rel}：抽出 {len(items)} 个实体 {[n for _s, n, _b in items]}")
    unresolved = entity_need - {n for items in extracted.values() for _s, n, _b in items}
    van_entities = set()
    for ap in (game / "gfx").rglob("*.asset"):
        van_entities |= set(re.findall(r"\bname\s*=\s*\"([A-Za-z0-9_]+)\"",
                                       ap.read_text(encoding="utf-8-sig", errors="replace")))
    if unresolved - van_entities:
        raise SystemExit(f"[资源失败] GPM 脚本用到的实体在 GPM 与原版里都找不到：{sorted(unresolved - van_entities)}")
    # mesh 里嵌的贴图名（相对 mesh 所在目录）
    for s, mid in UPSTREAM.items():
        root = ws / mid
        lower = {r.lower(): r for r in every[s]}
        for want in list(path_need):
            if want.endswith(".mesh") and want in lower:
                data = (root / lower[want]).read_bytes()
                base = want.rsplit("/", 1)[0]
                for tex in set(re.findall(rb"([A-Za-z0-9_\-]+\.dds)", data)):
                    path_need.add(f"{base}/{tex.decode().lower()}")
    for s, mid in UPSTREAM.items():
        root = ws / mid
        alls = [re.compile(x) for x in ASSETS[s]["copy_all"]]
        for r in every[s]:
            if Path(r).suffix.lower() not in BINARY_EXT:
                continue
            if any(p.fullmatch(r) for p in alls) or r.lower() in path_need:
                if r in out_bin and out_bin[r] != root / r:
                    raise SystemExit(f"[冲突] 两个上游 MOD 都有 {r}")
                out_bin[r] = root / r
                origin[r] = f"{s}:{r}"
    for rel in out_bin:
        if (mod / rel).exists() and rel not in prev_files:
            raise SystemExit(f"[冲突] {rel} 已经是本 MOD 自己的文件，上游也有同路径文件——需要手工处理")
    # 被保留文本引用、但哪里都没有的贴图
    have = {r.lower() for r in out_bin} | {p.relative_to(mod).as_posix().lower() for p in mod.rglob("*")
                                           if p.is_file()} - {x.lower() for x in prev_files}
    van = {p.relative_to(game).as_posix().lower() for d in ("gfx", "sound") for p in (game / d).rglob("*") if p.is_file()}
    missing = sorted(x for x in path_need if x not in have and x not in van and not x.endswith(".mesh"))

    # ---------- 5. 落盘（只写有变化的；上次写过、这次不要的删掉） ----------
    stale = prev_files - set(out_text) - set(out_bin)
    for rel in stale:
        p = mod / rel
        if p.exists():
            p.unlink()
    n_text = n_bin = 0
    for rel, raw in out_text.items():
        p = mod / rel
        if p.exists() and p.read_bytes() == raw:
            continue
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(raw)
        n_text += 1
    for rel, src in out_bin.items():
        p = mod / rel
        if p.exists():
            a, b = p.stat(), src.stat()
            if a.st_size == b.st_size and int(a.st_mtime) == int(b.st_mtime):
                continue
        p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, p)   # 保留修改时间，下次按「大小 + 修改时间」判断是否需要重拷
        n_bin += 1
    print(f"写入：文本 {n_text} 个、二进制 {n_bin} 个有变化；删除 {len(stale)} 个不再需要的上游文件")
    # 清掉因为删文件留下的空目录
    for d in sorted({(mod / r).parent for r in stale}, key=lambda x: -len(x.parts)):
        try:
            while d != mod and not any(d.iterdir()):
                d.rmdir(); d = d.parent
        except FileNotFoundError:
            pass

    files = {}
    for rel, raw in out_text.items():
        files[rel] = {"from": origin[rel], "sha1": hashlib.sha1(raw).hexdigest()}
    for rel in out_bin:
        files[rel] = {"from": origin[rel], "binary": True}
    MANIFEST.write_text(json.dumps({"upstream": {s: f"{NAMES[s]} ({mid})" for s, mid in UPSTREAM.items()},
                                    "files": dict(sorted(files.items()))},
                                   ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    gi = GITIGNORE.read_text(encoding="utf-8") if GITIGNORE.exists() else ""
    if GI_BEGIN in gi:
        gi = gi[:gi.index(GI_BEGIN)].rstrip("\n") + "\n" + gi[gi.index(GI_END) + len(GI_END):].lstrip("\n")
    section = [GI_BEGIN] + [f"/mod/{r}" for r in sorted(out_bin)] + [GI_END]
    GITIGNORE.write_text(gi.rstrip("\n") + "\n\n" + "\n".join(section) + "\n", encoding="utf-8")

    # ---------- 6. 报告 ----------
    tsize = sum(len(b) for b in out_text.values())
    bsize = sum(p.stat().st_size for p in out_bin.values())
    print(f"文本 {len(out_text)} 个（{tsize / 1e6:.1f} MB，进 git），二进制 {len(out_bin)} 个（{bsize / 1e6:.0f} MB，不进 git）")
    for s in UPSTREAM:
        n_t = sum(1 for r in out_text if origin[r].startswith(s + ":"))
        n_b = sum(1 for r in out_bin if origin[r].startswith(s + ":"))
        print(f"  {NAMES[s]}：文本 {n_t}，二进制 {n_b}")
        for line in report[s]:
            print(f"    · {line}")
    if missing:
        print(f"\n[提示] {len(missing)} 个被引用的贴图在上游、本 MOD、原版里都找不到（上游本身就缺，或路径大小写不一致）：")
        for x in missing[:20]:
            print(f"    {x}")
    print("\n校验通过：保留的上游脚本没有引用任何已删除的定义。")


if __name__ == "__main__":
    main()
