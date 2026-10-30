# -*- coding: utf-8 -*-
"""segD v22: 解析组件索引记录(V=7)中每个 u32 引用的目标记录, dump 目标.
Marker: 6 refs; LevelMesh: 2 refs; DialogHintTimed: 3 refs"""
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
rows = []
for j in range(c2):
    a, ko, t, e = struct.unpack_from("<4I", data, o2 + j*16)
    rows.append((a, s3(ko), t, e))

pat = re.compile(rb"BstNode_(\d+)\x00")
nodes = [(m.start(), int(m.group(1))) for m in pat.finditer(data, o4)]
recs = []
for i, (n, nid) in enumerate(nodes):
    V = struct.unpack_from("<I", data, n-4)[0]
    ne = n + 8 + len(str(nid)) + 1
    nxt = nodes[i+1][0] if i+1 < len(nodes) else o5 - 4
    recs.append((n, nid, V, ne, nxt))
relmap = {(r[0]-4) - o4: j for j, r in enumerate(recs)}
# 记录内部任意字节位置 -> 记录索引 (pos_rel = abs - 4 - o4 内即可)
posmap = {}
for j, (n, nid, V, ne, nxt) in enumerate(recs):
    posmap[(n-4) - o4] = j

def where(u):
    j = relmap.get(u)
    if j is not None:
        return ("recStart", j)
    # 找包含该相对偏移的记录
    import bisect
    keys = sorted(posmap)
    k = bisect.bisect_right(keys, u) - 1
    if k >= 0:
        j = posmap[keys[k]]
        n, nid, V, ne, nxt = recs[j]
        rel = u - keys[k]
        tag = "V" if rel < 4 else ("name" if rel < (ne-4) - o4 - keys[k] + (ne - (n-4)) else "payload/tail")
        return ("inside", j, rel, tag)
    return (None,)

bycomp = {}
for j, (n, nid, V, ne, nxt) in enumerate(recs):
    pl = nxt - ne - 4
    if pl >= 4:
        f = struct.unpack_from("<I", data, ne)[0]
        if f < c1 and comps[f][0]:
            bycomp.setdefault(comps[f][0], []).append(j)

def trace(cn, cnt=4):
    print(f"\n=== {cn} ===")
    for j in bycomp[cn][:cnt]:
        n, nid, V, ne, nxt = recs[j]
        pl = nxt - ne - 4
        us = [struct.unpack_from("<I", data, ne+4+k)[0] for k in range(0, pl-4, 4) if pl-4-k >= 4]
        print(f"rec{j} id={nid} V={V} plen={pl} refs={[hex(u) for u in us]}")
        for u in us:
            print("   ", hex(u), where(u))

for cn in ["Marker", "LevelMesh", "DialogHintTimed", "CandleObject"]:
    trace(cn)
