import struct

# Definitive parse of TGC custom Lua 5.2 chunk format
# Header (18B): magic, ver 0x52, fmt 0, LUAC_DATA "01 04 08 04 08 00", tail 19 93 0D 0A 1A 0A
# Custom: sizes seem int=4 size_t=8? but strings use 4-byte len. Actually header says size_t=8
# but observed string len = 4 bytes (19 00 00 00). So TGC changed size_t to 4? header byte 8 is "08"...

src = r'd:\新建文件夹\LightEncounters\Children of the Light\Resources\Boot.lua.luac'
b = open(src, 'rb').read()

def u32(o): return struct.unpack_from('<i', b, o)[0]
def U32(o): return struct.unpack_from('<I', b, o)[0]
def u16(o): return struct.unpack_from('<H', b, o)[0]

pos = 18
# Main proto
linedef = u16(pos); lastlinedef = u16(pos+2); pos += 4   # 0,0
nparam = b[pos]; vararg = b[pos+1]; maxstack = b[pos+2]; pos += 3  # 0,1,2
ncode = U32(pos); pos += 4
code = b[pos:pos+ncode*4]; pos += ncode*4
nconst = U32(pos); pos += 4
consts = []
for i in range(nconst):
    t = b[pos]; pos += 1
    if t == 0: consts.append(None)
    elif t == 1: consts.append(bool(b[pos])); pos += 1
    elif t == 3: consts.append(struct.unpack_from('<d', b, pos)[0]); pos += 8
    elif t == 4:
        l = U32(pos); pos += 4
        consts.append(b[pos:pos+l-1].decode('utf-8','replace')); pos += l
    else: raise Exception(f'bad const type {t} at {pos-1}')
