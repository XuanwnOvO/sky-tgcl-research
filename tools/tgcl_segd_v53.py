# -*- coding: utf-8 -*-
"""segD v53: V=0 记录 = 12B-ish 结构: 00 [u16 N] 00 00 00 00 00 00 [01] [b] ff ff ff ff [u16 M] 00 00
u32@1 = 递增 id? (11501,11507,11523,11540,11545...) 排序后递增! u32@14 = N+1 或其它.
这像【区间分配表】: [start=N][end=M]?  u32@1=N, u32@14 = ? 
样例1: N=11501, M bytes@14: ee 2c 00 00 → u32@14? p=19B: 00 ed 2c 00 00 00 00 00 00 01 00 ff ff ff ff ee 2c 00 00
u32@14 = 0x00002cee = 11502 = N+1! 
样例3: N=11523(0x2d03), 末尾 ec 03 = 0x03ec=1004?? 
p3 = 00 03 2d 00 00 01 00 00 00 01 01 ff ff ff ff ec 03 00 00: u32@14 = 0x03ec=1004. 
哦不是 N+1. 看 u16@14: 0x03ec. 但样例1 u16@14=0x2cee=N+1.
样例2: 00 f3 2c 00 00 00 00 00 00 01 01 ff ff ff ff f4 2c 00 00 → u16@14=0x2cf4=11508, N=11507, N+1 ✓
样例3: N=0x2d03=11523, 尾=0x03ec=1004 ✗ — 但中间 bytes5=01 (其它=00)!
含 byte5=01 的可能不同. 
其实 V=0 = 【父节点 range 声明】: [u32 start][u32 ?][b][u32 end]:
start=u32@1=11501, end=u32@14: 样例1 end=11502? 但样例3 end=1004.
hmm. 或 [u32 start][u32 count][flags][u32 ?]. 
样例3: start=11523, bytes5..8 = 01 00 00 00 → u32@5=1, b9=01, ff*4, end=1004?
也许是 [u32 start][u32 end][u32 flags][u32 null][u32 X]:
样例1: 11501, 0, 0x0100?, -1, 11502
不清晰. 但主题: V=0 = 区间/分组节点.
决定性测试: u32@1 (11501 等) 递增且不同 — 这些是什么 id 空间? 全文件 u32@1 排序后连续?
对 137 条 V=0: 收集 (u32@1, u32@14), 检查区间是否衔接覆盖 [11501, ?]."""
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

v0 = [data[ne:nxt-4] for (n, nid, V, ne, nxt) in recs if V == 0]
ivs = []
for p in v0:
    a = struct.unpack_from("<I", p, 1)[0]
    b = struct.unpack_from("<H", p, 14)[0]
    f5 = p[5]; f9 = p[9]
    ivs.append((a, b, f5, f9))
ivs.sort()
for iv in ivs[:40]:
    print(iv)
print("...")
print("max u32@1:", max(x[0] for x in ivs))
