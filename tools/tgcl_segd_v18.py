# -*- coding: utf-8 -*-
"""segD v18: 终局解析. 结构:
   rec = [u32 V][BstNode_<id>\\0][payload][u32 nextV]
   payload 内 4对齐 u32 中 30% 是 segD 相对偏移(指向其它记录的 V 字段) -> 子引用.
   本脚本: 按每个 V 组, 判定 payload 的语义; 并检查 V 是否= 子节点引用数 或 头部类型.
   关键: V=0 记录 payload 25B: 00 ed 2c 00 00 00 00 00 00 01 00 ff ff ff ff ee 2c 00 00
   按 [u32 off=0x2ced][...]: 0x2ced=11469 偏移 -> owner? """
import re, struct, bisect
from collections import Counter, defaultdict

P = r"Children of the Light\Levels\Dawn\Objects.level.bin"
data = open(P, "rb").read()
o1, o2, o3, o4, o5 = struct.unpack_from("<5I", data, 24)
c1, c2, c3, c4 = struct.unpack_from("<4I", data, 8)
SEG_D, END = o4, o5
segC = data[o3:o4]
def s3(u):
    e = segC.find(b"\x00", u); return segC[u:e].decode()
comps = [s3(struct.unpack_from('<I', data, o1+i*12)[0]) for i in range(c1)]

pat = re.compile(rb"BstNode_(\d+)\x00")
nodes = [(m.start(), int(m.group(1))) for m in pat.finditer(data, SEG_D)]
recs = []
for i, (n, nid) in enumerate(nodes):
    V = struct.unpack_from("<I", data, n-4)[0]
    ne = n + 8 + len(str(nid)) + 1
    nxt = nodes[i+1][0] if i+1 < len(nodes) else END - 4
    recs.append((n, nid, V, ne, nxt))
relmap = {}
for r in recs: relmap[(r[0]-4)-SEG_D] = r[1]
rels = sorted(relmap)
def is_ref(u): return u in relmap

# V=0 记录: 0x2ced 是否引用?
v0 = [r for r in recs if r[2]==0][:5]
for n,nid,V,ne,nxt in v0:
    pl = nxt-ne-4
    pay = data[ne:nxt-4]
    print(f"V0 id={nid} plen={pl} payload={pay.hex(' ')}")
    for off in range(0, pl-3):
        u = struct.unpack_from("<I", pay, off)[0] if off+4<=pl else None
        if u is not None and u in relmap:
            print(f"   ref at byte {off}: -> BstNode_{relmap[u]}")

# 检查 V 是否等于该记录 payload 中的引用数?
refcnt = Counter()
for n,nid,V,ne,nxt in recs:
    pl = nxt-ne-4
    c = sum(1 for off in range(0, pl-3, 4) if struct.unpack_from("<I", data, ne+off)[0] in relmap)
    refcnt[(V, c)] += 1
print("(V, refcnt) top:", refcnt.most_common(15))

# 检查 V=1..5 记录的 payload 解释: V=1 rec1 payload 有 'MemAp18Misfit5' 字符串 + refs
# 猜测: 记录类型由 V 决定: V=6/7 = 组件值块 (ci + refs/values); V=0/1 = 对象?
# 对象树: 谁 = 场景对象根? 统计被引用次数 (入度)
indeg = Counter()
for n,nid,V,ne,nxt in recs:
    pl = nxt-ne-4
    for off in range(0, pl-3, 4):
        u = struct.unpack_from("<I", data, ne+off)[0]
        if u in relmap: indeg[relmap[u]] += 1
print("in-degree top:", indeg.most_common(10), " zero-indeg:", len(recs)-len(indeg))
# 入度0的记录 V 分布
zv = Counter(r[2] for r in recs if r[1] not in indeg)
print("zero-indeg V dist:", zv.most_common(10))
# 入度高的记录 V 分布
hv = Counter(r[2] for r in recs if indeg.get(r[1],0) >= 10)
print("indeg>=10 V dist:", hv.most_common(10))
