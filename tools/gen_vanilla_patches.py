"""从原版文件生成「皇女的远征军EX」里整文件覆盖的两份原版文件，只改动必要的几处。

用法：python gen_vanilla_patches.py <群星安装目录> <MOD 根目录>
群星更新后重新运行即可；每处替换都会核对出现次数，原版改了写法就会直接报错，不会悄悄漏改。

- common/megastructures/11_mega_shipyard.txt：巨型船坞（自建完成、修复完成）的船坞数量 20 → 50
- events/ancient_relics_arcsite_events_2.txt：关掉 ancrel.12050 里 1/4 概率随机生成天选民的那一支
  （其余权重不变；天选民改由本 MOD 的 atb_ex_spawn_chosen 固定在 8 点生成）
- common/starbase_modules/00_starbase_modules.txt（3.0）：船坞模块的产能翻倍——每个船坞模块
  原本同时造 1 艘，加一条 starbase_shipyard_capacity_add = 1 变成 2 艘（对所有国家生效）
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
