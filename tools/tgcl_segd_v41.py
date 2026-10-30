# -*- coding: utf-8 -*-
"""segD v41: V=4 (12B) 记录 = 对象-组件链接? 样本 payload:
00 39 07 00 00 00 01 a0 01 25 a4 00
00 a5 2d 00 00 00 01 2b 03 25 a4 00
首 00, 然后 [u32]? 尝试解读: [00][u24 obj?][00][00][01][u8][u16][u8? u16?]
结构 12B: 00 XX XX 00 00 00 01 YY YY ZZ ZZ 00 ?
      或 [00][u16][u8 00]... 试逐B标注. 统计 798 条的每个字节分布."""
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

v4 = [(n, nid, ne, nxt) for (n, nid, V, ne, nxt) in recs if V == 4]
cols = [Counter() for _ in range(12)]
for (n, nid, ne, nxt) in v4:
    p = data[ne:nxt-4]
    for b in range(12):
        cols[b][p[b]] += 1
for b in range(12):
    print(f"byte{b}: distinct={len(cols[b])} top={cols[b].most_common(4)}")
# 试 u16@1, u16@7
u16_1 = Counter(); u16_7 = Counter(); u32_8 = Counter()
for (n, nid, ne, nxt) in v4:
    p = data[ne:nxt-4]
    u16_1[struct.unpack_from("<H", p, 1)[0]] += 1
    u16_7[struct.unpack_from("<H", p, 7)[0]] += 1
    u32_8[struct.unpack_from("<I", p, 8)[0]] += 1
print("u16@1 distinct:", len(u16_1), "max", max(u16_1))
print("u16@7 distinct:", len(u16_7), "max", max(u16_7), u16_7.most_common(5))
print("u32@8 distinct:", len(u32_8), u32_8.most_common(5))
