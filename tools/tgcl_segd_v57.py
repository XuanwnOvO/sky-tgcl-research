# -*- coding: utf-8 -*-
"""segD v57: V=2 记录 = 对象主值块 (335..1238B, 802条).
V=2 样本 (LevelMesh 引用目标): 
01 01 00 00 00 00 00 00 cd cc cc 3d ... 
cd cc cc 3d = 0.1f! 00 00 80 3f x3 = scale(1,1,1) — transform 内联在 V=2!
=> V=2 = 【对象的完整属性值块】(LevelMesh 等所有组件的值内联)
=> V=7 = 【组件槽声明】(compIdx + 指向 V=2 值块等子记录的引用)
这解释一切: Marker(V=7) 28B = [compIdx=6][6 个子记录索引引用]
值在引用目标中. transform/scale/quat/pos 都存在别处!
验证: Marker refs 目标 (V=6:49B x79次, V=2, V=4, ...) 中找 scale(1,1,1)/quat.
V=6 记录 1917 条固定 49B — dump 2 条看结构. 49B: 可能 = [.. pos(12) scale(12) quat(16)..]=40+9?"""
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
bycomp = {}
for j, (n, nid, V, ne, nxt) in enumerate(recs):
    pl = nxt - ne - 4
    if pl >= 4:
        f = struct.unpack_from("<I", data, ne)[0]
        if f < c1 and comps[f][0]:
            bycomp.setdefault(comps[f][0], []).append(j)

# Marker 第一个的 refs 目标
j = bycomp["Marker"][0]
n, nid, V, ne, nxt = recs[j]
pl = nxt - ne - 4
refs = [struct.unpack_from("<I", data, ne+k)[0] for k in range(4, pl-3, 4)]
print(f"Marker rec{j} refs: {refs}")
for u in refs[:3]:
    if u < len(recs):
        t = recs[u]
        print(f"  -> rec{u} V={t[2]} plen={t[4]-t[3]-4}")
        print("   ", data[t[3]:t[4]-4].hex(" "))

# V=6 样本 2条
c6 = 0
for (n, nid, V, ne, nxt) in recs:
    if V == 6 and c6 < 2:
        print(f"\nV=6 rec plen=49:", data[ne:nxt-4].hex(" "))
        c6 += 1
