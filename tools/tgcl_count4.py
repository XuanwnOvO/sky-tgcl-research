# -*- coding: utf-8 -*-
# 关键实验：固定 body 长度视角。body = L - hl - 4。按 body 长度重新分族，再对各族 dump 头 4 字节。
import os, re, struct, collections
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"
LVLS = sorted(os.listdir(root))

bybody = collections.defaultdict(list)
used = 0
for lv in LVLS:
    d = open(os.path.join(root, lv, 'Objects.level.bin'), 'rb').read()
    offs = struct.unpack_from('<5I', d, 24)
    o2, o3 = offs[1], offs[2]
    strpool = d[o2:o3]
    seg = d[o3:]
    ms = list(re.finditer(rb'BstNode_(\d{9,10})\x00', seg))
    for i, m in enumerate(ms):
        a, hl = m.start(), m.end()-m.start()
        e = ms[i+1].start() if i+1 < len(ms) else len(seg)
        body = seg[a+hl:e-4]
        if len(body) <= 80:
            bybody[len(body)].append((lv, body))
    used += 1
    if used >= 8: break

for L in sorted(bybody):
    if len(bybody[L]) < 20: continue
    # 头 u32 分布 + count==N-1 检查
    cm = 0; tot = 0; f0 = collections.Counter()
    for lv, b in bybody[L]:
        if len(b) < 4: continue
        c = struct.unpack_from('<I', b, 0)[0]
        tot += 1
        if c == L//4 - 1: cm += 1
        f0[c] += 1
    if tot < 10: continue
    top = f0.most_common(3)
    print(f"body={L}B n={tot} | count==N-1: {cm*100//tot}% | 头u32 top: {[(hex(k),v) for k,v in top]}")
    if top and top[0][0] != 0 and top[0][0] == L//4 - 1:
        for lv, b in bybody[L][:2]:
            refs = [struct.unpack_from('<I', b, 4+4*k)[0] for k in range(L//4-1)]
            hits = sum(1 for r in refs if r < len(strpool))
            print(f"   [{lv}] refs命中 {hits}/{len(refs)}")
