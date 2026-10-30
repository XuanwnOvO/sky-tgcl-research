import struct, re, os
root = r'd:\新建文件夹\LightEncounters\Children of the Light\Levels'
# 突破！188..268 混合: 部分命中 seg3 键 (setHair/b/a/disableEmotes), 部分是 0x8xxxxxxx 高位模式。
# 2147483696 = 0x80000010 → 高位标志 + 低 31 位键索引 0x10=16
# 63=b, 62=a → 直接索引。768=disableEmotes 直接索引? 768<2542 ✓
# 1288490240=0x4CCCCC80? = 0x4CCCCC80 → 高位 0x4CCC... 奇怪。其实是 float 3.2e8?
# 修正判读：这些不是整齐 u32 数组，是变长编码! 试 varint / LEB128:
d = open(os.path.join(root,'Dawn','Objects.level.bin'),'rb').read()
o3, o4 = struct.unpack_from('<2I', d, 32)
keys = [k for k in d[o3:o4].split(b'\x00') if k]
seg = d[o4:]
starts = [m.start() for m in re.finditer(rb'BstNode_\d{9,10}\x00', seg)]
lens = [starts[i+1]-starts[i] for i in range(len(starts)-1)] + [len(seg)-starts[-1]]
i391 = next(i for i,L in enumerate(lens) if L==391)
data = seg[starts[i391]:starts[i391]+lens[i391]][19:-4]
# 从 data184 开始按 LEB128 流解:
i = 184
vals=[]
while i < 280:
    v=0; sh=0
    while True:
        b = data[i]; i+=1
        v |= (b&0x7f)<<sh; sh+=7
        if not b&0x80: break
    vals.append((i,v, keys[v] if v<len(keys) else b''))
for v in vals[:25]: print(v)
