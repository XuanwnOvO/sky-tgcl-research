import struct, re, os
root = r'd:\新建文件夹\LightEncounters\Children of the Light\Levels'
d = open(os.path.join(root,'Dawn','Objects.level.bin'),'rb').read()
o1,o2,o3,o4,o5 = struct.unpack_from('<5I', d, 24)
seg2 = d[o2:o3]
# seg2 按 16B 记录切: (u32 a, u32 b, u32 c, u32 d) — b 像 0x6dc4/0x18de/0xe9a/0x67d0 = 28004/6366/3738/26576 疑 seg3 字节偏移
# 验证: 取 seg2 记录的 b 值, 看是否指向 seg3 内 NUL 结尾键名:
seg3 = d[o3:o4]
n = len(seg2)//16
print('seg2 16B recs:', n)
for k in range(0, n, n//15):
    a,b,c,e = struct.unpack_from('<4I', seg2, k*16)
    nm = seg3[b:b+24].split(b'\x00')[0] if b < len(seg3) else b'OOB'
    print(k, a, b, c, e, '→', nm.decode('latin1'))
# b 指向键名则 schema = [type?, keyOff, ?, ?] — 组件 schema 表实锤!
