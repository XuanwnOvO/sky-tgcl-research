# -*- coding: utf-8 -*-
"""segD v25: 系统验证 u32 引用命中方式.
A) relmap: rec_start_rel = (n-4)-o4
B) altA: ne-o4   C) altB: (n-4)-o4+4  D) altC: n-o4
对全部记录 payload 的 4 对齐 u32 统计命中率, 以及对齐偏移修正 -12..+12 命中率."""
import re, struct, bisect
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

maps = {
    "V起点": {(r[0]-4)-o4: 1 for r in recs},
    "名字起": {r[0]-o4: 1 for r in recs},
    "payload起": {r[3]-o4: 1 for r in recs},
}
tot = 0
hits = Counter()
for (n, nid, V, ne, nxt) in recs:
    pl = nxt - ne - 4
    for k in range(0, pl-3, 4):
        u = struct.unpack_from("<I", data, ne+k)[0]
        if u > 0x2ffff: continue
        tot += 1
        for nm, mp in maps.items():
            if u in mp: hits[nm] += 1
        for d in range(-12, 13, 4):
            if u+d in maps["V起点"]: hits[f"V{d:+d}"] += 1
print("total u32:", tot)
print(hits.most_common(20))

# 任意字节位置(记录内部)命中测试: 把 recs 转成区间, u32 命中 [start, end) 即 in-record
starts = sorted(((r[0]-4)-o4, j) for j, r in enumerate(recs))
keys = [s for s, _ in starts]
inside = 0
for (n, nid, V, ne, nxt) in recs:
    pl = nxt - ne - 4
    for k in range(0, pl-3, 4):
        u = struct.unpack_from("<I", data, ne+k)[0]
        if u > 0x2ffff: continue
        t = bisect.bisect_right(keys, u) - 1
        if t >= 0 and u < keys[t] + (recs[starts[t][1]][4]-4-o4 - keys[t]):
            inside += 1
print("inside-any-record:", inside, f"{inside/tot:.1%}")
