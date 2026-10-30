# -*- coding: utf-8 -*-
"""segD v24: 直接 dump Marker 引用目标点周围 48B, 判断被指字节是什么.
同时验证: 引用可能指向 [记录内某子块的起点], 子块自身格式 = [u32 ?][...]."""
import re, struct
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
bycomp = {}
for j, (n, nid, V, ne, nxt) in enumerate(recs):
    pl = nxt - ne - 4
    if pl >= 4:
        f = struct.unpack_from("<I", data, ne)[0]
        if f < c1 and comps[f][0]:
            bycomp.setdefault(comps[f][0], []).append(j)

# V 字段起点 rel = n-4-o4; 记录占 [start, nxt)
starts = sorted((r[0]-4) - o4 for r in recs)
import bisect
def owner(u):
    k = bisect.bisect_right(starts, u) - 1
    return k

for j in bycomp["Marker"][:2]:
    n, nid, V, ne, nxt = recs[j]
    pl = nxt - ne - 4
    for k in range(0, pl-8, 4):
        u = struct.unpack_from("<I", data, ne+4+k)[0]
        t = owner(u)
        if t is None:
            print(hex(u), "OOM"); continue
        rj = starts[t]
        rn, rid, rV, rne, rnxt = recs[t]
        chunk = data[rj+o4+u : rj+o4+u+40]
        print(f"rec{j}.{k} ref=0x{u:x} -> rec{t}(V={rV},id={rid}) rel_off={u-rj} ctx={chunk.hex(' ')}")
    print()

# 另一个假设: u32 不是引用, 是组件行号/键id? 统计全部 Marker u32 值域
vals = []
for j in bycomp["Marker"]:
    n, nid, V, ne, nxt = recs[j]
    pl = nxt - ne - 4
    for k in range(4, pl-3, 4):
        vals.append(struct.unpack_from("<I", data, ne+k)[0])
print("Marker u32 值域: min", min(vals), "max", max(vals), "count", len(vals))
print("mod 261:", Counter(v % 261 for v in vals).most_common(5))
