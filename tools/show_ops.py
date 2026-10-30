import sys
sys.path.insert(0, r'd:\新建文件夹\LightEncounters\tools')
import tgc2std
b = open(r'd:\新建文件夹\LightEncounters\Children of the Light\Resources\Boot.lua.luac','rb').read()
r = tgc2std.R(b); r.p = 18
main = tgc2std.parse_proto(r)
def show(p, ind=''):
    print(f"{ind}proto params={p['numparams']} vararg={p['is_vararg']} maxstack={p['maxstack']} ncode={len(p['code'])} nk={len(p['consts'])} nprotos={len(p['protos'])} nup={len(p['upvaldescs'])} lines={len(p['lineinfo'])} locs={len(p['locvars'])} upnames={len(p['upvalnames'])} source={p['source']}")
    for c in p['code']:
        op = c & 0x3F
        A = (c >> 6) & 0xFF
        C = (c >> 14) & 0x1FF
        B = (c >> 23) & 0x1FF
        k = (c >> 15) & 1 if False else 0
        print(f"{ind}  op={op:2d} A={A:3d} B={B:4d} C={C:4d} raw={c:08X}")
    for t,v in p['consts']:
        print(f"{ind}  K: t={t} {v!r}")
    for c in p['protos']:
        show(c, ind+'  ')
show(main)
