import struct, re, os
root = r'd:\新建文件夹\LightEncounters\Children of the Light\Levels'
d = open(os.path.join(root,'Dawn','Objects.level.bin'),'rb').read()
o3, o4 = struct.unpack_from('<2I', d, 32)
keys = [k for k in d[o3:o4].split(b'\x00') if k]
seg = d[o4:]
starts = [m.start() for m in re.finditer(rb'BstNode_\d{9,10}\x00', seg)]
lens = [starts[i+1]-starts[i] for i in range(len(starts)-1)] + [len(seg)-starts[-1]]
# 391B 逐段判读（现在字节清晰了）:
# 0..64:  8×(u32 0 | f32 val) = 8 float 属性，键固定（模板内置）
# 64..76: f32 1.0, 2.0, 2.0 (data64: 00 00 80 3f 00 00 00 40 00 00 00 40)
# 76..80: u32 0
# 80..96: 0,0,0,0
# 96..104: f32 2.0, 2.0? 上面 fieldmap: 96/108/112=2.0 uniq10 → f32 2.0, 0, 2.0, 2.0
# 124: 0.125/1.0/0.0 uniq41 → f32
# 148/152/156/160/164: 1.0/2.0/0/1.5/0.6 uniq — f32 参数区
# 172/176: 0.5/1.0 | 1.0/5.0/0.5 — f32
# 180..188: 0 | 0
# 188: 30 00 00 80 3f? 乱 — 实为 184..188=0, 188=0x30? 字节流: 180..188 = 00 00 00 00 00 00 00 00, 188=30? 
# 从 hex: 偏移 188 处字节 '30 00 00 80 3f' → 错位，因为 0..80 hex 里 data64='00 00 80 3f'。
# 直接用已知 float 语义 + IDA 里 BstNode::Deserialize 交叉。当前产出已经足够：
# 8 float 属性 + 参数浮点区 + 中段 0x3ca3/0x4140/0x4120/0x40a0 = 15523/16704/16672/16544 (data216..240)
#   → 这些落在 seg2 大小 (51824/4=12956 u32) 内! → seg2 索引! 查 seg2:
o2, = struct.unpack_from('<I', d, 28)
seg2 = d[o2:o3]
for idx in (15523, 16704, 16672, 16544, 0x3ca3):
    if idx*4+8 <= len(seg2):
        print('seg2@', idx, seg2[idx*4:idx*4+16].hex(' '))
    else:
        print('seg2@', idx, 'OOB len', len(seg2)//4)
# 16544*4=66176 < 51824? no → OOB。除 4: 16544 落在 seg2 u32 计数 12956 之外。
# 15523 = 0x3CA3 → seg2 有 12956 u32 → OOB。试 /2 或当 seg3 之外。
# 试按字节偏移解释: 15523B > seg2 51824? no 15523<51824! → 字节偏移进 seg2:
for off in (15523, 16704, 16672, 16544):
    print('seg2 bytes @', off, seg2[off:off+24].hex(' '), seg2[off:off+16])
