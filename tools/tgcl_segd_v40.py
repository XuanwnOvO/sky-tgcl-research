# -*- coding: utf-8 -*-
"""segD v40: 结构全景统计.
1) 每个 V 值: 记录数, plen 最小/最大/众数
2) refs as rec-index 全组件验证: 所有 V=7 组件值块的 u32 (<11501) 用 rec-index 解读,
   看"目标 id 高位与源相同"的比例 (按组件分)
3) id 结构: 10位 id = (objId<<12 | localId)? 统计 id>>12 的 distinct 数 vs c4=42919"""
import re, struct
from collections import Counter, defaultdict

P = r"Children of the Light\Levels\Dawn\Objects.level.bin"
data = open(P, "rb").read()
o1, o2, o3, o4, o5 = struct.unpack_from("<5I", data, 24)
c1, c2, c3, c4 = struct.unpack_from("<4I", data, 8)
segC = data[o3:o4]
def s3(u):
    e = segC.find(b"\x00", u)
    return segC[u:e].decode("utf-8", "replace")
comps = []
for i in range(c1):
    a, st, pc = struct.unpack_from("<3I", data, o1 + i*12)
    comps.append((s3(a), st, pc))

pat = re.compile(rb"BstNode_(\d+)\x00")
nodes = [(m.start(), int(m.group(1))) for m in pat.finditer(data, o4)]
recs = []
for i, (n, nid) in enumerate(nodes):
    V = struct.unpack_from("<I", data, n-4)[0]
    ne = n + 8 + len(str(nid)) + 1
    nxt = nodes[i+1][0] if i+1 < len(nodes) else o5 - 4
    recs.append((n, nid, V, ne, nxt))

# 1) V 全景
byv = defaultdict(list)
for (n, nid, V, ne, nxt) in recs:
    byv[V].append(nxt - ne - 4)
print("V 全景 (V: n, plen min/max):")
for V in sorted(byv):
    L = byv[V]
    c = Counter(L)
    print(f"  V={V}: n={len(L)} plen {min(L)}..{max(L)} 众数 {c.most_common(2)}")

# 2) id>>12 distinct
hi = set(r[1] >> 12 for r in recs)
print("\nid>>12 distinct:", len(hi), " (c4=", c4, ")")
# 3) 位移扫描: 找 s 使 distinct(id>>s) 最接近 42919
for s in range(4, 20):
    d = len(set(r[1] >> s for r in recs))
    if abs(d - c4) < c4 * 0.5:
        print(f"id>>{s}: {d}")
