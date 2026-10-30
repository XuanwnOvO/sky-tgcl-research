import struct

src = r'd:\新建文件夹\LightEncounters\Children of the Light\Resources\Boot.lua.luac'
b = open(src, 'rb').read()

def u32(o): return struct.unpack_from('<I', b, o)[0]

def dump_hex(off, n=80):
    seg = b[off:off+n]
    return ' '.join(f'{x:02X}' for x in seg)

# Where does the "10 00 00 00" run start? Earlier dump showed at off=368+... let's find exact
# dump around 395-420
for start in (395, 400, 405, 410):
    print(start, dump_hex(start, 48))
