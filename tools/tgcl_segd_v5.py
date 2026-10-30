# -*- coding: utf-8 -*-
"""segD v5: 正确切 payload (name_end = n+8+digits+1); 样本 dump"""
import re, struct
from collections import Counter, defaultdict

P = r"Children of the Light\Levels\Dawn\Objects.level.bin"
data = open(P, "rb").read()
o1, o2, o3, o4, o5 = struct.unpack_from("<5I", data, 24)
c1, c2, c3, c4 = struct.unpack_from("<4I", data, 8)
SEG_D, END = o4, o5

schema = {}
for i in range(c1):
    no, ss, pc = struct.unpack_from("<3I", data, o1 + i*12)
    schema[i] = (data[no:data.find(b"\x00", no)].decode("latin1"), pc)
rows = []
for i in range(c2):
    a, ko, t, e = struct.unpack_from("<4I", data, o2 + i*16)
    rows.append((a, data[ko:data.find(b"\x00", ko)].decode("latin1"), t, e))

pat = re.compile(rb"BstNode_(\d+)\x00")
nodes = [(m.start(), int(m.group(1))) for m in pat.finditer(data, SEG_D)]

recs = []
for i, (n, nid) in enumerate(nodes):
    V = struct.unpack_from("<I", data, n-4)[0]
    ne = n + 8 + len(str(nid)) + 1
    nxt = nodes[i+1][0] if i+1 < len(nodes) else END - 4
    recs.append((n, nid, V, ne, nxt))

# 组件索引判定: schema 名应为大写字母开头可读名, 且 payload 继续有 1B type-ish 字节
# 真正的组件索引记录: payload 首 u32 <261 且 schema 名是已知组件.  schema 里可能有怪名(空), 用白名单过滤:
known = {nm for nm,_ in schema.values() if nm and nm[0].isupper() and nm.isalnum()+True}
def compname(f):
    nm, pc = schema[f]
    return nm if nm and nm.replace('_','').isalnum() and nm[0].isupper() else None

comp = Counter(); bycomp = defaultdict(list)
for n, nid, V, ne, nxt in recs:
    pl = nxt - ne - 4
    if pl >= 4:
        f = struct.unpack_from("<I", data, ne)[0]
        cn = compname(f) if f < c1 else None
        if cn:
            comp[cn] += 1
            bycomp[cn].append((n, nid, V, ne, nxt, pl))
print("comp-index count:", sum(comp.values()), "top:", comp.most_common(12))

# dump 样本
def dump(cn, count=3, plen=None):
    print(f"\n--- {cn} ---")
    k = 0
    for n, nid, V, ne, nxt, pl in bycomp.get(cn, []):
        if plen is not None and pl != plen: continue
        print(f"V={V} id={nid} plen={pl} payload={data[ne:nxt-4].hex(' ')}")
        k += 1
        if k >= count: break
dump("Marker", 4)
dump("AudioMixToHaptics", 2)
dump("IfEnabled", 3)
dump("LevelMesh", 3)

# 若Enabled plen 分布
for cn in bycomp:
    L = bycomp[cn]
    print(cn, "n=", len(L), "plens:", sorted(set(x[5] for x in L))[:20])
