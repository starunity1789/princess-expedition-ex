import re, sys, pathlib
from collections import Counter
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from planets import analyze, bucket
G = pathlib.Path(r"C:\Program Files (x86)\Steam\steamapps\workshop\content\281990\865040033\common\static_modifiers")
where = {}
for f in G.glob("*.txt"):
    for n in re.findall(r"^([A-Za-z0-9_]+)\s*=\s*\{", f.read_text(encoding="utf-8-sig", errors="replace"), re.M):
        where[n] = f.name.replace("gpm_static_modifiers_", "").replace(".txt", "")
def freq(p):
    _f, st = analyze(p); n = len(st); c = Counter(); cs = Counter()
    for pc, mods in st:
        for m in mods:
            if m.startswith("gpm_"):
                c[m] += 1
                if bucket(pc) == "恒星": cs[m] += 1
    return n, c, cs
n0, c0, s0 = freq(sys.argv[1])
olds = [freq(p) for p in sys.argv[2:]]
n1 = sum(o[0] for o in olds); c1 = sum((o[1] for o in olds), Counter()); s1 = sum((o[2] for o in olds), Counter())
# 按来源文件汇总：每千颗星球的修正数
agg0, agg1 = Counter(), Counter()
for m, v in c0.items(): agg0[where.get(m, "?")] += v
for m, v in c1.items(): agg1[where.get(m, "?")] += v
print("按 GPM 修正所在文件汇总（每千颗星球）：")
print(f"  {'文件':28s} {'原版':>7s} {'现在':>7s}")
for k in sorted(set(agg0) | set(agg1), key=lambda k: -(agg1[k] / n1)):
    a, b = agg1[k] / n1 * 1000, agg0[k] / n0 * 1000
    flag = "  ← 少了" if b < a * 0.6 and a > 5 else ""
    print(f"  {k:28s} {a:7.1f} {b:7.1f}{flag}")
print("\n现在完全没出现、原版每千颗 ≥5 个的修正：")
for m, v in sorted(c1.items(), key=lambda x: -x[1]):
    if m not in c0 and v / n1 * 1000 >= 5:
        print(f"  {v / n1 * 1000:6.1f}  {m}  ({where.get(m, '?')})")
