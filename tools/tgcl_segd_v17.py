# -*- coding: utf-8 -*-
"""segD v17: 换个思路 —— 引用 u32 是【节点名起点 - SEG_D + 4】还是【记录起点(V字段)-SEG_D】?
   之前 v15 delta=4 命中 64% 是在【含非对齐】的 tot 上. 现在统一测试多个公式:
   u32 = X. 检查 X 与每个节点记录特征偏移的差值匹配:
     F1: X = name_start - SEG_D          (名起点)
     F2: X = name_start - SEG_D - 4      (V 字段)
     F3: X = name_start - SEG_D + 4      (名后)
     F4: X = node id ? (小 id)
   并只在 4 对齐 u32 上统计."""
import re, struct, bisect
from collections import Counter

P = r"Children of the Light\Levels\Dawn\Objects.level.bin"
data = open(P, "rb").read()
o1, o2, o3, o4, o5 = struct.unpack_from("<5I", data, 24)
c1, c2, c3, c4 = struct.unpack_from("<4I", data, 8)
SEG_D, END = o4, o5

pat = re.compile(rb"BstNode_(\d+)\x00")
nodes = [(m.start(), int(m.group(1))) for m in pat.finditer(data, SEG_D)]
recs = []
for i, (n, nid) in enumerate(nodes):
    V = struct.unpack_from("<I", data, n-4)[0]
    ne = n + 8 + len(str(nid)) + 1
    nxt = nodes[i+1][0] if i+1 < len(nodes) else END - 4
    recs.append((n, nid, V, ne, nxt))
# 注意: name_start 不一定 4 对齐 (V 字段在 n-4, 一定对齐因为递推). 检查 n-4 对齐性:
print("record V-field 4-aligned:", all((r[0]-4-SEG_D)%4==0 for r in recs))
print("first rec n-4:", recs[0][0]-4-SEG_D)
# 记录起点相对 SEG_D: 0?
print("rel starts mod 4:", Counter((r[0]-4-SEG_D)%4 for r in recs))

# 候选公式: u32 = rec_start_rel (即 V 字段相对 segD)
relmap = {}
for r in recs:
    relmap[(r[0]-4)-SEG_D] = r
rels = sorted(relmap)
hit1 = hit2 = hit3 = tot = 0
for n,nid,V,ne,nxt in recs:
    pl = nxt-ne-4
    for off in range(0, pl-3, 4):
        u = struct.unpack_from("<I", data, ne+off)[0]
        tot += 1
        if u in relmap: hit1 += 1
        if u+4 in relmap: hit2 += 1
        if u>=4 and u-4 in relmap: hit3 += 1
print(f"u32 == rec_start_rel: {hit1}/{tot}   ==rec_start_rel-4: {hit3}/{tot}  ==rec_start_rel+4: {hit2}/{tot}")
