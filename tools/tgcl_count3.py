# -*- coding: utf-8 -*-
# 决定性实验：对 71B transform 样本，确认字节 0 是 u8 type、随后是 scale。
# 以及验证:  0x01010100(65793) 实为 u32 = ? 检查这些 nomatch 记录的 4B 对齐解析为 float 的合理性
# 更直接: 检查 payload 头部是否 = "u32 attrCount" + "u32 totalCount"? 
import os, re, struct, collections
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"
LVLS = sorted(os.listdir(root))

# 观察 71B: 01 ee7ed03e ... -> 01 后 40B transform + 剩余? 71B: hl=? body = 71 - hl(name len) - 4
# name len 9 or 10 -> body 58 or 57. 但 71B 族不分 name 长度说明 body 长度可变 -> 记录长度 = name + body + 4
# 上面假设 body 定长不成立。打印同一长度族里 name 长度分布
bylen = collections.defaultdict(collections.Counter)
used = 0
for lv in LVLS:
    d = open(os.path.join(root, lv, 'Objects.level.bin'), 'rb').read()
    offs = struct.unpack_from('<5I', d, 24)
    o3 = offs[2]
    seg = d[o3:]
    ms = list(re.finditer(rb'BstNode_(\d{9,10})\x00', seg))
    for i, m in enumerate(ms):
        a, hl = m.start(), m.end()-m.start()
        e = ms[i+1].start() if i+1 < len(ms) else len(seg)
        L = e - a
        if L in (71, 51, 72, 35):
            bylen[L][hl] += 1
    used += 1
    if used >= 15: break

for L in sorted(bylen):
    print(f"{L}B: header(name)长度分布 = {dict(bylen[L])}")
