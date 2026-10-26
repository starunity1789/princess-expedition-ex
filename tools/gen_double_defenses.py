"""把原版所有能量盾和装甲的数值翻倍。

用法：python gen_double_defenses.py <群星安装目录> <MOD 根目录> [倍率]

原理：原版 common/component_templates/ 里每一条 ship_armor_add / ship_shield_add 都写成
`= @变量`，没有一条写死数字（4.5.2 实测只有一行被注释掉的字面量）。这些变量又全部定义在
同一个文件 common/scripted_variables/02_scripted_variables_component_cost.txt 里。

所以这里不去碰庞大的组件文件，而是：
  1. 扫描 component_templates，收集被 ship_armor_add / ship_shield_add 引用的变量名；
  2. 读原版那一个 scripted_variables 文件，只把这些变量的值乘以倍率，其余原样保留；
  3. 整份写进 MOD 的同名路径，覆盖原版。

覆盖的范围包括常规护盾/装甲、灵能盾、暗物质偏导器、龙鳞装甲、天矿装甲、晶体装甲、
考古装甲/护盾、生物舰船的甲壳与护盾，以及太空生物（fauna）的装甲与护盾。

群星每次大版本更新后要重新跑一次，否则这份文件会把新版原版的其他数值一起冻结在旧值上。
"""
import re
import sys
from pathlib import Path

GAME = Path(sys.argv[1])
MOD = Path(sys.argv[2])
FACTOR = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0

REL = "common/scripted_variables/02_scripted_variables_component_cost.txt"
COMPONENTS = GAME / "common/component_templates"
SRC = GAME / REL

if not SRC.exists():
    sys.exit(f"找不到原版文件：{SRC}")

# 1. 收集被护盾/装甲引用的变量名
ref = re.compile(r"ship_(?:armor|shield)_add\s*=\s*@([A-Za-z0-9_]+)")
wanted: set[str] = set()
for f in sorted(COMPONENTS.glob("*.txt")):
    for line in f.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        if line.lstrip().startswith("#"):
            continue
        wanted.update(ref.findall(line))
if not wanted:
    sys.exit("没有在 component_templates 里找到任何 ship_armor_add / ship_shield_add 变量引用")

# 顺带检查有没有写死数字的漏网之鱼，有就报出来人工处理
literal = re.compile(r"ship_(?:armor|shield)_add\s*=\s*(-?[0-9]+(?:\.[0-9]+)?)\s*(?:#.*)?$")
strays = []
for f in sorted(COMPONENTS.glob("*.txt")):
    for i, line in enumerate(f.read_text(encoding="utf-8-sig", errors="replace").splitlines(), 1):
        if line.lstrip().startswith("#"):
            continue
        if literal.search(line.strip()):
            strays.append(f"{f.name}:{i}: {line.strip()}")

# 2. 逐行改写原版的 scripted_variables
assign = re.compile(r"^(@([A-Za-z0-9_]+)\s*=\s*)(-?[0-9]+(?:\.[0-9]+)?)(.*)$")


def scale(text: str) -> str:
    value = float(text) * FACTOR
    return str(int(value)) if value == int(value) and "." not in text else f"{value:g}"


out, hit = [], set()
for line in SRC.read_text(encoding="utf-8-sig").splitlines():
    m = assign.match(line)
    if m and m.group(2) in wanted:
        hit.add(m.group(2))
        out.append(f"{m.group(1)}{scale(m.group(3))}{m.group(4)}")
    else:
        out.append(line)

missing = sorted(wanted - hit)

header = [
    "# 皇女的远征军EX：原版能量盾与装甲数值翻倍",
    f"# 由 tools/gen_double_defenses.py 从原版 {REL} 生成，倍率 {FACTOR:g}，请勿手改。",
    "# 这是一份覆盖原版的同名文件：群星更新后必须用新版原版重新生成，",
    "# 否则文件里未改动的其他数值会被冻结在旧版本上。",
    f"# 本次翻倍的变量：{len(hit)} 个（常规护盾装甲、灵能盾、暗物质偏导器、龙鳞装甲、"
    "晶体/天矿/考古装甲、生物舰船与太空生物的护盾装甲）。",
    "",
]

dest = MOD / REL
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text("\n".join(header + out) + "\n", encoding="utf-8", newline="\n")

print(f"已写入 {dest}")
print(f"引用到的变量 {len(wanted)} 个，成功翻倍 {len(hit)} 个")
if missing:
    print("！这些变量在 scripted_variables 里没找到定义，需要人工确认：", ", ".join(missing))
if strays:
    print("！这些组件把护盾/装甲写成了字面量，没有被翻倍：")
    for s in strays:
        print("   ", s)
