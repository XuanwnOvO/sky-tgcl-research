# -*- coding: utf-8 -*-
"""segD v30: 引用精确语义.
假设: u32 引用 rel = u - rec_start_rel, 且多数应落在 payload 起点 (rel = ne - start).
检查全局 rel_rec 中落在 [4, 4+namelen) (名字区) vs [payload) 的比例,
以及引用是否总指向 payload 的 4 对齐偏移 (rel 对齐 payload 起点对齐?)."""
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

# 命中位置分区: 0=V字段, 1..4+namelen-1=名字区, >=4+namelen=payload区(含尾)
zone = Counter()
namez = Counter()
payz = Counter()
for (n, nid, V, ne, nxt) in recs:
    pl = nxt - ne - 4
    for k in range(0, pl-3, 4):
        u = struct.unpack_from("<I", data, ne+k)[0]
        t = bisect.bisect_right(keys, u) - 1
        if t < 0: continue
        rel = u - keys[t]
        j = starts[t][1]
        rn, rid, rV, rne, rnxt = recs[j]
        nsz = 8 + len(str(rid)) + 1
        if rel < 4: zone["V"] += 1
        elif rel < 4 + nsz: zone["name"] += 1
        elif rel < (rnxt-4) - o4 - keys[t]: zone["payload"] += 1; payz[rel - (4+nsz)] += 1
        else: zone["tail"] += 1
print(zone.most_common())
print("payload 内偏移 top15:", payz.most_common(15))
