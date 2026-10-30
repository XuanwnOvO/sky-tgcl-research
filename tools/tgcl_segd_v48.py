# -*- coding: utf-8 -*-
"""segD v48: refs 不是 keyOff. 换思路: refs 是【BstNode id 的 hash 索引】?
或者: refs = (目标记录 id>>8)&0xFFFF 失败; id&0xFFFF 命中 84/476 太低.
彻底换角度: 看同一个【对象组(id>>8 相同)】内多条 Marker 的 refs 是否相同?
若不同 → refs 是实例相关 (per-instance); 若相同 → 是共享 key.
另外测试: refs 值是否在 segC 之外的某个表? 检查 refs 值域: 0x2cc..0x284d (max 0x284d=13325).
11501 条记录! refs < 11501. rec-index 假设 476/480 在界内不是巧合.
关键检验: rec-index 目标的 id 前缀是否与 Marker 所在【对象】有语义关联 —
对象组 2753888 包含 rec6646 (V=4), 但 9315 不在组里.
等一下! V=4 payload = 00 [u16A] 00 00 00 [f] [b7] [u24=id>>8] 00.
u24@8 = id>>8 = 0xC9BE04 = 目标对象组! 而 V=4 记录就是【对象-成员链接】!
ref 值 = 6646 可能 = 该 V=4 链接记录在 segD 的记录序号!
测试: Marker refs[i] 对应 recs[u] 是否为 V=4 记录, 且其 u24@8 组内含 Marker?
v38 显示 rec6646 是 V=4, rec716 是 V=4, rec5531 是 V=4, rec9315 是 V=42...
统计 Marker refs 目标记录的 V 分布 (rec-index 解读)."""
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

tv = Counter(); tot = 0; same_u24 = 0
for j in bycomp["Marker"]:
    n, nid, V, ne, nxt = recs[j]
    pl = nxt - ne - 4
    for k in range(4, pl-3, 4):
        u = struct.unpack_from("<I", data, ne+k)[0]
        if u >= len(recs): continue
        tot += 1
        t = recs[u]
        tv[t[2]] += 1
        if t[1] >> 8 == nid >> 8: same_u24 += 1
print(f"Marker refs(rec-index) 目标 V 分布: {tv.most_common(12)}  same u24 组: {same_u24}/{tot}")

# 同组多条 Marker refs 相同?
from collections import defaultdict
gm = defaultdict(list)
for j in bycomp["Marker"]:
    gm[recs[j][1] >> 8].append(j)
rep = 0
for g, js in gm.items():
    if len(js) > 1: rep += 1
print("含多条 Marker 的组:", rep, "/", len(gm))
