"""从原版文件生成「皇女的远征军EX」里整文件覆盖的两份原版文件，只改动必要的几处。

用法：python gen_vanilla_patches.py <群星安装目录> <MOD 根目录>
群星更新后重新运行即可；每处替换都会核对出现次数，原版改了写法就会直接报错，不会悄悄漏改。

- common/megastructures/11_mega_shipyard.txt：巨型船坞（自建完成、修复完成）的船坞数量 20 → 50
- events/ancient_relics_arcsite_events_2.txt：关掉 ancrel.12050 里 1/4 概率随机生成天选民的那一支
  （其余权重不变；天选民改由本 MOD 的 atb_ex_spawn_chosen 固定在 8 点生成）
- common/starbase_modules/00_starbase_modules.txt（3.0）：船坞模块的产能翻倍——每个船坞模块
  原本同时造 1 艘，加一条 starbase_shipyard_capacity_add = 1 变成 2 艘（对所有国家生效）
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
            "（那一支的权重不变，抽中时什么也不做），天选民改由本 MOD 固定在 8 点生成。群星更新后用新版原版重新生成。",
        ],
        # 整段注释掉：只注释 system_event 会留下空的 random_rim_system，error.log 会报警告
        replace=[("\t\t\t\trandom_rim_system = {\n"
                  "\t\t\t\t\tlimit = { is_mindwardens_story_system = no }\n"
                  "\t\t\t\t\tsystem_event = { id = fircon.3500 }\n"
                  "\t\t\t\t}\n",
                  "\t\t\t\t# 皇女的远征军EX：天选民改由 atb_ex_spawn_chosen 固定在 8 点生成\n"
                  "\t\t\t\t# random_rim_system = {\n"
                  "\t\t\t\t# \tlimit = { is_mindwardens_story_system = no }\n"
                  "\t\t\t\t# \tsystem_event = { id = fircon.3500 }\n"
                  "\t\t\t\t# }\n", 1)],
    ),
    dict(
        path="common/starbase_modules/00_starbase_modules.txt",
        header=[
            "皇女的远征军EX：覆盖原版 common/starbase_modules/00_starbase_modules.txt。",
            "由 tools/gen_vanilla_patches.py 生成，请勿手改；与原版唯一的区别：船坞模块（shipyard）",
            "加了 station_modifier = { starbase_shipyard_capacity_add = 1 }，每个船坞模块同时造 2 艘船。",
            "群星更新后用新版原版重新生成。",
        ],
        replace=[("shipyard = {\n"
                  "\ticon = \"GFX_starbase_shipyard\"\n"
                  "\tsection = \"ASSEMBLYYARD_STARBASE_SECTION\"\n"
                  "\tconstruction_days = 180\n"
                  "\tcategory = sm_naval_support_cat\n"
                  "\tinitial = yes\n",
                  "shipyard = {\n"
                  "\ticon = \"GFX_starbase_shipyard\"\n"
                  "\tsection = \"ASSEMBLYYARD_STARBASE_SECTION\"\n"
                  "\tconstruction_days = 180\n"
                  "\tcategory = sm_naval_support_cat\n"
                  "\tinitial = yes\n"
                  "\n"
                  "\t# 皇女的远征军EX：船坞产能翻倍（每个模块同时造 2 艘）\n"
                  "\tstation_modifier = {\n"
                  "\t\tstarbase_shipyard_capacity_add = 1\n"
                  "\t}\n", 1)],
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
