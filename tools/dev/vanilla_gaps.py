import re, sys, json, pathlib
sys.stdout.reconfigure(encoding="utf-8")
V = pathlib.Path(r"C:\Program Files (x86)\Steam\steamapps\common\Stellaris")
MOD = pathlib.Path(r"C:\Users\sol3u\Documents\GitHub\princess-expedition-ex\mod")
man = json.load(open(MOD.parent / "tools" / "upstream_manifest.json", encoding="utf-8"))["files"]
def keys(p):
    t = re.sub(r"#[^\n]*", "", p.read_text(encoding="utf-8-sig", errors="replace"))
    return set(re.findall(r"^([A-Za-z0-9_@\-]+)\s*=", t, re.M))
total = 0
for rel, v in sorted(man.items()):
    if v.get("binary") or not rel.endswith(".txt"): continue
    if not (V / rel).exists(): continue
    miss = sorted(keys(V / rel) - keys(MOD / rel))
    miss = [m for m in miss if not m.startswith("@")] + [m for m in miss if m.startswith("@")]
    if miss:
        total += len(miss)
        print(f"[{v['from'].split(':')[0]}] {rel}：原版有、上游版没有 {len(miss)} 个 -> {miss[:8]}")
print(f"\n合计 {total} 个")
