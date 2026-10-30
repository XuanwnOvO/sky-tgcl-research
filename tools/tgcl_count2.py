# -*- coding: utf-8 -*-
# 验证假设B：payload = u8 type + u8 flags? + u16 count + N×u32？（0x010101=65793 暗示字节结构）
# 直接对 count!=N 的记录 dump 首字节分布
import os, re, struct, collections
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"
LVLS = sorted(os.listdir(root))

firstbyte = collections.Counter()
u16_at2 = collections.Counter()
samples = collections.defaultdict(list)
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
        if n < 8 or n % 4: continue
        c = struct.unpack_from('<I', body, 0)[0]
        if n//4 - 1 == c: continue  # already match
        firstbyte[body[0]] += 1
        if body[1] == 0:
            u16_at2[struct.unpack_from('<H', body, 2)[0]] += 1
        if len(samples[body[0]]) < 3:
            samples[body[0]].append((lv, n, body[:32].hex()))
    used += 1
    if used >= 20: break

print("nomatch 组首字节 top:", firstbyte.most_common(15))
print("byte1==0 时 u16@2 top:", u16_at2.most_common(15))
