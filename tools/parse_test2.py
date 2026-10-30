import struct

src = r'd:\新建文件夹\LightEncounters\Children of the Light\Resources\Boot.lua.luac'
b = open(src, 'rb').read()

def dump_hex(off, n=64):
    seg = b[off:off+n]
    return ' '.join(f'{x:02X}' for x in seg)

off = 368
# guess protos: nupvals(4), then upval names, then nested protos; or nproto directly
# bytes: 00 00 00 00 | 01 00 00 00 | 01 00 | 19 00 00 00 ...
# maybe: nupvalues(4)=0? then nproto(4)=1? then proto: linedef(4)=0x19=25? linedef 25, lastlinedef? 0x01?
# try: nupval(4)=0, nproto(4)=1, proto: linedef(4)=25, lastlinedef(4)=1?? weird
# alt: after consts: nupval(4)=0 then nproto(4)=1 then child proto starts at off+8
off2 = off
nup = struct.unpack_from('<I', b, off2)[0]; off2 += 4
print('nupval?', nup)
nproto = struct.unpack_from('<I', b, off2)[0]; off2 += 4
print('nproto?', nproto)
linedef, lastlinedef = struct.unpack_from('<ii', b, off2); off2 += 8
nparam, vararg, maxstack = b[off2], b[off2+1], b[off2+2]; off2 += 3
ncode = struct.unpack_from('<I', b, off2)[0]; off2 += 4
print(f'child: linedef={linedef} last={lastlinedef} nparam={nparam} vararg={vararg} maxstack={maxstack} ncode={ncode}')
# vararg=0x19? print raw
print(dump_hex(off, 40))
