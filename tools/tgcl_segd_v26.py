# -*- coding: utf-8 -*-
"""segD v26: 引用语义判定.
1) 65% 命中的 relmap[u]: 目标记录的 V 分布? 目标 = 被指记录本身.
2) 检验"链"假设: rec 内引用指向下一记录? 还是随机?
3) 每个引用值的 delta = target_rec_start - cur_rec_start 的分布.
4) c4=42919 = 总对象数? 统计 distinct 引用目标数."""
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

nextV_target = 0
same_rec = 0
total_hit = 0
targV = Counter()
deltas = Counter()
targs = set()
for j, (n, nid, V, ne, nxt) in enumerate(recs):
    pl = nxt - ne - 4
    for k in range(0, pl-3, 4):
        u = struct.unpack_from("<I", data, ne+k)[0]
        t = relmap.get(u)
        if t is None: continue
        total_hit += 1
        targs.add(t)
        tn, tnid, tV, tne, tnxt = recs[t]
        targV[tV] += 1
        if t == j: same_rec += 1
        if t == j + 1: nextV_target += 1
        deltas[t - j] += 1

print("总命中:", total_hit, " 独立目标:", len(targs))
print("目标==自身:", same_rec, " 目标==下一条:", nextV_target)
print("目标V分布 top15:", targV.most_common(15))
print("delta(t-j) top15:", deltas.most_common(15))
print("c4 =", c4)
