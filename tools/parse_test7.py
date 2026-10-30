import struct

src = r'd:\新建文件夹\LightEncounters\Children of the Light\Resources\Boot.lua.luac'
b = open(src, 'rb').read()

def u32(o): return struct.unpack_from('<I', b, o)[0]

def dump_hex(off, n=80):
    seg = b[off:off+n]
    return ' '.join(f'{x:02X}' for x in seg)

# So the region at 407 has ncode=30 but values 0x10,0x13 repeated -> those are LINE NUMBERS not code!
# So layout is: ... nlineinfo(4)=30, lineinfo[30]  (debug lines!)
# Meaning after source string comes DEBUG lineinfo, not code.
# Revised layout for child proto: [linedef?][...][source][nlineinfo][lineinfo]...
# Hmm but main chunk had code first. Actually maybe order: header, protos?? no.
# New hypothesis for MAIN chunk layout (TGC custom, no source):
#   18: linedef(4)=0, lastlinedef(4)=0, nparam=0,vararg=1,maxstack=2 (26,27,28)
#   29: ncode(4)=30, code[30] (33..152)
#   153: nconst(4)=13, consts (..367)
#   368: nlineinfo(4)=0  <- the 00 00 00 00!
#   372: nprotos(4)=1? no wait 372-375=01 00 00 00 -> nprotos=1
#   376: child proto: 01 00 = ? hmm child: linedef(4)? 376-379 = 01 00 19 00? no
#   child at 376: bytes 01 00 | 19 00 00 00 | 40 | Data...
#   maybe: nlineinfo(2)? no...
#   child: linedef(4)=0x00190001? unlikely
#   OR child: nupvals(2)=1, upval name len(4)=25?? "Data/Resources/Boot.lua" as upval name? no that's source!
#   Actually maybe custom child: [linedef(2)=1][lastlinedef(2)=25]?? 0x0019=25! linedef=1,last=25? hmm
#   then [sourcelen(4)]=0x40?? no. then 40?
#   Wait: after 376 "01 00", 378: 19 00 00 00 = 25, then 382: 40 = ?
#   If string: len 25 at 378, string 382..407 = "@Data/Resources/Boot.lua\0"? 0x40='@' doesn't fit.
#   Unless len field is 24 (19 00 00 00 misaligned): try 379: 00 00 00 40?? no.
#   What if: 376: 01 00 = linedef(2)=1? 378: 19 00 = lastlinedef(2)=25? 380: 00 00 = nparam(1)=0,vararg(1)=0?
#   382: 40 = maxstack=0x40? no way (max 255 but 64? possible but weird)
#   383: string len?? byte at 383 = 0x44 'D'... no
# Try another split: 376: 01 00 19 00 00 00 40 as: linedef(4)=0x00190001?? 
# Hmm. What if child proto = [nupvals(4)]=0x00000100?? no.
# Let's brute: string "Data/Resources/Boot.lua\0" = 24 bytes, starts at 383, ends 406 inclusive of null? 
# 383+24=407. ncode?? at 407 = 1E 00 00 00 = 30.
# If 407 is nlineinfo=30 and lineinfo 30*4=120 -> 411..530, then 531: 00 00 00 00 = nprotos? =0
# 535: 01 00 00 00? = nupvals?? then 05 00 00 00 = len 5, "_ENV\0" -> upvalue name _ENV!
# So tail: [nprotos=0][nupvals=1]["_ENV\0"] = debug upvalue names. 
# So chunk ends with upvalue names. And the 407 nlineinfo=30 with lines 16..: plausible!
# Then child proto structure: [?? 376..382][source][nlineinfo][lineinfo][nprotos][nupvals][upvalnames]
# The "01 00 19 00 00 00 40" hmm... maybe: linedef(2)=1, lastlinedef(2)=0x19=25?? but 19 00 = 25 yes!
# then nparam(1)=0? vararg(1)=0? maxstack(1)=0x40?? no.
# OR linedef(4) little endian = 00 01 00 19?? no.
# Whatever - key insight: it's close to 5.2 with source present and 2-byte line fields
# Let's compare with real Lua 5.2 chunk of similar script structure via luac if available
print("see analysis comments")
print(dump_hex(368, 48))
print(dump_hex(531, 17))
