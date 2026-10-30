# -*- coding: utf-8 -*-
# 391B 材质块尾部解析：'DarkStone\0' + f32 组 → 是材质名+参数！
# 结构假设: [头157B][5×(u32 uniformIdx? + 名字\0 + 20B)][材质名\0][参数f32组][材质名2\0][f32组]
import os, re, struct, collections
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"
d = open(os.path.join(root, "DuskGraveyard", "Objects.level.bin"), "rb").read()
o4 = struct.unpack_from("<5I", d, 24)[3]
seg = d[o4:]
ms = list(re.finditer(rb"BstNode_(\d+)\x00", seg))
mats = []
for i, m in enumerate(ms):
    a = m.start()
    e = ms[i+1].start() if i+1 < len(ms) else len(seg)
    body = seg[a:e-4]; hl = m.end()-m.start(); p = body[hl:]
    if len(p) == 391:
        mats.append(p)
print("391B 材质块数:", len(mats))
# 尾部结构：找所有可读串
names = collections.Counter()
fvals = collections.Counter()
for p in mats[:80]:
    for sm in re.finditer(rb'([A-Z][A-Za-z0-9_]{3,40})\x00', p):
        names[sm.group(1).decode()] += 1
    # 扫 f32: 已知 0x447a0000=1000.0, 0x3f800000=1.0 常见
print("尾部材质名 top:", names.most_common(20))
# 尾段固定: ...'DarkStone'后: 00 00 | 00 00 00 a4 00 cf 7a 01 00 01 00 00 70 41(15.0f) 00 00 00 41(8.0f) 00 00 c0 3f(1.5f)...
# 验证跨块: 尾 64B 打印 3 个样本
for p in mats[:3]:
    print("\n尾 80B:", p[-80:].hex(" "))
