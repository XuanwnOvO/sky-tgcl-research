# -*- coding: utf-8 -*-
"""segD v12: k1/k2 = segD 相对偏移指向的位置内容分类. 
   读取 data[SEG_D+k1] 处 u32 及其附近字节, 判断指向什么."""
import re, struct, bisect
from collections import Counter

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
        return j, recs[j]
    return None, None

v7 = []
for i,(n, nid, V, ne, nxt) in enumerate(recs):
    pl = nxt - ne - 4
    if V == 7 and pl >= 12:
        ci, k1, k2 = struct.unpack_from("<3I", data, ne)
        if ci < c1 and comps[ci][0]:
            v7.append((i, nid, ci, k1, k2, pl))

# 分类 k1 指向位置相对 owner 记录的偏移类型
rel_kind = Counter(); ex = []
for i,nid,ci,k1,k2,pl in v7:
    a = SEG_D + k1
    j, r = owner(a)
    if r is None:
        rel_kind["none"] += 1
        continue
    n_,nid_,V_,ne_,nxt_ = r
    d = a - n_
    if d < 4: rel_kind["preV"] += 1
    elif d < 8: rel_kind["inV/name boundary"] += 1
    elif a < ne_: rel_kind["inName"] += 1
    elif a < nxt_-4: rel_kind["inPayload+%d" % ((a-ne_)//4 if a>=ne_ else -1)] += 1
    else: rel_kind["tail4"] += 1
    if len(ex) < 12:
        ex.append((comps[ci][0], nid, k1, "owner=%d(id=%s,V=%d) d=%d" % (j, r[1], r[2], a-n_),
                   data[a:a+16].hex(' ')))
print("rel kind:", rel_kind.most_common(10))
for e in ex: print(" ", e)

# 若指向 payload 内某 u32 -> 可能是"属性值数组的元素指针"? 更可能: 这些 u32 是【值池】引用!
# 检查指向 payload 里的位置所读出的 u32, 是否一致 (即值是共享的)
# 也检查: k 值总和覆盖: 若 V=7 记录的 payload 12B 全是偏移, 28B Marker = 3偏移+4值?
# 反例检查: 把 k1,k2 后面的 16B 看作 4 个 u32, 判断这 4 个是否也是 segD 偏移!
mkhit = 0; tot = 0
for i,nid,ci,k1,k2,pl in v7:
    if pl < 28: continue
    a = ne if False else recs[i][3]
    rest = data[a+12:nxt] if False else data[recs[i][3]+12:recs[i][4]-4]
    for off in range(0, len(rest)-3, 4):
        u = struct.unpack_from("<I", rest, off)[0]
        tot += 1
        if u < len(data) - SEG_D and SEG_D + u < END:
            j, r = owner(SEG_D + u)
            if r is not None: mkhit += 1
print("extra-u32 as offsets pointing into records:", mkhit, "/", tot)