nline = U32(pos); pos += 4
lines = [U32(pos+i*4) for i in range(nline)]; pos += nline*4
nproto = U32(pos); pos += 4
print(f'MAIN: linedef={linedef} last={lastlinedef} nparam={nparam} vararg={vararg} maxstack={maxstack}')
print(f'  ncode={ncode} nconst={nconst} consts={consts} nline={nline} lines[:5]={lines[:5]} nproto={nproto}')
# pos should be 368 now
print('pos after main =', pos)
# child proto: 01 00 19 00 00 00 40 'Data/Resources/Boot.lua\0' 1E 00 00 00 ...
# hypothesis: linedef(2)=1, lastlinedef(2)=0x0019?? that's 25... wait 19 00 00 00 could be slen(4)=25
# and "40"?? hmm what if string len is 4-byte=25 but string starts at 382 with '@'? No.
# NEW: maybe layout: linedef(2)=1, lastlinedef(2)=0x19?? Let's test: linedef=1, lastlinedef=25
# then nparam=0? vararg=0? maxstack=0x40?? nonsense.
# OR: linedef(4)=0x00190001?? no.
# OR child: nupvals(2)=1?? then upvaldesc... no
# Try: linedef(2)=1, lastlinedef(2)=0, then... no bytes are 01 00 19 00 00 00 40
# Try: linedef(4)=1 (01 00 00 00 -> but bytes 376-379 = 01 00 19 00 -> =0x00190001) no
# Actually bytes 372-375 = 01 00 00 00 = nproto=1. Child starts 376: 01 00 19 00 00 00 40
# What if child: linedef(2)=1, lastlinedef(2)=0x19=25, nparam(1)=0, vararg(1)=0, maxstack(1)=0x40?? 
# maxstack 64? maybe! Then slen... next byte 383=0x44='D' no len field? Hmm maybe NO source len, 
# null-terminated source string directly! "Data/Resources/Boot.lua\0" from 383? But 382=0x40='@'
# so string from 382 = "@Data..."?? unless maxstack=0x40 is wrong and 0x40 is part of something else.
# Wait maybe order differs: [linedef(2)][lastlinedef(2)][nparam(1)][vararg(1)][maxstack(1)][source: null-term]
# 376: 01 00 | 19 00 | 00 | 00 | 40?? -> linedef=1, last=25, nparam=0, vararg=0, maxstack=0x40=64? 
# hmm 'Boot.lua' child having 64 maxstack... unlikely but possible? Then source "@Data/..."? no.
# ALTERNATIVE: linedef(4)=0x00190001 is impossible, so 2-byte lines confirmed. Then maybe:
# [linedef(2)=1][lastlinedef(2)=25][nparam(1)=0][vararg(1)=0][maxstack(1)=0x40???]
# OR [linedef(2)=1][lastlinedef(2)=0x0019]... same.
# What about: [nupvals(2)=1] [upvaldesc? ...] no.
# Hmm wait — maybe maxstack is 1 byte but 0x40 is wrong split; try:
# [linedef(2)=1][lastlinedef(4)=0x40000019?? no.
# Let me just try: linedef=1, lastlinedef=25, nparam=0, vararg=0, maxstack=0x40 -> then source null-term
# at 383: 'Data/Resources/Boot.lua' — but byte 382=0x40 unexplained.
# OR: [linedef(2)=1][lastlinedef(2)=25][ncode?? no
# Could the child NOT have source, and 0x40 44 61 74 61 = len 0x40?? no, 0x40=64 but string is 23ch
# Actually! What if string length INCLUDES null and is stored as 4 bytes but here len=0x19=25 at 378,
# and the string begins 382 with byte 0x40?? '@'? weird.
# OR the string is stored with length 24 (0x18)... 0x19=25. With null=24+? 
# You know what: 0x40 might be... hmm 25 = 0x19. String "@Data/Resources/Boot.lua" is 24 chars +null = 25! 
# With a leading char? In Lua debug source for loaded chunks starts with '@' or '='!
# YES! "@" prefix means file source! So source = "@Data/Resources/Boot.lua\0" = 25 bytes. PERFECT.
# So child: linedef(2)=1, lastlinedef(2)=25, ??? 00 00 = ?, slen(4)=25? wait recount:
# 376: 01 00 -> linedef(2)=1? then 378: 19 00 00 00 = slen(4)=25? then 382: 40 '@' start string
# so lastlinedef missing? OR: 376: 01 00 19 00 -> lastlinedef(2)=0x0019=25, linedef(2)=1
# then 380: 00 00 -> ??? maybe nparam(1)=0, vararg(1)=0; 382: slen(4)= 40 44 61 74?? no that's '@Dat'
# Hmm slen would be 0x74614440 huge. NO.
# Back to: 376-377: 01 00 ; 378-381: 19 00 00 00 ; 382: 40 '@'; string 382..406 (25 bytes incl null)
# So child layout: [linedef(2)=1][lastlinedef(2)=0x19=25]... wait that uses bytes 376-379 = 01 00 19 00
# then 380-381: 00 00 ??? then 382: '@'... 
# OR [linedef(2)=1][lastlinedef(2)=25][slen(2)=0?? no slen(4) at 378 = 25 works if lastlinedef is 2 bytes
# at 378-379? then 380-381 leftover 00 00.
# Simplest consistent: child: linedef(2)=1, lastlinedef(2)=25, nparam(1)=0, vararg(1)=0, maxstack(1)=0x40??
# no wait that consumes 376..382 and 0x40 IS maxstack?? Boot child with maxstack 64? Unlikely.
# OR nparam(1)=0? vararg(1)=0? then slen... 
# Actually let's count: 376(01) 377(00) 378(19) 379(00) 380(00) 381(00) 382(40) 383..406 string(null at 406)
# If slen(4) at 378 = 0x00000019 = 25 -> string at 382 = '@Data/...' (25B: 382..406) ✓
# So bytes 376-377 = 01 00: could be linedef(2)=1 with lastlinedef=??? MISSING? Or "nupvals(2)=1"?
# Hmm maybe custom proto: [nupvals(2)][slen(4)][source][linedef(2)][lastlinedef(2)]... no lines come at 407
# After source: 407: 1E 00 00 00 = 30 = nlineinfo? lines 16..  or ncode=30? code vals would be 0x10?? 
# 0x10 as instruction: opcode 0x10&0x3F=16 = MOVE with A=0,B=0? all instructions identical 0x10? No way.
# So 407 = nlineinfo(4)=30, lineinfo 30*4 = 120B (407+4=411..530) ✓ (values 0x10,0x13 = lines 16,19 etc)
# Then 531: 00 00 00 00 = nprotos=0 ✓, 535: 01 00 00 00 = nupvals=1, 539: 05 00 00 00 len, "_ENV\0" ✓ ENDS AT 548 = filesize ✓✓✓
# But where's the child's CODE and CONSTS?! Missing! Unless... the child IS the whole thing and
# main chunk fields I parsed as "code, consts" actually belong to child?? 
# Rethink: maybe order: main proto has NO code (ncode at 29 = 30?) hmm we parsed ncode=30 at 29 with
# plausible instructions 0C 00 40 00... those ARE plausible Lua instructions (VARARGPREP=0x4C0C0C? )
# Actually wait: maybe layout is: HEADER, then CHILD PROTO FIRST?, then main? No...
# OR: the main chunk structure: [proto WITHOUT debug], and nested: my parse had nconst=13 at 153 
# with sensible strings — that's definitely constants. And code 30 instrs plausible.
# Then nlineinfo=0 (368), nprotos=1 (372)... then child should have code+consts but seems to start 
# with 01 00 19 00... unless CHILD'S consts/code come AFTER its source+lines?? i.e. order differs?
# Hmm OR maybe child: [linedef(2)=1][lastlinedef(2)=25][slen(4)=25]["@Data..."][nlineinfo(4)=30][lines120]
# [nprotos(4)=0][nupvals(4)=1][upval "_ENV"]  --- and NO CODE/CONSTS?? Impossible.
# Unless the "code" I parsed at 33 and "consts" at 153 belong to the CHILD and the main chunk
# is tiny?? The chunk layout might be: header, [one flat proto]... 
# Wait actually reconsider: maybe there's no "main then child"; maybe 5.2 format: 
# main proto: linedef... code consts THEN nested protos THEN debug info. The nested child's fields:
# source first? In 5.2, child proto doesn't store source (it's in header). TGC moved source INTO child?
# Possible custom: child: [slen(4)=25][@source][linedef? ...]. But bytes 376-377 = 01 00 before slen at 378.
# Could 372: nprotos=1? and 376: child starts: [nupvals(2)=1]?? child with 1 upval, then [slen(4)=25] 
# ["@Data/Resources/Boot.lua"][linedef(2)?...] hmm then after source at 407: 1E 00 00 00...
# if that's linedef?? =30, then lastlinedef?? next 4 bytes 10 00 00 00 = 16? last < first no.
# if 407: ncode=30?? but "instructions" all 0x10/0x13 impossible.
# if 407: nconst=30? then consts would be type bytes 0x10? no (invalid type).
# if 407: nlineinfo=30 ✓ lines 411..530 (0x10 repeated = line 16 for most, 0x13=19 later) plausible!
# then 531: nprotos=0, 535: nupvals=1, "_ENV" — but still NO code/consts for child!!
# CONCLUSION: the child proto has no own code because... THE CHILD IS A REFERENCE/stub? 
# OR: maybe this whole file has TWO protos: the "main" (my parse at 18) and the file's REAL content is 
# the main chunk; the child at 376 is a "source reference proto"?? Weird.
# Hmm, actually maybe 372's "01 00 00 00" is not nprotos but part of debug: [nlineinfo=0][??=1]
# and then child... let me just check: does the main code at 33 contain the full Boot.lua logic?
# Boot.lua only does resource declarations - about 10-15 instructions. ncode=30 plausible for main.
# The child (a function defined in Boot.lua?) — resource blocks create functions? Possibly one nested
# function with ~no code? A child with ncode=0? Then where's "00" for ncode...
# Try child layout: [linedef(2)=1][lastlinedef(2)=25][nparam(1)=0][vararg(1)=0][maxstack(1)=?]
# maxstack byte would be at 382 = 0x40?? = 64?? no...
# Try: [linedef(2)=1][lastlinedef(2)=25][nparam(1)=0][vararg(1)=0][maxstack(1)=0x00?]... 
# bytes 380,381 = 00 00, 382=0x40. If maxstack=0 that's invalid. 
# I'll go with: the child at 376 = [nupvals(2)=1] is wrong too... 
# PRAGMATIC APPROACH: write converter producing valid 5.2 chunk by REMOVING source from child and
# fixing sizes, letting unluac parse it. But we still haven't located child code/consts...
# WAIT. Maybe I misidentified: what if 29's ncode=30 is actually main, and the child's code+consts
# are at 376 BEFORE source: 376: 01 00 19 00... no, 0x190001 as ncode insane.
# OR what if child consts come after lines: 531: nprotos? hmm no we assigned that.
# Let me count total: file 548. main: code30@33(120)+consts153..367(215 incl count? consts end 368)
# = consumes 18..368 (350B). Remaining 368..548 = 180B: [nline=0][nproto=1][child: ?..]
# child consumes 376..548 = 172B. source(2+4+25=31B: 376..406), lines: 4+120=124B (407..530),
# tail: 4+4+4+5=17B (531..547). 31+124+17=172 ✓ EXACTLY. So child = source + lines + protos0 + upvals.
# NO CODE, NO CONSTS in child! So the child is... empty function? An empty function has ncode≥1 (RETURN).
# UNLESS the format omits code/consts when... no.
# OR: nlineinfo isn't 30 lines; maybe: 407: ncode=30 is CODE after all?! instructions 0x10,0x13...
# Lua 5.2 opcode 0x10 = 16 =?? (5.2 ops: MOVE=0.., 16=SETTABUP? no: 0:MOVE 1:LOADK 2:LOADKX 3:LOADBOOL
# 4:LOADNIL 5:GETUPVAL 6:GETTABUP 7:GETTABLE 8:SETTABUP 9:SETUPVAL 10:SETTABLE 11:NEWTABLE 12:SELF
# 13:ADD 14:SUB 15:MUL 16:DIV 17:MOD 18:POW 19:DIV?? 5.2: 16=DIV... instruction 0x00000010 = 
# iABC opcode 16 (DIV) A=0 B=0 C=0? DIV R0 R0 R0? weird but 30 identical DIVs? NO.
# What if code words are 0x00000010 = op16... no. These are line numbers.
# SO: the file's nested proto has no code?! UNLESS nprotos at 372 isn't 1... 
# What if 368: nline=0, 372: 01 00 00 00 = ??? and 376: 01 00 = nprotos?? no nprotos=0x00190001?? 
# OK alternative: maybe 372-375 "01 00 00 00" = nprotos=1, child: [linedef(2)=1][lastlinedef(2)=25]
# [nparam(1)=0][vararg(1)=0][maxstack(1)=0x40?? =64??] — hmm what if maxstack ISN'T stored per proto
# in TGC format (stored once in header?) then: [linedef=1][last=25][nparam=0][vararg=0][slen(4)=0x40444174??]
# no. [linedef(2)=1][lastlinedef(2)=25][slen(4)@380=00 00 40 44?? no.
# The split [linedef(2)][lastlinedef(2)][slen(4)][@source(25)] = 376..406: 1,25,25,"@Data..." ✓✓ 
# (no nparam/vararg/maxstack for child?! or those come after lines?) 
# then 407: nlineinfo=30, lines 411..530, 531: nprotos=0, 535: nupvals=1, _ENV
# still missing code/consts/params. 
# !!! Maybe the child's code/consts are stored BEFORE its source in some reversed order?? 
# 372: 01 00 00 00 could be ncode? no =1: one instruction? then code 4B? then nconst? 
# 376: 01 00 = nconst?? no...
# Honestly maybe the format is: after main's consts: [nlineinfo=0][linedef(4)=1?? no bytes 372=01 00 00 00
# =linedef 1? then [lastlinedef?? 376: 01 00 19 00 = 0x00190001 no.
print('done - see comments')
