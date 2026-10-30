# -*- coding: utf-8 -*-
"""segD v7: 正确 schema 解析 (keyOff -> segC). 重做组件索引匹配与样本 dump"""
import re, struct
from collections import Counter, defaultdict

P = r"Children of the Light\Levels\Dawn\Objects.level.bin"
data = open(P, "rb").read()
o1, o2, o3, o4, o5 = struct.unpack_from("<5I", data, 24)
c1, c2, c3, c4 = struct.unpack_from("<4I", data, 8)
SEG_D, END = o4, o5
segC = data[o3:o4]
def s3(u):
    e = segC.find(b"\x00", u)
    return segC[u:e].decode("utf-8", "replace")

comps = []
for i in range(c1):
    a, st, pc = struct.unpack_from("<3I", data, o1 + i*12)
    comps.append((s3(a), st, pc))
compnames = {c[0]: i for i, c in enumerate(comps)}
rows = []
for j in range(c2):
    a, ko, t, e = struct.unpack_from("<4I", data, o2 + j*16)
    rows.append((a, s3(ko), t, e))

pat = re.compile(rb"BstNode_(\d+)\x00")
nodes = [(m.start(), int(m.group(1))) for m in pat.finditer(data, SEG_D)]
recs = []
for i, (n, nid) in enumerate(nodes):
    V = struct.unpack_from("<I", data, n-4)[0]
    ne = n + 8 + len(str(nid)) + 1
    nxt = nodes[i+1][0] if i+1 < len(nodes) else END - 4
    recs.append((n, nid, V, ne, nxt))
print("recs:", len(recs))

# V 链验证 (已证 11500/11500). payload = [ne, nxt-4)
comp = Counter(); bycomp = defaultdict(list)
for n, nid, V, ne, nxt in recs:
    pl = nxt - ne - 4
    if pl >= 4:
        f = struct.unpack_from("<I", data, ne)[0]
        if f < c1 and comps[f][0]:
            comp[comps[f][0]] += 1
            bycomp[comps[f][0]].append((n, nid, V, ne, nxt, pl))
print("comp-index count:", sum(comp.values()), "top:", comp.most_common(15))

def props_of(ci):
    nm, st, pc = comps[ci]
    return [(rows[j][1], rows[j][2]) for j in range(st, st+pc)]

def dump(cn, count=3):
    ci = compnames[cn]
    print(f"\n--- {cn} (compIdx {ci}) props={props_of(ci)}")
    for k,(n,nid,V,ne,nxt,pl) in enumerate(bycomp.get(cn,[])):
        print(f"V={V} id={nid} plen={pl} payload={data[ne:nxt-4].hex(' ')}")
        if k+1>=count: break
for cn in ["Marker","AudioMixToHaptics","IfEnabled","LevelMesh"]:
    dump(cn)

print()
for cn in list(bycomp)[:50]:
    L = bycomp[cn]
    print(cn, "n=", len(L), "plens:", sorted(set(x[5] for x in L))[:20])
