# -*- coding: utf-8 -*-
# BstBaked.meshes chunk 头精细解析（LVL0 | 61 | 3 | GEO0 | 0x88 | 0x2e1341 | LOD0 ...）
import os, re, struct, collections
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"
d = open(os.path.join(root, "Dawn", "BstBaked.meshes"), "rb").read()
print("大小:", len(d))
# 按字面看：'LVL0' u32=0x3d(61) u32=3 'GEO0' u32=0x88(136) u32=0x2e1341(3019073) 'LOD0'
print("验证: LVL0 @0, u32@4 =", struct.unpack_from('<I', d, 4)[0],
      " u32@8 =", struct.unpack_from('<I', d, 8)[0])
# 结构假设: magic(4) + version(4) + chunkCount(4) + entries
# entry = 'GEO0' + u32 something + u32 offset?
hdr = d[:64]
print("GEO0@12, u32@16 =", struct.unpack_from('<I', d, 16)[0], "(136)")
print("u32@20 =", struct.unpack_from('<I', d, 20)[0], f"(0x{struct.unpack_from('<I', d, 20)[0]:x})", "(3019073)")
print("LOD0@24, u32@28 =", struct.unpack_from('<I', d, 28)[0], f"(0x{struct.unpack_from('<I', d, 28)[0]:x})")
print("u32@32 =", struct.unpack_from('<I', d, 32)[0], f"(0x{struct.unpack_from('<I', d, 32)[0]:x})")
print("METR@36, u32@40 =", struct.unpack_from('<I', d, 40)[0], "(64)")
print("u32@44 =", struct.unpack_from('<I', d, 44)[0], f"(0x{struct.unpack_from('<I', d, 44)[0]:x})")
# METR 后 = 36+8+4+4 = 48 开始数据?
print("\n@48 起 64B:", d[48:112].hex(" "))
# u32@20 = 0x2e1341 = 3019073 接近 LOD0 后数据起点? LOD0 数据应该很大
# 假设每 entry: tag(4) + param(4) + size/offset(4)，METR param=64=条目数?
# 检查 0x88=136 和 0x2e1341 的关系: 0x2e1341 = 3019073; LOD0 区间 = 3019073?
print("\n假设: GEO0 段长 136, LOD0 段长 3019073, METR 条目数 64?")
print("METR 数据起始 @48, 64 条 × 4B = 256B → @48+256=304")
print("@304 起 32B:", d[304:336].hex(" "))
# 64 个 u32 表?
tbl = struct.unpack_from('<64I', d, 48)
print("METR 前 16 个 u32:", tbl[:16])
print("METR 后 16 个 u32:", tbl[-16:])
# GEO0 数据（@288 之后?）尝试从 304 找 GEO 数据
# 也扫一下 'BstBaked' 内更多 tag
tags = collections.Counter(m.group(1) for m in re.finditer(rb'([A-Z]{3}[0-9]|[A-Z]{4})\x00', d[:300000]))
print("\nNUL 结尾大写 tag:", dict(list(tags.items())[:20]))
