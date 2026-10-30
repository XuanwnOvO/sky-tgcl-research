# -*- coding: utf-8 -*-
"""segD v56: type 宽度定量收尾.
方法: 对每个组件, 若值内联则 plen ≈ 1(compIdx u8?) ... 但 compIdx 是 u32 4B.
更稳: V=7 记录 plen 固定的组件 + 其 propTypes → 解方程: 
plen = 4(compIdx u32) + Σ(width[type])
用多个固定 plen 组件联立解 width: type1=?, type4=?, type16=?, type64=?, type0=?
数据 (来自 v7/v54b):
CandleObject: plen=24, props 7×type1 + 3×type4 + 1×type64 → 20 = 7a+3b+1c
LevelMesh: plen=12, 38×1+11×4+3×16+1×64+8×0 → 8 = 38a+11b+3c+d (太约束!)
不对——LevelMesh plen=12 只有 2 refs, 说明【大多数 prop 是默认值, 不内联】!
=> 记录只存【非默认/修改过的属性】! Marker 4 props 全显式 → 6 u32.
这解释了矛盾: plen 因实例而异, 无法从 schema 预测. 但"24B矛盾"的原始说法是
"Marker 期望 40B transform 但值块 24B" — 因为根本不内联 transform, 是引用!
最终验证: 每个 type=16/64 的值是否总通过引用存储. 看 V=20 (346条 83B) — 这些是
LevelMesh transform 的实际存储? 检查某 LevelMesh 引用目标是否 V=20.
LevelMesh plen=12 = compIdx + 2 refs. refs[0], refs[1]. 目标是什么 V?"""
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

# LevelMesh 2 个 refs 的目标 V (rec-index 解读)
tv = Counter()
for j in bycomp["LevelMesh"]:
    n, nid, V, ne, nxt = recs[j]
    pl = nxt - ne - 4
    for k in range(4, pl-3, 4):
        u = struct.unpack_from("<I", data, ne+k)[0]
        if u < len(recs):
            tv[recs[u][2]] += 1
print("LevelMesh refs(rec-index) 目标 V:", tv.most_common(10))

# refs[0] 目标 = resourceName(字符串)? refs[1] = transform?
j = bycomp["LevelMesh"][0]
n, nid, V, ne, nxt = recs[j]
u0 = struct.unpack_from("<I", data, ne+4)[0]
u1 = struct.unpack_from("<I", data, ne+8)[0]
print(f"LevelMesh rec{j}: refs={u0},{u1}")
print("target0:", recs[u0][2], recs[u0][1], data[recs[u0][3]:recs[u0][4]-4][:60].hex(" "))
print("target1:", recs[u1][2], recs[u1][1], data[recs[u1][3]:recs[u1][4]-4][:60].hex(" "))
