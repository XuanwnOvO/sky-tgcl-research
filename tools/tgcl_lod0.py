# -*- coding: utf-8 -*-
# LOD0 条目解析：mesh 实例条目结构
import os, re, struct, collections
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"
d = open(os.path.join(root, "Dawn", "BstBaked.meshes"), "rb").read()
lo, le = 3019721, 7354603
lod = d[lo:le]
print("LOD0 段长:", len(lod))
print("段头 96B:", lod[:96].hex(" "))
# 之前看到: f0 86 31 03 00 00 0d 00 00 00 'AP07Butterfly' 07 05 08 a8 01 00 00 00 00 36 00 00 00 44 00 00 00 'HHH' ff 05 00 ...
# 第 0-3B 可能是前一条目的数据。找 'Prop_Tent_012' 偏移，回看条目头
for probe in [b'Prop_Tent_012', b'AP07Butterfly', b'JarMediumLoQ']:
    i = lod.find(probe)
    if i < 0: continue
    print(f"\n{probe.decode()} @段内 {i}")
    print("  前 24B:", lod[max(0,i-24):i].hex(" "))
    print("  名后 32B:", lod[i+len(probe):i+len(probe)+32].hex(" "))
# 统计名字前的 u32 分布（猜测 hash/count）
names = [(m.start(), m.group(1)) for m in re.finditer(rb'([A-Za-z][A-Za-z0-9_]{4,40})\x00', lod)]
print("\n名字条数:", len(names))
# 每个名字前 12B 的第 3 个 u32（可能是条目长度）
lens = []
for s, nm in names[:100]:
    pre = struct.unpack_from('<3I', lod, s-12)
    lens.append(pre)
print("前 12B 三元组样例:", lens[:10])
# 名字后的字节模式
aft = collections.Counter()
for s, nm in names:
    b = lod[s+len(nm)+1]
    aft[b] += 1
print("名后第一字节分布:", aft.most_common(10))
