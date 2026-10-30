# -*- coding: utf-8 -*-
# Lua↔TGCL 交叉对照：Dawn Resources.lua 的资源名 ↔ segD 49B 参数块/segC 字符串池
import re, struct, collections, os
root = r"d:\新建文件夹\LightEncounters"

# ① Lua 侧：Dawn Resources.lua 资源类型分布 + 全名集合
src = open(os.path.join(root, r"decompiled_lua\Levels\Dawn\Resources.lua"), encoding="utf-8").read()
types = collections.Counter(re.findall(r'resource\("([^"]+)"\)', src))
print("== Dawn Resources.lua 资源类型 ==")
for t, c in types.most_common(25):
    print(f"  {c:>4}  {t}")
lua_names = set(re.findall(r'resource\("[^"]+"\)\("([^"]+)"\)', src))
print("资源名总数:", len(lua_names))
print("行数:", src.count("\n"))

# ② TGCL 侧：segC 字符串池全部字符串
d = open(os.path.join(root, r"Children of the Light\Levels\Dawn\Objects.level.bin"), "rb").read()
o3, o4 = struct.unpack_from("<5I", d, 24)[2:4]
segC = d[o3:o4]
pool = set(s.decode('utf-8', 'replace') for s in segC.split(b'\x00') if len(s) >= 4)
print("\n== segC 字符串池 ==", len(pool), "条(≥4字符)")

# ③ 交叉命中
hit = lua_names & pool
print("Lua资源名 ∩ segC池:", len(hit), "条")
for s in sorted(hit)[:40]:
    print("  ", s)

# ④ segD 49B 参数块真串 ∩ Lua 名
seg = d[o4:]
ms = list(re.finditer(rb"BstNode_(\d+)\x00", seg))
pat = re.compile(rb'(?<=\x00)([A-Za-z][A-Za-z0-9_./-]{4,60})(?=\x00|$)')
p49 = []
for i, m in enumerate(ms):
    a = m.start()
    e = ms[i+1].start() if i+1 < len(ms) else len(seg)
    body = seg[a:e-4]; hl = m.end()-m.start(); p = body[hl:]
    if len(p) == 49:
        for sm in pat.finditer(p):
            p49.append((i, int(m.group(1)), sm.group(1).decode()))
print("\n== 49B 参数块真串 ==", len(p49))
for i, rid, s in p49[:20]:
    inlua = s in lua_names
    print(f"  rec={i:>5} id={rid} {s} {'<-- Lua资源!' if inlua else ''}")

# ⑤ 组件槽 comp 名 ∩ Lua 脚本函数（粗查 Dawn/Script.level 源码是否存在）
for cand in [r"decompiled_lua\Levels\Dawn\Script.lua"]:
    print(cand, os.path.exists(os.path.join(root, cand)))
