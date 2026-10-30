# -*- coding: utf-8 -*-
"""segD v42: V=4 深挖. bytes2 都是 ASCII 数字('0'-'9')! byte2 top=49('1'),53('5'),50('2'),45('-')
byte1/byte7 随机 — 可能是字符串的一部分!? '00 39 07...' 不像.
等等: 00 39 07 00 00 00 01 a0 01 25 a4 00: byte2=0x07 非ASCII. 但统计里 byte2 大多是 ASCII?
byte2 top 49='1',53='5',50='2',45='-' 是 ASCII. 但也有 0x07. 混合.
另一思路: u32@8 ~13221376..81 = 0xC9C000..0xC9C041 → 0xC9C0xx 高位? 13221381=0xC9C005.
0xC9C0 = ? 常见偏移? 13221377 = 0xC9C001. 挺聚集.
分解: byte8=low, byte9,10 中, byte11=0. u24@8 = 0xC9C0xx?
dump 30 条 V=4 原始 + id. 看 id 与 payload 的关系 (id%? id vs payload u32)."""
import re, struct
from collections import Counter

P = r"Children of the Light\Levels\Dawn\Objects.level.bin"
data = open(P, "rb").read()
o1, o2, o3, o4, o5 = struct.unpack_from("<5I", data, 24)

pat = re.compile(rb"BstNode_(\d+)\x00")
nodes = [(m.start(), int(m.group(1))) for m in pat.finditer(data, o4)]
recs = []
for i, (n, nid) in enumerate(nodes):
    V = struct.unpack_from("<I", data, n-4)[0]
    ne = n + 8 + len(str(nid)) + 1
    nxt = nodes[i+1][0] if i+1 < len(nodes) else o5 - 4
    recs.append((n, nid, V, ne, nxt))

v4 = [(nid, data[ne:nxt-4]) for (n, nid, V, ne, nxt) in recs if V == 4]
for nid, p in v4[:30]:
    print(nid, p.hex(" "))
# id 与 u32@5 (bytes5..8) 关系
rel = []
for nid, p in v4:
    u = struct.unpack_from("<I", p, 5)[0] & 0xFFFFFF
    rel.append((nid, u))
print("id mod 4096 vs u24@5 相关系数检查: 样例", rel[:10])
