import struct, re, os
from collections import Counter, defaultdict
root = r'd:\新建文件夹\LightEncounters\Children of the Light\Levels'
# 策略：按"模板长度+长度内锚点字节签名"聚类所有关卡的同型记录，交叉对比定字段。
# 先收集 Dawn+DuskGraveyard+MainStreet 的 72B/391B/106B/147B/35B 记录数据。
targets = [72, 391, 106, 147, 35]
buckets = defaultdict(list)
for lv in ['Dawn','DuskGraveyard','MainStreet','Prairie_Island','Night_PaintedWorld']:
    d = open(os.path.join(root, lv, 'Objects.level.bin'),'rb').read()
    o4, = struct.unpack_from('<I', d, 36)
    seg = d[o4:]
    starts = [m.start() for m in re.finditer(rb'BstNode_\d{9,10}\x00', seg)]
    lens = [starts[i+1]-starts[i] for i in range(len(starts)-1)] + [len(seg)-starts[-1]]
    for i,L in enumerate(lens):
        if L in targets:
            buckets[L].append((lv, seg[starts[i]:starts[i]+L]))
for L in targets:
    print(L, 'records:', len(buckets[L]))
# 72B: 已定。391B: 对齐比较多条，找不变字节（u32 字段）与可变 float
import math
def f32(b, off): return struct.unpack_from('<f', b, off)[0]
def isf(v): return abs(v)<1e7 and (abs(v)>1e-6 or v==0)
recs391 = [r for _,r in buckets[391]]
# 逐字节位：全 0 / 全同 / float 可变 / u32 可变
n = 391-19-4
col = []
for off in range(19, 19+n, 4):
    vals = [struct.unpack_from('<I', r, off)[0] for r in recs391]
    fv = [f32(r, off) for r in recs391]
    uniq = len(set(vals))
    col.append((off-19, uniq, fv[0], fv[1], fv[2]))
print('391B field map (offset, uniqU32, f0,f1,f2):')
for row in col[:96]:
    print(row)
