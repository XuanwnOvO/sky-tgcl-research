# -*- coding: utf-8 -*-
# mesh 头结构定案：4 个 entry（tag + off + size），off/size 指向数据区
import os, struct
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"
d = open(os.path.join(root, "Dawn", "BstBaked.meshes"), "rb").read()
# 头：LVL0 ver=61 count=3? 其实是 4 个 tag。逐个读 entry(tag@X, u32@X+4, u32@X+8)
ents = [("GEO0", 12), ("LOD0", 24), ("METR", 36)]
print("头 48B 逐字段:")
for i in range(0, 48, 4):
    u = struct.unpack_from('<I', d, i)[0]
    f = struct.unpack_from('<f', d, i)[0]
    s = d[i:i+4]
    print(f"  @{i:>3}: u32={u:>10} f32={f:>14.4g} ascii={s}")
# 假设: entry = tag(4) + offset(4) + size(4)
# GEO0: off=136, size=3019585? 但 3019585 > LOD0@24。更可能 tag(4)+size(4)+? 
# 试: GEO0 size=136? 不合理。GEO0 u32=136 = 0x88, u32=0x2e1341
# LOD0 u32=0x2e13c9=3019721, u32=0x7038eb=7354603
# METR u32=10374324=0x9e4cb4, u32=64
# 文件大小 10374388; METR off=10374324 → 距尾 64B! → METR 尾块 64B(条目数64? 不, 64=距尾大小)
# 所以 entry = tag + offset + ? : GEO0 off=0x88=136, LOD0 off=0x2e13c9=3019721, METR off=0x9e4cb4=10374324
# 第二个 u32: GEO0 0x2e1341=3019585 ≈ LOD0 off(3019721)-136(头部?) 
print()
print("GEO0 off=136, LOD0 off=3019721, METR off=10374324, 尾部64B")
print("GEO0 段 = [136, 3019585)?  长度 =", 3019585-136)
print("LOD0 段 = [3019721, 7354603)? 长度 =", 7354603-3019721)
print("METR 段 = [10374324, 10374388) 长 64 = 尾 64B")
# 验证 GEO0 段内容
print("\nGEO0 段首 64B @136:", d[136:200].hex(" "))
print("LOD0 段首 64B @3019721:", d[3019721:3019785].hex(" "))
print("文件尾 64B @10374324:", d[10374324:].hex(" "))
# 尾 64B 像什么? 全是计数?
tail = struct.unpack_from('<16I', d, 10374324)
print("尾 16×u32:", tail)
# LOD0 段内是 mesh 名字表：'AP07Butterfly' 等 → 扫全部名字
import re
names = [m.group(1).decode() for m in re.finditer(rb'([A-Za-z][A-Za-z0-9_./-]{3,60})\x00', d[3019721:7354603])]
print("\nLOD0 段 mesh 名字数:", len(names), "唯一:", len(set(names)))
print("样例 20:", names[:20])
pref = {}
import collections
pc = collections.Counter(n.split('_')[0][:6] for n in names)
print("前缀 top15:", pc.most_common(15))
# GEO0 段是否有名字
gnames = [m.group(1).decode() for m in re.finditer(rb'([A-Za-z][A-Za-z0-9_./-]{3,60})\x00', d[136:3019585])]
print("GEO0 段名字数:", len(gnames), gnames[:10])
# METR 尾 64B 与头部关系: 尾含 3019585(=GEO0 u32@20!) → 头部第二 u32 是"段结束偏移"
# GEO0: off=136, end=3019585 → 段长 3019449
# LOD0: off=3019721, end=7354603
# METR: off=10374324, end=10374388(=文件尾)
# 差 3019721-3019585=136 = 头部大小! 说明 off/end 是绝对偏移，中间还有数据（重叠?）
print("\n头部大小验证: LOD0.off - GEO0.end =", 3019721 - 3019585)
