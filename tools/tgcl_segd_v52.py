# -*- coding: utf-8 -*-
"""segD v52: 重大线索! rec0 off1 = 0x2ced = 11501 = 记录总数!!! off15 = 0x2cee = 11502!
=> rec0 payload = 【计数/边界信息】: 11501 = 记录数!
=> 而 0x2ced 处(=11501)可能是【哨兵】. rec0 = BST 根, key=2310602845,
   payload = [00][u32 11501][u32 0][01 00][ff ff ff ff][u32 11502]
   BST 结构: [min_key_range?]... 
   BST 节点 payload 或许 = [00][u32 count][u32 ?][flag][u32 -1][u32 end]
   但 V=6 记录 plen=49 (1917条), V=9 plen=368 — 固定! BST 子节点指针怎么只有这些?
   也许: BstNode_<id> 是【对象树节点】, V = 节点类型枚举, payload = 节点数据,
   refs = 子节点 rec-index (树结构) — Marker 6 个 refs = 6 个子节点!
   rec0 (root) 有 2 个子: 0x2ced=11501 越界(11501条, 索引 0..11500), 
   11501 越界! 除非 rec-index 是 1-based: 11501 = 最后一条?
   或 refs 是【字节偏移/其它】. 
   测试: rec0 payload 的 0x2ced=11501: 若 1-based rec-index → recs[11500]?
   recs[11500] 是最后一条. 检查其 id 与 rec0 关系.
   另一解释: payload = [00][u32 cnt=11501][00 00 00 00][01][00 ff ff ff ff][u32 11502]
   像版本头: count=11501, ?, ?, null, count+1?
   直接检查其它 V=0 记录 (137条) 是否都是 19B 同构."""
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

v0 = [(nid, data[ne:nxt-4]) for (n, nid, V, ne, nxt) in recs if V == 0]
print("V=0 记录数:", len(v0))
for nid, p in v0[:10]:
    print(nid, p.hex(" "))
# u32@1 分布
u1 = Counter(struct.unpack_from("<I", p, 1)[0] for nid, p in v0)
print("u32@1 top:", u1.most_common(5))
u4 = Counter(struct.unpack_from("<I", p, 14)[0] for nid, p in v0)
print("u32@14 top:", u4.most_common(5))
# 最后一条记录
print("last rec:", recs[-1][1], recs[-1][2])
