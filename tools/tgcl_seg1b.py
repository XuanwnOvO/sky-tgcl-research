import struct, re, os
root = r'd:\新建文件夹\LightEncounters\Children of the Light\Levels'
d = open(os.path.join(root,'Dawn','Objects.level.bin'),'rb').read()
o1,o2,o3,o4,o5 = struct.unpack_from('<5I', d, 24)
seg1 = d[o1:o2]; seg3 = d[o3:o4]
# 0x4600/0x3544 指向 seg3 里的**组件类名**! seg1 = 组件字符串偏移索引。
# 但 seg1 模式是 (X, off) 交替: (7,0x4600)(7,0x14)... 试 [u32 count][u32 strOff]?
# 头: a3 8e 00 00 | 00 00 00 00 | 07 00 00 00 | 00 46 00 00 | 07 00 00 00 | 14 00 00 00 | 44 35 00 00 | 1b 00 00 00 | 3d 00 00 00 | 5a 76 00 00 ...
# 0x8ea3=36515 < seg3 len(36988)! → seg1[0] = seg3 偏移!
seg3[0x8ea3:0x8ea3+32]
pairs = []
for k in range(0, len(seg1)//4):
    v, = struct.unpack_from('<I', seg1, k*4)
    pairs.append(v)
# 全部值都 < seg3 len?
inr = sum(1 for v in pairs if v < len(seg3))
print('seg1 u32 count', len(pairs), 'in seg3 range:', inr, '/', len(pairs))
# 解读为 seg3 内字符串偏移表 (组件/类名索引):
names = []
for v in pairs[:20]:
    nm = seg3[v:v+40].split(b'\x00')[0]
    names.append(nm.decode('latin1'))
print(names)
# 头两个 0 是 null。模式: [0,0,7,0x4600...] 7 是啥? 可能 [len][off]。0x4600=17920 处 'Npc_MemoryPose'
# 7 = 名字长度? Npc_MemoryPose=15 不对。先输出 (v, next) 交替看:
alt = [(pairs[i], pairs[i+1]) for i in range(0, 24, 2)]
print('alt pairs:', alt)
