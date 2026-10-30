import struct

src = r'd:\新建文件夹\LightEncounters\Children of the Light\Resources\Boot.lua.luac'
b = open(src, 'rb').read()

def dump_hex(off, n=64):
    seg = b[off:off+n]
    return ' '.join(f'{x:02X}' for x in seg)

off = 368
# Try: nupvals(4)=0? No — maybe 4 bytes = num upvalues, then each upvalue "instack idx" etc.
# Bytes: 00 00 00 00 | 01 00 00 00 | 01 00 | 19 00 00 00 | 40 | "Data/Resources/Boot.lua\0" (24 bytes incl null)
# Hypothesis: after consts: nupvalues? Actually maybe: nupvalues=0 (4B), nparams... hmm
# Alternative hypothesis: custom layout: nprotos(4)=0? no, 00 00 00 00 then 01 00 00 00...
# Try: source length! In 5.2 chunk: after maxstack comes ncode. We did consts. Then nupvals(4), upval descs, nprotos(4)...
# Try: 00 00 00 00 = nupvalues(4)=0? Then 01 00 00 00 = nprotos(4)=1. Then child proto:
# In 5.2 proto: source? no. linedef(4), lastlinedef(4), nparam(1), vararg(1), maxstack(1), ncode(4)
# bytes at child start: 01 00 19 00 00 00 40 ... doesn't fit linedef as int
# Maybe custom: child starts with ncode? 01 00 00 00 = ncode=1?? then code 19 00 00 00 (VARARGPREP?), then
# then nconst 40?? no.
# Try hypothesis B: 00 00 00 00 = linedef/lastlinedef pair of TOP chunk (we already had linedef=0 last=0 at 18)
# Wait — maybe the file has NO debug info: order: code, consts, protos(nupvals then protos), debug.
# Let's assume: 00 00 00 00 = nupvalues of chunk?? chunk vararg=1 so upvals... 5.2: upvalue descs for main = _ENV
# Actually 5.2 official: after consts: nupvals(4), then upvalue names (debug), then nprotos(4)...
# But here first 4 bytes are 0 -> nupvals=0? but main has _ENV upval... maybe stripped.
# Then nprotos=1, child proto: 01 00 19 00 00 00 40 | "Data/Resources/Boot.lua\0" |
# child: linedef? could be custom: linedef(4)=? bytes 01 00 19 00 -> 0x00190001? unlikely
# Maybe child proto format: linedef(2) lastlinedef(2)? 01 00 = 1, 19 00 = 25? then nparam=0? byte 00, vararg 00,
# maxstack 40? '@'=64? no.
# OR: this string "Data/Resources/Boot.lua" suggests SOURCE stored per-proto here! len 0x19=25 -> string with len(4)=25.
# So child: ncode(4)=? Let's try: 01 00 00 00 = ncode=1, code=19 00 00 00? that's not vararg prep...
# Actually 19 00 00 00 as instruction: opcode=0x19&0x3F=25... Lua 5.2 op 25 = SETTABUP? hmm but code 1 inst?
# Wait maybe: 01 00 = nupvals(2)=1, 19 00 00 00 = string len 25, "Data/...", then 1E 00 00 00 = ncode=30?!
# That matches main chunk's 30 instructions! This might be a SECOND copy/relocated meta?
print(dump_hex(off, 100))
