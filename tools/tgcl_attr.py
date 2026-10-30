import struct, re, os, math
root = r'd:\新建文件夹\LightEncounters\Children of the Light\Levels'
# 最后一块：属性值如何挂在节点上。391B 模板中段那些 15523/16704 等 u32 其实 = schema 行号?
# Dawn schema 3239 行, 15523 超界。但 DuskGraveyard schema 1948 行, 16704 也超界。
# 这些值 0x3ca3/0x4140 = 15523/16704 —— 可能是 seg3 字节偏移! seg3 len 36988: 15523/16704 < 36988 ✓
d = open(os.path.join(root,'Dawn','Objects.level.bin'),'rb').read()
o1,o2,o3,o4,o5 = struct.unpack_from('<5I', d, 24)
seg3 = d[o3:o4]
for off in (15523, 16704, 16672, 16544, 0x41):
    print(off, seg3[off:off+24])
