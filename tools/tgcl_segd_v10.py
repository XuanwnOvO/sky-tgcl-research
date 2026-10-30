# -*- coding: utf-8 -*-
"""segD v10: 决定性验证 —— k1/k2 是 segD 内字节偏移(相对 SEG_D=91988)?
   检查 rec[k1] 或 data[SEG_D+k1] 是否落在某节点内部/附近."""
import re, struct
from collections import Counter

P = r"Children of the Light\Levels\Dawn\Objects.level.bin"
data = open(P, "rb").read()
o1, o2, o3, o4, o5 = struct.unpack_from("<5I", data, 24)
c1, c2, c3, c4 = struct.unpack_from("<4I", data, 8)
SEG_D, END = o4, o5
segC = data[o3:o4]
def s3(u):
    e = segC.find(b"\x00", u); return segC[u:e].decode()
comps = []
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

v7 = []
for i,(n, nid, V, ne, nxt) in enumerate(recs):
    pl = nxt - ne - 4
    if V == 7 and pl >= 12:
        ci, k1, k2 = struct.unpack_from("<3I", data, ne)
        if ci < c1 and comps[ci][0]:
            v7.append((i, nid, ci, k1, k2, pl))

# 假设 A: k1/k2 = segD 内偏移 (abs = SEG_D + k)
import bisect
starts = [r[0] for r in recs]
def owner(a):
    j = bisect.bisect_right(starts, a) - 1
    if 0 <= j < len(recs) and recs[j][0] <= a < recs[j][4]:
        return recs[j][1]
    return None
hA = sum(1 for i,nid,ci,k1,k2,pl in v7 if owner(SEG_D+k1))
hB = sum(1 for i,nid,ci,k1,k2,pl in v7 if owner(k1))
print("k as segD-rel offset owner hit:", hA, "/", len(v7))
print("k as abs offset owner hit:", hB, "/", len(v7))
# 对命中的, owner 是否==自身节点?
hSame = sum(1 for i,nid,ci,k1,k2,pl in v7 if owner(SEG_D+k1)==nid)
print("owner==self:", hSame)
# 样本: owner 与自身关系
for i,nid,ci,k1,k2,pl in v7[:10]:
    print(f"  {comps[ci][0]} node={nid} k1={k1} owner={owner(SEG_D+k1)} k2={k2} owner2={owner(SEG_D+k2)}")
