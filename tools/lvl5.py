import struct, re

b = open(r'Children of the Light\Levels\Dawn\Objects.level.bin','rb').read()

# 精确对齐: name 'BstNode_2310602845\0' 结束后 1 字节 \x00 pad? 
# raw: name后 = ed 2c 00 00 | 00 00 00 00 | 01 00 | ff ff ff ff | ee 2c 00 00 | 01 00 00 00
# u32: 0x2ced | 0 | 0x00010000... 等等 raw 是 'ed2c0000 00000000 0100ffff ffffee2c 00000100 0000'
# 逐字节: ed2c0000 = 0x2ced, 00000000 = 0, 0100 = u16 1, ffffffff = -1, ee2c0000 = 0x2cee, 01000000 = 1
# → 结构: name | u32 selfIdx(0x2ced) | u32 ?(0) | u16 depth(1) | i32 parent(-1) | u32 nextIdx(0x2cee) | u32 flag(1)
# 0x2ced 是记录索引号! (11501 条, 索引范围?) 第二条 0x2cee = 11502? 不对 0x2cee=11502 > count.
# 但两条记录索引连续 → 索引号。parent=-1 = 根节点
pos = [m.start() for m in re.finditer(rb'BstNode_[0-9]+\x00', b)]
idxs = []
for p in pos[:5]:
    name_end = b.index(b'\x00', p) + 1
    ea = name_end
    if ea % 2: ea += 1
    u = struct.unpack_from('<Ii', b, ea)
    idxs.append(u)
print(idxs)

# 简化验证: 直接统计索引值域
ea0 = b.index(b'BstNode_2310602845\x00') + 19
print('first idx @', hex(ea0), struct.unpack_from('<I', b, ea0)[0])
