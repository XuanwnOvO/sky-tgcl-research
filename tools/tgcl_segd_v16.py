# -*- coding: utf-8 -*-
"""segD v16: 决定性. delta=4 命中 64% -> u32 值 v 满足 SEG_D+v+4 = 某节点名起点
   即 v = 节点名起点相对 SEG_D - 4 = V字段位置相对 SEG_D. 等价 delta=-4 检查错了符号?
   delta=4: a = SEG_D+u+4 == name start -> u = (name_start - SEG_D) - 4 -> 指向 V 字段(u32).
   那就是说: payload 里 64% 的 u32 是【子节点引用偏移】(指向 [u32 V][BstNode_x\0]).
   但 tot 包含大量小值/非4对齐. 重新精确统计: 只统计 4 对齐 u32 且完全精确."""
import re, struct, bisect
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
starts = [r[0] for r in recs]
ss = sorted(starts)
name_of = {r[0]: (r[1], r[2]) for r in recs}

hit = tot = 0
refs_by_rec = {}
for n,nid,V,ne,nxt in recs:
    pl = nxt-ne-4
    rl = []
    for off in range(0, pl-3, 4):
        u = struct.unpack_from("<I", data, ne+off)[0]
        tot += 1
        if u < 4 or u >= END-SEG_D: continue
        a = SEG_D + u + 4
        j = bisect.bisect_right(ss, a) - 1
        if 0 <= j < len(ss) and ss[j] == a:
            hit += 1
            rl.append((off, name_of[ss[j]]))
    if rl: refs_by_rec[nid] = (V, pl, rl)
print(f"4-aligned u32 total={tot}, exact child-node refs={hit} ({hit*100//tot}%)")

# 样本: V=7 LevelMesh plen=12 记录 [ci][k1][k2] -> k1,k2 都应是子节点引用
cnt2 = 0
for nid,(V,pl,rl) in refs_by_rec.items():
    pass
# 直接检查 LevelMesh V7
import collections
segC = data[o3:o4]
def s3(u):
    e = segC.find(b"\x00", u); return segC[u:e].decode()
comps = [s3(struct.unpack_from('<I', data, o1+i*12)[0]) for i in range(c1)]
lmn = 0; lmtot = 0
for n,nid,V,ne,nxt in recs:
    pl = nxt-ne-4
    if V==7 and pl==12:
        ci,k1,k2 = struct.unpack_from("<3I", data, ne)
        if ci < c1 and comps[ci]:
            lmtot += 1
            ok = 0
            for u in (k1,k2):
                if u < END-SEG_D:
                    a = SEG_D+u+4
                    j = bisect.bisect_right(ss,a)-1
                    if j>=0 and ss[j]==a: ok += 1
            if ok==2: lmn += 1
print(f"LevelMesh V7 plen12: both u32 are child refs: {lmn}/{lmtot}")

# 打印几个完整的 V=7 记录的引用树 (2层)
def show(nid, depth=0, seen=None):
    if seen is None: seen = set()
    if nid in seen or depth > 3: return
    seen.add(nid)
    r = refs_by_rec.get(nid)
    n = None
    for rec in recs:
        if rec[1]==nid: n = rec; break
    pay = data[n[3]:n[4]-4] if n else b''
    print("  "*depth + f"BstNode_{nid} V={n[2]} plen={n[4]-n[3]-4} payload={pay[:24].hex(' ')}")
    if r:
        for off,(cid,cv) in r:
            show(cid, depth+1, seen)
for nid in list(refs_by_rec)[:0]: pass
# 找 107B 案例的父: 含 BstNode_973 的 LevelMesh
t = data.find(b"BstNode_973\x00", SEG_D)
j = bisect.bisect_right(ss, t)-1
par = recs[j]
print("\n107B case parent:", par[1], "V=", par[2], "span=", par[4]-par[0])
print("parent payload:", data[par[3]:par[4]-4].hex(' '))
if par[1] in refs_by_rec:
    V, pl, rl = refs_by_rec[par[1]]
    print("child refs:", rl)
    for off,(cid,cv) in rl:
        c = [r for r in recs if r[1]==cid][0]
        print(f"  child BstNode_{cid} V={cv} plen={c[4]-c[3]-4} payload={data[c[3]:c[4]-4].hex(' ')}")
