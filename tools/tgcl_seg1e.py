import struct, re, os
root = r'd:\新建文件夹\LightEncounters\Children of the Light\Levels'
d = open(os.path.join(root,'Dawn','Objects.level.bin'),'rb').read()
o1,o2,o3,o4,o5 = struct.unpack_from('<5I', d, 24)
seg1 = d[o1:o2]; seg3 = d[o3:o4]
# 顺序是 (off, len)! 条目 = (off, prefixLen): 名 = seg3[off-prefixLen : off] + seg3[off : +NUL]
# 验证: (17920,7) → seg3[17913:17920]+seg3[17920:..NUL]:
for a,b in [(17920,7),(20,7),(27,13636)]:
    print(seg3[a-b:a].decode('latin1','replace'), '+', seg3[a:a+40].split(b'\x00')[0].decode('latin1'))
# (13636,27): 前缀 27 字符 = seg3[13609:13636] + 'LevelMesh'
print('prefix27:', seg3[13609:13636])
print('full:', (seg3[13609:13636]+seg3[13636:13636+30].split(b'\x00')[0]))
# 那条目对遍历顺序: k=0 (36515,0)? 但 (36515,0) 应该是 (off=36515, plen=0) → 'IfEnabled' ✓
# 重新按 (off, plen) 解析全部 783 条:
names=[]
for k in range(0, len(seg1)-4, 8):
    off, plen = struct.unpack_from('<2I', seg1, k)
    full = seg3[off-plen:off+64].split(b'\x00')[0].decode('latin1')
    names.append(full)
print(len(names))
print(names[:30])
