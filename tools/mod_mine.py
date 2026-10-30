# -*- coding: utf-8 -*-
# 模块内剩余挖掘：CompressDictionary.zst / ContentPackages / Boot / Persistent / LoadLevel
import os, re, struct, collections
root = r"d:\新建文件夹\LightEncounters\Children of the Light"
out = []

# ① zstd 字典：头部 magic 0xEC30A437，然后 entropy tables + content
p = os.path.join(root, "Resources", "CompressDictionary.zst")
d = open(p, "rb").read()
print("== CompressDictionary.zst ==")
print("头:", d[:8].hex(" "), "magic ok =", struct.unpack_from('<I', d, 0)[0] == 0xEC30A437)
# 字典格式: dictID(4) + entropy + content + huffman tables。尾部 content 部分是训练文本
# zstd 字典的 content 在前段之后，直接粗暴扫可读串
strs = [s.decode() for s in re.findall(rb'[\x20-\x7e]{6,}', d)]
print("可读串数:", len(strs))
# 分类
keys = [s for s in strs if re.match(r'^[a-z][A-Za-z0-9_.]{3,40}$', s)]
pascal = [s for s in strs if re.match(r'^[A-Z][a-z]\w{3,40}$', s)]
print("camel 样例:", keys[:25])
print("Pascal 样例:", pascal[:25])
cnt = collections.Counter(strs)
print("高频串 top20:", cnt.most_common(20))

# ② ContentPackages 内容
print("\n== ContentPackages ==")
cp = os.path.join(root, "Resources", "ContentPackages")
for dp, dn, fn in os.walk(cp):
    for f in fn:
        fp = os.path.join(dp, f)
        sz = os.path.getsize(fp)
        head = open(fp, "rb").read(48)
        print(f"  {os.path.relpath(fp, cp)}  {sz}B  头: {head[:16].hex(' ')}")

# ③ Boot.lua / Vars.lua 源码直接看
print("\n== Boot.lua ==")
print(open(os.path.join(root, "decompiled_lua", "Resources", "Boot.lua"), encoding="utf-8", errors="replace").read()[:1200])
