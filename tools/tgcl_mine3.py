# -*- coding: utf-8 -*-
# 391B shader 块：uniform 名字前的头 157B + 名字后值域精确切分
import os, re, struct
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"
d = open(os.path.join(root, "DuskGraveyard", "Objects.level.bin"), "rb").read()
o4 = struct.unpack_from("<5I", d, 24)[3]
seg = d[o4:]
ms = list(re.finditer(rb"BstNode_(\d+)\x00", seg))
blk = None
for i, m in enumerate(ms):
    a = m.start()
    e = ms[i+1].start() if i+1 < len(ms) else len(seg)
    body = seg[a:e-4]; hl = m.end()-m.start(); p = body[hl:]
    if len(p) == 391 and b'u_texSpots' in p:
        blk = p; break
names = [b'u_texSpots', b'u_diffuseColor', b'u_normal', b'u_uvOffset', b'u_spotsColor']
offs = {n: blk.find(n) for n in names}
print("名字偏移:", offs)
# 名字间空隙 = 值
gaps = [(offs[names[k]], offs[names[k+1]]) for k in range(len(names)-1)]
print("串间隔（值域大小）:", [b-a for a, b in gaps])
# 名字尾(含\0)到下一名字首之间
for k in range(len(names)-1):
    s = offs[names[k]] + len(names[k]) + 1  # 跳过 \0
    e = offs[names[k+1]]
    v = blk[s:e]
    if len(v) >= 4:
        print(f"{names[k].decode():16} 值域 {len(v):>2}B: {v[:16].hex(' ')} f32={[round(x,4) for x in struct.unpack_from('<3f' if len(v)>=12 else '<f', v, 0)]}")
    else:
        print(f"{names[k].decode():16} 值域 {len(v)}B: {v.hex(' ')}")
tail = blk[offs[names[-1]]+len(names[-1])+1:]
print("尾值域:", tail.hex(" "))
print("头 157B（第一个名字前）:")
print(blk[:157].hex(" "))
hdr = struct.unpack_from('<16f', blk, 0)
print("头按 f32×16:", [round(x,4) for x in hdr])
