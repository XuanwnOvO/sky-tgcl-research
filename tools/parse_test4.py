import struct

src = r'd:\新建文件夹\LightEncounters\Children of the Light\Resources\Boot.lua.luac'
b = open(src, 'rb').read()

def u32(o): return struct.unpack_from('<I', b, o)[0]

off = 368
# Layout guess v2: nupvals(4)=0? then nprotos(4)=1, child:
#   nupvals(4)? = 0x00000100?? no...
# Try: 00 00 00 00 = upvalue count? OR padding
# Alternative: maybe it's: nupvals(4)=0, nprotos(4)=1, child proto:
#   linedef(4)=1? bytes 01 00 00 00 = 1! then lastlinedef(4)=0x00001900? no
# bytes child: 01 00 00 00 | 01 00 | 19 00 00 00 | 40 | 44 61 74 61 ...
# Interpretation C: linedef=1 (4B), nparam=1? vararg=0? maxstack=1? -> 01 00 | 19 00 ...
# Hmm "01 00" then "19 00 00 00" then 0x40 then string len 0x19=25
# What if: linedef(4)=1, then... "01 00" could be numparams=1,vararg=0, maxstack... no 2 bytes only
# What if custom: nupvals(2)=1? then source len(4)=25, source string, then ncode(4)=30
# So child = [nupvals:2][sourcelen:4][source][ncode:4][code...]
# And before child: 00 00 00 00 01 00 00 00 -> hmm then nupvals at off+? 
# Try: off368: 00 00 00 00 = ?(4), 01 00 00 00 = nprotos=1, child starts 376: 01 00 = nupvals(2)=1,
# then 19 00 00 00 = len 25, source "Data/Resources/Boot.lua\0", then 1E 00 00 00 = ncode=30!
# YES! ncode=30 matches! then code 30*4 bytes of line info?? wait next bytes are 10 00 00 00 repeated...
# Those look like DEBUG line info! 0x10=16,0x13=19... these are line numbers per instruction!
# So actually maybe those 4-byte values ARE code (instructions)? 0x10 as instruction = opcode 16 MOVE? no...
# OR these are the "line defined" debug entries
# Hmm but main chunk had code at 33 with real instructions 0C 00 40 00...
# For child: ncode=30 at off=368+2+4+25+... let me just compute
child = 368
nup = struct.unpack_from('<H', b, child)[0]
slen = u32(child+2)
srcstr = b[child+6:child+6+slen].rstrip(b'\x00')
p = child + 6 + slen
ncode = u32(p); p += 4
print(f'child: nupvals={nup} slen={slen} source={srcstr} ncode={ncode} codeoff={p}')
print('first code:', [hex(u32(p+i*4)) for i in range(6)])
# if these are line numbers (debug), real code might come after; check values
lines = [u32(p+i*4) for i in range(min(ncode,10))]
print('vals:', lines)
