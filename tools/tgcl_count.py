# -*- coding: utf-8 -*-
# 验证假设：payload = u32 count + N×u32（引用表）
import os, re, struct, collections
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"
LVLS = sorted(os.listdir(root))

stat = collections.Counter()  # (match, mismatch, payloadlen%4!=0)
firstval = collections.Counter()
examples = collections.defaultdict(list)
used = 0
for lv in LVLS:
    d = open(os.path.join(root, lv, 'Objects.level.bin'), 'rb').read()
    offs = struct.unpack_from('<5I', d, 24)
    o2, o3 = offs[1], offs[2]
    strpool = d[o2:o3]
    slen = len(strpool)
    seg = d[o3:]
    ms = list(re.finditer(rb'BstNode_(\d{9,10})\x00', seg))
    for i, m in enumerate(ms):
        a, hl = m.start(), m.end()-m.start()
        e = ms[i+1].start() if i+1 < len(ms) else len(seg)
        body = seg[a+hl:e-4]
        n = len(body)
        if n < 4:
            stat['short'] += 1
            continue
        c = struct.unpack_from('<I', body, 0)[0]
        firstval[c] += 1
        if n % 4 == 0 and c == n//4 - 1:
            stat['match'] += 1
            # verify refs
            if len(examples['match']) < 3 and lv in ('Dawn',):
                refs = [struct.unpack_from('<I', body, 4+4*k)[0] for k in range(c)]
                hits = sum(1 for r in refs if r < slen)
                examples['match'].append((lv, c, hits, max(c,1) and hits*100//c))
        elif n % 4 == 0 and c < n//4:
            stat['c<n'] += 1
        else:
            stat['nomatch'] += 1
    used += 1
    if used >= 20: break

print(stat)
print("match 样例(lv,count,refs命中seg3数,命中率):")
for x in examples['match']: print(" ", x)
print("首 u32 top20:", firstval.most_common(20))
