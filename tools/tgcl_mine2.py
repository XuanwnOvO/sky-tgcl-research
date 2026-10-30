# -*- coding: utf-8 -*-
# 深挖批：49B 真串过滤 / 391B shader uniform 结构 / BstBaked.meshes chunk 表
import os, re, struct, collections
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"
LEVELS = ["Dawn", "CandleSpace", "DuskGraveyard", "RainForest"]

print("=" * 30, "① 49B 参数块真串（严格过滤）", "=" * 30)
# 真串标准：以字母开头、只含 [A-Za-z0-9_./-]、≥5 字符、且后面跟 \0 或至少不被 0x00 打断
pat = re.compile(rb'(?:(?<=[\x00\x01])|(?<=\x00))([A-Za-z][A-Za-z0-9_./-]{4,60})(?=\x00|$)', re.M)
allnames = collections.Counter()
per_lv = {}
for lv in LEVELS:
    d = open(os.path.join(root, lv, "Objects.level.bin"), "rb").read()
    o4 = struct.unpack_from("<5I", d, 24)[3]
    seg = d[o4:]
    ms = list(re.finditer(rb"BstNode_(\d+)\x00", seg))
    names = []
    for i, m in enumerate(ms):
        a = m.start()
        e = ms[i+1].start() if i+1 < len(ms) else len(seg)
        body = seg[a:e-4]; hl = m.end()-m.start(); p = body[hl:]
        if len(p) != 49: continue
        for sm in pat.finditer(p):
            names.append(sm.group(1).decode())
    per_lv[lv] = collections.Counter(names)
    allnames.update(names)
    print(f"{lv:14} 真串 {len(names):>4} 条, 唯一 {len(set(names)):>4}")
print("\n跨关唯一:", len(allnames))
print("全部串（按频次）:")
for s, c in allnames.most_common(60):
    print(f"  {c:>3}  {s}")

print("\n" + "=" * 30, "② 391B 块 uniform 结构", "=" * 30)
d = open(os.path.join(root, "DuskGraveyard", "Objects.level.bin"), "rb").read()
o4 = struct.unpack_from("<5I", d, 24)[3]
seg = d[o4:]
ms = list(re.finditer(rb"BstNode_(\d+)\x00", seg))
blk = None
for i, m in enumerate(ms):
    a = m.start()
    e = ms[i+1].start() if i+1 < len(ms) else len(seg)
    body = seg[a:e-4]; hl = m.end()-m.start(); p = body[hl:]
    if len(p) == 391 and b'u_texSpots' in p:
        blk = p; break
if blk:
    names = [b'u_texSpots', b'u_diffuseColor', b'u_normal', b'u_uvOffset', b'u_spotsColor']
    print("串偏移:", {n.decode(): blk.find(n) for n in names})
    # 假设：uniform 块 = N 个条目 [名字\0][值]，按偏移切
    pos = blk.find(b'u_texSpots')
    print("前 40B（串前）:", blk[:40].hex(" "))
    print("u_texSpots 后 32B:", blk[pos+10:pos+42].hex(" "))
    f = struct.unpack_from('<4f', blk, pos+10)
    print("  按 f32×4:", [round(x,4) for x in f])
    # 找 u_diffuseColor 后面的值
    p2 = blk.find(b'u_diffuseColor')
    print(f"u_diffuseColor@{p2} 后 16B:", blk[p2+14:p2+30].hex(" "),
          [round(x,4) for x in struct.unpack_from('<4f', blk, p2+14)])
    p3 = blk.find(b'u_spotsColor')
    print(f"u_spotsColor@{p3} 尾部:", blk[p3+12:p3+28].hex(" "),
          [round(x,4) for x in struct.unpack_from('<4f', blk, p3+12)])
    print("尾部 24B:", blk[-24:].hex(" "))

print("\n" + "=" * 30, "③ BstBaked.meshes chunk 表", "=" * 30)
d = open(os.path.join(root, "Dawn", "BstBaked.meshes"), "rb").read()
print("大小:", len(d))
# 头: 'LVL0' + u32? + u32 count?
print("头 16B:", d[:16].hex(" "), "=", d[:4], struct.unpack_from('<2I', d, 4))
# 扫 chunk 标签
tags = collections.Counter()
positions = {}
for m in re.finditer(rb'(GEO0|LOD0|METR|LVL0|MAT0|SHD0|TEX0|BONE|VERT|IDX0)', d[:2000000]):
    tags[m.group(1)] += 1
    positions.setdefault(m.group(1), []).append(m.start())
print("chunk 标签计数:", dict(tags))
for t, ps in positions.items():
    print(f"  {t}: 首偏移 {ps[:5]}")
# LVL0 头解析
c = struct.unpack_from('<I', d, 4)[0]
print(f"LVL0 头: u32@4 = {c} (可能是 chunk 数)")
off = 8
for i in range(min(c, 8)):
    sz = struct.unpack_from('<I', d, off)[0]
    print(f"  chunk[{i}] @+{off+4}: size={sz}")
    off += 4 + sz
