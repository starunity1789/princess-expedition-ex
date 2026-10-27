"""把内置的两套肖像包挂进原版的 portrait_sets。

用法：python gen_portrait_sets.py <群星安装目录> <MOD 根目录>

为什么要这样做：两个原包各自在 common/portrait_sets/ 下用 mammalians、reptilians 这类
原版已有的集合名另开文件。实测在 4.5.2 下不生效，游戏日志报

    portrait 'kmpp_kemonomimi' for the class 'MAM' is not found in portrait set database

改成新集合名（kmpp_mammalians 等）再注册进 portrait_categories 也一样没用。
最后采用最稳的做法：整文件覆盖原版 00_portrait_sets.txt，把肖像组直接追加进原版
已有的那几个集合的 portraits 列表里——这些集合原版一定会读，也已经挂在对应分类下。

群星每次大版本更新后要重新跑一次。
"""
import re
import sys
from pathlib import Path

GAME = Path(sys.argv[1])
MOD = Path(sys.argv[2])
REL = "common/portrait_sets/00_portrait_sets.txt"

# 原版集合名 -> 要追加的肖像组
ADD = {
    "mammalians": ["kmpp_kemonomimi"],
    "machines": ["kmpp_kemonomimi_machine"],
    "robots": ["kmpp_kemonomimi_machine"],
    "reptilians": ["adpp_ancient_dragonkin"],
    "infernals": ["adpp_ancient_dragonkin_inf"],
}

src = GAME / REL
if not src.exists():
    sys.exit(f"找不到原版文件：{src}")
text = src.read_text(encoding="utf-8-sig", newline="")
nl = "\r\n" if "\r\n" in text else "\n"

done = []
for setname, groups in ADD.items():
    # 定位该集合块里的第一个 portraits = { ... }，在它的收尾花括号前插入
    block = re.compile(
        rf"(?ms)^{re.escape(setname)}\s*=\s*\{{.*?^\tportraits\s*=\s*\{{(?P<body>.*?)^\t\}}")
    m = block.search(text)
    if not m:
        sys.exit(f"原版 {REL} 里找不到集合 {setname} 的 portraits 列表，需人工确认")
    already = [g for g in groups if re.search(rf'"{re.escape(g)}"', m.group("body"))]
    todo = [g for g in groups if g not in already]
    if not todo:
        continue
    ins = "".join(f'\t\t"{g}"{nl}' for g in todo)
    text = text[: m.end("body")] + ins + text[m.end("body"):]
    done.append(f"{setname} += {', '.join(todo)}")

header = (
    f"# 皇女的远征军EX：覆盖原版 {REL}，把内置的两套肖像包挂进原版已有的集合。{nl}"
    f"# 由 tools/gen_portrait_sets.py 生成，请勿手改；群星更新后用新版原版重新生成。{nl}"
    f"# 相对原版新增的内容：{'；'.join(done)}{nl}"
    f"{nl}"
)
dest = MOD / REL
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(header + text, encoding="utf-8", newline="")

print(f"已写入 {dest}")
for d in done:
    print("  ", d)
