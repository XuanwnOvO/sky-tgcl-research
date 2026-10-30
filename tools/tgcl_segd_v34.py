# -*- coding: utf-8 -*-
"""segD v34: 重新定界! payload 不是4对齐.
关键: u32 值大量出现 '未对齐' 模式: 0x3f (=0x3f000000>>?), 0x3f80, 0x3f8000
→ 这些是 float 1.0 (00 00 80 3f) 在**非4对齐**位置被 4对齐 读出的移位版本!
0x5f750000 = "u_" 字符串 (75 5f = 'u_' 反序) — 未对齐字符串!
结论: payload 是【字节流】, 非 4对齐. 之前所有 4对齐统计都失真.
真正结构: payload 内对象 = 变长 TLV 或 定界子块.
回到未对齐 u32 扫描: 每1B步进读 u32, 看 rec_start_rel 命中率."""
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
relmap = {(r[0]-4) - o4: j for j, r in enumerate(recs)}

# 未对齐扫描 (排除 0 和 0xffffffff)
tot = 0; hit = 0; hitd = Counter()
for (n, nid, V, ne, nxt) in recs:
    pl = nxt - ne - 4
    for off in range(0, pl-3):
        u = struct.unpack_from("<I", data, ne+off)[0]
        if u == 0 or u == 0xffffffff: continue
        tot += 1
        t = relmap.get(u)
        if t is not None:
            hit += 1
            hitd[off] += 1
print(f"未对齐u32(非0) 总数: {tot}, 命中 rec_start_rel: {hit} ({hit/tot:.1%})")
print("命中位置(payload内off) top15:", hitd.most_common(15))
