# -*- coding: utf-8 -*-
"""segD v20: V=20 payload 字段级解码 + Marker(组件索引型) 4个引用目标追踪
目标: 判定 Marker 的 transform 值是否通过引用存到别处 -> 解释 24B 矛盾"""
import struct, re
from collections import Counter

data = open(r"Children of the Light\Levels\Dawn\Objects.level.bin", "rb").read()
SEG_D, END = 91988, 2134009
pat = re.compile(rb"BstNode_(\d+)\x00")
nodes = [(m.start(), int(m.group(1))) for m in pat.finditer(data, SEG_D)]
recs = []
for i, (n, nid) in enumerate(nodes):
    V = struct.unpack_from("<I", data, n - 4)[0]
    ne = n + 8 + len(str(nid)) + 1
    nxt = nodes[i + 1][0] if i + 1 < len(nodes) else END - 4
    recs.append((n, nid, V, ne, nxt))
relmap = {(r[0] - 4) - SEG_D: j for j, r in enumerate(recs)}

# ---- 1) V=20 payload 未对齐 u32 扫描: 统计命中 rec_start_rel 的位置(相对 payload) ----
hitpos = Counter()
for (n, nid, V, ne, nxt) in recs:
    if V != 20:
        continue
    pl = nxt - 4 - ne
    for off in range(0, pl - 3):
        u = struct.unpack_from("<I", data, ne + off)[0]
        if u in relmap:
            hitpos[off] += 1
print("V=20 payload 内引用命中位置(off:count) top20:", hitpos.most_common(20))
print("V=20 总记录:", sum(1 for r in recs if r[2] == 20))

# ---- 2) 找 Marker 组件索引 ----
# segB: 3176..55000 每行16B (a,keyOff,type,e); segC 字符串池 55000..91988
def cstr(off):
    e = data.index(b"\0", off)
    return data[off:e].decode("utf-8", "replace")
marker_rows = []
for i in range(3239):
    o = 3176 + i * 16
    a, ko, tp, e = struct.unpack_from("<IIII", data, o)
    nm = cstr(ko)
    if "Marker" in nm:
        marker_rows.append((i, a, nm, tp, e))
print("Marker 行:", marker_rows[:10])

# ---- 3) Marker 型记录(V=7 组件索引型) rest 4 个 u32 的目标解析 ----
# 组件索引 -> compId
compnames = {}
for i in range(261):
    o = 44 + i * 12
    no, ss, pc = struct.unpack_from("<III", data, o)
    compnames[i] = cstr(no)
markerComp = {i for i, nm in compnames.items() if "Marker" in nm}
print("Marker compId:", markerComp)

def target_of(u):
    j = relmap.get(u)
    if j is None:
        return None
    (n, nid, V, ne, nxt) = recs[j]
    return (j, nid, V, nxt - 4 - ne)

stats = Counter()
for (n, nid, V, ne, nxt) in recs:
    pl = nxt - 4 - ne
    if pl < 4:
        continue
    c = struct.unpack_from("<I", data, ne)[0]
    if c not in markerComp:
        continue
    rest = data[ne + 4: nxt - 4]
    ts = []
    for k in range(0, len(rest) - 3, 4):
        u = struct.unpack_from("<I", rest, k)[0]
        ts.append(target_of(u))
    for t in ts:
        if t:
            stats[t[2]] += 1
        else:
            stats["miss"] += 1
print("Marker rest u32 目标 V 分布:", stats.most_common(15))

# ---- 4) 被引用目标样本 dump (前3个 V=20 目标) ----
shown = 0
for (n, nid, V, ne, nxt) in recs:
    pl = nxt - 4 - ne
    if pl < 4:
        continue
    c = struct.unpack_from("<I", data, ne)[0]
    if c not in markerComp:
        continue
    rest = data[ne + 4: nxt - 4]
    for k in range(0, len(rest) - 3, 4):
        u = struct.unpack_from("<I", rest, k)[0]
        t = target_of(u)
        if t and t[2] == 20 and shown < 3:
            j = t[0]
            tn, tid, tV, tne, tnxt = recs[j]
            print(f"Marker rec id={nid} -> ref 0x{u:x} rec id={tid} plen={tnxt-4-tne}:",
                  data[tne:tnxt-4][:50].hex(" "))
            shown += 1
    if shown >= 3:
        break
