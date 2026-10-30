import struct, re, os, math
root = r'd:\新建文件夹\LightEncounters\Children of the Light\Levels'
# 147B 结构已明（样本完整判读）：
# data0 u32 0 | data4 quat 4f (单位) | data20 u32 0 | data24 3f = dir/rot2 (0.595,-0.436,-0.163) | data36 0
# data40 3f (0.541,-0.426,-0.296) | data52 0 | data56 3f pos(286,167,249) | data68 3f scale(1,1,1)
# data80 zeros | data88 u32 3 | data92 f 80.0 | data96 0 | data100 f 120.0 | ... | data116 -1.0 | data120 0
# quat 419/518 ok → 99 条不是 quat 开头 → 147B 模板有两个子型? 或 quat 后跟 w 在前面?
# 试 w-first: quat = (w=0.581? no) 试 data4 3f + data16 1f:
#   (0.581,-0.041,-0.813) + w@data16=0.0 → 不单位
# 99 bad 可能是 quat=(x,y,z,w) 顺序变体或另一组件同长。可接受。
# 35B 已明: [u8 0][u32 A][u8 0][u8 01][u32 hash][u8 0]  = name 19 + 12 data + 4 seq
#   A: 0x2cf0,0xf34,0x1692,0x2cf8,0x1c2d — 前 4 条和 0x2cfx 系列像节点ID引用, hash 4B = 事件/资源 hash
#   01 标志位。→ 35B = "引用/事件绑定节点" (id + hash)
# seg2 组件 schema 验证: 391B 中段小整数 (e-41~e-44 = 0x2xxxxxxx 位模式) 是 seg3 键索引×? 对一下:
# 391B data188..264 是 u32 键索引区。取一条 391B 的键索引, 查 seg3 字典:
d = open(os.path.join(root,'Dawn','Objects.level.bin'),'rb').read()
o3, o4 = struct.unpack_from('<2I', d, 32)
seg3 = d[o3:o4]
keys = [k for k in seg3.split(b'\x00') if k]
print('seg3 dict size', len(keys))
seg = d[o4:]
starts = [m.start() for m in re.finditer(rb'BstNode_\d{9,10}\x00', seg)]
lens = [starts[i+1]-starts[i] for i in range(len(starts)-1)] + [len(seg)-starts[-1]]
i391 = next(i for i,L in enumerate(lens) if L==391)
rec = seg[starts[i391]:starts[i391]+lens[i391]]
data = rec[19:-4]
# dump data 184..268 as u32
for off in range(184, 268, 4):
    v, = struct.unpack_from('<I', data, off)
    ks = keys[v] if v < len(keys) else b'??'
    print(off, v, ks.decode('latin1'))
