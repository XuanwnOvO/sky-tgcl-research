# -*- coding: utf-8 -*-
# 值域混合：一半是小值/计数，还有 1073741824(2.0f 位型)/1065353216(1.0f) —— 其实是 float！
# 结论修正：组件索引型块里，u32 序列就是属性值流（bool 打包成 u32 位、float 就是 f32、
# 小整数=枚举），且 Marker 的 scale/quat/pos 是【数组 type16】=  count+elems？
# Marker 24B = enabled + scale + quat + pos 6 个 u32。
# 若 type16 数组 = u32 count + count*elem：scale(3f)+quat(4f)+pos(3f) 至少 40B>24 —— 矛盾
# 除非：数组属性【默认值不存储】，非默认才存！Marker 里全是默认 -> 只剩 6 个 u32 = ?
# 验证：找有 transform(type64) 的 LevelMesh 值块，看是否 40B transform 出现
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
ci_mesh = [i for i,c in enumerate(comps) if c[0]=='LevelMesh'][0]

seg = d[o4:]
ms = list(re.finditer(rb'BstNode_(\d{9,10})\x00', seg))
shown = 0
sizes = collections.Counter()
for i, m in enumerate(ms):
    a, hl = m.start(), m.end()-m.start()
    e = ms[i+1].start() if i+1 < len(ms) else len(seg)
    body = seg[a+hl:e-4]
    if len(body) < 4: continue
    u = struct.unpack_from('<I', body, 0)[0]
    if u == ci_mesh:
        sizes[len(body)-4] += 1
        if shown < 4 and len(body) > 80:
            print(f"LevelMesh 值块 {len(body)-4}B:")
            hx = body[4:].hex()
            for k in range(0, min(len(hx), 480), 32):
                print(f"  +{k//2:3d}: {hx[k:k+32]}")
            shown += 1
print("LevelMesh 值块长度分布:", sizes.most_common(10))
