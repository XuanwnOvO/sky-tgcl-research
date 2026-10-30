# -*- coding: utf-8 -*-
# 联立求解 type 宽度：对每个组件收集值块长度集合，解 size = c4 + sum(w[type])
# Marker: 4 props (1,16,16,16) -> 24B 全样本
# 假设数组=4(count)+n*elem? 先收集数据
import os, re, struct, collections
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"
lv = 'Dawn'
d = open(os.path.join(root, lv, 'Objects.level.bin'), 'rb').read()
o1, o2, o3, o4, o5 = struct.unpack_from('<5I', d, 24)
segC = d[o3:o4]
def s3(u):
    e = segC.find(b'\x00', u)
    return segC[u:e].decode('utf-8', 'replace')
segA, segB = d[o1:o2], d[o2:o3]
comps = []
for i in range(261):
    a, st, pc = struct.unpack_from('<3I', segA, i*12)
    comps.append((s3(a), st, pc))

seg = d[o4:]
ms = list(re.finditer(rb'BstNode_(\d{9,10})\x00', seg))
sizes = collections.defaultdict(collections.Counter)  # compIdx -> {bodylen: count}
for i, m in enumerate(ms):
    a, hl = m.start(), m.end()-m.start()
    e = ms[i+1].start() if i+1 < len(ms) else len(seg)
    body = seg[a+hl:e-4]
    if len(body) < 4: continue
    u = struct.unpack_from('<I', body, 0)[0]
    if u < 261:
        sizes[u][len(body)-4] += 1

# 打印单长度组件（最可解）
solved = []
for ci, cnt in sorted(sizes.items()):
    if len(cnt) == 1 and sum(cnt.values()) >= 5:
        L = next(iter(cnt))
        name, st, pc = comps[ci]
        types = [struct.unpack_from('<4I', segB, j*16)[2] for j in range(st, st+pc)]
        solved.append((L, ci, name, types, sum(cnt.values())))
solved.sort()
for L, ci, name, types, n in solved[:40]:
    print(f"{name:30s} props={types} 值块={L}B (n={n})")
