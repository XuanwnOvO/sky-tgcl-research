# -*- coding: utf-8 -*-
"""segD v54(实): Marker 4 个 prop 值的可能编码 + V=20 transform 解码.
Marker props: enabled(1), scale(16), quat(16), pos(16) — 4 prop, 6 u32 refs.
若 refs = [x1][x2][y1..y4]: 前 2 个 + 4 个. enabled 是 bool 1B?? 
换个真正的测试: DialogHintTimed 160 条 plen=16 = compIdx + 3 u32.
props? 查 schema. 且 CandleObject 24B, compIdx+5 u32.
看规律: refs 数 = prop 数 + 2? Marker: 4 props + 2 = 6 ✓; Candle: ? props + 2 = 5 → 3 props?
DialogHintTimed: 1 + ? props = 3 → ?  验证 schema prop 数!
若成立: [compIdx][k1][k2][per-prop u32 ref]. k1/k2 = 每记录公共头 (如 parent/对象链接).
然后 per-prop u32 = 该属性值的存储位置 (rec-index).
验证各组件: propCount+2 == (plen-4)/4 ?"""
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
    rows.append((a, s3(ko), t, e))

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

for cn in ["Marker", "CandleObject", "DialogHintTimed", "LevelMesh", "AudioMixToHaptics",
           "IfEnabled", "Enable", "MoteParams", "TerrainBlob", "Clump", "ShowHUDTimed",
           "CameraKeyFrame", "PlayAvatarAnimSeq", "Npc_MemoryPose", "SkyArtBookSetup", "RedeemReward"]:
    if cn not in bycomp: continue
    ci = [i for i, c in enumerate(comps) if c[0] == cn][0]
    nm, st, pc = comps[ci]
    j = bycomp[cn][0]
    n, nid, V, ne, nxt = recs[j]
    pl = nxt - ne - 4
    nref = (pl - 4) // 4
    types = [rows[st+p][2] for p in range(pc)]
    tc = Counter(types)
    print(f"{cn}: props={pc} refs={nref} plen={pl} propTypes={dict(tc)} match={(pc+2==nref)}")
