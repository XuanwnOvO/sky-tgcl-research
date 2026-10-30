# -*- coding: utf-8 -*-
"""segD v9: 节点 id -> 记录索引; V=7 记录的 k1/k2 验证为节点引用; Marker 值 6×u32 含义"""
import re, struct
from collections import Counter, defaultdict

P = r"Children of the Light\Levels\Dawn\Objects.level.bin"
data = open(P, "rb").read()
o1, o2, o3, o4, o5 = struct.unpack_from("<5I", data, 24)
c1, c2, c3, c4 = struct.unpack_from("<4I", data, 8)
SEG_D, END = o4, o5

comps = []
segC = data[o3:o4]
def s3(u):
    e = segC.find(b"\x00", u); return segC[u:e].decode()
for i in range(c1):
    a, st, pc = struct.unpack_from("<3I", data, o1 + i*12)
    comps.append((s3(a), st, pc))

pat = re.compile(rb"BstNode_(\d+)\x00")
nodes = [(m.start(), int(m.group(1))) for m in pat.finditer(data, SEG_D)]
recs = []
for i, (n, nid) in enumerate(nodes):
    V = struct.unpack_from("<I", data, n-4)[0]
    ne = n + 8 + len(str(nid)) + 1
    nxt = nodes[i+1][0] if i+1 < len(nodes) else END - 4
    recs.append((n, nid, V, ne, nxt))

idset = set(r[1] for r in recs)
# id -> 记录序号(文件顺序)
idorder = {r[1]: i for i, r in enumerate(recs)}

# V=7 记录: (compIdx, k1, k2) -> k1/k2 是否节点 id
v7 = []
for n, nid, V, ne, nxt in recs:
    pl = nxt - ne - 4
    if V == 7 and pl >= 12:
        ci, k1, k2 = struct.unpack_from("<3I", data, ne)
        if ci < c1 and comps[ci][0]:
            v7.append((nid, ci, k1, k2, pl))
print("V7 comp recs:", len(v7))
print("k1 in idset:", sum(1 for x in v7 if x[2] in idset), "/", len(v7))
print("k2 in idset:", sum(1 for x in v7 if x[3] in idset), "/", len(v7))
# 若不是 id, 是否是记录序号 0..11500?
print("k1 < 11501:", sum(1 for x in v7 if x[2] < 11501), " k2 < 11501:", sum(1 for x in v7 if x[3] < 11501))
# 序号验证: rec[k1] 的 id 是否与某节点匹配 -> 打印样例
for nid, ci, k1, k2, pl in v7[:5]:
    n1 = recs[k1][1] if k1 < len(recs) else None
    n2 = recs[k2][1] if k2 < len(recs) else None
    print(f"  comp={comps[ci][0]} node={nid} k1={k1}(id={n1}) k2={k2}(id={n2}) pl={pl}")

# 但 V=7 记录里 Marker plen=28: 12B 头 + 16B = 4×u32.  payload 首 u32 已判为 compIdx;
# 那么 k1,k2 + 4 个 u32。也许结构实际是 [compIdx][payload 16B], 而 k1,k2 是 payload 的一部分?
# Marker props: enabled(bool) scale(16) quat(16) pos(16) -> 若值是内联: bool=? scale=vec3 f32=12B quat=16B pos=12B
# 16B rest = ? 试 scale(vec3=12)+1B? 打印多个 Marker rest 为 u32 和 f32
print("\nMarker samples:")
mk = [x for x in v7 if comps[x[1]][0]=="Marker"]
for nid, ci, k1, k2, pl in mk[:6]:
    n,_,_,ne,nxt = recs[idorder[nid]]
    rest = data[ne+12:nxt-4]
    print(f"  id={nid} k1={k1} k2={k2} rest_u32={struct.unpack('<4I',rest)} rest_f32={tuple(round(f,3) for f in struct.unpack('<4f',rest))}")

# 或者: V=7 记录结构可能是 [compIdx][prevNodeRef?][nextNodeRef?] + payload(k1,k2 是前2个payload字段)
# 检查 k1/k2 与其它 V 记录序号的关系: k1 是否总是 < 本记录序号?
rel = []
for nid, ci, k1, k2, pl in v7:
    i = idorder[nid]
    rel.append((k1 < 11501, k1 < i, k2 < i))
print("k1<self_idx:", sum(1 for a,b,c in rel if b), " k2<self_idx:", sum(1 for a,b,c in rel if c), "/", len(rel))

# 全部记录的 V: 打印 V 分布完整
vd = Counter(r[2] for r in recs)
print("\nV full dist (v:n) sorted:", sorted(vd.items()))
