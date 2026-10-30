# -*- coding: utf-8 -*-
# seg3 内偏移 → 字符串：偏移可能指向串中间（共享后缀），向前回退找串起点
import os, re, struct, collections
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"
lv = 'Dawn'
d = open(os.path.join(root, lv, 'Objects.level.bin'), 'rb').read()
offs = struct.unpack_from('<5I', d, 24)
o2, o3 = offs[1], offs[2]
strpool = d[o2:o3]

def resolve(u, back=64):
    if u >= len(strpool): return None
    # 向前回退到上一个 NUL 之后
    st = max(0, u - back)
    z = strpool.rfind(b'\x00', st, u + 1)
    st = z + 1 if z >= 0 else st
    e = strpool.find(b'\x00', u)
    return strpool[st:e].decode('utf-8', 'replace')

# 测试已知的偏移
for u in [15523, 16704]:
    print(u, '→', repr(resolve(u)))

# 验证 ref 记录的偏移全部能解析出可读串
seg = d[o3:]
ms = list(re.finditer(rb'BstNode_(\d{9,10})\x00', seg))
hits = 0; tot = 0; bad = []
shown = 0
for i, m in enumerate(ms):
    a, hl = m.start(), m.end()-m.start()
    e = ms[i+1].start() if i+1 < len(ms) else len(seg)
    body = seg[a+hl:e-4]
    n = len(body)
    if n < 8 or n % 4: continue
    c = struct.unpack_from('<I', body, 0)[0]
    if c != n//4 - 1 or c == 0: continue
    for k in range(c):
        u = struct.unpack_from('<I', body, 4+4*k)[0]
        tot += 1
        s = resolve(u)
        if s is not None and all(32 <= ord(ch) < 127 for ch in s):
            hits += 1
            if shown < 10:
                print(f"  ref[{k}] @{u}: {s[:60]!r}")
                shown += 1
        elif len(bad) < 5:
            bad.append((u, s))
print(f"可读串命中: {hits}/{tot} = {hits*100//max(tot,1)}%")
print("bad 样例:", bad)
