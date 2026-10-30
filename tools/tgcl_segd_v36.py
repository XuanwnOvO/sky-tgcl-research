# -*- coding: utf-8 -*-
"""segD v36: 修正引用假设 — 之前 v17 的 30% 命中其实是 relmap 含 root(0)+巧合?
重新精确验证: rec_start_rel 是 (n-4)-o4. 检查 rec 起点值范围: max(rel)?
若 max rel > 0x3000, Marker refs (<0x3000) 只能指向文件开头部分记录.
统计 rec_start_rel 分布: 有多少 < 0x3000? 与 476 个 refs 的分布比较."""
import re, struct
from collections import Counter

P = r"Children of the Light\Levels\Dawn\Objects.level.bin"
data = open(P, "rb").read()
o1, o2, o3, o4, o5 = struct.unpack_from("<5I", data, 24)
c1, c2, c3, c4 = struct.unpack_from("<4I", data, 8)

pat = re.compile(rb"BstNode_(\d+)\x00")
nodes = [(m.start(), int(m.group(1))) for m in pat.finditer(data, o4)]
recs = []
for i, (n, nid) in enumerate(nodes):
    V = struct.unpack_from("<I", data, n-4)[0]
    ne = n + 8 + len(str(nid)) + 1
    nxt = nodes[i+1][0] if i+1 < len(nodes) else o5 - 4
    recs.append((n, nid, V, ne, nxt))
starts_rel = sorted((r[0]-4) - o4 for r in recs)
print("rec_start_rel: min", starts_rel[0], "max", starts_rel[-1], "count", len(starts_rel))
print("< 0x3000 的记录数:", sum(1 for s in starts_rel if s < 0x3000))
print("前30个:", [hex(s) for s in starts_rel[:30]])

# Marker refs 的值分布
segC = data[o3:o4]
def s3(u):
    e = segC.find(b"\x00", u)
    return segC[u:e].decode("utf-8", "replace")
comps = []
for i in range(c1):
    a, st, pc = struct.unpack_from("<3I", data, o1 + i*12)
    comps.append((s3(a), st, pc))
bycomp = {}
for j, (n, nid, V, ne, nxt) in enumerate(recs):
    pl = nxt - ne - 4
    if pl >= 4:
        f = struct.unpack_from("<I", data, ne)[0]
        if f < c1 and comps[f][0]:
            bycomp.setdefault(comps[f][0], []).append(j)
rv = []
for j in bycomp["Marker"]:
    n, nid, V, ne, nxt = recs[j]
    pl = nxt - ne - 4
    for k in range(4, pl-3, 4):
        rv.append(struct.unpack_from("<I", data, ne+k)[0])
print("Marker refs: min", min(rv), "max", max(rv))
print("值样例:", [hex(x) for x in rv[:20]])
