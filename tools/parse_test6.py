import struct

src = r'd:\新建文件夹\LightEncounters\Children of the Light\Resources\Boot.lua.luac'
b = open(src, 'rb').read()

def u32(o): return struct.unpack_from('<I', b, o)[0]

def dump_hex(off, n=80):
    seg = b[off:off+n]
    return ' '.join(f'{x:02X}' for x in seg)

# After "Boot.lua\0" at 406 ends (string starts 406? "Data/..." starts at 406-? let's compute:
# child start 368: 01 00 (nupvals=1) | 19 00 00 00 (len 25) | 40 = ?
# Wait byte at 374 is 0x40 '@'. String "Data/Resources/Boot.lua" is 23 chars + null = 24, len field said 25?
# 0x19 = 25. Hmm string starts at 375? bytes: 40 44 61 74 61... -> 0x40 then 'D a t a'
# so maybe len=0x19=25 includes something, and 0x40 is '@'?? Or len is 24 and 0x40 is separate
# Let's map: 368: 01 00 | 00 00 19 00?? no.
# Fresh eyes: dump 368..406: 01 00 00 00 | 01 00 | 19 00 00 00 | 40 | 44 61 74 ...
# What if: nupvals(4)=1 -> upval desc: instack(1)=0? idx... 5.2 upvaldesc = instack,idx (2 bytes) = 01 00!
# then nprotos... but next is 19 00 00 00 = 25 = string len! then 40?? no, string len 25 then string starts
# at 376? bytes 376: 40 44 61 74 61 = "@Data"?? no string is "Data"...
# OR upval desc is 2 bytes (01 00), then source len(4) = 19 00 00 00 = 25?? then string 25 bytes starting
# 376: 40 44 61 74 61 2F...40+23+null = 25 bytes! 0x40='@'? No wait 25 bytes: '@Data/Resources/Boot.lua\0'?
# That's weird but 375+25 = 400. Then 1E 00 00 00 = ncode=30 at 400? bytes at 400: 6F 74... no.
# Hmm 400 shows 'ot.lua\0 1E 00 00 00' -> so string ends at 406, and 1E 00 00 00 (ncode=30) at 406!
# String start = 406-25 = 381? bytes at 381: 44 61 74 61 = 'Data'! YES
# So: 368: 01 00 00 00 | 01 00 | 19 00 00 00 ... wait 381-368=13
# layout: [00 00 00 00]@[368] = ??? 4 bytes
# [01 00 00 00]@372? no we saw 01 00 00 00 at 372: bytes 372-375 = 01 00 00 00? from dump:
# 368: 00 00 00 00 | 01 00 00 00 | 01 00 | 19 00 00 00 | 40 | 'Data...' 
# positions: 368-371=00000000, 372-375=01000000, 376-377=0100, 378-381=19000000?? 
# but dump shows: 00 00 00 00 01 00 00 00 01 00 19 00 00 00 40 44 61...
# index:        368 369 370 371 372 373 374 375 376 377 378 ...
# So: 368-371: 00 00 00 00 ; 372-375: 01 00 00 00 ; 376: 01 00 -> wait that's only 376,377 = 01,00
# then 378: 19 00 00 00 = len 25 -> string 382..406? but Data starts at... 
# bytes: 378=19,379=00,380=00,381=00,382=40,383=44('D')! So len at 378=25, string 382..407, ends 407?
# string = '@Data/Resources/Boot.lua\0'? 0x40='@' included? 382='@',383='D'... 
# OR string len includes a leading marker. Whatever: 'Data/Resources/Boot.lua\0' = 24 bytes at 383..406
# then 407: 1E 00 00 00 = ncode=30! then code 30*4=120 bytes at 411..530, remaining 18 bytes = debug
# Check: 411+120 = 531, file len 548, 17 bytes left: nparam,vararg,maxstack? etc.
ncode_off = 407
ncode = u32(ncode_off)
print('ncode=', ncode)
code = [u32(ncode_off+4+i*4) for i in range(ncode)]
print('instructions:', ' '.join(f'{c:08X}' for c in code[:10]))
p = ncode_off+4+ncode*4
print('after code off=', p, 'remaining=', 548-p)
print(dump_hex(p, 548-p))
