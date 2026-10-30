# -*- coding: utf-8 -*-
"""segD v47: 换角度 — ref 可能是【全局属性池索引】.
Marker props = enabled(1), scale(16), quat(16), pos(16) — 4个属性, 但 payload 有 6 个 u32.
注意 ref 顺序: 若 [k1][k2] 之后 4 个 u32 对应 4 个 prop!
k1=0x19f6, k2=0x2463 = enabled/scale/quat/pos 的 key id? (segB keyOff → segC 偏移!)
验证: k1/k2/… 6个 u32 中前几个是否 = segB 行的 segC key 偏移?
Marker props 在 segB 的 keyOff: enabled=?, scale=?, quat=?, pos=?
若 keyOff 值正好等于 refs 值 → refs 是 keyOff 引用!"""
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
rows = []
for j in range(c2):
    a, ko, t, e = struct.unpack_from("<4I", data, o2 + j*16)
    rows.append((a, s3(ko), t, e, ko))

ci = [i for i, c in enumerate(comps) if c[0] == "Marker"][0]
nm, st, pc = comps[ci]
print("Marker props segB 行:")
mk_keys = set()
for p in range(pc):
    r = rows[st + p]
    print(f"  prop{p}: key={r[1]} type={r[2]} keyOff={r[4]} ({hex(r[4])})")
    mk_keys.add(r[4])

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

# Marker payload u32 vs keyOff
for j in bycomp["Marker"][:3]:
    n, nid, V, ne, nxt = recs[j]
    pl = nxt - ne - 4
    us = [struct.unpack_from("<I", data, ne+k)[0] for k in range(4, pl-3, 4)]
    print(f"rec{j} u32s:", [hex(u) for u in us])
    print("  命中 keyOff 集:", [hex(u) for u in us if u in mk_keys])
