# -*- coding: utf-8 -*-
# 值块与组件的关联假设：值块 payload 前可能有 u32 组件索引；
# 或者 payload 首 u32 大值 = 组件表索引。检查 payload 首字段分布与 261/3239 的关系
import os, re, struct, collections
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"
lv = 'Dawn'
d = open(os.path.join(root, lv, 'Objects.level.bin'), 'rb').read()
o1, o2, o3, o4, o5 = struct.unpack_from('<5I', d, 24)
segC = d[o3:o4]
def s3(u):
    e = segC.find(b'\x00', u)
    return segC[u:e].decode('utf-8', 'replace')
segA = d[o1:o2]
comps = []
for i in range(261):
    a, st, pc = struct.unpack_from('<3I', segA, i*12)
    comps.append(s3(a))
comp_idx = {n: i for i, n in enumerate(comps)}

seg = d[o4:]
ms = list(re.finditer(rb'BstNode_(\d{9,10})\x00', seg))
first = collections.Counter()
samples = collections.defaultdict(list)
for i, m in enumerate(ms):
    a, hl = m.start(), m.end()-m.start()
    e = ms[i+1].start() if i+1 < len(ms) else len(seg)
    body = seg[a+hl:e-4]
    if len(body) < 4: continue
    u = struct.unpack_from('<I', body, 0)[0]
    if u < 261:
        first[f'compidx {comps[u]}'] += 1
        if len(samples[u]) < 2: samples[u].append((i, len(body), body[:24].hex()))
    elif u < 3239:
        first[f'schemaRow {u}'] += 1
    else:
        first['other'] += 1
print("payload 首 u32 分类:", first.most_common(15))
# 抽样看 compidx 记录
shown = 0
for k, v in first.most_common():
    if k.startswith('compidx') and shown < 10:
        u = comp_idx[k.split(' ', 1)[1]]
        for i, bl, hx in samples[u]:
            print(f"  {k}: body={bl}B {hx}")
        shown += 1
