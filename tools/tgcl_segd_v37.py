# -*- coding: utf-8 -*-
"""segD v37: 假设 — Marker 的 6 个 u32 是【属性 key 名在 segC 的偏移】? 不对, segC 只有 37KB.
0x2463=9315 < segC size (91988-55000=36988=0x907C). 都可能!
测试: refs 是否命中 segC 中字符串起点, 读出的字符串是什么?"""
import re, struct
from collections import Counter

P = r"Children of the Light\Levels\Dawn\Objects.level.bin"
data = open(P, "rb").read()
o1, o2, o3, o4, o5 = struct.unpack_from("<5I", data, 24)
c1, c2, c3, c4 = struct.unpack_from("<4I", data, 8)
segC = data[o3:o4]
SC = o4 - o3  # segC size
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

# Marker refs -> segC 字符串
for j in bycomp["Marker"][:4]:
    n, nid, V, ne, nxt = recs[j]
    pl = nxt - ne - 4
    out = []
    for k in range(4, pl-3, 4):
        u = struct.unpack_from("<I", data, ne+k)[0]
        s = None
        if u < SC and segC[u-1:u] in (b"\x00", b""):
            cand = s3(u)
            if cand and cand.isprintable():
                s = cand
        out.append((hex(u), s))
    print(f"rec{j}:", out)
