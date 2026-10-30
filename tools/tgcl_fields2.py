import struct, re, os
from collections import Counter, defaultdict
root = r'd:\新建文件夹\LightEncounters\Children of the Light\Levels'
# 391B 头 64B 已明: (0,8,16,32,48 偏移是 u32 0 哨兵) — 即 [f,0]×8 → 但 0,8 位置 uniq=16/2456?
# 重读: 偏移 4,12,20,28,36,44,52,60 是 float 属性(uniq 2456~3700 高变体), 0,8,16,32,48 偏移低 uniq(1~16) = u32 哨兵/键
# 键值对: [u32 key][f32 value] ×8, key=0 常见但 8 位置 2456 uniq → 8 位置也是 float!
# 更正: 前 64B = 8×(u32 lowvar, f32 highvar)。0 位 uniq16, 8 位 uniq2456 → 交替键少。其实 0..64 是 float 流 + 插零。
# 391 中段 188-264 是小整数位模式(e-41~e-44) = u32 键序号(指向 seg3 字典)! e-41 ≈ 0x26xxxxxx
# 268 位 uniq 2922 = 高变体 → 又是 float。272 uniq 275…
# 尾 364: 65/50/60 (uniq62) = 常量类 int。
# 下一步硬骨头: 106B 与 147B 与 35B 模板字段图。用同样方法:
def load(lv):
    d = open(os.path.join(root, lv, 'Objects.level.bin'),'rb').read()
    o4, = struct.unpack_from('<I', d, 36)
    seg = d[o4:]
    starts = [m.start() for m in re.finditer(rb'BstNode_\d{9,10}\x00', seg)]
    lens = [starts[i+1]-starts[i] for i in range(len(starts)-1)] + [len(seg)-starts[-1]]
    return seg, starts, lens

buckets = defaultdict(list)
for lv in ['Dawn','DuskGraveyard','MainStreet','Night_PaintedWorld']:
    seg, starts, lens = load(lv)
    for i,L in enumerate(lens):
        if L in (106,147,35):
            buckets[L].append(seg[starts[i]:starts[i]+L])

for L in (106,147,35):
    recs = buckets[L]
    n = L-19-4
    print(f'\n=== {L}B field map ({len(recs)} recs, data {n}B) ===')
    for off in range(19, 19+(n//4)*4, 4):
        iv = [struct.unpack_from('<I', r, off)[0] for r in recs]
        fv = [struct.unpack_from('<f', r, off)[0] for r in recs]
        uniq = len(set(iv))
        sample_f = [round(v,4) if abs(v)<1e7 and (abs(v)>1e-6 or v==0) else v for v in fv[:3]]
        print(off-19, 'uniq', uniq, 'u32', sorted(set(iv))[:5], 'f', sample_f)
