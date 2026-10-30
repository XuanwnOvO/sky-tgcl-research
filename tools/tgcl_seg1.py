import struct, re, os
root = r'd:\新建文件夹\LightEncounters\Children of the Light\Levels'
d = open(os.path.join(root,'Dawn','Objects.level.bin'),'rb').read()
o1,o2,o3,o4,o5 = struct.unpack_from('<5I', d, 24)
seg1 = d[o1:o2]
# seg1 低熵 (3.87) u32 交替: 0x8ea3 | 0 | 7 | 0x4600 | 7 | 0x14 | 0x3544 | 0x1b | 0x3d | 0x765a | 0x58 ...
# 模式: (小值 u32, 中值 u32) 交替 → (值, 长度?) 或 (count, offset)。0x4600=17920 < 51824(seg2 len)!
# 假设 seg1 = 变长记录索引: [u32 X][u32 off][u32 Y][u32 off2]... off 指向 seg2? 17920*16=286720 > seg2 len. 17920 < 51824 → seg2 字节偏移? 
# 试: seg1[12]=0x4600=17920 → seg2[17920:17920+16]:
seg2 = d[o2:o3]
for off in (0x4600, 0x3544, 0x765a, 0x4792, 0x4b47):
    print(hex(off), seg2[off:off+16].hex(' '))
# 若指向组件记录位置 → seg1 = prefab/节点模板索引表
# 检查 0x4600 处是否是 schema 记录对齐（16B 边界）: 17920/16=1120 ✓; 0x3544/16=0x354.4 ✗
# 13636/16=852.25 不是边界。可能指向 seg1 自身或 seg3:
seg3 = d[o3:o4]
for off in (0x4600, 0x3544, 0x765a, 0x8eae):
    print('seg3', hex(off), seg3[off:off+24])
