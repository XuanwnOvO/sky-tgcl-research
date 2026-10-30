# -*- coding: utf-8 -*-
"""segD v43: V=4 解码突破!
payload: 00 [u16 off?] 00 00 00 [b6:0/1] [b7] [b8=idx] [u16 const] 00
u16@1 递增! (0x2cf0=11440, 0xf34, 0x1692, 0x2cf8, 0x1c2d, 0x2d01...) 这些像【segD 相对偏移】!
const@9: u16@9: 0x6dd7, 0xc9be, 0xa808, 0x72d8, 0x7ccb...  也可疑.
重新读: p[0]=00, p[1:3]=u16A, p[3:6]=000000, p[6]=flag, p[7], p[8], p[9:11]=u16B, p[11]=00
检查 u16A 是否命中记录起点 rel (relmap). u16B 命中什么?"""
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
relmap = {(r[0]-4) - o4: j for j, r in enumerate(recs)}

v4 = [(nid, data[ne:nxt-4]) for (n, nid, V, ne, nxt) in recs if V == 4]
hA = 0; hB = 0
bv = Counter()
for nid, p in v4:
    A = struct.unpack_from("<H", p, 1)[0]
    B = struct.unpack_from("<H", p, 9)[0]
    if A in relmap: hA += 1
    if B in relmap: hB += 1
    bv[B] += 1
print(f"u16@1 命中 relmap: {hA}/{len(v4)}")
print(f"u16@9 命中 relmap: {hB}/{len(v4)}")
print("u16@9 常量分布 top10:", bv.most_common(10))
# 命中目标统计
tv = Counter()
for nid, p in v4:
    A = struct.unpack_from("<H", p, 1)[0]
    if A in relmap:
        tv[recs[relmap[A]][2]] += 1
print("u16@1 目标 V 分布:", tv.most_common(10))
