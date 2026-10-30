# -*- coding: utf-8 -*-
"""segD 流式解析假设验证: node = [u32 X][u32 Y][u32 totalLen][name\\0][payload totalLen-len(name)]"""
import re, struct
from collections import Counter, defaultdict

P = r"Children of the Light\Levels\Dawn\Objects.level.bin"
data = open(P, "rb").read()
o1, o2, o3, o4, o5 = struct.unpack_from("<5I", data, 24)
c1, c2, c3, c4 = struct.unpack_from("<4I", data, 8)
print("counts", (c1, c2, c3, c4), "offsets", (o1, o2, o3, o4, o5))
SEG_D, END = o4, o5

# schema
schema = {}
for i in range(c1):
    no, ss, pc = struct.unpack_from("<3I", data, o1 + i*12)
    schema[i] = (data[no:data.find(b"\x00", no)].decode("latin1"), pc)

# segB rows
rows = []
for i in range(c2):
    a, ko, t, e = struct.unpack_from("<4I", data, o2 + i*16)
    key = data[ko:data.find(b"\x00", ko)].decode("latin1")
    rows.append((a, key, t, e))

pos = SEG_D
nodes = []   # (off, X, Y, totalLen, id, payload_start, payload_end, totalRecEnd)
fails = 0
while pos < END - 4:
    if pos + 12 > END: fails += 1; break
    X, Y, L = struct.unpack_from("<3I", data, pos)
    # 找名字: 从 pos+12 开始的 NUL 结尾串
    ne = data.find(b"\x00", pos + 12, pos + 12 + 64)
    if ne < 0: fails += 1; print("no name at", pos, data[pos:pos+16].hex(' ')); break
    name = data[pos+12:ne]
    if not name.startswith(b"BstNode_"):
        fails += 1
        print("non-BstNode at", hex(pos), data[pos:pos+20].hex(' '))
        break
    nid = int(name[8:])
    nlen = ne - (pos + 12) + 1
    rec_end = pos + 12 + L  # L 从 3u32 头之后算? 先试 L 含名字: totalLen = L
    ps = ne + 1
    pe = pos + 12 + L
    if pe < ps: fails += 1; print("neg payload", nid, L, nlen); break
    nodes.append((pos, X, Y, L, nid, ps, pe, pe))
    pos = pe
print("parsed nodes:", len(nodes), "fails:", fails, "final pos:", hex(pos), "END:", hex(END))
if pos != END - 4:
    print("gap bytes:", data[pos:END].hex(' ')[:100])
print("last4:", struct.unpack_from("<I", data, END-4)[0])

# L - nlen 分布
dl = Counter(L - nlen for (_,_,_,L,nid,ps,pe,_) in nodes for nlen in [len(b"BstNode_%d\x00"%nid)])
print("payloadLen hist top:", dl.most_common(15))

# X,Y 语义: X/Y 是否互相引用（成对出现）
xs = Counter(X for (_,X,_,_,_,_,_,_) in nodes)
ys = Counter(Y for (_,_,Y,_,_,_,_,_) in nodes)
print("distinct X:", len(xs), "distinct Y:", len(ys))
print("X top:", xs.most_common(8)); print("Y top:", ys.most_common(8))
# X 是否也是节点 id?
idset = set(n[4] for n in nodes)
x_in = sum(1 for (_,X,_,_,_,_,_,_) in nodes if X in idset)
y_in = sum(1 for (_,_,Y,_,_,_,_,_) in nodes if Y in idset)
print("X in idset:", x_in, "/", len(nodes), "  Y in idset:", y_in)

# X 是否 < 261 (组件索引)?
x_comp = sum(1 for (_,X,_,_,_,_,_,_) in nodes if X < c1)
print("X < 261:", x_comp)
# X<261 时组件名分布
cc = Counter(schema[X][0] for (_,X,_,_,_,_,_,_) in nodes if X < c1)
print("comp dist:", cc.most_common(10))

# Y 递增？取前 30 个
for n in nodes[:20]:
    off,X,Y,L,nid,ps,pe,_ = n
    print(f"off={off} X={X} Y={Y} L={L} id={nid} plen={pe-ps} payload={data[ps:min(pe,ps+24)].hex(' ')}")
