import struct, re, os
root = r'd:\新建文件夹\LightEncounters\Children of the Light\Levels'
d = open(os.path.join(root,'Dawn','Objects.level.bin'),'rb').read()
o3, o4 = struct.unpack_from('<2I', d, 32)
keys = [k for k in d[o3:o4].split(b'\x00') if k]
seg = d[o4:]
starts = [m.start() for m in re.finditer(rb'BstNode_\d{9,10}\x00', seg)]
lens = [starts[i+1]-starts[i] for i in range(len(starts)-1)] + [len(seg)-starts[-1]]
# 391B 头 64B 修正：field map 显示 4/12/20/28/36/44/52/60 是高变 float，0/8/16/32/48 低变
# 0 位 uniq16: u32 0..15 → 键索引 0..15! → 头 64B = [u8? no] — 试 [u32 key][f32 val]×8, key uniq 低!
i391s = [i for i,L in enumerate(lens) if L==391][:20]
for i in i391s[:4]:
    rec = seg[starts[i]:starts[i]+lens[i]]
    data = rec[19:-4]
    pairs=[]
    for k in range(8):
        kv, = struct.unpack_from('<I', data, k*8)
        fv, = struct.unpack_from('<f', data, k*8+4)
        pairs.append((kv, keys[kv].decode('latin1') if kv<len(keys) else '?', round(fv,3)))
    print(rec[19:37], pairs)
# 106B 头判读: 19..23 = 2e e4 87 bf? 上面 106 样本 data0 = float -0.066? 而位模式 uniq194 → 也可能是 [u32 key][f32]×?
# 106 data: 2e e4 87 bf | 0 | 41 bb 93 3e | 0 | 0 | 82 39 3e 3f... 交替 f,0 → 8 个 (f,0) 同 391 头型但 key=0
# 35B 12B data: [u8 0][u32 A][u8 0][u8 01][u32 hash][u8 0]
#   换判读: u32@20 = 0x00002cf0 → LEB? 试 LEB from data0:
i35 = [i for i,L in enumerate(lens) if L==35][:3]
for i in i35:
    rec = seg[starts[i]:starts[i]+35]
    data = rec[19:31]
    j=0; vals=[]
    while j < len(data):
        v=0; sh=0
        while True:
            b=data[j]; j+=1
            v |= (b&0x7f)<<sh; sh+=7
            if not b&0x80: break
        vals.append(v)
    print('35B LEB:', vals, [keys[v].decode('latin1') if v<len(keys) else hex(v) for v in vals])
