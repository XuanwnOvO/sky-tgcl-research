import struct, sys, os

class R:
    def __init__(self, b):
        self.b = b; self.p = 0
    def byte(self):
        v = self.b[self.p]; self.p += 1; return v
    def i32(self):
        v = struct.unpack_from('<i', self.b, self.p)[0]; self.p += 4; return v
    def f64(self):
        v = struct.unpack_from('<d', self.b, self.p)[0]; self.p += 8; return v
    def string(self):
        n = self.i32()
        if n <= 0: return None
        s = self.b[self.p:self.p+n]; self.p += n
        return s  # includes trailing \0

# TGC opcode -> standard Lua 5.2 opcode
# (recovered from luaV_execute @ sub_F87BA8 in libBootloader.so:
#  TGC moves DIV/MOD/POW/ADD/SUB/MUL to 0..5; rest matches std 5.2)
OPMAP = {
    0: 16,  # DIV
    1: 17,  # MOD
    2: 18,  # POW
    3: 13,  # ADD
    4: 14,  # SUB
    5: 15,  # MUL
    6: 0,   # MOVE
    7: 1,   # LOADK
    8: 2,   # LOADKX
    9: 3, 10: 4, 11: 5, 12: 6, 13: 7, 14: 8, 15: 9, 16: 10, 17: 11, 18: 12,
    # 19..39 identical
}

def parse_proto(r):
    p = {}
    p['linedef'] = r.i32()
    p['lastlinedef'] = r.i32()
    p['numparams'] = r.byte()
    p['is_vararg'] = r.byte()
    p['maxstack'] = r.byte()
    ncode = r.i32()
    code = []
    for _ in range(ncode):
        c = r.i32() & 0xFFFFFFFF
        op = c & 0x3F
        if op in OPMAP:
            c = (c & ~0x3F) | OPMAP[op]
        code.append(c)
    p['code'] = code
    nk = r.i32()
    consts = []
    for _ in range(nk):
        t = r.byte()
        if t == 0: consts.append((0, None))
        elif t == 1: consts.append((1, r.byte()))
        elif t == 3: consts.append((3, r.f64()))
        elif t == 4: consts.append((4, r.string()))
        else: raise Exception(f'bad const type {t} at {r.p-1}')
    p['consts'] = consts
    nprotos = r.i32()
    p['protos'] = [parse_proto(r) for _ in range(nprotos)]
    nup = r.i32()
    p['upvaldescs'] = [(r.byte(), r.byte()) for _ in range(nup)]
    p['source'] = r.string()
    nline = r.i32()
    p['lineinfo'] = [r.i32() for _ in range(nline)]
    nloc = r.i32()
    locs = []
    for _ in range(nloc):
        name = r.string(); start = r.i32(); end = r.i32()
        locs.append((name, start, end))
    p['locvars'] = locs
    nupn = r.i32()
    p['upvalnames'] = [r.string() for _ in range(nupn)]
    return p

class W:
    def __init__(self):
        self.b = bytearray()
    def raw(self, x): self.b += x
    def byte(self, v): self.b.append(v & 0xFF)
    def i32(self, v): self.b += struct.pack('<I', v & 0xFFFFFFFF)
    def f64(self, v): self.b += struct.pack('<d', v)
    def string(self, s):
        if s is None: self.i32(0); return
        self.i32(len(s)); self.b += s

def emit_proto(w, p, top):
    w.i32(p['linedef']); w.i32(p['lastlinedef'])
    w.byte(p['numparams']); w.byte(p['is_vararg']); w.byte(p['maxstack'])
    w.i32(len(p['code']))
    for c in p['code']: w.i32(c)
    w.i32(len(p['consts']))
    for t, v in p['consts']:
        w.byte(t)
        if t == 0: pass
        elif t == 1: w.byte(v)
        elif t == 3: w.f64(v)
        elif t == 4: w.string(v)
    w.i32(len(p['protos']))
    for c in p['protos']: emit_proto(w, c, False)
    w.i32(len(p['upvaldescs']))
    for instack, idx in p['upvaldescs']:
        w.byte(instack); w.byte(idx)
    # debug: source, lineinfo, locvars, upvalnames
    w.string(p['source'])
    w.i32(len(p['lineinfo']))
    for l in p['lineinfo']: w.i32(l)
    w.i32(len(p['locvars']))
    for name, s, e in p['locvars']:
        w.string(name); w.i32(s); w.i32(e)
    w.i32(len(p['upvalnames']))
    for n in p['upvalnames']: w.string(n)

def convert(src, dst):
    b = open(src, 'rb').read()
    assert b[:4] == b'\x1bLua', 'not luac'
    r = R(b); r.p = 18  # skip custom header
    main = parse_proto(r)
    assert r.p == len(b), f'trailing bytes: {len(b)-r.p}'
    # build standard 5.2 chunk: header(18) with size_t=4
    w = W()
    w.raw(b'\x1bLua')          # magic
    w.raw(b'\x52')             # version 5.2
    w.raw(b'\x00')             # format
    w.raw(b'\x01')             # endianness LE
    w.raw(b'\x04')             # int size
    w.raw(b'\x04')             # size_t = 4 (so string lens are 4B)
    w.raw(b'\x04')             # instruction size
    w.raw(b'\x08')             # lua_Number size
    w.raw(b'\x00')             # integral flag (double)
    w.raw(b'\x19\x93\r\n\x1a\n')  # LUAC_TAIL
    emit_proto(w, main, True)
    open(dst, 'wb').write(w.b)
    return r.p, len(w.b)

if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    consumed, outsz = convert(src, dst)
    print(f'OK {src} -> {dst} (consumed {consumed}, wrote {outsz})')
