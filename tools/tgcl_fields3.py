import struct, re, os
from collections import Counter, defaultdict
root = r'd:\新建文件夹\LightEncounters\Children of the Light\Levels'
# 147B 已完全定界! 717 条：
#   0..16: [u8 flag][4f quat?] —— 4,8,12 uniq 519~661 = 高变 float，模长近 1 → quat
#   16..20: u32 0（uniq17 低变）
#   20..32: pos 3f（高变 float）
#   32..36: u32 0
#   36..48: 又一组 3f? (36,40,44 uniq 635~672) → pos2
#   48..52: u32 0
#   52..64: pos 3f uniq 685~704 → pos3/worldPos
#   64: 1.0,1.0,1.0 → scale 3f (64,68,72 uniq 18~25 低变=1.0/0.0)
#   88: 1,2,3,4 递增小整数 = 子链序号
#   92: 20.0/60.0, 100: 7.0 → 标量参数
# 验证 quat 单位长度 + pos 有限：
def load(lv):
    d = open(os.path.join(root, lv, 'Objects.level.bin'),'rb').read()
    o4, = struct.unpack_from('<I', d, 36)
    seg = d[o4:]
    starts = [m.start() for m in re.finditer(rb'BstNode_\d{9,10}\x00', seg)]
    lens = [starts[i+1]-starts[i] for i in range(len(starts)-1)] + [len(seg)-starts[-1]]
    return seg, starts, lens
import math
ok=bad=0
for lv in ['Dawn','MainStreet']:
    seg, starts, lens = load(lv)
    for i,L in enumerate(lens):
        if L==147:
            r = seg[starts[i]:starts[i]+L]
            q = struct.unpack_from('<4f', r, 4)
            m = math.sqrt(sum(x*x for x in q))
            if 0.85<m<1.15: ok+=1
            else: bad+=1
print('147B quat@4 unit check:', ok, 'ok /', bad, 'bad')
# 106B: 全部位 uniq 都高 → 106B = 压缩数据 (OBB/物理盒 or 动画 clip?)。看字节熵:
seg, starts, lens = load('Dawn')
r106 = next(seg[starts[i]:starts[i]+lens[i]] for i,L in enumerate(lens) if L==106)
print('106B sample hex:'); print(r106.hex(' '))
# 35B: data 12B uniq ~2000 全高变 u32 → 三 u32 引用（资源ID/指针表索引）。采样:
r35s = [seg[starts[i]:starts[i]+35] for i,L in enumerate(lens) if L==35][:5]
for r in r35s: print('35B:', r[19:31].hex(' '), 'seq', struct.unpack_from('<I',r,31)[0])
