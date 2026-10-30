import struct, sys

# Debug: read our converted file the way unluac 5.2 expects
# Header: 1B 4C 75 61 52 00 01 04 04 04 08 00 + tail(6) = 18 bytes, then source string
b = open(r'D:\boot_std.luac','rb').read()
print(' '.join(f'{x:02X}' for x in b[:40]))
p = 18
n = struct.unpack_from('<I', b, p)[0]; p += 4
print('source len', n, b[p:p+n])
p += n
# proto: linedef(4) lastlinedef(4) nparam vararg maxstack ncode(4)
print('linedef', struct.unpack_from('<ii', b, p))
p += 8
print('nparam/vararg/maxstack', b[p], b[p+1], b[p+2]); p += 3
ncode = struct.unpack_from('<I', b, p)[0]; print('ncode', ncode)
