import struct
d = open(r'd:\新建文件夹\LightEncounters\Children of the Light\Levels\Dawn\Objects.level.bin','rb').read()
o4 = 91988
# 精确 dump 头 3 条记录原始字节，人工判读结构
seg = d[o4:o4+600]
i = 0
# 打印到下一个 BstNode_ 的字节距离
pos = [m for m in range(len(seg)) if seg.startswith(b'BstNode_', m)]
print('BstNode offsets in first 600B:', pos)
# 记录间隔 = 结构尺寸线索
# dump 第一条到第二条之间的完整 hex+ascii
a, b = pos[0], pos[1]
print(f'--- record 1: {b-a} bytes')
chunk = seg[a:b]
print(chunk.hex(' '))
print(repr(chunk))
b2 = pos[2] if len(pos)>2 else len(seg)
chunk2 = seg[b:b2]
print(f'--- record 2: {b2-b} bytes')
print(chunk2.hex(' '))
print(repr(chunk2))
