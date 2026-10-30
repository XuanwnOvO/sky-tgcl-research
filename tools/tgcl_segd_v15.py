# -*- coding: utf-8 -*-
"""segD v15: 结构判定核心实验 —— BstNode_x 是【共享子树】(类似哈希树/dedup树).
   检查: V=7 记录 payload 的所有 u32 (含 ci?) 是否 = segD 偏移链,
   且这些偏移指向的正是 107B 案例中的 "BstNode_973" 内嵌 —— 即【子节点名偏移】!
   决定性: V=7 记录 payload 某 u32 是否直接指向 'BstNode_<id>\0' 字符串起点 (即名字 - 4?)"""
import re, struct
from collections import Counter

P = r"Children of the Light\Levels\Dawn\Objects.level.bin"
data = open(P, "rb").read()
o1, o2, o3, o4, o5 = struct.unpack_from("<5I", data, 24)
c1, c2, c3, c4 = struct.unpack_from("<4I", data, 8)
SEG_D, END = o4, o5

pat = re.compile(rb"BstNode_(\d+)\x00")
nodes = [(m.start(), int(m.group(1))) for m in pat.finditer(data, SEG_D)]
recs = []
for i, (n, nid) in enumerate(nodes):
    V = struct.unpack_from("<I", data, n-4)[0]
    ne = n + 8 + len(str(nid)) + 1
    nxt = nodes[i+1][0] if i+1 < len(nodes) else END - 4
    recs.append((n, nid, V, ne, nxt))
name_at = {r[0]: r[1] for r in recs}
starts = sorted(name_at)

# 收集所有记录 payload 中的全部 u32, 统计命中 "恰好等于某节点名起点(-k)" 的比例
import bisect
for delta in [0, -4, -1, 4]:
    hit = 0; tot = 0
    for n,nid,V,ne,nxt in recs:
        pl = nxt-ne-4
        for off in range(4 if pl>=4 else 0, pl-3, 4) if pl>=8 else []:
            u = struct.unpack_from("<I", data, ne+off)[0]
            if u >= (END-SEG_D): continue
            a = SEG_D + u + delta
            j = bisect.bisect_right(starts, a) - 1
            if 0 <= j < len(starts) and starts[j] == a:
                hit += 1
            tot += 1
    print(f"delta={delta}: u32 pointing exactly at node-name-start(+{delta}): {hit}/{tot}")

# 若 delta=-4 命中高 -> u32 指向节点 V 字段, 即引用子节点! 打印样例树
delta = -4
def ref_target(u):
    if u >= END-SEG_D: return None
    a = SEG_D + u + delta
    j = bisect.bisect_right(starts, a) - 1
    if 0 <= j < len(starts) and starts[j] == a: return recs[j][1]
    return None
ex = 0
for n,nid,V,ne,nxt in recs:
    pl = nxt-ne-4
    refs = []
    for off in range(0, max(pl-3,0), 4):
        u = struct.unpack_from("<I", data, ne+off)[0]
        t = ref_target(u)
        if t is not None: refs.append((off, t))
    if refs and ex < 8:
        print(f"rec id={nid} V={V} plen={pl} childrefs={refs}")
        ex += 1
