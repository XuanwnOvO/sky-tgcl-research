# -*- coding: utf-8 -*-
"""segD v38: 关键重审 — Marker refs 大部分 < 0x3000, segD 有89条记录起点 <0x3000.
v35 显示 x1 命中仅3/476. 但注意: rec_start_rel 前缀有 0x0,0x2a,0x7b,0x4e4,0x521,0x86a...
0x2cc 应命中 0x2a/0x7b 之间? 0x2cc 没有. 但 v35 x1 命中3个!
可能 refs 是【对象id(递增序号)】而非偏移. c4=42919 = 对象总数?
试: refs 值域 vs 全部 V=7 组件值块记录的 refs 值域. 若 refs 大多 < 记录数(11501),
则 refs = 记录序号(rec index)! 测: refs[i] 直接当 recs 索引读."""
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
bycomp = {}
for j, (n, nid, V, ne, nxt) in enumerate(recs):
    pl = nxt - ne - 4
    if pl >= 4:
        f = struct.unpack_from("<I", data, ne)[0]
        if f < c1 and comps[f][0]:
            bycomp.setdefault(comps[f][0], []).append(j)

# rec-index 假设: refs < 11501 的比例
cnt = Counter(); tot = 0
sample = []
for j in bycomp["Marker"]:
    n, nid, V, ne, nxt = recs[j]
    pl = nxt - ne - 4
    for k in range(4, pl-3, 4):
        u = struct.unpack_from("<I", data, ne+k)[0]
        tot += 1
        if u < len(recs):
            cnt["<11501"] += 1
            if len(sample) < 5:
                t = recs[u]
                sample.append((j, k, u, t[2], t[1], t[4]-t[3]-4))
        else:
            cnt[">=11501"] += 1
print("Marker refs as rec-index:", cnt, "/", tot)
for s in sample:
    j, k, u, tV, tid, tpl = s
    print(f"  rec{j} k={k} -> recs[{u}] V={tV} id={tid} plen={tpl}")
    print("   payload:", data[recs[u][3]:recs[u][4]-4].hex(" "))
