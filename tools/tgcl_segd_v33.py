# -*- coding: utf-8 -*-
"""segD v33: 关键假设 — 引用不是绝对 rel, 而是 rel 相对【当前记录起点】的差值?
Marker ref 0x19f6=6654, 但目标在 rec42 内 rel=41. 说明这个 u32 不是直接偏移.
新假设: u32 = 绝对 rel - 某个基址. 或者 u32 是【BstNode id 的 hash 表索引】.
另一假设: u32 = 【段内偏移但基准是 o4+X】 或 u32 是 (对象id) 索引到 c4=42919 的对象池?
测: 6 个 ref 的 u32 值除以 261, 或对比 Schema propCount.
也测: ref*? = rel? 0x19f6=6654 vs rel=41. no.
试: ref 值域统计 — 所有 V=7 记录的 refs: max? 如果都 < 0x4000, 可能是"短偏移"。
之前命中 relmap 的 65% 是 130817/201033, 且都是 root rel=0 (0x0000). 因为 0 命中所有映射.
**root 引用 = 0x00000000 (null/默认)** — 130657 次是"值为0的u32"! 不是引用!
所以 65% 命中只是 u32=0 的巧合. 引用机制还没找到.
检查: 0x00000000 在 payload u32 中的比例, 以及 0xffffffff(=null) 比例."""
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

zc = 0; ffc = 0; tot = 0
vals = Counter()
for (n, nid, V, ne, nxt) in recs:
    pl = nxt - ne - 4
    for k in range(0, pl-3, 4):
        u = struct.unpack_from("<I", data, ne+k)[0]
        tot += 1
        vals[u] += 1
print("payload 4对齐u32 总数:", tot)
print("u32==0:", vals[0], " u32==0xffffffff:", vals[0xffffffff])
print("top10 u32 值:", [(hex(v), c) for v, c in vals.most_common(10)])
