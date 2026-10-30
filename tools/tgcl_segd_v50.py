# -*- coding: utf-8 -*-
"""segD v50: BST 排序检验 — 全部记录按文件顺序的 id 是否构成 BST 的数组表示?
堆性质: 父=i, 子=2i+1/2i+2? 检查 recs[i] 与 recs[2i+1], recs[2i+2] 的 id 大小关系.
以及: refs 的 rec-index 是否满足 ref < 源 (BST 数组中子节点在父之后?) 476中248<, 228> 不成立.
另一决定性测试: root rec0 (id=2310602845) 应是 BST 根. 其它所有 id < / > 根的分布?
或者 BST key 不是 id 而是 V + compIdx?
先检查【堆性质】(完全二叉树数组): recs[(i-1)//2] vs recs[i].id"""
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

ok_p = 0; bad_p = 0
for i in range(1, len(recs)):
    par = (i - 1) // 2
    if recs[i][1] < recs[par][1]: ok_p += 1
    else: bad_p += 1
print(f"min-heap (id): {ok_p}/{len(recs)-1}")

# 或者: refs 指向 (源索引的函数)? 检查 ref - 源index 分布
d = Counter()
segC = data[o3:o4]
def s3(u):
    e = segC.find(b"\x00", u)
    return segC[u:e].decode("utf-8", "replace")
comps = []
for i in range(c1):
    a, st, pc = struct.unpack_from("<3I", data, o1 + i*12)
    comps.append((s3(a), st, pc))
for j, (n, nid, V, ne, nxt) in enumerate(recs):
    pl = nxt - ne - 4
    if pl >= 4:
        f = struct.unpack_from("<I", data, ne)[0]
        if f < c1 and comps[f][0] == "Marker":
            for k in range(4, pl-3, 4):
                u = struct.unpack_from("<I", data, ne+k)[0]
                if u < len(recs): d[u - j] += 1
print("ref - 源index top:", d.most_common(10))
