import struct

src = r'd:\新建文件夹\LightEncounters\Children of the Light\Resources\Boot.lua.luac'
b = open(src, 'rb').read()

def dump_hex(off, n=64):
    seg = b[off:off+n]
    return ' '.join(f'{x:02X}' for x in seg)

off = 18
# guess: linedef(4) lastlinedef(4) numparams vararg maxstack ncode(4)
linedef, lastlinedef = struct.unpack_from('<ii', b, off); off += 8
numparams, vararg, maxstack = b[off], b[off+1], b[off+2]; off += 3
ncode = struct.unpack_from('<I', b, off)[0]; off += 4
print(f'linedef={linedef} last={lastlinedef} nparam={numparams} vararg={vararg} maxstack={maxstack} ncode={ncode} codeoff={off}')
print('code[0:8]:', dump_hex(off, 16))
off += ncode*4
print('after code off=', off, dump_hex(off, 32))

# try: nconst then entries with size_t=4? try string length as 4-byte
nconst = struct.unpack_from('<I', b, off)[0]; off += 4
print('nconst=', nconst)
try:
    for i in range(nconst):
        t = b[off]; off += 1
        if t == 0:
            print(i, 'nil')
        elif t == 1:
            print(i, 'bool', b[off]); off += 1
        elif t == 3:
            v = struct.unpack_from('<d', b, off)[0]; off += 8; print(i, 'num', v)
        elif t == 4:
            l = struct.unpack_from('<I', b, off)[0]; off += 4
            s = b[off:off+l-1]; off += l
            print(i, 'str', repr(s[:60]))
        else:
            print(i, 'UNKNOWN type', t, 'at off', off-1); break
except Exception as e:
    print('err', e)
print('after consts off=', off, 'remaining=', len(b)-off)
print(dump_hex(off, 64))
