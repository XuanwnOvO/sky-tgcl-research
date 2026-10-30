# -*- coding: utf-8 -*-
"""segD v51: BST 假设的真正检验 — refs = [left_child_idx, right_child_idx]?
BST 节点在【key 排序数组】中的存储: 若节点 i 的左子 = refs[0], 检验:
refs[0] 子树的 key 全部 < 源, refs[1] 子树全部 > 源 — 需要递归. 简化:
检查 refs[0] 与 refs[1] 的 id: refs[0].id < refs[1].id ? (BST: 左<右)
以及 root=rec0: rec0 的 refs 应指向两个子节点, 一切 id 递归可覆盖全部?
root rec0 payload: 00 ed 2c 00 00 | 00 00 00 00 | 01 00 ff ff ff ff | ee 2c 00 00
= 0x2ced, 0, 0x0001?, 0xffffffff(-1), 0x2cee?
嗯 rec0 的 payload 不是 u32 队列! 是 00 ed 2c 00 00... 首字节 00!
若偏移基准是 payload 起点后 1B: ed 2c 00 00 = 0x2ced = 11469 = SEG_D+11469 → rec80!
所以【u32 是未对齐的, 起点 = payload+1】!
验证 rec0: [00][u32 0x2ced][u32 0x0000][01][00 ff ff ff ff]? no...
或 [00][u32=0x2ced][u32=0x000000][01 00 ff ff][ff ff ee 2c][00 00]
换读法: payload+1 起: ed 2c 00 00=0x2ced(11469), 00 00 01 00=0x100(256), ff ff ff ff=-1, ee 2c 00 00=0x2cee(11470)
0x2ced=11469 -> rec80 rel? 之前算过 SEG_D+11469 在 rec80 rel=15 (V=6).
不对. 试 rec_start_rel: 11469 是哪个记录起点? rec80 起点 = ?"""
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

# 未对齐 u32 从 payload+1
h = 0; tot = 0
for (n, nid, V, ne, nxt) in recs:
    pl = nxt - ne - 4
    for off in range(1, pl-3):
        u = struct.unpack_from("<I", data, ne+off)[0]
        if u == 0 or u == 0xFFFFFFFF: continue
        tot += 1
        if u in relmap: h += 1
print(f"payload+1 起未对齐 u32 命中 relmap: {h}/{tot}")

# rec0 的解析
ne0 = recs[0][3]
p = data[ne0:recs[0][4]-4]
print("rec0 payload:", p.hex(" "))
for off in range(0, 16):
    u = struct.unpack_from("<I", p, off)[0]
    print(f"  off{off}: {u} ({hex(u)}) {'<- relmap rec'+str(relmap[u]) if u in relmap else ''}")
