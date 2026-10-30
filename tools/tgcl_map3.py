# -*- coding: utf-8 -*-
# 终局解析器：payload = u32 compIdx + 属性值块（按 segA[compIdx] 的 schema 逐字段读）
import os, re, struct, collections, json
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"
lv = 'Dawn'
d = open(os.path.join(root, lv, 'Objects.level.bin'), 'rb').read()
o1, o2, o3, o4, o5 = struct.unpack_from('<5I', d, 24)
segC = d[o3:o4]
def s3(u):
    e = segC.find(b'\x00', u)
    return segC[u:e].decode('utf-8', 'replace')
segA = d[o1:o2]
segB = d[o2:o3]
comps = []
for i in range(261):
    a, st, pc = struct.unpack_from('<3I', segA, i*12)
    comps.append((s3(a), st, pc))

# 打印几个组件的 schema（键名+type）
for name in ['Marker', 'CandleObject', 'Enable', 'LevelMesh', 'IfEnabled']:
    ci = [i for i, c in enumerate(comps) if c[0] == name][0]
    _, st, pc = comps[ci]
    print(f"== compIdx {ci}: {name} props={pc}")
    for j in range(st, st+pc):
        a, keyOff, t, e = struct.unpack_from('<4I', segB, j*16)
        print(f"   row{j}: a={a} key={s3(keyOff)!r} type={t} e={e}")
