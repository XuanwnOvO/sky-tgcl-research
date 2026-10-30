# -*- coding: utf-8 -*-
"""segD v39: rec-index 假设非常强(476/480). 但 4 个超界可能是别的字段.
检验: rec-index 是否稳定 — 同一 u32 值在不同 Marker 中是否指向同类记录?
更严格: refs 指向的记录 id 前缀模式 (2753888xxx 同 Marker id 2753888733 接近!)
=> id 是【对象实例 id】! Marker id=2753888733, 引用目标 id=2753888672/2753888852...
前缀 2753888 相同! 这些是同一【对象】的组件/子值!
=> 引用 = 【节点 id (10位大数)】? 不, refs 值 0x19f6=6646 是 rec index.
=> 或者 id 前缀编码对象, recs[6646].id 与 Marker.id 高位相同 = 同对象.
验证: 统计 Marker rec 与其 refs 目标 rec 的 id 高 20bit 相同比例."""
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

same_hi = 0; tot = 0; vv = Counter()
for j in bycomp["Marker"]:
    n, nid, V, ne, nxt = recs[j]
    pl = nxt - ne - 4
    hi = nid >> 12
    for k in range(4, pl-3, 4):
        u = struct.unpack_from("<I", data, ne+k)[0]
        if u >= len(recs): continue
        tot += 1
        t = recs[u]
        vv[t[2]] += 1
        if (t[1] >> 12) == hi:
            same_hi += 1
print(f"id 高位相同: {same_hi}/{tot}")
print("目标 V 分布:", vv.most_common(15))

# 目标 V=4 (12B) 记录数 & 全文件 V=4 记录数
n4 = sum(1 for r in recs if r[2]==4)
print("全文件 V=4 记录:", n4)
# V=42 记录
n42 = sum(1 for r in recs if r[2]==42)
print("全文件 V=42 记录:", n42)
