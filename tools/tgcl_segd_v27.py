# -*- coding: utf-8 -*-
"""segD v27: 根模板 + 各记录真实引用.
1) BstNode_2310602845 完整解析 (V=0, payload)
2) Marker 6 引用中非根模板的目标 dump
3) 引用值 -> 相对 [payload 起点还是 V 起点] 再验证, 分辨 root-ref vs data-ref"""
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

# 根模板位置
root_rel = None
for j, (n, nid, V, ne, nxt) in enumerate(recs):
    if nid == 2310602845:
        root_rel = (n-4) - o4
        print(f"ROOT rec{j} V={V} rel=0x{root_rel:x} plen={nxt-ne-4}")
        print("payload:", data[ne:nxt-4].hex(" "))
        break

# Marker 引用目标追踪 (排除 root)
bycomp = {}
for j, (n, nid, V, ne, nxt) in enumerate(recs):
    pl = nxt - ne - 4
    if pl >= 4:
        f = struct.unpack_from("<I", data, ne)[0]
        if f < c1 and comps[f][0]:
            bycomp.setdefault(comps[f][0], []).append(j)

for j in bycomp["Marker"][:3]:
    n, nid, V, ne, nxt = recs[j]
    pl = nxt - ne - 4
    for k in range(4, pl-3, 4):
        u = struct.unpack_from("<I", data, ne+k)[0]
        t = relmap.get(u)
        if t is None:
            print(f"rec{j} k={k} ref=0x{u:x} NO-MATCH")
        elif recs[t][1] == 2310602845:
            pass
        else:
            tn, tnid, tV, tne, tnxt = recs[t]
            print(f"rec{j} k={k} ref=0x{u:x} -> rec{t} id={tnid} V={tV} plen={tnxt-tne-4}")
            print("   payload:", data[tne:tnxt-4].hex(" "))

# 全文件非 root 引用统计
nonroot = Counter(); nonroot_targetV = Counter()
for j, (n, nid, V, ne, nxt) in enumerate(recs):
    pl = nxt - ne - 4
    for k in range(0, pl-3, 4):
        u = struct.unpack_from("<I", data, ne+k)[0]
        t = relmap.get(u)
        if t is None or recs[t][1] == 2310602845: continue
        nonroot[t] += 1
        nonroot_targetV[recs[t][2]] += 1
print("\n非root引用总数:", sum(nonroot.values()), "独立目标:", len(nonroot))
print("非root 目标V分布:", nonroot_targetV.most_common(15))
print("被引用最多目标:", nonroot.most_common(5))
