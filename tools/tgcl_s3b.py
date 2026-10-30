# -*- coding: utf-8 -*-
# seg3 结构再探：ref 偏移 83% 可读但样例显示空串 → 打印 raw bytes 看真实内容
import os, re, struct
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"
lv = 'Dawn'
d = open(os.path.join(root, lv, 'Objects.level.bin'), 'rb').read()
offs = struct.unpack_from('<5I', d, 24)
o2, o3 = offs[1], offs[2]
strpool = d[o2:o3]
print("strpool len:", len(strpool))

for u in [15523, 16704, 2042, 6999, 39, 8874, 10400]:
    lo = max(0, u-8); hi = min(len(strpool), u+40)
    raw = strpool[lo:hi]
    asc = ''.join(chr(b) if 32 <= b < 127 else '.' for b in raw)
    print(f"@{u}: {raw.hex()}  |{asc}|")
