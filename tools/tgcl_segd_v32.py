# -*- coding: utf-8 -*-
"""segD v32: 对象结构假设验证.
新模型: rec0(root) 是【对象列表头】. 对象 = [u32 V][BstNode_<objId>][obj fields]
其中 V=2 的记录可能是【对象头】 (含 transform, objId 小). 检查 V=2 记录样本.
另外: 每个组件值块(V=7) 6个u32 引用 -> 引用 = 对象的对象头记录 rel?
测试: Marker refs (非root) 的目标记录里, 是否能找到 [u8 objId 对齐] 的规律.
直接 dump 每个目标 rel 处 ±16B."""
import re, struct, bisect
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
starts = sorted(((r[0]-4) - o4, j) for j, r in enumerate(recs))
keys = [s for s, _ in starts]

bycomp = {}
for j, (n, nid, V, ne, nxt) in enumerate(recs):
    pl = nxt - ne - 4
    if pl >= 4:
        f = struct.unpack_from("<I", data, ne)[0]
        if f < c1 and comps[f][0]:
            bycomp.setdefault(comps[f][0], []).append(j)

j = bycomp["Marker"][0]
n, nid, V, ne, nxt = recs[j]
pl = nxt - ne - 4
print(f"Marker rec{j}:")
for k in range(4, pl-3, 4):
    u = struct.unpack_from("<I", data, ne+k)[0]
    t = bisect.bisect_right(keys, u) - 1
    if t < 0:
        print(f"  ref 0x{u:x}: OOM")
        continue
    sj, tj = starts[t]
    r = recs[tj]
    rel = u - sj
    print(f"  ref 0x{u:x} -> rec{tj} (V={r[2]}, id={r[1]}, rel={rel})")
    a = o4 + u
    print("    bytes:", data[a:a+24].hex(" "))
    # 尝试: 若 rel 指向 payload, payload 内容 [00 ?objId? 00 ?levelId?] 可能 = (对象id, levelId)
