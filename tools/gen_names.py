"""生成「皇女的远征军EX」内置的名称集「苍神缘起帝国」（cgen_ 前缀）。

用法：python gen_names.py <MOD 根目录> <文档目录>
源数据是 tools/cgen_names_source.json，改名字都改那里，然后重新运行；不要手改生成出来的 .txt/.yml。
名称集原本是独立 MOD「苍神缘起帝国·名称集 0.1.0」，2.6 起并入本 MOD。与原包的区别：
- 名称集 .txt 加了 UTF-8 BOM（原包没有，游戏会在 error.log 里报 should be in utf8-bom encoding）
- 2.7：殖民船、运输舰、防御平台（含各类空间站）、离子炮不再用 sequential_name 编号——原版只给恒星基地这样用，
  其他舰体用了会显示成很长的数字。改为和原版一样的具名舰名池（源数据里 ship_sequential 留空）

- MOD 根目录：common/name_lists/00_cgen_azure_genesis.txt 与 10 种语言的 localisation/<语言>/cgen_names_l_<语言>.yml
- 文档目录：cgen_名称总览.md（审阅用的总览）与 cgen_characters.txt（全部人名）
"""
import hashlib
import itertools
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
MOD = Path(sys.argv[1]).resolve()
DOCS = Path(sys.argv[2]).resolve()
d = json.loads((HERE / "cgen_names_source.json").read_text(encoding="utf8"))
loc = {}


def put(rel, text, bom=False):
    p = MOD / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8-sig" if bom else "utf8", newline="\n")


def key(group, value):
    """本地化键取名字的哈希，增删或调整顺序时已有的键不会变。"""
    k = "CGEN_" + group + "_" + hashlib.sha256(value.encode("utf8")).hexdigest()[:12].upper()
    if k in loc and loc[k] != value:
        raise ValueError("Hash collision")
    loc[k] = value
    return k


def rows_tokens(tokens, indent="\t\t\t", width=6):
    return "\n".join(indent + " ".join(tokens[i:i + width]) for i in range(0, len(tokens), width))


poolkeys = {g: [key("SHIP", v) for v in vals] for g, vals in d["ship_pools"].items()}
classkeys = {g: [key("CLASS", v) for v in vals] for g, vals in d["class_pools"].items()}
seqkeys = {g: key("SEQ_SHIP", v) for g, v in d["ship_sequential"].items()}
loc["name_list_" + d["id"]] = "苍神缘起帝国"
fleetkey = key("SEQ_FLEET", d["fleet_sequential"])
armykey = key("SEQ_ARMY", d["army_sequential"])
planetkeys = [key("PLANET", v) for v in d["surname_order"]]
artificialkeys = planetkeys + [key("PLANET", v) for v in d["artificial_planets"]]
aliases = d["coverage"]["ship_aliases"]


def target(k):
    """顺着原版 use_shipnames_from 的关联找到最终的舰种。"""
    seen = set()
    while k in aliases:
        assert k not in seen
        seen.add(k)
        k = aliases[k]
    return k


# ---------------------------------------------------------------- 名称集本体
lines = ["# Azure Genesis naming pack. Additive list; no base definitions replaced.",
         d["id"] + " = {", '\tcategory = "Humanoid"', "\tselectable = { always = yes }", "\trandomized = no",
         "\tship_names = {", "\t\tgeneric = { } # Deliberately empty: no 50-percent mixing into dedicated ship names."]
ship_routes = {}
for k in d["coverage"]["ship_sizes"]:
    t = target(k)
    p = t if t in poolkeys or t in seqkeys else "auxiliary"
    ship_routes[k] = p
    lines.append("\t\t" + k + " = {")
    lines.append("\t\t\tsequential_name = " + seqkeys[p] if p in seqkeys else rows_tokens(poolkeys[p]))
    lines.append("\t\t}")
lines += ["\t}", "\tship_class_names = {", "\t\tgeneric = { }"]
for k in d["coverage"]["ship_sizes"]:
    cls = classkeys.get(ship_routes[k], classkeys["auxiliary"])
    lines += ["\t\t" + k + " = { " + " ".join(cls) + " }"]
lines += ["\t}", "\tfleet_names = { sequential_name = " + fleetkey + " }", "\tarmy_names = {",
          "\t\tgeneric = { sequential_name = " + armykey + " }"]
for k in d["coverage"]["armies"]:
    lines.append("\t\t" + k + " = { sequential_name = " + armykey + " }")
lines += ["\t}", "\tplanet_names = {", "\t\tgeneric = {", "\t\t\tnames = {", "\t" + rows_tokens(planetkeys), "\t\t\t}", "\t\t}"]
# 自然星球只用部落姓；人造星球再加上公民理念名
artificial = ["pc_machine", "pc_machine_broken", "pc_ai", "pc_cybrex", "pc_nanotech", "pc_gray_goo", "pc_city",
              "pc_habitat", "pc_ringworld_habitable", "pc_ringworld_habitable_damaged", "pc_shattered_ring_habitable",
              "pc_ringworld_tech", "pc_ringworld_tech_damaged", "pc_ringworld_seam", "pc_ringworld_seam_damaged",
              "pc_crystal_habitat", "pc_cosmogenesis_world", "pc_ark"]
