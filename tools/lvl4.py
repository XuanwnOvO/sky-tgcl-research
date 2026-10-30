import struct, re

b = open(r'Children of the Light\Levels\Dawn\Objects.level.bin','rb').read()

# 记录格式假设: name NUL | u8 depth/flag | ... 子节点链
# BstNode_2819097706\x00 后跟 \x01 → flag=1, 然后下一行: d6 1e 00 00 | 6a 04 08 | 'MemAp18Misfit5' NUL | ff ff ff ff | 00 ef 2c 00 | 00 ff ff ff ff | 01
# "MemAp18Misfit5" = prefab 名! 偏移 0x2cef = 前一条记录 idx 区
# 模式: u32 = prefab 名字符串偏移(0x1ed6), u8 len(0x04=4?), ...
# 0x1ed6 处应指向字符串 'MemAp18Misfit5'
print(repr(b[0x1ed6:0x1ee8]))
# 6a 04 08 → 0x46a = 该对象数据大小? 0x08=?
print(repr(b[0x46a:0x47a]))

# 第一条 BstNode_2310602845: 后面 ed2c 0000 0000 0000 0100 ffffffff ee2c 0000 0100 0000
# 0x2ced/u 0x2cee → 相邻索引! → 是 (childOffset u16, ?, parentRef) 
# ffffffff = 无父。 0x2cee = 下一条索引 → 树结构: 记录含 firstChild u32 + parent u32
# 结构: name NUL | u32 firstChild(或self-ref链) | u32 parent | u32 sibling...
ea = b.find(b'BstNode_2310602845\x00')+19
print('rec1 raw:', b[ea:ea+24].hex())
u = struct.unpack_from('<6I', b, ea)
print([hex(x) for x in u])
# 验证 0x2ced 处是什么
print('@0x2ced:', repr(b[0x2ced:0x2ce0+40]))
