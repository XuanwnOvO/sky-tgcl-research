# -*- coding: utf-8 -*-
"""segD v14: 类型判定. 关键认识: payload 字节流 = TLV? 试从 Marker payload 首部找 1B type:
   Marker payload(28B): 06 00 00 00 | f6 19 00 00 | 63 24 00 00 | cc 02 9b 15 e7 09 bb 06...
   假设: [u32 compIdx][TLV 流]: 每 TLV = [1B key?]...  但后面全是 u32 小值.
   对比 V=6 记录 (1917条, plen=49): 也许 V 不是"类型"而是【父链/深度】.
   本脚本: 检查 V=7 记录 payload 第 4..12B 的两个 u32 —— 是否 = 邻近记录的引用计数,
   或者干脆检查 V=7 记录 payload 的 u32 数量与 schema props 数关系."""
import re, struct
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
rows = []
for j in range(c2):
    a, ko, t, e = struct.unpack_from("<4I", data, o2 + j*16)
    rows.append((a, s3(ko), t, e))

pat = re.compile(rb"BstNode_(\d+)\x00")
nodes = [(m.start(), int(m.group(1))) for m in pat.finditer(data, SEG_D)]
recs = []
for i, (n, nid) in enumerate(nodes):
    V = struct.unpack_from("<I", data, n-4)[0]
    ne = n + 8 + len(str(nid)) + 1
    nxt = nodes[i+1][0] if i+1 < len(nodes) else END - 4
    recs.append((n, nid, V, ne, nxt))

# 对每个组件: 收集 V=7 记录 payload, 尝试解释: payload = [ci][u32 X][u32 Y][值...]
# X/Y 之前是 segD 偏移 -> 可能指向共享默认值或引用对象
# Marker: plen=28 = ci(4)+X(4)+Y(4)+16B 值. props: enabled(bool) scale(vec3f) quat(quat4f) pos(vec3f) = 1+12+16+12 = 41B != 16
# 若 16B = quat(16)? 那 scale/pos 呢? 也许 scale/pos 是 0? 或 16B = 4 floats.
# 另一假设: 值块不是内联而是 CODER: 16B = [u32 a][u32 b][u32 c][u32 d] 是 4 个 segD 偏移 -> 指向 scale/quat/pos 数据
# 验证: rest 4 u32 (716,5531,2535,1723) 作为偏移 owner
import bisect
starts = [r[0] for r in recs]
def owner(a):
    j = bisect.bisect_right(starts, a) - 1
    if 0 <= j < len(recs) and recs[j][0] <= a < recs[j][4]: return j
    return None
hit = 0; tot = 0
for n,nid,V,ne,nxt in recs:
    pl = nxt-ne-4
    if V==7 and pl>=28:
        ci = struct.unpack_from("<I", data, ne)[0]
        if ci<c1 and comps[ci][0]=="Marker":
            rest = data[ne+12:nxt-4]
            for off in range(0,len(rest),4):
                u = struct.unpack_from("<I", rest, off)[0]
                tot += 1
                if SEG_D+u < END and owner(SEG_D+u) is not None: hit += 1
print("Marker rest u32 as offsets into segD records:", hit, "/", tot)
# 它们的绝对偏移(相对 SEG_D) 范围:
us = []
for n,nid,V,ne,nxt in recs:
    pl = nxt-ne-4
    if V==7 and pl>=28:
        ci = struct.unpack_from("<I", data, ne)[0]
        if ci<c1 and comps[ci][0]=="Marker":
            rest = data[ne+12:nxt-4]
            us += list(struct.unpack("<4I", rest))
print("Marker rest u32 range:", min(us), "-", max(us), "segD size:", END-SEG_D)
# 这些值域 (0x2cc~0x2ae8) 均在 segD 内 -> 几乎肯定是偏移
# 检查 owner 记录 payload 在该偏移后的内容: 是否是 16B quat / 12B vec3
for n,nid,V,ne,nxt in recs[:]:
    pl = nxt-ne-4
    if V==7 and pl>=28:
        ci = struct.unpack_from("<I", data, ne)[0]
        if ci<c1 and comps[ci][0]=="Marker":
            rest = data[ne+12:nxt-4]
            for off in range(0,16,4):
                u = struct.unpack_from("<I", rest, off)[0]
                j = owner(SEG_D+u)
                if j is not None:
                    r = recs[j]
                    d = SEG_D+u - r[0]
                    print("Marker id=%d ref@%d -> rec id=%d V=%d d=%d bytes=%s" % (nid, off, r[1], r[2], d, data[SEG_D+u:SEG_D+u+20].hex(' ')))
            break
