# -*- coding: utf-8 -*-
# 静态扫尾批：c4 含义 / 49B 参数块细分 / bigblock 签名 / segB type 枚举 / 附带文件头
import os, re, struct, json, collections
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"
LEVELS = ["Dawn", "CandleSpace", "DuskGraveyard", "RainForest"]

print("=" * 30, "① 头部 c4/o5 vs 文件大小", "=" * 30)
for lv in LEVELS:
    d = open(os.path.join(root, lv, "Objects.level.bin"), "rb").read()
    c1, c2, c3, c4 = struct.unpack_from("<4I", d, 8)
    o1, o2, o3, o4, o5 = struct.unpack_from("<5I", d, 24)
    segd = len(d) - o4
    print(f"{lv:14} size={len(d):>8} c4={c4:>8} o5={o5:>8} o4={o4:>8} segD={segd:>8} "
          f"c4/segD={c4/max(segd,1):.3f} o5==size?{o5==len(d)} c4-o4={c4-o4}")

print("\n" + "=" * 30, "② 49B 参数块内嵌串提取", "=" * 30)
strpool = collections.Counter()
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
        sm = re.search(rb'[\x20-\x7e]{4,}', p)
        if sm: names.append(sm.group(0).decode())
    strpool.update(names)
    print(f"{lv:14} 49B参数块 {len(names):>5} 条, 唯一串 {len(set(names)):>5}")
print("跨关唯一串总数:", len(strpool))
print("样例 30:", list(strpool)[:30])
# 分类
pref = collections.Counter(s.split('_')[0] for s in strpool)
print("前缀分布:", pref.most_common(15))

print("\n" + "=" * 30, "③ bigblock(391B) 四关签名对比", "=" * 30)
sigs = {}
for lv in LEVELS:
    d = open(os.path.join(root, lv, "Objects.level.bin"), "rb").read()
    o4 = struct.unpack_from("<5I", d, 24)[3]
    seg = d[o4:]
    ms = list(re.finditer(rb"BstNode_(\d+)\x00", seg))
    for i, m in enumerate(ms):
        a = m.start()
        e = ms[i+1].start() if i+1 < len(ms) else len(seg)
        body = seg[a:e-4]; hl = m.end()-m.start(); p = body[hl:]
        if len(p) == 391:
            sigs[lv] = p
            break
lvs = list(sigs)
if len(lvs) >= 2:
    a, b = sigs[lvs[0]], sigs[lvs[1]]
    same = sum(1 for i in range(391) if a[i] == b[i])
    print(f"{lvs[0]} vs {lvs[1]} 391B 相同字节: {same}/391 ({same*100//391}%)")
    print(lvs[0], "头64B:", sigs[lvs[0]][:64].hex(" "))
    # 找内嵌串
    for lv in lvs:
        sm = re.findall(rb'[\x20-\x7e]{4,}', sigs[lv])
        print(lv, "内嵌串:", sm[:5])

print("\n" + "=" * 30, "④ segB type 字节跨关枚举", "=" * 30)
for lv in LEVELS:
    d = open(os.path.join(root, lv, "Objects.level.bin"), "rb").read()
    c1, c2, c3, c4 = struct.unpack_from("<4I", d, 8)
    o1, o2, o3, o4, o5 = struct.unpack_from("<5I", d, 24)
    segB = d[o2:o3]
    types = collections.Counter()
    for j in range(c2):
        t = struct.unpack_from("<4I", segB, j*16)[2]
        types[t] += 1
    print(f"{lv:14} {dict(types.most_common(12))}")

print("\n" + "=" * 30, "⑤ 附带文件头", "=" * 30)
lv = "Dawn"
for fn in ["Resources.lua.luac", "BstBaked.meshes"]:
    p = os.path.join(root, lv, fn)
    if os.path.exists(p):
        b = open(p, "rb").read(96)
        print(f"\n{fn}  size={os.path.getsize(p)}")
        print("  头64B:", b[:64].hex(" "))
        print("  可读片段:", re.findall(rb'[\x20-\x7e]{4,}', b)[:5])
