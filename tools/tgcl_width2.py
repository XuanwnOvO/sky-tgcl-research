# -*- coding: utf-8 -*-
# 从具体值块逐字节解码，标定 type 宽度。
# AudioMixToHaptics: props=[1,1,4,4,4] 84B —— bool 84B?? 说明 bool 不是 1B！
# 逐块 dump hex + schema 键名，人工对齐
import os, re, struct
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
target = {c[0] for c in [('AudioMixToHaptics',0,0), ('AvatarPlayEmote',0,0), ('Marker',0,0)]}

seg = d[o4:]
ms = list(re.finditer(rb'BstNode_(\d{9,10})\x00', seg))
shown = 0
for i, m in enumerate(ms):
    a, hl = m.start(), m.end()-m.start()
    e = ms[i+1].start() if i+1 < len(ms) else len(seg)
    body = seg[a+hl:e-4]
    if len(body) < 4: continue
    u = struct.unpack_from('<I', body, 0)[0]
    if u >= 261: continue
    name, st, pc = comps[u]
    if name not in ('AudioMixToHaptics', 'AvatarPlayEmote', 'Marker'): continue
    keys = [struct.unpack_from('<4I', segB, j*16) for j in range(st, st+pc)]
    print(f"== {name} node={ms[i].group(1).decode()} 值块={len(body)-4}B")
    for (aa, ko, t, ee) in keys:
        print(f"   key={s3(ko)!r} type={t}")
    hx = body[4:].hex()
    for k in range(0, len(hx), 32):
        print(f"   +{k//2:3d}: {hx[k:k+32]}")
    shown += 1
    if shown >= 6: break
