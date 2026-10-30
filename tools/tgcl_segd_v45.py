# -*- coding: utf-8 -*-
"""segD v45: 对象组模型确立. 现在把整个 segD 按 id>>8 分组,
看一个组里有哪些 V 类型 — 验证【一个对象 = 一组记录, 共享 id 高位】.
并解决 Marker 矛盾: Marker 组件值块 (V=7) 的 6 个 u32 引用 = ?
之前 rec-index 假设 476/480 <11501. 但 id 前缀模型更合理:
Marker rec64 id=2753888733, 目标 id=2753888672 (同组 2753888).
refs 值 0x19f6=6646 — 与 id 无直接关系. 但 476/480 值 < 11501 太巧.
替代解释: refs = 【组内成员的记录序号】? 或【对象内字段 offset】?
决定性测试: 同一 Marker 的 refs 是否都指向【同 id>>8 组】的记录?
用 rec-index 解读: recs[u] 的 id>>8 == Marker.id>>8 的比例 (之前 237/476 = 50%). 50%一般.
另一测试: refs 是否 = 组内第几个记录? 找 Marker 所在组的全部记录序号, 看 refs 是否在其中."""
import re, struct
from collections import Counter, defaultdict

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
bycomp = {}
for j, (n, nid, V, ne, nxt) in enumerate(recs):
    pl = nxt - ne - 4
    if pl >= 4:
        f = struct.unpack_from("<I", data, ne)[0]
        if f < c1 and comps[f][0]:
            bycomp.setdefault(comps[f][0], []).append(j)

groups = defaultdict(list)
for j, r in enumerate(recs):
    groups[r[1] >> 8].append(j)

# Marker: refs (rec-index 解读) 是否落在同组?
ing = 0; tot = 0
for j in bycomp["Marker"]:
    n, nid, V, ne, nxt = recs[j]
    pl = nxt - ne - 4
    g = groups[nid >> 8]
    gset = set(g)
    for k in range(4, pl-3, 4):
        u = struct.unpack_from("<I", data, ne+k)[0]
        if u >= len(recs): continue
        tot += 1
        if u in gset: ing += 1
print(f"Marker refs(rec-index) 落在同 id>>8 组: {ing}/{tot}")
# 组大小分布
gs = Counter(len(v) for v in groups.values())
print("组大小分布 top:", gs.most_common(8))
# Marker 组样例
j = bycomp["Marker"][0]
g = groups[recs[j][1] >> 8]
print("Marker 组成员 (recIdx,V,id,plen):")
for m in g:
    print("  ", m, recs[m][2], recs[m][1], recs[m][4]-recs[m][3]-4)
