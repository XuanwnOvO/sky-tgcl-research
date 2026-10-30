import struct, re, os, math
root = r'd:\新建文件夹\LightEncounters\Children of the Light\Levels'
# 106B hex 判读成功:
# 19: 2e e4 87 bf = -0.066  | 27: 41 bb 93 3e = 0.288 | 35: 82 39 3e 3f = 0.744
# 43: 00... 51: 41 bb 93 be = -0.288 | 59: 2e e4 87 bf 重复! → 半边对称 → OBB half extents 或 phys capsule
# 67: d0 2d cd 43 = 408.8 | 71: 1c 31 6c 42 = 92.7 | 75: 14 c8 07 c1 = -8.65 (pos)
# 79: 00 00 80 3f = 1.0 | 83: 0 | 87: 01 | 91: 00 01 40 02 | 95: 4c ff 00 00 | 99: 00 00
# 尾: 06 00 00 00 = seq 6
# 106B = [f rot?][0][f][0][f][0][f][0][f][0][pos 3f][1.0][0][u8 1][...] → 物理体/触发器节点
# 147B quat@4 不单位 → 147B 结构重判。看 147B 原始 hex：
def load(lv):
    d = open(os.path.join(root, lv, 'Objects.level.bin'),'rb').read()
    o4, = struct.unpack_from('<I', d, 36)
    seg = d[o4:]
    starts = [m.start() for m in re.finditer(rb'BstNode_\d{9,10}\x00', seg)]
    lens = [starts[i+1]-starts[i] for i in range(len(starts)-1)] + [len(seg)-starts[-1]]
    return seg, starts, lens
seg, starts, lens = load('Dawn')
r = next(seg[starts[i]:starts[i]+lens[i]] for i,L in enumerate(lens) if L==147)
print('147B sample:'); print(r.hex(' '))
# 147B = 19 name + 124 data + 4 seq. 124 = 4+16+4+12+4+12+4+12+4+12+4+12+4+12+... 试 3 组 [u32 0 | quat 16B] + 3 组 pos + scale
# 假设: flag(4) | quat(16) | 0(4) | pos(12) | 0(4) | quat2?(16)? 不对 124
# 4 + (4+16)*2 + (4+12)*3 + (4+12) = 4+40+48+16=108 ≠124
# 4+(4+16)*3+(4+12)*2+(4+12)+... 枚举: 3 组 quat 块(20B)=60, 2 组 pos 块(16B)=32, scale(12)+pad(4)=16 → 108
# 直接按 field map: 0(0), 4,8,12(高变f), 16(0), 20,24,28(高变f), 32(0), 36,40,44(高变f), 48(0), 52,56,60(高变f), 64,68,72(=1.0/0 低变), 76..120(低变 u32)
# → [u32 0][4f quat][u32 0][3f pos][u32 0][3f pos2][u32 0][3f pos3][3f scale][u32 count][小整数们][标量]
# quat 在 4..20: q=(0.58,?,?) 不单位？重算精确:
for i,L in enumerate(lens):
    if L==147:
        r = seg[starts[i]:starts[i]+L]
        q = struct.unpack_from('<4f', r, 4+19-19+4)  # data off 4 = rec off 23? off 计算错了！
# field map 里的 off 是 data 内偏移(减 19)。quat data@4 → rec@19+4=23
r = next(seg[starts[i]:starts[i]+lens[i]] for i,L in enumerate(lens) if L==147)
q = struct.unpack_from('<4f', r, 23)
print('quat@data4:', q, '|len|', math.sqrt(sum(x*x for x in q)))
# 哦上面 147B 检查里用的 r[4] 是错位(应为 19+4=23)。重跑校验:
ok=bad=0
for lv in ['Dawn','MainStreet']:
    seg2, s2, l2 = load(lv)
    for i,L in enumerate(l2):
        if L==147:
            rr = seg2[s2[i]:s2[i]+L]
            qq = struct.unpack_from('<4f', rr, 23)
            m = math.sqrt(sum(x*x for x in qq))
            if 0.85<m<1.15: ok+=1
            else: bad+=1
print('147B quat@data4 unit:', ok, '/', bad)
