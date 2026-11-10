import re, sys
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
def norm(line):
    line = re.sub(r"^\[[0-9:]+\]", "", line.strip())
    line = re.sub(r"\[([a-z_]+\.(?:cpp|h)):\d+\]", r"[\1]", line)
    line = re.sub(r"line: ?\d+|line \d+|column \d+", "line N", line)
    return line
def load(p):
    return Counter(norm(l) for l in open(p, encoding="utf-8", errors="replace") if l.strip())
base = load(sys.argv[1]); merged = load(sys.argv[2])
only_m = {k: v for k, v in merged.items() if k not in base and "Invalid supported_version" not in k}
only_b = {k: v for k, v in base.items() if k not in merged and "Invalid supported_version" not in k}
print(f"只在合并版出现：{sum(only_m.values())} 行（{len(only_m)} 种）")
for k, v in sorted(only_m.items(), key=lambda x: -x[1])[:40]:
    print(f"  {v:3d}  {k[:170]}")
print(f"\n只在基线出现（合并后消失）：{sum(only_b.values())} 行（{len(only_b)} 种）")
cats = Counter(re.sub(r"\[([a-z_]+\.(?:cpp|h))\].*", r"\1", k) for k in only_b)
for k, v in cats.most_common(10): print(f"  {v:3d}  {k}")
