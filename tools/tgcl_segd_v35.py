# -*- coding: utf-8 -*-
"""segD v35: 已证 65% relmap 命中全是 u32=0 巧合. 引用机制重新思考.
Marker rec64 payload: 06 00 00 00 f6 19 00 00 63 24 00 00 cc 02 00 00 9b 15 00 00 e7 09 00 00 bb 06 00 00
refs = 0x19f6, 0x2463, 0x2cc, 0x159b, 0x9e7, 0x6bb — 都 < 0x3000
segD = 121,4021 B. 若这些是偏移, 单位可能是【4字节块】? 0x19f6*4 = 0x67d8=26584 — segD 大小内!
测试: refs*4 命中 relmap?  refs*2?  refs*8?
另: 0x2cc*4=0xB30=2864, relmap 中有没有 2864?"""
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
relmap = {(r[0]-4) - o4: j for j, r in enumerate(recs)}
segd_size = o5 - o4
print("segD size:", segd_size, hex(segd_size))

bycomp = {}
for j, (n, nid, V, ne, nxt) in enumerate(recs):
    pl = nxt - ne - 4
    if pl >= 4:
        f = struct.unpack_from("<I", data, ne)[0]
        if f < c1 and comps[f][0]:
            bycomp.setdefault(comps[f][0], []).append(j)

for mul, name in [(1,"x1"),(2,"x2"),(4,"x4"),(8,"x8")]:
    h = 0; tot = 0
    for j in bycomp["Marker"]:
        n, nid, V, ne, nxt = recs[j]
        pl = nxt - ne - 4
        for k in range(4, pl-3, 4):
            u = struct.unpack_from("<I", data, ne+k)[0]
            if u == 0 or u == 0xffffffff: continue
            tot += 1
            if u*mul in relmap: h += 1
    print(f"refs*{name}: {h}/{tot}")
    if h:
        # dump 一个命中
        for j in bycomp["Marker"]:
            n, nid, V, ne, nxt = recs[j]
            pl = nxt - ne - 4
            for k in range(4, pl-3, 4):
                u = struct.unpack_from("<I", data, ne+k)[0]
                if u and u != 0xffffffff and u*mul in relmap:
                    t = relmap[u*mul]
                    print(f"   {hex(u)}*{mul}={hex(u*mul)} -> rec{t} V={recs[t][2]} plen={recs[t][4]-recs[t][3]-4}")
                    print("   payload:", data[recs[t][3]:recs[t][4]-4].hex(" "))
                    break
            else: continue
            break
