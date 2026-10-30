import struct, re, os
root = r'd:\新建文件夹\LightEncounters\Children of the Light\Levels'
d = open(os.path.join(root,'Dawn','Objects.level.bin'),'rb').read()
o3, o4 = struct.unpack_from('<2I', d, 32)
keys = [k for k in d[o3:o4].split(b'\x00') if k]
seg = d[o4:]
starts = [m.start() for m in re.finditer(rb'BstNode_\d{9,10}\x00', seg)]
lens = [starts[i+1]-starts[i] for i in range(len(starts)-1)] + [len(seg)-starts[-1]]
# 391 头 64B: [u32 key][f32 val] 不对 — key 高变。反转: [f32 val][u32 0] 交替，值在 4 偏移。
# 实际 data: 0,0,0,0 | 0x3f082b1f | 0,0,0,0 | 0x3ea394d9 ... = [u32 0][f32]×8 → 8 个 float 属性，键索引不在此
# 那 8 个 float 的键是什么？→ 391 模板本身就是"固定 8 float 组件"（如 BoxCollider 尺寸或 Light 参数）
# 35B LEB 流解码出 setHair(0)/eventName(1)/Quest(4) 等键名混杂 → LEB 误切（0 索引过多）。
# 换判读 35B: data = 00 | f0 2c 00 00 | 00 | 01 | 9a 01 d7 6d | 00
#   u32@1=0x2cf0=11504... 这些是 seg4 节点文件序号? 之前 Dawn 首条 idA 也是 0x2ced 系。
# 而 391B 尾部 "0a 00 00 00"=10 前有 "9a 99 59 3f 00 00 00 3f 00 00 00 82 42" = (0.85,0.5,65.0) floats!
# 判定: 391B 尾部 = [f, f, f][u32 N]。N=10/6/15 = 子属性计数!
# 综合: 模板中段那些 0x2xxxxxxx 位模式其实是 float 大值? 0x3e000000≈0.125 之类。重看 188..264:
i391 = next(i for i,L in enumerate(lens) if L==391)
data = seg[starts[i391]:starts[i391]+lens[i391]][19:-4]
for off in range(184, 268, 4):
    fv, = struct.unpack_from('<f', data, off)
    iv, = struct.unpack_from('<I', data, off)
    tag = 'f' if 1e-8 < abs(fv) < 1e8 or fv == 0 else 'u'
    print(off, f'{fv:14.6g}', f'0x{iv:08x}', tag)
