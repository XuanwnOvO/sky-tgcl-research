# -*- coding: utf-8 -*-
"""segD v46: Marker refs 最终判定.
Marker rec64 refs=[6646,9315,716,5531,2535,1747?] (rec-index解读, <11501)
Marker 组含 recs: 6646 ✓(V=4), 9315? 组里无 9315... 组里 V=42 记录在 1346, 但 9315 不在组里.
等等 rec64 k=8 ref=9315 -> recs[9315] V=42 plen=450 (selfLit 块) — 不在组 2753888 里.
但组里有 V=42 rec1346 id=2753888671 plen=453! 接近.
换个思路: refs = 【对象实例 id 的低 16 位】+ 常量?
Marker id=2753888733 & 0xFFFF = 0x1BDD? 2753888733 % 65536 = ?
id>>8=10757372? 2753888733 >> 8 = 10757370 低16位 = 2753888733>>8 & 0xFFFF.
refs 6646=0x19F6. 目标 rec6646 id=2753888672 >>8 = 10757370&0xFFFF? 
2753888672>>8 = 10757369 → 低16 = 0x19F9? 算算: 10757369 = 0xA419F9 → 低16=0x19F9≠0x19F6.
=> refs 可能 = id>>8 的低16位! 2753888672>>8=10757369=0xA419F9, 低16位 0x19F9, 但 ref=0x19F6.
接近但不等. 精确测试: refs[i] == (target_id>>8)&0xFFFF 对 rec-index 目标?"""
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
compIdx = {c[0]: i for i, c in enumerate(comps)}

pat = re.compile(rb"BstNode_(\d+)\x00")
nodes = [(m.start(), int(m.group(1))) for m in pat.finditer(data, o4)]
recs = []
for i, (n, nid) in enumerate(nodes):
    V = struct.unpack_from("<I", data, n-4)[0]
    ne = n + 8 + len(str(nid)) + 1
    nxt = nodes[i+1][0] if i+1 < len(nodes) else o5 - 4
    recs.append((n, nid, V, ne, nxt))
bycomp = {}
for j, (n, nid, V, ne, nxt) in enumerate(recs):
    pl = nxt - ne - 4
    if pl >= 4:
        f = struct.unpack_from("<I", data, ne)[0]
        if f < c1 and comps[f][0]:
            bycomp.setdefault(comps[f][0], []).append(j)

# 假设: ref = 目标记录 id>>8 的低16位. 遍历全部记录建 map: (id>>8)&0xFFFF -> list of recIdx
m16 = {}
for j, r in enumerate(recs):
    m16.setdefault((r[1] >> 8) & 0xFFFF, []).append(j)
hit = 0; tot = 0; exact = 0
for j in bycomp["Marker"]:
    n, nid, V, ne, nxt = recs[j]
    pl = nxt - ne - 4
    for k in range(4, pl-3, 4):
        u = struct.unpack_from("<I", data, ne+k)[0]
        if u == 0 or u == 0xFFFFFFFF: continue
        tot += 1
        cands = m16.get(u)
        if cands:
            hit += 1
            if len(cands) == 1: exact += 1
print(f"ref == (id>>8)&0xFFFF 命中: {hit}/{tot}, 唯一目标: {exact}")

# 更直接: V=4 记录里 u24@8 = id>>8. 那 V=7 Marker payload 的 u32 里,
# ref 0x19f6=6646 vs recs[6646].id=2753888672 >>8 = 10757369... 
# 不等. 那 ref 是什么? 试 ref == recs[t].id & 0xFFFF?
mid = {}
for j, r in enumerate(recs):
    mid.setdefault(r[1] & 0xFFFF, []).append(j)
h2 = 0
for j in bycomp["Marker"]:
    n, nid, V, ne, nxt = recs[j]
    pl = nxt - ne - 4
    for k in range(4, pl-3, 4):
        u = struct.unpack_from("<I", data, ne+k)[0]
        if u and u != 0xFFFFFFFF and u in mid: h2 += 1
print(f"ref == id&0xFFFF 命中: {h2}/{tot}")
