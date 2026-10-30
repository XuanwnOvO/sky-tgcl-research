# -*- coding: utf-8 -*-
"""segD v23: Marker 引用目标对象字段解码. 目标 payload 首部有 pattern 00 X 00 (无ff邻域),
猜测 [00][compId:u8][00][levelId:u8 0..7][u24 递增字段][floats...].
dump 目标完整 payload + 统计 byte1 分布与 float 段."""
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

# 收集 Marker 引用目标
targets = set()
for j in bycomp["Marker"]:
    n, nid, V, ne, nxt = recs[j]
    pl = nxt - ne - 4
    for k in range(0, pl-8, 4):
        u = struct.unpack_from("<I", data, ne+4+k)[0]
        if u in relmap:
            targets.add(relmap[u])
print("Marker 引用目标数:", len(targets))

# byte1 分布 (payload[1])
b1 = Counter(); f404 = Counter()
for j in targets:
    n, nid, V, ne, nxt = recs[j]
    pl = nxt - ne - 4
    if pl < 2: continue
    b1[data[ne+1]] += 1
    # 找 00 00 40 后的 u8
    if pl >= 8 and data[ne+4:ne+7] == b"\x00\x00@":
        f404[data[ne+7]] += 1
print("目标 payload byte1 top:", b1.most_common(10))
print("00 00 40 后字节分布:", f404.most_common(10))

# dump 前5个目标
for j in sorted(targets)[:5]:
    n, nid, V, ne, nxt = recs[j]
    pl = nxt - ne - 4
    p = data[ne:nxt-4]
    print(f"\nrec{j} id={nid} V={V} plen={pl}\n  {p.hex(' ')}")