for k in artificial:
    if k in d["coverage"]["planet_classes"]:
        lines += ["\t\t" + k + " = {", "\t\t\tnames = {", "\t" + rows_tokens(artificialkeys), "\t\t\t}", "\t\t}"]
lines += ["\t}", "\tcharacter_names = {"]
allnames = []
for i, c in enumerate(d["clans"], 1):
    # 姓名按「部落姓=个人名=长名」预先组合成 full_names，不需要改原版的 TWO_NAMES_FORMAT
    names = [c["surname"] + "=" + n + "=" + e for n, e in itertools.product(c["given_names"], c["epithets"])]
    allnames += names
    keys = [key("CHR", v) for v in names]
    lines += ["\t\tclan_" + str(i).zfill(2) + " = {", "\t\t\tweight = 1", "\t\t\tfull_names = {",
              "\t" + rows_tokens(keys), "\t\t\t}", "\t\t}"]
lines += ["\t}", "}"]
put("common/name_lists/00_cgen_azure_genesis.txt", "\n".join(lines) + "\n", True)
# 10 种界面语言都显示同一套中文名字
for lang in d["languages"]:
    content = "l_" + lang + ":\n" + "\n".join(" " + k + ":0 " + json.dumps(v, ensure_ascii=False) for k, v in loc.items()) + "\n"
    put("localisation/" + lang + "/cgen_names_l_" + lang + ".yml", content, True)

# ---------------------------------------------------------------- 审阅用文档（不进 MOD）
labels = {"corvette": "护卫舰", "destroyer": "驱逐舰", "cruiser": "巡洋舰", "battleship": "战列舰（无畏舰沿用）", "titan": "泰坦",
          "colossus": "巨像", "juggernaut": "主宰", "science": "科研船", "constructor": "工程船", "colonizer": "殖民船",
          "transport": "运输舰", "military_station_small": "防御平台", "ion_cannon": "离子加农炮", "auxiliary": "未单独定制的其他类型"}
review = ["# 苍神缘起帝国·名称总览", "", "由 tools/gen_names.py 从 tools/cgen_names_source.json 生成。参考观星者项目中的原创文明背景。", "",
          "人物固定使用 24 个部落姓，按部落主题组合个人名与长名，统一显示为“姓=名=长名”。男女和君主共用，无额外王朝姓氏。", "",
          "## 舰船与舰级", "", "| 舰种 | 舰级候选 | 舰名数／规则 |", "|---|---|---|"]
for g, vals in d["class_pools"].items():
    rule = d["ship_sequential"].get(g, str(len(d["ship_pools"].get(g, []))) + " 个名字")
    review.append("| " + labels[g] + " | " + "、".join(vals) + " | " + rule.replace("$C$", "数字编号") + " |")
review += ["", "巨像和主宰各 7 个舰级，是填写表明确指定的例外。科研船／工程船分别选择 2 个元素舰级，其余元素用作单艘船名。"
           "殖民船、运输舰、防御平台、离子炮和原版一样用具名舰名池，不用编号。", "",
           "本 MOD 的无畏舰写了 use_shipnames_from = battleship，舰名与舰级都沿用战列舰。", ""]
for g, vals in d["ship_pools"].items():
    review += ["### " + labels[g], "", "、".join(vals), ""]
review += ["## 人物姓名", "", f"共 {len(allnames):,} 个候选；每个部落同权重。以下列出构成部分，完整组合见 cgen_characters.txt。", ""]
for c in d["clans"]:
    review += ["### " + c["surname"] + "（" + c["theme"] + "）", "", "个人名：" + "、".join(c["given_names"]), "",
               "长名／称号：" + "、".join(c["epithets"]), "", "保留示例：" + "；".join(c["provided_examples"]), ""]
review += ["## 星球", "", "自然殖民地：" + "、".join(d["surname_order"]), "", "非自然殖民地额外候选：" + "、".join(d["artificial_planets"]), "",
           "## 舰队与陆军", "", "舰队：帝国第 1 舰队、帝国第 2 舰队……", "", "陆军：帝国第 1 军团、帝国第 2 军团……", "",
           "## 原创设定来源", "", d["source_repo"], ""]
DOCS.mkdir(parents=True, exist_ok=True)
(DOCS / "cgen_名称总览.md").write_text("\n".join(review), encoding="utf8", newline="\n")
(DOCS / "cgen_characters.txt").write_text("\n".join(allnames) + "\n", encoding="utf-8-sig", newline="\n")
print(f"generated name list {d['id']}: {len(allnames)} characters, {len(d['clans'])} clans, "
      f"{len(ship_routes)} ship types, {len(loc)} localisation keys x {len(d['languages'])} languages")
