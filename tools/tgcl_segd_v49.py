# -*- coding: utf-8 -*-
"""segD v49: refs 语义仍未定. 换终极思路: BST = Binary Search Tree!
BstNode 名字暗示 BST. V = 值, id = BST key (hash). 记录 = BST 节点按【key 排序】存储!
排序验证: 节点 id 是否按某种顺序 (数字升序?) 排列? 显然不是 (2753888733, 1624802026...)
但 BST 中序遍历: 左子树<根<右子树. refs = [left, right] 子节点指针!
Marker rec64 payload: 06 [refs...] 但首个u32=6=compIdx. hmm.
其实 refs 6 个 u32 可能不是引用而是其它东西.
重新看 rec64: 06 00 00 00 | f6 19 00 00 | 63 24 00 00 | cc 02 00 00 | 9b 15 00 00 | e7 09 00 00 | bb 06 00 00
0x19f6=6646, 0x2463=9315, 0x2cc=716, 0x159b=5531, 0x9e7=2535, 0x6bb=1747
 BST 假设: 节点按 key=BST hash 存在数组中, refs = [left, right] 子节点指针!
root rec0 (id=2310602845) 是 BST 根. 每个节点 6 个 u32?
Marker 有 6 refs, LevelMesh 2 refs, DialogHintTimed 3 refs, CandleObject 5 refs — 不定长!
如果是 BST: 节点应有 left/right 两个指针. 6≠2. 除非 = [left,right,data...].
测试: 对 rec-index 解读, 检查 refs 指向的记录 id 与源 id 的大小关系:
BST: left < parent < right (按数字 key). 统计 refs 目标 id < 源 id 和 > 源 id 的比例."""
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

lt = gt = 0
for j in bycomp["Marker"]:
    n, nid, V, ne, nxt = recs[j]
    pl = nxt - ne - 4
    for k in range(4, pl-3, 4):
        u = struct.unpack_from("<I", data, ne+k)[0]
        if u >= len(recs): continue
        tid = recs[u][1]
        if tid < nid: lt += 1
        else: gt += 1
print(f"refs 目标 id < 源: {lt}, >= 源: {gt}")

# BST 中 left = 第一个 ref? 检查 refs[0] < 源 且 refs[1] > 源 (按 id)
l0 = g1 = n0 = 0
for j in bycomp["Marker"]:
    n, nid, V, ne, nxt = recs[j]
    pl = nxt - ne - 4
    if pl < 12: continue
    u0 = struct.unpack_from("<I", data, ne+4)[0]
    u1 = struct.unpack_from("<I", data, ne+8)[0]
    if u0 < len(recs) and recs[u0][1] < nid: l0 += 1
    if u1 < len(recs) and recs[u1][1] > nid: g1 += 1
    n0 += 1
print(f"refs[0]<源: {l0}/{n0}, refs[1]>源: {g1}/{n0}")
