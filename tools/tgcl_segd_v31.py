# -*- coding: utf-8 -*-
"""segD v31: 深入 root rec0 (BstNode_2310602845, V=0, plen=19) 与对象头.
root payload: 00 ed 2c 00 00 00 00 00 00 01 00 ff ff ff ff ee 2c 00 00
   0x2ced=11469 出现两次! 0x2ced 是 segD 内偏移吗? 检查 11469 是哪个记录/边界.
另外 rec0 的 name 在 SEG_D+4, 0x2ced 可能指向某个全局表.
还检查: 0xff ff ff ff = null 引用. 统计 0xffffffff 出现次数.
还有一个大问题: 42919=c4 vs 4294967295(=-1) 意义. c4 或许= 引用总数?"""
import re, struct
from collections import Counter

P = r"Children of the Light\Levels\Dawn\Objects.level.bin"
data = open(P, "rb").read()
o1, o2, o3, o4, o5 = struct.unpack_from("<5I", data, 24)
c1, c2, c3, c4 = struct.unpack_from("<4I", data, 8)

pat = re.compile(rb"BstNode_(\d+)\x00")
nodes = [(m.start(), int(m.group(1))) for m in pat.finditer(data, o4)]
recs = []
for i, (n, nid) in enumerate(nodes):
    V = struct.unpack_from("<I", data, n-4)[0]
    ne = n + 8 + len(str(nid)) + 1
    nxt = nodes[i+1][0] if i+1 < len(nodes) else o5 - 4
    recs.append((n, nid, V, ne, nxt))

# 11469 处是什么
a = o4 + 11469
print("SEG_D+11469 附近:", data[a-8:a+16].hex(" "))
# 找最近的记录
for j, (n, nid, V, ne, nxt) in enumerate(recs):
    if n-4 <= a < nxt:
        print(f"位于 rec{j} id={nid} V={V} 内, rel={a-(n-4)}")

# 0xffffffff 频率
ff = data[o4:o5].count(b"\xff\xff\xff\xff")
print("0xffffffff u32 次数(segD):", ff)

# 0x2ced 在 segD 中出现次数与位置
positions = [m.start() for m in re.finditer(re.escape(b"\xed\x2c\x00\x00"), data[o4:o5])]
print("0x00002ced 出现次数:", len(positions), "前5:", [p for p in positions[:5]])
