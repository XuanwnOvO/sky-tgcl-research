# -*- coding: utf-8 -*-
"""segD v13: 终局判定. 假设: 节点 id 互相共享字符串/树片段; V=7 节点是【属性模板/原型】,
   payload 里的 u32 全是 segD 相对偏移 -> 指向【共享值块】.
   决定性检查: 对一个 V=7 记录(如 LevelMesh plen=12: [compIdx][k1][k2]),
   owner(k1) 记录的 payload 在 d 偏移处开始的字节是否构成 LevelMesh 的属性值!
   更强假设: k1/k2 不是指针而是【共享节点】, 该节点 payload 就是值块."""
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
comps = []
for i in range(c1):
    a, st, pc = struct.unpack_from("<3I", data, o1 + i*12)
    comps.append((s3(a), st, pc))

pat = re.compile(rb"BstNode_(\d+)\x00")
nodes = [(m.start(), int(m.group(1))) for m in pat.finditer(data, SEG_D)]
recs = []
for i, (n, nid) in enumerate(nodes):
    V = struct.unpack_from("<I", data, n-4)[0]
    ne = n + 8 + len(str(nid)) + 1
    nxt = nodes[i+1][0] if i+1 < len(nodes) else END - 4
    recs.append((n, nid, V, ne, nxt))
starts = [r[0] for r in recs]
def owner(a):
    j = bisect.bisect_right(starts, a) - 1
    if 0 <= j < len(recs) and recs[j][0] <= a < recs[j][4]:
        return j
    return None

# LevelMesh V=7 记录: plen=12 = [ci][k1][k2]
lm = []
for i,(n,nid,V,ne,nxt) in enumerate(recs):
    pl = nxt-ne-4
    if V==7 and pl>=12:
        ci = struct.unpack_from("<I", data, ne)[0]
        if ci < c1 and comps[ci][0]=="LevelMesh":
            lm.append((i, nid, *struct.unpack_from("<2I", data, ne+4)))
print("LevelMesh V7 recs:", len(lm))
# k1/k2 的 owner 记录的 V 值分布
vs = Counter()
for i, nid, k1, k2 in lm:
    j = owner(SEG_D+k1)
    if j is not None: vs[recs[j][2]] += 1
print("k1-owner V dist:", vs.most_common(10))
# 检查同一 k1 被多个 LevelMesh 共享?
k1s = Counter(k1 for _,_,k1,_ in lm)
print("distinct k1:", len(k1s), "top:", k1s.most_common(5))
k2s = Counter(k2 for _,_,_,k2 in lm)
print("distinct k2:", len(k2s), "top:", k2s.most_common(5))
# k1 共享记录的 payload 是什么
top_k1 = k1s.most_common(1)[0][0]
j = owner(SEG_D+top_k1)
r = recs[j]
off = SEG_D+top_k1 - r[0]
print("top k1=%d owner rec id=%d V=%d, offset in rec=%d" % (top_k1, r[1], r[2], off))
print("bytes there:", data[SEG_D+top_k1:SEG_D+top_k1+64].hex(' '))

# 再看 LevelMesh 名下常见字符串 resourceName: V=10 记录 (n=108) 样本
# V=10 记录 payload 是否含字符串?
n10 = [r for r in recs if r[2]==10][:3]
for r in n10:
    print("V10 rec id=%d payload=%s" % (r[1], data[r[3]:r[4]-4].hex(' ')))
