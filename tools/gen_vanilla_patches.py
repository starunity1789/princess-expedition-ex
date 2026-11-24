"""从原版文件生成「皇女的远征军EX」里整文件覆盖的两份原版文件，只改动必要的几处。

用法：python gen_vanilla_patches.py <群星安装目录> <MOD 根目录>
群星更新后重新运行即可；每处替换都会核对出现次数，原版改了写法就会直接报错，不会悄悄漏改。

- common/megastructures/11_mega_shipyard.txt：巨型船坞（自建完成、修复完成）的船坞数量 20 → 50
- events/ancient_relics_arcsite_events_2.txt：关掉 ancrel.12050 里 1/4 概率随机生成天选民的那一支
  （其余权重不变；天选民改由本 MOD 的 atb_ex_spawn_chosen 固定在 7 点半生成（3.10 前为 8 点））
- （3.0～3.6 还覆盖过 common/starbase_modules/00_starbase_modules.txt 让船坞产能翻倍，3.7 起恢复原版）
- common/event_chains/00_event_chains_distant_stars.txt（3.10）：L 星门线索 7 → 3（3.14 起 5）
- common/ai_budget/01_alloys_budget.txt（3.0.3）：AI 超出海军容量后造舰预算大幅降低——×0.75 → ×0.1；
  「邻国成为天灾时 ×5」只在舰容 100% 以内生效（原版 150%）。AI 有了自动星球以后合金很多，原版规则下
  会一直超容造舰，舰船数量翻倍拖慢游戏（系列 21 实测）
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
GAME = Path(sys.argv[1])
MOD = Path(sys.argv[2])

MEGA_SHIPYARD_CAPACITY = 50

PATCHES = [
    dict(
        path="common/megastructures/11_mega_shipyard.txt",
        header=[
            "皇女的远征军EX：覆盖原版 common/megastructures/11_mega_shipyard.txt。",
            f"由 tools/gen_vanilla_patches.py 生成，请勿手改；与原版唯一的区别：巨型船坞的船坞数量 20 → {MEGA_SHIPYARD_CAPACITY}",
            "（mega_shipyard_3 与 mega_shipyard_restored，对所有国家生效）。群星更新后用新版原版重新生成。",
        ],
        replace=[("starbase_shipyard_capacity_add = 20",
                  f"starbase_shipyard_capacity_add = {MEGA_SHIPYARD_CAPACITY}", 2)],
    ),
    dict(
        path="events/ancient_relics_arcsite_events_2.txt",
        header=[
            "皇女的远征军EX：覆盖原版 events/ancient_relics_arcsite_events_2.txt。",
            "由 tools/gen_vanilla_patches.py 生成，请勿手改；与原版唯一的区别：ancrel.12050 不再随机生成天选民",
            "（那一支的权重不变，抽中时什么也不做），天选民改由本 MOD 固定在 7 点半生成（3.10 前为 8 点）。群星更新后用新版原版重新生成。",
        ],
        # 整段注释掉：只注释 system_event 会留下空的 random_rim_system，error.log 会报警告
        replace=[("\t\t\t\trandom_rim_system = {\n"
                  "\t\t\t\t\tlimit = { is_mindwardens_story_system = no }\n"
                  "\t\t\t\t\tsystem_event = { id = fircon.3500 }\n"
                  "\t\t\t\t}\n",
                  "\t\t\t\t# 皇女的远征军EX：天选民改由 atb_ex_spawn_chosen 固定在 7 点半生成（3.10 前为 8 点）\n"
                  "\t\t\t\t# random_rim_system = {\n"
                  "\t\t\t\t# \tlimit = { is_mindwardens_story_system = no }\n"
                  "\t\t\t\t# \tsystem_event = { id = fircon.3500 }\n"
                  "\t\t\t\t# }\n", 1)],
    ),
    dict(
        path="common/ai_budget/01_alloys_budget.txt",
        header=[
            "皇女的远征军EX：覆盖原版 common/ai_budget/01_alloys_budget.txt。",
            "由 tools/gen_vanilla_patches.py 生成，请勿手改；与原版的区别只在 alloys_expenditure_ships：",
            "超出海军容量后造舰预算 ×0.75 → ×0.1；「邻国成为天灾时 ×5」的门槛 150% → 100%。",
            "群星更新后用新版原版重新生成。",
        ],
        replace=[
            ("\t\t# spend less alloys on ships if over capacity\n"
             "\t\tmodifier = {\n"
             "\t\t\tfactor = 0.75\n"
             "\t\t\tused_naval_capacity_percent >= 1.0\n",
             "\t\t# spend less alloys on ships if over capacity\n"
             "\t\t# 皇女的远征军EX：原版 0.75，超容后几乎照造；改成 0.1\n"
             "\t\tmodifier = {\n"
             "\t\t\tfactor = 0.1\n"
             "\t\t\tused_naval_capacity_percent >= 1.0\n", 1),
            ("\t\t\tfactor = 5\n"
             "\t\t\tused_naval_capacity_percent < 1.5\n",
             "\t\t\tfactor = 5\n"
             "\t\t\tused_naval_capacity_percent < 1.0\t# 皇女的远征军EX：原版 1.5\n", 1),
        ],
    ),
    # ---- 3.6：苍神缘起帝国（远征军）的灵能飞升路线 ----
    # 原版把「合成繁衍」起源本身算作已合成飞升（has_synthetic_ascension），灵能飞升、灵能传统树、
    # 两个灵能议程一律关闭。迷雾之影 DLC 已经有机器人专用的灵能特质（trait_robot_(latent_)psionic），
    # 所以只给开启了灵能之路的国家（国家旗标 atb_psionic_path_open，由二皇女的事件 atb.50 设置）开例外，
    # 其余条件、与基因/赛博/合成飞升技能的互斥都不动；不改 has_synthetic_ascension 本身（原版几十处合成内容在用）。
    dict(
        path="common/ascension_perks/00_ascension_paths.txt",
        header=[
            "皇女的远征军EX：覆盖原版 common/ascension_perks/00_ascension_paths.txt。",
            "由 tools/gen_vanilla_patches.py 生成，请勿手改；与原版的区别只在灵能飞升 ap_mind_over_matter：",
            "开启了灵能之路（国家旗标 atb_psionic_path_open）的国家不因「合成繁衍」起源而隐藏、不因主物种是机械而禁止。",
            "群星更新后用新版原版重新生成。",
        ],
        replace=[
            # 锚点从 ratling_country 起，只有 ap_mind_over_matter 的 potential 是这样开头
            ("\t\t\thas_country_flag = ratling_country\n"
             "\t\t\thas_ascension_perk = ap_engineered_evolution\n"
             "\t\t\thas_ascension_perk = ap_the_flesh_is_weak \n"
             "\t\t\thas_ascension_perk = ap_organo_machine_interfacing\n"
             "\t\t\thas_ascension_perk = ap_organo_machine_interfacing_assimilator\n"
             "\t\t\thas_ascension_perk = ap_synthetic_evolution\n"
             "\t\t\thas_ascension_perk = ap_mind_over_matter\n"
             "\t\t\thas_ascension_perk = ap_synthetic_age\n"
             "\t\t\thas_origin = origin_shroudwalker_apprentice\n"
             "\t\t\thas_origin = origin_cybernetic_creed\n"
             "\t\t\thas_origin = origin_synthetic_fertility\n",
             "\t\t\thas_country_flag = ratling_country\n"
             "\t\t\thas_ascension_perk = ap_engineered_evolution\n"
             "\t\t\thas_ascension_perk = ap_the_flesh_is_weak \n"
             "\t\t\thas_ascension_perk = ap_organo_machine_interfacing\n"
             "\t\t\thas_ascension_perk = ap_organo_machine_interfacing_assimilator\n"
             "\t\t\thas_ascension_perk = ap_synthetic_evolution\n"
             "\t\t\thas_ascension_perk = ap_mind_over_matter\n"
             "\t\t\thas_ascension_perk = ap_synthetic_age\n"
             "\t\t\thas_origin = origin_shroudwalker_apprentice\n"
             "\t\t\thas_origin = origin_cybernetic_creed\n"
             "\t\t\t# 皇女的远征军EX：开启了灵能之路的合成繁衍帝国例外\n"
             "\t\t\tAND = {\n"
             "\t\t\t\thas_origin = origin_synthetic_fertility\n"
             "\t\t\t\tNOT = { has_country_flag = atb_psionic_path_open }\n"
             "\t\t\t}\n", 1),
            ("\t\tcustom_tooltip = {\n"
             "\t\t\tfail_text = \"synthetic_empire_psionic_ascension\"\n"
             "\t\t\tNOT = { has_trait = trait_mechanical }\n"
             "\t\t}\n",
             "\t\tcustom_tooltip = {\n"
             "\t\t\tfail_text = \"synthetic_empire_psionic_ascension\"\n"
             "\t\t\tOR = {\n"
             "\t\t\t\tNOT = { has_trait = trait_mechanical }\n"
             "\t\t\t\thas_country_flag = atb_psionic_path_open\t# 皇女的远征军EX\n"
             "\t\t\t}\n"
             "\t\t}\n", 1),
        ],
    ),
    dict(
        path="common/tradition_categories/01_psionics_shroud.txt",
        header=[
            "皇女的远征军EX：覆盖原版 common/tradition_categories/01_psionics_shroud.txt。",
            "由 tools/gen_vanilla_patches.py 生成，请勿手改；与原版唯一的区别：开启了灵能之路",
            "（国家旗标 atb_psionic_path_open）的国家不因已合成飞升而隐藏这棵传统树。群星更新后用新版原版重新生成。",
        ],
        replace=[("\t\t\thas_synthetic_ascension = yes\n",
                  "\t\t\tAND = {\t# 皇女的远征军EX：开启了灵能之路的国家例外\n"
                  "\t\t\t\thas_synthetic_ascension = yes\n"
                  "\t\t\t\tNOT = { has_country_flag = atb_psionic_path_open }\n"
                  "\t\t\t}\n", 1)],
    ),
    dict(
        path="common/council_agendas/02_council_agendas_ascensions.txt",
        header=[
            "皇女的远征军EX：覆盖原版 common/council_agendas/02_council_agendas_ascensions.txt。",
            "由 tools/gen_vanilla_patches.py 生成，请勿手改；与原版的区别只在 agenda_mind_over_matter 与",
            "agenda_psionic_supremacy_shroud：开启了灵能之路（国家旗标 atb_psionic_path_open）的国家不因已合成飞升而隐藏。",
            "群星更新后用新版原版重新生成。",
        ],
        replace=[
            ("\t\tNAND = {\n"
             "\t\t\thas_technology = tech_psionic_theory\n",
             "\t\tNAND = {\n"
             "\t\t\thas_technology = tech_psionic_theory\n", 1),  # 只用来确认 agenda_mind_over_matter 的写法没变
            ("\t\t\thas_synthetic_ascension = yes\n"
             "\t\t\tis_natural_design_empire = yes\n"
             "\t\t\thas_purity_ascension = yes\n"
             "\t\t\thas_cloning_ascension = yes\n"
             "\t\t\thas_mutation_ascension = yes\n"
             "\t\t}\n"
             "\t\tNAND = {\n"
             "\t\t\thas_technology = tech_psionic_theory\n",
             "\t\t\tAND = {\t# 皇女的远征军EX：开启了灵能之路的国家例外\n"
             "\t\t\t\thas_synthetic_ascension = yes\n"
             "\t\t\t\tNOT = { has_country_flag = atb_psionic_path_open }\n"
             "\t\t\t}\n"
             "\t\t\tis_natural_design_empire = yes\n"
             "\t\t\thas_purity_ascension = yes\n"
             "\t\t\thas_cloning_ascension = yes\n"
             "\t\t\thas_mutation_ascension = yes\n"
             "\t\t}\n"
             "\t\tNAND = {\n"
             "\t\t\thas_technology = tech_psionic_theory\n", 1),
            ("\t\thas_shroud_dlc = yes\n"
             "\t\tNOR = {\n"
             "\t\t\thas_cybernetic_ascension = yes\n"
             "\t\t\thas_genetic_ascension = yes\n"
             "\t\t\thas_synthetic_ascension = yes\n"
             "\t\t\tis_natural_design_empire = yes\n"
             "\t\t\tis_individual_machine = yes\n"
             "\t\t}\n",
             "\t\thas_shroud_dlc = yes\n"
             "\t\tNOR = {\n"
             "\t\t\thas_cybernetic_ascension = yes\n"
             "\t\t\thas_genetic_ascension = yes\n"
             "\t\t\tAND = {\t# 皇女的远征军EX：开启了灵能之路的国家例外\n"
             "\t\t\t\thas_synthetic_ascension = yes\n"
             "\t\t\t\tNOT = { has_country_flag = atb_psionic_path_open }\n"
             "\t\t\t}\n"
             "\t\t\tis_natural_design_empire = yes\n"
             "\t\t\tis_individual_machine = yes\n"
             "\t\t}\n", 1),
        ],
    ),
    # ---- 3.10：L 星门线索 7 → 3；3.14 改为 5 ----
    dict(
        path="common/event_chains/00_event_chains_distant_stars.txt",
        header=[
            "皇女的远征军EX：覆盖原版 common/event_chains/00_event_chains_distant_stars.txt。",
            "由 tools/gen_vanilla_patches.py 生成，请勿手改；与原版唯一的区别：L 星群事件链（l_cluster_chain）",
            "需要的 L 星门线索 7 → 5（对所有国家生效；3.10～3.13 为 3）。群星更新后用新版原版重新生成。",
        ],
        replace=[("l_cluster_chain = {\n"
                  "\ticon = \"gfx/interface/icons/situation_log/situation_log_main_quest.dds\"\n"
                  "\tpicture = GFX_evt_surreal_visions\n"
                  "\tcounter = {\n"
                  "\t\tclues = {\n"
                  "\t\t\tmax = 7\n",
                  "l_cluster_chain = {\n"
                  "\ticon = \"gfx/interface/icons/situation_log/situation_log_main_quest.dds\"\n"
                  "\tpicture = GFX_evt_surreal_visions\n"
                  "\tcounter = {\n"
                  "\t\tclues = {\n"
                  "\t\t\tmax = 5\t# 皇女的远征军EX：原版 7（3.10～3.13 为 3）\n", 1)],
    ),
    # ---- 以下 4 个 3.15 起改由本脚本生成（之前手工维护，群星 4.6 改了这几个原版文件） ----
    # 乌托邦富足在远征军体制下不要求平等主义
    dict(
        path="common/species_rights/living_standards/00_living_standards.txt",
        header=[
            "皇女的远征军：覆盖原版 common/species_rights/living_standards/00_living_standards.txt。",
            "由 tools/gen_vanilla_patches.py 生成，请勿手改；与原版唯一的区别：乌托邦富足（living_standard_utopian）",
            "在远征军体制下不要求平等主义。群星更新后用新版原版重新生成。",
        ],
        replace=[("\t\t\tfail_text = empire_not_egalitarian\n"
                  "\t\t\tfrom = {\n"
                  "\t\t\t\tis_egalitarian = yes\n"
                  "\t\t\t}\n",
                  "\t\t\tfail_text = empire_not_egalitarian\n"
                  "\t\t\tfrom = {\n"
                  "\t\t\t\tOR = {\n"
                  "\t\t\t\t\tis_egalitarian = yes\n"
                  "\t\t\t\t\t# 皇女的远征军：远征军体制也可以使用乌托邦富足\n"
                  "\t\t\t\t\thas_country_flag = atb_expedition_regime\n"
                  "\t\t\t\t}\n"
                  "\t\t\t}\n", 1)],
    ),
    # 光耀者起源：远征军第一幕结束后触发 atb.51，不改为帝制
    dict(
        path="events/origin_events_paragon.txt",
        header=[
            "皇女的远征军：覆盖原版 events/origin_events_paragon.txt（光耀者起源事件）。",
            "由 tools/gen_vanilla_patches.py 生成，请勿手改；与原版的区别只有三处，都只对远征军（国家标记 atb_princess_expedition）生效：",
            "- paragon.5008 / paragon.5009：第一幕结束后改为触发 atb.51，不再触发 paragon.5020",
            "- paragon.5020：远征军不触发（原版这里会把政体改为帝制）",
            "第三幕由国家标记 paragon_origin_purges 挡住（原版 paragon.5061 的条件），见 atb_effects.txt。",
        ],
        replace=[
            ("\t\tcountry_event = {\n"
             "\t\t\tid = paragon.5020 days = 180 random = 360\n"
             "\t\t}\n",
             "\t\t# 皇女的远征军：远征军不走「改为帝制」的分支，改由 atb.51 收束第一幕\n"
             "\t\tif = {\n"
             "\t\t\tlimit = { has_country_flag = atb_princess_expedition }\n"
             "\t\t\tcountry_event = {\n"
             "\t\t\t\tid = atb.51 days = 180 random = 360\n"
             "\t\t\t}\n"
             "\t\t}\n"
             "\t\telse = {\n"
             "\t\t\tcountry_event = {\n"
             "\t\t\t\tid = paragon.5020 days = 180 random = 360\n"
             "\t\t\t}\n"
             "\t\t}\n", 2),
            ("\tid = paragon.5020\n"
             "\ttitle = \"paragon.5020.name\"\n"
             "\tdesc = \"paragon.5020.desc\"\n"
             "\tpicture = GFX_evt_enclave_overlord\n"
             "\tshow_sound = event_factions\n"
             "\n"
             "\tis_triggered_only = yes\n"
             "\n"
             "\ttrigger = {\n"
             "\t}\n",
             "\tid = paragon.5020\n"
             "\ttitle = \"paragon.5020.name\"\n"
             "\tdesc = \"paragon.5020.desc\"\n"
             "\tpicture = GFX_evt_enclave_overlord\n"
             "\tshow_sound = event_factions\n"
             "\n"
             "\tis_triggered_only = yes\n"
             "\n"
             "\ttrigger = {\n"
             "\t\t# 皇女的远征军：远征军的起源与体制都依赖独裁制，不能改为帝制\n"
             "\t\tNOT = { has_country_flag = atb_princess_expedition }\n"
             "\t}\n", 1),
        ],
    ),
    # 远征军体制：独裁制的一种高级体制替换；独裁流型、虚拟独裁在远征军体制生效时让位
    dict(
        path="common/governments/authorities/00_authorities.txt",
        header=[
            "皇女的远征军：覆盖原版 common/governments/authorities/00_authorities.txt。",
            "由 tools/gen_vanilla_patches.py 生成，请勿手改；与原版的区别只在 auth_dictatorial：新增体制「远征军体制」",
            "auth_atb_expedition，并让独裁流型（物理 / 虚拟）在远征军体制生效时让位。群星更新后用新版原版重新生成。",
        ],
        replace=[
            ("\tadvanced_authority_swap\t= {\n"
             "\t\tname = \"auth_synth_dictatorial_physical\"\n"
             "\t\tdescription = \"auth_synth_dictatorial_physical_desc\"\n"
             "\t\tinherit_icon = no\n"
             "\t\tinherit_effects = no\n"
             "\t\ttrigger = {\n"
             "\t\t\tis_scope_valid = yes\n"
             "\t\t\thas_country_flag = synth_physical\n",
             "\t# 皇女的远征军：远征军体制\n"
             "\t# 数值与独裁流型（auth_synth_dictatorial_physical）相同；采用时会同时设置 synth_physical，\n"
             "\t# 因此同样能解锁高级机器人特质。额外效果：可用乌托邦富足生活水平（见 00_living_standards.txt），\n"
             "\t# 来自人口和区划的帝国规模 -12%。\n"
             "\tadvanced_authority_swap\t= {\n"
             "\t\tname = \"auth_atb_expedition\"\n"
             "\t\tdescription = \"auth_atb_expedition_desc\"\n"
             "\t\tinherit_icon = no\n"
             "\t\tinherit_effects = no\n"
             "\t\ttrigger = {\n"
             "\t\t\tis_scope_valid = yes\n"
             "\t\t\thas_country_flag = atb_expedition_regime\n"
             "\t\t}\n"
             "\t\tmodifier = {\n"
             "\t\t\tcustom_tooltip = auth_atb_expedition_tt\n"
             "\t\t\tshow_only_custom_tooltip = no\n"
             "\t\t\truler_skill_add = 5\n"
             "\t\t\tall_technology_research_speed = -0.05\n"
             "\t\t\tplanet_jobs_worker_produces_mult = 0.15\n"
             "\t\t\tplanet_structures_cost_mult = -0.25\n"
             "\t\t\tplanet_structures_upkeep_mult = -0.50\n"
             "\t\t\tempire_size_pops_mult = -0.12\n"
             "\t\t\tempire_size_districts_mult = -0.12\n"
             "\t\t}\n"
             "\t}\n"
             "\n"
             "\tadvanced_authority_swap\t= {\n"
             "\t\tname = \"auth_synth_dictatorial_physical\"\n"
             "\t\tdescription = \"auth_synth_dictatorial_physical_desc\"\n"
             "\t\tinherit_icon = no\n"
             "\t\tinherit_effects = no\n"
             "\t\ttrigger = {\n"
             "\t\t\tis_scope_valid = yes\n"
             "\t\t\thas_country_flag = synth_physical\n"
             "\t\t\tNOT = { has_country_flag = atb_expedition_regime }\n", 1),
            ("\t\tname = \"auth_synth_dictatorial_virtual\"\n"
             "\t\tdescription = \"auth_synth_dictatorial_virtual_desc\"\n"
             "\t\tinherit_icon = no\n"
             "\t\tinherit_effects = no\n"
             "\t\ttrigger = {\n"
             "\t\t\tis_scope_valid = yes\n"
             "\t\t\thas_country_flag = synth_virtual\n",
             "\t\tname = \"auth_synth_dictatorial_virtual\"\n"
             "\t\tdescription = \"auth_synth_dictatorial_virtual_desc\"\n"
             "\t\tinherit_icon = no\n"
             "\t\tinherit_effects = no\n"
             "\t\ttrigger = {\n"
             "\t\t\tis_scope_valid = yes\n"
             "\t\t\thas_country_flag = synth_virtual\n"
             "\t\t\tNOT = { has_country_flag = atb_expedition_regime }\n", 1),
        ],
    ),
    # ---- 3.15：远征军融合「黄金世代」起源的学院与培养领袖部分（意志之力 DLC） ----
    # 远征军开局切换成合成繁衍起源，不能再有黄金世代起源，所以把下列原版文件里的
    # has_origin = origin_golden_generation 换成 atb_has_golden_generation = yes（= 有该起源或有国家标记 atb_golden_generation，
    # 见 scripted_triggers/atb_triggers.txt）。只覆盖学院、培养事件链、毕业、精英学院 / 博物馆相关的文件；
    # 意识形态（教条 00_tenets.txt、事件链后期编纂黄金世代意识形态的 forceofwill.5695→5699→5700）与成就事件不改，远征军不触发
    *[dict(
        path=p,
        header=[
            f"皇女的远征军：覆盖原版 {p}。",
            "由 tools/gen_vanilla_patches.py 生成，请勿手改；与原版的区别：has_origin = origin_golden_generation 换成",
            "atb_has_golden_generation = yes（远征军融合黄金世代的学院与培养领袖部分）。群星更新后用新版原版重新生成。",
        ],
        replace=[("has_origin = origin_golden_generation", "atb_has_golden_generation = yes", n)],
    ) for p, n in (
        ("common/buildings/25_forceofwill_buildings.txt", 6),
        ("common/event_chains/00_event_chains_force_of_will.txt", 1),
        ("common/inline_scripts/game_start/origin_golden_generation.txt", 1),
        ("common/scripted_effects/forceofwill_scripted_effects.txt", 3),
        ("common/scripted_triggers/10_scripted_triggers_forceofwill.txt", 2),
    )],
    dict(
        path="events/origin_events_forceofwill.txt",
        header=[
            "皇女的远征军：覆盖原版 events/origin_events_forceofwill.txt。",
            "由 tools/gen_vanilla_patches.py 生成，请勿手改；与原版的区别（远征军融合黄金世代的学院与培养领袖部分）：",
            "- has_origin = origin_golden_generation 换成 atb_has_golden_generation = yes，forceofwill.5695 除外",
            "  （它安排 5699→5700 把黄金世代编纂成意识形态，远征军不要意识形态部分）",
            "- forceofwill.5800 / 5810（黄金学院失去）：原版 set_origin = origin_default，远征军的起源是合成繁衍，",
            "  不能被清掉，改为只对真正的黄金世代起源改默认起源，远征军去掉标记 atb_golden_generation",
            "群星更新后用新版原版重新生成。",
        ],
        replace=[
            ("has_origin = origin_golden_generation", "atb_has_golden_generation = yes", 72),
            ("\t\towner? = {\n"
             "\t\t\tatb_has_golden_generation = yes\n"
             "\t\t\tNOT = { has_country_flag = golden_generation_codifying_ideology } # set in forceofwill.5699\n",
             "\t\towner? = {\n"
             "\t\t\thas_origin = origin_golden_generation\t# 皇女的远征军：意识形态部分远征军不触发\n"
             "\t\t\tNOT = { has_country_flag = golden_generation_codifying_ideology } # set in forceofwill.5699\n", 1),
            ("\t\tset_origin = origin_default\n"
             "\t\tremove_modifier = golden_academy_budget_modifier\n",
             "\t\t# 皇女的远征军：远征军的起源是合成繁衍，只去掉黄金世代标记\n"
             "\t\tif = {\n"
             "\t\t\tlimit = { has_origin = origin_golden_generation }\n"
             "\t\t\tset_origin = origin_default\n"
             "\t\t}\n"
             "\t\tremove_country_flag = atb_golden_generation\n"
             "\t\tremove_modifier = golden_academy_budget_modifier\n", 1),
            ("\t\t\tset_origin = origin_default\n"
             "\t\t}\n"
             "\t}\n"
             "\n"
             "\toption = {\n"
             "\t\tname = forceofwill.5810.a\n",
             "\t\t\t# 皇女的远征军：远征军的起源是合成繁衍，只去掉黄金世代标记\n"
             "\t\t\tif = {\n"
             "\t\t\t\tlimit = { has_origin = origin_golden_generation }\n"
             "\t\t\t\tset_origin = origin_default\n"
             "\t\t\t}\n"
             "\t\t\tremove_country_flag = atb_golden_generation\n"
             "\t\t}\n"
             "\t}\n"
             "\n"
             "\toption = {\n"
             "\t\tname = forceofwill.5810.a\n", 1),
        ],
    ),
    # 可编入舰队的主宰 atb_juggernaut 加进舰船组件 / 定位触发器；原版主宰停建（3.19 起删除了无畏舰 atb_dreadnought）
    dict(
        path="common/scripted_triggers/07_scripted_triggers_ships.txt",
        header=[
            "皇女的远征军：覆盖原版 common/scripted_triggers/07_scripted_triggers_ships.txt。",
            "由 tools/gen_vanilla_patches.py 生成，请勿手改。与原版的区别：",
            "3.10：可编入舰队的主宰 atb_juggernaut 加进 ship_uses_titan_components / ship_uses_juggernaut_components /",
            "ship_uses_artillery_role / ship_uses_carrier_role / ship_uses_juggernaut_reactors / ship_uses_colossus_thrusters；",
            "原版主宰的 juggernaut_potential_construction 改为 always = no，原内容改名 atb_juggernaut_potential_construction。",
        ],
        replace=[(f"{trig} = {{\n\tOR = {{\n",
                  f"{trig} = {{\n\tOR = {{\n" + "".join(
                      {"j": "\t\t# 皇女的远征军：可编入舰队的主宰（3.10）\n\t\tis_ship_size = atb_juggernaut\n"}[c] for c in who), 1)
                 for trig, who in (
                     ("ship_uses_titan_components", "j"),
                     ("ship_uses_artillery_role", "j"),
                     ("ship_uses_carrier_role", "j"),
                     ("ship_uses_juggernaut_reactors", "j"),
                     ("ship_uses_colossus_thrusters", "j"),
                 )] + [
            ("ship_uses_juggernaut_components = {\n\tis_ship_size = juggernaut\n}\n",
             "ship_uses_juggernaut_components = {\n"
             "\tOR = {\n"
             "\t\tis_ship_size = juggernaut\n"
             "\t\t# 皇女的远征军：可编入舰队的主宰（3.10）\n"
             "\t\tis_ship_size = atb_juggernaut\n"
             "\t}\n"
             "}\n", 1),
            ("\njuggernaut_potential_construction = {\n",
             "\n# 皇女的远征军 3.10：原版主宰（移动船坞）不再能建造，改由可编入舰队的 atb_juggernaut 代替\n"
             "juggernaut_potential_construction = {\n"
             "\talways = no\n"
             "}\n"
             "\n"
             "# 原版 juggernaut_potential_construction 的内容，给 atb_juggernaut 用（主宰本身不再是恒星基地，这里照抄无妨）\n"
             "atb_juggernaut_potential_construction = {\n", 1),
        ],
    ),
]

for patch in PATCHES:
    raw = (GAME / patch["path"]).read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    text = raw.decode("utf-8-sig")
    crlf = "\r\n" in text
    text = text.replace("\r\n", "\n")
    for old, new, count in patch["replace"]:
        found = text.count(old)
        if found != count:
            sys.exit(f"{patch['path']}：「{old}」应出现 {count} 次，实际 {found} 次——原版可能改了写法，请手动核对")
        text = text.replace(old, new)
    text = "".join(f"# {line}\n" for line in patch["header"]) + "\n" + text
    if crlf:
        text = text.replace("\n", "\r\n")
    out = MOD / patch["path"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes((b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8"))
    print("generated", patch["path"])


# ---- 3.11：遥远之约定搬进 L 星群的原版特殊星系 ----
# 原版这些初始化器都有 max_instances = 1，银河生成时用掉了名额（清掉银河里那份也不退），spawn_system 会报
# 「reached its max_instances limit」而不生成。这里照抄原版、换成 atb_lc_ 前缀的新键，去掉随机生成相关的
# usage / usage_odds / max_instances / spawn_chance，只供 atb_ex_lcluster_extra_systems 用 spawn_system 生成。
# 内容取原版（不取 Real Space 等 MOD 的改写，它们用到自己的脚本变量）。
LC_INITIALIZERS = [
    "time_loop_world_system", "living_planet_system", "scavenger_system", "guardians_init_dragon",
    "guardians_artist_init_01", "guardians_artist_init_02", "guardians_artist_init_03",
    "guardians_curator_init_01", "guardians_curator_init_02", "guardians_curator_init_03",
    "great_wound_system", "elderly_tiyanki_system", "locust_system_initializer_01",
    "voidworms_spawn_system_medium",
]
LC_STRIP = ("usage", "usage_odds", "max_instances", "spawn_chance", "scaled_spawn_chance", "primitive_system")


def lc_blocks(text):
    import re
    i, n = 0, len(text)
    for m in re.finditer(r"(?m)^([A-Za-z_0-9]+)\s*=\s*\{", text):
        if m.start() < i:
            continue
        depth, j = 0, m.end() - 1
        while j < n:
            c = text[j]
            if c == "#":
                j = text.find("\n", j)
                j = n if j < 0 else j
                continue
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        yield m.group(1), text[m.start():j + 1]
        i = j + 1


def lc_strip_top(block):
    """去掉初始化器第一层的随机生成参数（含整个 usage_odds 块）"""
    import re
    out, lines, k = [], block.split("\n"), 0
    while k < len(lines):
        line = lines[k]
        m = re.match(r"^\t([A-Za-z_]+)\s*=", line)
        if m and m.group(1) in LC_STRIP:
            depth = line.split("#")[0].count("{") - line.split("#")[0].count("}")
            k += 1
            while depth > 0:
                code = lines[k].split("#")[0]
                depth += code.count("{") - code.count("}")
                k += 1
            continue
        out.append(line)
        k += 1
    return "\n".join(out)


lc_found = {}
for f in sorted((GAME / "common/solar_system_initializers").glob("*.txt")):
    for key, block in lc_blocks(f.read_text(encoding="utf-8-sig").replace("\r\n", "\n")):
        if key in LC_INITIALIZERS:
            lc_found[key] = (f.name, block)
missing = [k for k in LC_INITIALIZERS if k not in lc_found]
if missing:
    sys.exit(f"原版里找不到初始化器：{missing}")

VOIDWORM_INLINE = ("\tinline_script = {\n"
                   "\t\tscript = grand_archive/voidworms_system_planet_initializer\n"
                   "\t\tSIZE = medium\n"
                   "\t}\n")
lc_out = [
    "# 皇女的远征军EX：遥远之约定搬进 L 星群的原版特殊星系（3.11）。",
    "# 由 tools/gen_vanilla_patches.py 从原版照抄生成，请勿手改：键名加 atb_lc_ 前缀，去掉 usage / usage_odds /",
    "# max_instances / spawn_chance（原版 max_instances = 1 的名额在银河生成时已用掉，spawn_system 会拒绝生成）。",
    "# 只由 atb_ex_lcluster_extra_systems 用 spawn_system 生成，不参与银河生成。群星更新后重新生成。",
    "",
]
for key in LC_INITIALIZERS:
    fname, block = lc_found[key]
    if key == "voidworms_spawn_system_medium":
        if block.count(VOIDWORM_INLINE) != 1:
            sys.exit("voidworms_spawn_system_medium 的写法变了，请手动核对")
        inline = (GAME / "common/inline_scripts/grand_archive/voidworms_system_planet_initializer.txt") \
            .read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("$SIZE$", "medium").strip("\n")
        inline = "\n".join(("\t" + l) if l else l for l in inline.split("\n")) + "\n"
        block = block.replace(VOIDWORM_INLINE, inline)
    block = lc_strip_top(block)
    # 3.15：巡逻用的 find_closest_planet 等 trigger 带全局唯一的 id（dragon.home.1、scav.1……），照抄会与原版重名，
    # 游戏报 "id has to be unique" 并让原版那份读取失败（原版星系里的以太龙、拾荒者等就不再巡逻）。加 atb_lc. 前缀
    import re
    block, n_ids = re.subn(r'(trigger = \{\s*\n\s*id = )"?([\w.]+)"?', r'\1"atb_lc.\2"', block)
    if "max_instances" in block or "usage_odds" in block:
        sys.exit(f"{key}：没去干净随机生成参数，请手动核对")
    lc_out.append(f"# 原版 {fname} 的 {key}")
    lc_out.append("atb_lc_" + block)
    lc_out.append("")
out = MOD / "common/solar_system_initializers/atb_lc_initializers.txt"
out.write_text("\n".join(lc_out), encoding="utf-8", newline="\n")
print("generated", out.relative_to(MOD).as_posix())


# ---- 3.14：两项开局科技，照抄原版先驱者科技（只改名） ----
# 农业生产聚合体 = 巴奥有机工厂（tech_secrets_baol + 建筑 building_baol_organic_plant）
# 集中工业产线枢纽 = 伊拉斯人海军船坞（tech_secrets_irassian + 恒星基地建筑 irassian_naval_yards / arkship_irassian_naval_yards）
# 科技加 start_tech = yes（所有国家开局就有，potential 照原版要求远古遗迹 DLC），图标沿用原版；
# 建筑与恒星基地建筑照抄，只把键名和前置科技换成新的。与原版那两项先驱者科技互不影响，都有时两种建筑都能造。
PRECURSOR_RENAME = {
    "tech_secrets_baol": "tech_atb_agri_aggregate",
    "tech_secrets_irassian": "tech_atb_industrial_hub",
    "building_baol_organic_plant": "building_atb_agri_aggregate",
    "arkship_irassian_naval_yards": "atb_arkship_industrial_hub",
    "irassian_naval_yards": "atb_industrial_hub",
}
PRECURSOR_COPIES = [
    # (原版目录, 原版键, 输出文件, 额外插在第一行之后的内容)
    ("common/technology", "tech_secrets_baol", "common/technology/atb_precursor_copy_tech.txt",
     '\ticon = "tech_secrets_baol"\n\tstart_tech = yes\t# 皇女的远征军EX：开局科技\n'),
    ("common/technology", "tech_secrets_irassian", "common/technology/atb_precursor_copy_tech.txt",
     '\ticon = "tech_secrets_irassian"\n\tstart_tech = yes\t# 皇女的远征军EX：开局科技\n'),
    ("common/buildings", "building_baol_organic_plant", "common/buildings/atb_precursor_copy_buildings.txt",
     "\ticon = building_baol_organic_plant\n"),
    ("common/starbase_buildings", "irassian_naval_yards", "common/starbase_buildings/atb_precursor_copy_starbase_buildings.txt", ""),
    ("common/starbase_buildings", "arkship_irassian_naval_yards", "common/starbase_buildings/atb_precursor_copy_starbase_buildings.txt", ""),
]


def precursor_rename(block):
    import re
    # 长的键先换（arkship_irassian_naval_yards 含 irassian_naval_yards）；只换整词，图标名 GFX_starbase_irassian_naval_yards 不动
    for old in sorted(PRECURSOR_RENAME, key=len, reverse=True):
        block = re.sub(rf"(?<![A-Za-z0-9_]){old}(?![A-Za-z0-9_])", PRECURSOR_RENAME[old], block)
    return block


pc_out = {}
for folder, key, outrel, extra in PRECURSOR_COPIES:
    found = None
    for f in sorted((GAME / folder).glob("*.txt")):
        for k, block in lc_blocks(f.read_text(encoding="utf-8-sig").replace("\r\n", "\n")):
            if k == key:
                found = (f.name, block)
    if not found:
        sys.exit(f"原版 {folder} 里找不到 {key}")
    fname, block = found
    new = precursor_rename(block)
    first, rest = new.split("\n", 1)
    new = first + "\n" + extra + rest
    pc_out.setdefault(outrel, []).append(f"# 原版 {folder}/{fname} 的 {key}\n{new}\n")
for outrel, parts in pc_out.items():
    head = ("# 皇女的远征军EX 3.14：开局科技「农业生产聚合体」「集中工业产线枢纽」，照抄原版先驱者科技（巴奥有机工厂、伊拉斯人海军船坞）只改名。\n"
            "# 由 tools/gen_vanilla_patches.py 从原版生成，请勿手改；群星更新后重新生成。\n\n")
    out = MOD / outrel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(head + "\n".join(parts), encoding="utf-8", newline="\n")
    print("generated", outrel)


# ---- 3.19：开局科技「行星团结机构」，换皮原版「文化中心」（Ministry of Culture，building_artist_patron） ----
# 原版文化中心只有和艺术团做交易（国家标记 artist_building_patron）才能建。这里照抄建筑、只改键名，
# 改由开局科技 tech_atb_planetary_unity 解锁（全帝国限 1 座，效果完全相同）；
# 原版触发器 has_ethics_output（文化工作者按思潮产出）里写死了 building_artist_patron，照抄一份把新建筑加进去
UNITY_TECH = """tech_atb_planetary_unity = {
	icon = "tech_planetary_unification"
	start_tech = yes	# 皇女的远征军EX 3.19：开局科技
	cost = @tier1cost1
	area = society
	tier = 1
	category = { statecraft }
	weight = 0
	is_rare = yes
}
"""
ab = None
for f in sorted((GAME / "common/buildings").glob("*.txt")):
    for k, block in lc_blocks(f.read_text(encoding="utf-8-sig").replace("\r\n", "\n")):
        if k == "building_artist_patron":
            ab = (f.name, block)
if not ab:
    sys.exit("原版里找不到 building_artist_patron")
fname, block = ab
POT_OLD = ("\tpotential = {\n"
           "\t\tcustom_tooltip = {\n"
           "\t\t\ttext = EMPIRE_UNIQUE_BUILDING\n"
           "\t\t\towner = {\n"
           "\t\t\t\thas_country_flag = artist_building_patron\n"
           "\t\t\t}\n"
           "\t\t}\n")
if block.count(POT_OLD) != 1:
    sys.exit("building_artist_patron 的 potential 写法变了，请手动核对")
block = block.replace(POT_OLD, "\tpotential = {\n", 1)
block = block.replace("building_artist_patron_gestalt_desc", "building_atb_unity_agency_gestalt_desc")
block = block.replace("building_artist_patron_desc", "building_atb_unity_agency_desc")
block = "building_atb_unity_agency" + block[len("building_artist_patron"):]
first, rest = block.split("\n", 1)
block = first + "\n\ticon = building_artist_patron\n" + rest
block = block[:block.rindex("}")] + "\tprerequisites = { \"tech_atb_planetary_unity\" }\n}"
(MOD / "common/technology/atb_unity_tech.txt").write_text(
    "# 皇女的远征军EX 3.19：开局科技「行星团结机构」，解锁换皮原版文化中心的同名建筑。由 tools/gen_vanilla_patches.py 生成，请勿手改。\n\n"
    + UNITY_TECH, encoding="utf-8", newline="\n")
print("generated common/technology/atb_unity_tech.txt")
(MOD / "common/buildings/atb_unity_agency_buildings.txt").write_text(
    f"# 皇女的远征军EX 3.19：「行星团结机构」，照抄原版 common/buildings/{fname} 的 building_artist_patron（文化中心），\n"
    "# 只改键名与解锁方式（开局科技 tech_atb_planetary_unity，不再要求艺术团交易的国家标记）。由 tools/gen_vanilla_patches.py 生成，请勿手改。\n\n"
    + block + "\n", encoding="utf-8", newline="\n")
print("generated common/buildings/atb_unity_agency_buildings.txt")
st = None
for f in sorted((GAME / "common/scripted_triggers").glob("*.txt")):
    for k, b in lc_blocks(f.read_text(encoding="utf-8-sig").replace("\r\n", "\n")):
        if k == "has_ethics_output":
            st = (f.name, b)
if not st:
    sys.exit("原版里找不到 has_ethics_output")
line = "\t\thas_active_building = building_artist_patron\n"
if st[1].count(line) != 1:
    sys.exit("has_ethics_output 的写法变了，请手动核对")
b = st[1].replace(line, line + "\t\thas_active_building = building_atb_unity_agency\t# 皇女的远征军EX 3.19\n", 1)
(MOD / "common/scripted_triggers/zz_atb_unity_agency_triggers.txt").write_text(
    f"# 皇女的远征军EX 3.19：覆盖原版 common/scripted_triggers/{st[0]} 的 has_ethics_output，只多一行「行星团结机构」。\n"
    "# 由 tools/gen_vanilla_patches.py 生成，请勿手改；群星更新后重新生成。\n\n" + b + "\n", encoding="utf-8", newline="\n")
print("generated common/scripted_triggers/zz_atb_unity_agency_triggers.txt")
