import re
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")


def block_after(text, start):
    """text[start] 起找到第一个 { 并返回到配对 } 的内容"""
    i = text.index("{", start)
    d = 0
    for j in range(i, len(text)):
        c = text[j]
        if c == "{":
            d += 1
        elif c == "}":
            d -= 1
            if d == 0:
                return text[i + 1:j]
    raise ValueError


def analyze(path):
    t = open(path, encoding="utf-8", errors="replace").read()
    fm = re.search(r"^flags=\n", t, re.M)
    flags = sorted(set(re.findall(r"^\t(gpm_[a-z_]+)=", block_after(t, fm.end()), re.M)))
    pm = re.search(r"^planets=\n", t, re.M)
    planets = block_after(t, pm.end())
    inner = block_after(planets, re.search(r"^\tplanet=\n", planets, re.M).end())
    entries = re.split(r"\n\t\t(?=\d+=\n\t\t\{)", inner)
    stats = []
    for e in entries:
        m = re.search(r'\bplanet_class="([^"]+)"', e)
        if m:
            stats.append((m.group(1), re.findall(r'modifier="([^"]+)"', e)))
    return flags, stats


def bucket(pc):
    if "asteroid" in pc:
        return "小行星"
    if any(x in pc for x in ("_star", "black_hole", "neutron", "pulsar")):
        return "恒星"
    if "gas_giant" in pc:
        return "气态巨星"
    if pc in ("pc_barren", "pc_barren_cold", "pc_molten", "pc_frozen", "pc_toxic", "pc_nuked",
              "pc_broken", "pc_shattered"):
        return "原版不宜居"
    if pc.startswith("pc_pd_"):
        return "PD 新类型"
    return "原版宜居/其他"


if __name__ == "__main__":
    labels = ["现在（整合版，2200.02）", "原版 GPM 局 6（2200.08）", "原版 GPM 局 2（2201.01）"]
    for label, p in zip(labels, sys.argv[1:]):
        flags, st = analyze(p)
        n = len(st)
        g = [sum(1 for x in m if x.startswith("gpm_")) for _, m in st]
        withg = sum(1 for x in g if x)
        print(f"\n===== {label} =====")
        print(f"星球 {n} 颗；带 GPM 修正 {withg} 颗（{withg / n:.0%}）；GPM 修正共 {sum(g)} 个，平均每颗 {sum(g) / n:.2f}")
        print("GPM 全局旗标:", ", ".join(flags) or "（无）")
        by = defaultdict(lambda: [0, 0, 0])
        for (pc, _m), k in zip(st, g):
            b = by[bucket(pc)]
            b[0] += 1
            b[1] += 1 if k else 0
            b[2] += k
        for b, (cnt, w, tot) in sorted(by.items(), key=lambda x: -x[1][0]):
            print(f"   {b:14s} {cnt:5d} 颗  带修正 {w / cnt:5.0%}  平均 {tot / cnt:.2f}")
