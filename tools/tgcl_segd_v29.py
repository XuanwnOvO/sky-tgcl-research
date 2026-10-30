# -*- coding: utf-8 -*-
"""segD v29: 引用命中记录内部 — 精确到记录内位置 (rel_rec = u - rec_start_rel).
统计 rel_rec 分布; 检查 rel_rec 是否总指向 payload 或固定子结构 (如 payload+[0])."""
import re, struct, bisect
from collections import Counter

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
starts = sorted(((r[0]-4) - o4, j) for j, r in enumerate(recs))
keys = [s for s, _ in starts]

bycomp = {}
for j, (n, nid, V, ne, nxt) in enumerate(recs):
    pl = nxt - ne - 4
    if pl >= 4:
        f = struct.unpack_from("<I", data, ne)[0]
        if f < c1 and comps[f][0]:
            bycomp.setdefault(comps[f][0], []).append(j)

# 所有记录内 4对齐 u32 -> rel_rec 分布
rel_rec = Counter()
for (n, nid, V, ne, nxt) in recs:
    pl = nxt - ne - 4
    for k in range(0, pl-3, 4):
        u = struct.unpack_from("<I", data, ne+k)[0]
        t = bisect.bisect_right(keys, u) - 1
        if t >= 0:
            rel_rec[u - keys[t]] += 1
print("rel_rec 分布 top20:", rel_rec.most_common(20))
print("distinct rel_rec:", len(rel_rec), "total:", sum(rel_rec.values()))

# Marker 的 rel_rec 分布
mr = Counter()
for j in bycomp["Marker"]:
    n, nid, V, ne, nxt = recs[j]
    pl = nxt - ne - 4
    for k in range(4, pl-3, 4):
        u = struct.unpack_from("<I", data, ne+k)[0]
        t = bisect.bisect_right(keys, u) - 1
        if t >= 0:
            mr[u - keys[t]] += 1
print("Marker rel_rec top20:", mr.most_common(20))
