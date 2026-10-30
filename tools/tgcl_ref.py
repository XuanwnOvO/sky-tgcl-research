# -*- coding: utf-8 -*-
# ref u32 到底指向哪：候选 A=segB 字节偏移(16B行) B=segA字节偏移 C=其他
# 实验：对 ref u，检查 u%16 与 u%12 分布，以及 segB[u:u+12] 的三字段解读
import os, re, struct, collections
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"
lv = 'Dawn'
d = open(os.path.join(root, lv, 'Objects.level.bin'), 'rb').read()
ver, c1, c2, c3, c4 = struct.unpack_from('<5I', d, 4)
o1, o2, o3, o4, o5 = struct.unpack_from('<5I', d, 24)

seg = d[o4:]  # segD 节点树
ms = list(re.finditer(rb'BstNode_(\d{9,10})\x00', seg))
refs = []
for i, m in enumerate(ms[:500]):
    a, hl = m.start(), m.end()-m.start()
    e = ms[i+1].start() if i+1 < len(ms) else len(seg)
    body = seg[a+hl:e-4]
    n = len(body)
    if n < 8 or n % 4: continue
    c = struct.unpack_from('<I', body, 0)[0]
    if c != n//4 - 1 or c == 0: continue
    refs += list(struct.unpack_from(f'<{c}I', body, 4))

mod16 = collections.Counter(r % 16 for r in refs)
mod12 = collections.Counter(r % 12 for r in refs)
mod4 = collections.Counter(r % 4 for r in refs)
print("ref 总数", len(refs), "max", max(refs))
print("mod16 top:", mod16.most_common(8))
print("mod12 top:", mod12.most_common(8))
print("mod4 top:", mod4.most_common(8))

# 实验：segA 是 3132B = 261×12 (c1=261)。ref < 3132 的比例？
inA = sum(1 for r in refs if r < o2-o1)
inB = sum(1 for r in refs if r < o3-o2)
print(f"ref < segA大小: {inA}/{len(refs)}; ref < segB大小: {inB}/{len(refs)}")

# 若指向 segA(12B行): u%12
# 若指向 segB(16B行): u%16
# 打印几个 ref 的 segB 上下文
print("\nsegB 上下文样本:")
for r in refs[:8]:
    lo, hi = max(0, r-8), r+20
    raw = d[o2+lo:o2+hi]
    print(f"  @{r}: {raw.hex()}")
# segA 上下文
print("\nsegA 上下文样本:")
for r in [x for x in refs if x < 3132][:5]:
    lo, hi = max(0, r-8), r+20
    raw = d[o1+lo:o1+hi]
    print(f"  @{r}: {raw.hex()}")
