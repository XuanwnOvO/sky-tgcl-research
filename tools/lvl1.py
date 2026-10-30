import re, struct, collections

b = open(r'Children of the Light\Levels\Dawn\Objects.level.bin','rb').read()

# 头部: 'TGCL' + u32 ver=1, 然后 4 个递增值(261,3239,14651,42919)=?,
# 44,3176,55000,91988,2134009 = 段偏移（字符串区@44, ?@3176, Bst区@55000, ?@91988, size）
# 0x2c 起的记录序列: 看起来是 (u32 id, u32 len/id2) 对的数组
# 解析 0x2c~0x10b: 模式 07 00 00 00 00 46 00 00 = (7, 0x4600)?
vals = struct.unpack_from('<%dI' % ((0x110-0x2c)//4), b, 0x2c)
print('vals @0x2c:', vals[:20])

# 0x34 起: 07 00 00 00 | 00 46 00 00 ... 尝试 (type_idx u16, size u16)?
# 对比 91988 处
v2 = struct.unpack_from('<%dI' % (32), b, 91988)
print('@91988:', v2[:16])
print('ctx @91988:', repr(b[91988:91988+64]))

# 55000 处 Bst 区开头
print('@55000:', repr(b[55000:55000+64]))
print('@3176:', repr(b[3176:3176+64]))
print('@261:', repr(b[261:261+48]))
