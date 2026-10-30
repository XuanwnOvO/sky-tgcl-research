# -*- coding: utf-8 -*-
"""segD v6: 直接检查组件索引记录。先前发现 payload 首字节 0x00/0x01/0x8f/0x04 等小于261 -> 那是 1B? 
   重审: 3297 条 payload 首字节 00 -> 若按 1B 读是组件0? schema[0] 是什么?
   检查 schema[0..5] 名字与 segA 原始 12B 行, 以及 payload 首 1B/2B 解释."""
import re, struct
from collections import Counter, defaultdict

P = r"Children of the Light\Levels\Dawn\Objects.level.bin"
data = open(P, "rb").read()
o1, o2, o3, o4, o5 = struct.unpack_from("<5I", data, 24)
c1, c2, c3, c4 = struct.unpack_from("<4I", data, 8)
SEG_D, END = o4, o5

schema = []
for i in range(c1):
    no, ss, pc = struct.unpack_from("<3I", data, o1 + i*12)
    schema.append((data[no:data.find(b"\x00", no)].decode("latin1"), pc, ss))
for i in range(8):
    print("schema", i, schema[i])

pat = re.compile(rb"BstNode_(\d+)\x00")
nodes = [(m.start(), int(m.group(1))) for m in pat.finditer(data, SEG_D)]
recs = []
for i, (n, nid) in enumerate(nodes):
    V = struct.unpack_from("<I", data, n-4)[0]
    ne = n + 8 + len(str(nid)) + 1
    nxt = nodes[i+1][0] if i+1 < len(nodes) else END - 4
    recs.append((n, nid, V, ne, nxt))

# 组件索引判定用 schema 中真实组件名: 找 payload 首 u32 <261 且 schema 名可读的
readable = [i for i,(nm,pc,ss) in enumerate(schema) if nm and all(ch.isalnum() or ch=='_' for ch in nm) and nm[0].isupper()]
print("readable schema entries:", len(readable), "sample:", [(i, schema[i][0], schema[i][1]) for i in readable[:10]])
rset = set(readable)

comp = Counter(); bycomp = defaultdict(list)
for n, nid, V, ne, nxt in recs:
    pl = nxt - ne - 4
    if pl >= 4:
        f = struct.unpack_from("<I", data, ne)[0]
        if f in rset:
            comp[schema[f][0]] += 1
            bycomp[schema[f][0]].append((n, nid, V, ne, nxt, pl))
print("comp-index count:", sum(comp.values()), "top:", comp.most_common(12))

def dump(cn, count=3):
    print(f"\n--- {cn} props={[r for r in rows if r[0] == [i for i in readable if schema[i][0]==cn][0]]} ---")
    for k,(n,nid,V,ne,nxt,pl) in enumerate(bycomp.get(cn,[])):
        print(f"V={V} id={nid} plen={pl} payload={data[ne:nxt-4].hex(' ')}")
        if k+1>=count: break
for cn in ["Marker","AudioMixToHaptics","IfEnabled","LevelMesh","CandleObject"]:
    if cn in bycomp: dump(cn)

# 每组件 plen 集合
print()
for cn in list(bycomp)[:40]:
    L = bycomp[cn]
    print(cn, "n=", len(L), "plens:", sorted(set(x[5] for x in L))[:20])
