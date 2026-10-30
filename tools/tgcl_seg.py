import struct
d = open(r'd:\新建文件夹\LightEncounters\Children of the Light\Levels\Dawn\Objects.level.bin','rb').read()
ver, = struct.unpack_from('<I', d, 4)
c1,c2,c3,c4 = struct.unpack_from('<4I', d, 8)
o1,o2,o3,o4,o5 = struct.unpack_from('<5I', d, 24)
print(f'ver={ver} counts=({c1},{c2},{c3},{c4}) offs=({o1},{o2},{o3},{o4},{o5}) size={len(d)}')
# o1..o4 是 4 个段起点，o5 是文件大小。段长度：o2-o1, o3-o2, o4-o3, o5-o4
print('seg lens:', o2-o1, o3-o2, o4-o3, o5-o4)
# 头后面 44 字节前还有没有 0x2C=44 头。检查 o1 前的 44..48
# dump 头部 hex
print(d[:64].hex(' '))
# 段1: 44..3176 —— 可能是字符串/属性键表
seg1 = d[o1:o2]
# 看是否 NUL 分隔键名
keys = seg1.split(b'\x00')
print('seg1 tokens:', len(keys), 'first 20:', [k.decode('latin1') for k in keys[:20]])
# seg2: 3176..55000
seg2 = d[o2:o3]
print('seg2 head hex:', seg2[:64].hex(' '))
# seg3: 55000..91988 属性字符串区?
seg3 = d[o3:o4]
s3 = seg3.split(b'\x00')
print('seg3 tokens:', len(s3), 'first 15:', [k.decode('latin1') for k in s3[:15]])
# seg4: 91988..end 节点区
seg4 = d[o4:]
print('seg4 head hex:', seg4[:96].hex(' '))
print('seg4 head ascii:', seg4[:80])
