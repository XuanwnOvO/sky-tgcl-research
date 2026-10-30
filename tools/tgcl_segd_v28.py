# -*- coding: utf-8 -*-
"""segD v28: Marker refs 值都 < 0x3000 但没命中 relmap, 会命中 records 区间吗?
其实 rec_start_rel 分布在 0..0x2xxxx (SEG_D 大小~121KB). relmap 命中率只有0? 之前是65%!
之前relmap是用全部 4对齐u32测的. 但 Marker 的 k=4..24 这6个u32不命中 relmap?
检查: rec_start_rel 集合大小 = 11501; Marker refs 是 0x19f6=6654 等, relmap 有无 6654?
另外用"记录区间"测试这些 refs 的落点."""
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
relmap = {(r[0]-4) - o4: j for j, r in enumerate(recs)}
starts = sorted(((r[0]-4) - o4, j) for j, r in enumerate(recs))
keys = [s for s, _ in starts]

bycomp = {}
for j, (n, nid, V, ne, nxt) in enumerate(recs):
    pl = nxt - ne - 4
    if pl >= 4:
        f = struct.unpack_from("<I", data, ne)[0]
        if f < c1 and comps[f][0]:
            bycomp.setdefault(comps[f][0], []).append(j)

res = Counter()
for j in bycomp["Marker"]:
    n, nid, V, ne, nxt = recs[j]
    pl = nxt - ne - 4
    for k in range(4, pl-3, 4):
        u = struct.unpack_from("<I", data, ne+k)[0]
        if u in relmap: res["recStart"] += 1
        else:
            t = bisect.bisect_right(keys, u) - 1
            if t >= 0:
                sj, tj = starts[t]
                res["inside"] += 1
                res[f"inV{recs[tj][2]}"] += 1
            else:
                res["miss"] += 1
print("Marker refs 落点:", res.most_common(20))

# 试: rel_off+1? 引用可能指向 name 内部 = 目标记录的 BstNode_xxx id 起点
# 记录起点(V) 到 name 间隔 4B. 若 ref 指向 id 文本起点, rel = recstart+4
res2 = Counter()
for j in bycomp["Marker"]:
    n, nid, V, ne, nxt = recs[j]
    pl = nxt - ne - 4
    for k in range(4, pl-3, 4):
        u = struct.unpack_from("<I", data, ne+k)[0]
        for d in range(-8, 9):
            if u - d in relmap:
                res2[d] += 1
print("Marker refs relmap delta 分布:", res2.most_common(10))
