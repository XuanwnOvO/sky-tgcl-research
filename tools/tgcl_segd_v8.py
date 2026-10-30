# -*- coding: utf-8 -*-
"""segD v8: V=7 类记录 (payload = [u32 compIdx][u32 k1][u32 k2]) 的 u32 分布 & 与 c3/c4 对齐"""
import re, struct
from collections import Counter, defaultdict

P = r"Children of the Light\Levels\Dawn\Objects.level.bin"
data = open(P, "rb").read()
o1, o2, o3, o4, o5 = struct.unpack_from("<5I", data, 24)
c1, c2, c3, c4 = struct.unpack_from("<4I", data, 8)
SEG_D, END = o4, o5
segC = data[o3:o4]

comps = []
for i in range(c1):
    a, st, pc = struct.unpack_from("<3I", data, o1 + i*12)
    e = segC.find(b"\x00", a)
    comps.append((segC[a:e].decode(), st, pc))

pat = re.compile(rb"BstNode_(\d+)\x00")
nodes = [(m.start(), int(m.group(1))) for m in pat.finditer(data, SEG_D)]
recs = []
for i, (n, nid) in enumerate(nodes):
    V = struct.unpack_from("<I", data, n-4)[0]
    ne = n + 8 + len(str(nid)) + 1
    nxt = nodes[i+1][0] if i+1 < len(nodes) else END - 4
    recs.append((n, nid, V, ne, nxt))

# 统计所有记录 V 分布
vdist = Counter(r[2] for r in recs)
print("V dist:", vdist.most_common(20), "max:", max(vdist))

# V=7 记录: payload 首 u32 < 261
v7 = []
for n, nid, V, ne, nxt in recs:
    pl = nxt - ne - 4
    if V == 7 and pl == 12:
        ci, k1, k2 = struct.unpack_from("<3I", data, ne)
        if ci < c1:
            v7.append((nid, ci, k1, k2))
print("V=7 comp records:", len(v7))
k1s = Counter(x[2] for x in v7); k2s = Counter(x[3] for x in v7)
print("k1 max:", max(k1s), "k1 min:", min(k1s), "distinct:", len(k1s))
print("k2 max:", max(k2s), "k2 min:", min(k2s), "distinct:", len(k2s))
# k1+? 与节点总数 11501 对比: k1 max vs 11501
print("k1 < 11501:", sum(1 for x in v7 if x[2] < 11501), "/", len(v7))
print("k2 < 11501:", sum(1 for x in v7 if x[3] < 11501), "/", len(v7))
# k1/k2 是否是 BstNode id?
idset = set(n[1] for n in nodes)
print("k1 in ids:", sum(1 for x in v7 if x[2] in idset), "k2 in ids:", sum(1 for x in v7 if x[3] in idset))

# V=7 但 plen != 12 或首 u32>=261 的记录样本
odd = [(nid, V, pl) for n,nid,V,ne,nxt in recs for pl in [nxt-ne-4] if V==7 and (pl!=12 or struct.unpack_from('<I',data,ne)[0]>=c1)]
print("V=7 odd:", len(odd), odd[:10])

# 其它 V 的记录 payload 首 u32 分布
for v in sorted(set(r[2] for r in recs)):
    if v == 7: continue
    cnt = 0; ex = []
    for n, nid, V, ne, nxt in recs:
        if V != v: continue
        pl = nxt - ne - 4
        cnt += 1
        if len(ex) < 2:
            ex.append((nid, pl, data[ne:min(nxt-4, ne+32)].hex(' ')))
    print(f"V={v} n={cnt} ex={ex}")

# Marker 样本重验: 之前的 24B 是否其实是 (k1,k2) 之外的——Marker plen=28 = 12 + 16: 12B 头 + 4×f32 scale?
for n, nid, V, ne, nxt in recs:
    pl = nxt - ne - 4
    if V == 7 and pl >= 12:
        ci = struct.unpack_from("<I", data, ne)[0]
        if ci < c1 and comps[ci][0] == "Marker":
            rest = data[ne+12:nxt-4]
            print("Marker: hdr k1=%d k2=%d rest16=%s as 4f=%s" % (
                struct.unpack_from("<I",data,ne+4)[0], struct.unpack_from("<I",data,ne+8)[0],
                rest.hex(' '), struct.unpack("<4f", rest)))
            break
# CandleObject plen=24: 12B 头 + 12B
for n, nid, V, ne, nxt in recs:
    pl = nxt - ne - 4
    if V == 7 and pl >= 12:
        ci = struct.unpack_from("<I", data, ne)[0]
        if ci < c1 and comps[ci][0] == "CandleObject":
            rest = data[ne+12:nxt-4]
            print("Candle: k1=%d k2=%d rest=%s as3f=%s" % (
                struct.unpack_from("<I",data,ne+4)[0], struct.unpack_from("<I",data,ne+8)[0],
                rest.hex(' '), struct.unpack("<3f", rest)))
            break
# Enable plen=20: 12B头 + 8B
for n, nid, V, ne, nxt in recs:
    pl = nxt - ne - 4
    if V == 7 and pl >= 12:
        ci = struct.unpack_from("<I", data, ne)[0]
        if ci < c1 and comps[ci][0] == "Enable":
            rest = data[ne+12:nxt-4]
            print("Enable: k1=%d k2=%d rest=%s as2f=%s as2u=%s" % (
                struct.unpack_from("<I",data,ne+4)[0], struct.unpack_from("<I",data,ne+8)[0],
                rest.hex(' '), struct.unpack("<2f", rest), struct.unpack("<2I", rest)))
            break
