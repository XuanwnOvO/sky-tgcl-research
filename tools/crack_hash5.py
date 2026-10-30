# -*- coding: utf-8 -*-
# crack_hash5.py — 定向: 验证 FNV 素数结构 + 编码/输入变体爆破
import re
from collections import Counter

M64 = 1 << 64
P = 0x100000001B3
Pinv = pow(P, -1, M64)

# ---------- 载入 ----------
recs = []
cur = '?'
with open(r'd:\新建文件夹\LightEncounters\dump.cs', 'r', encoding='utf-8', errors='replace') as f:
    for ln, line in enumerate(f, 1):
        mc = re.match(r'\s*class\s+(\S+)', line)
        if mc: cur = mc.group(1)
        for m in re.finditer(r'\b([0-9A-F]{16})\b', line):
            h = m.group(1)
            if re.match(r'\s*(public|private|protected|internal).*\s' + h + r'\s*;', line):
                recs.append((ln, int(h, 16), str(cur)))
targets = {h: cls for ln, h, cls in recs}
targets = {k: (v if isinstance(v, str) else '?') for k, v in targets.items()}
print(f"[load] {len(recs)} 个脱敏字段, {len(targets)} 个唯一值")

# ---------- 明文名 ----------
names = set()
with open(r'd:\新建文件夹\LightEncounters\reg_all.txt', 'r', encoding='utf-8', errors='replace') as f:
    for line in f:
        m = re.search(r"name='([^']+)'", line)
        if m: names.add(m.group(1))
print(f"[load] {len(names)} 个明文名")

# ---------- 1. δ = Δ/P 结构 ----------
byclass = {}
for ln, h, cls in recs:
    byclass.setdefault(cls, []).append((ln, h))
print("\n--- δ = Δ * P^-1 分析 (类内相邻差) ---")
deltas = []
for cls, lst in byclass.items():
    lst.sort()
    for i in range(len(lst) - 1):
        D = lst[i+1][1] - lst[i][1]
        d = (D * Pinv) % M64
        deltas.append((cls, lst[i][1], lst[i+1][1], D, d))
def band(d):
    if d < 128 or d >= M64 - 128: return '<2^7'
    if d < (1<<16) or d >= M64 - (1<<16): return '<2^16'
    if d < (1<<24) or d >= M64 - (1<<24): return '<2^24'
    if d < (1<<32) or d >= M64 - (1<<32): return '<2^32'
    if d < (1<<40) or d >= M64 - (1<<40): return '<2^40'
    return 'big'
cb = Counter(band(d) for *_, d in deltas)
print(f"δ 分布: {dict(cb)}  (共 {len(deltas)})")
small = [(cls, h1, h2, d) for cls, h1, h2, D, d in deltas
         if d < (1 << 16) or d >= M64 - (1 << 16)]
print(f"δ < 2^16 的对 ({len(small)}):")
for cls, h1, h2, d in small[:20]:
    dd = d if d < (1<<63) else d - M64
    print(f"  {cls}: {h1:#018x} -> {h2:#018x}  δ={dd}")

# δ 相同值聚类（同一对末字符 + 同一前缀哈希低字节 → δ 相同）
dc = Counter(d for *_, d in deltas if d < (1<<40) or d >= M64-(1<<40))
print("小 δ 重复值(前10):", [(hex(k), v) for k, v in dc.most_common(10)])

# ---------- 2. 变体爆破 ----------
def fnv1a(data, basis):
    h = basis
    for c in data:
        h ^= c; h = (h * P) % M64
    return h
def fnv1(data, basis):
    h = basis
    for c in data:
        h = (h * P) % M64; h ^= c
    return h
def poly(data, basis):
    h = basis
    for c in data:
        h = (h * P + c) % M64
    return h

BASIS = [0xCBF29CE484222325, 0, 0x811C9DC5, 0x9E3779B97F4A7C15]
schemes = [('fnv1a', fnv1a), ('fnv1', fnv1), ('poly', poly)]

def variants(cls, nm):
    cls = str(cls) if not isinstance(cls, str) else cls
    nm = str(nm)
    encs = {
        'u8': nm.encode(), 'u16': nm.encode('utf-16-le'),
        'u8z': nm.encode() + b'\x00', 'u16z': nm.encode('utf-16-le') + b'\x00\x00',
        'u16be': nm.encode('utf-16-be'),
    }
    outs = {}
    for k, b in encs.items(): outs[k] = b
    if cls and cls != '?':
        for sep in ('.', '_', '/', ':'):
            outs['cls' + sep + 'u8'] = (cls + sep + nm).encode()
            outs['cls' + sep + 'u16'] = (cls + sep + nm).encode('utf-16-le')
            outs['u8' + sep + 'cls'] = (nm + sep + cls).encode()
    outs['lower_u8'] = nm.lower().encode()
    return outs

print("\n--- 爆破 (scheme × basis × input-variant, 预计算比对) ---")
hits = []
# 收集所有变体输入
all_inputs = []  # (vk, bytes)
seen_inputs = set()
for cls in set(targets.values()):
    for nm in names:
        for vk, vb in variants(cls, nm).items():
            if vb not in seen_inputs:
                seen_inputs.add(vb)
                all_inputs.append((vk, cls, nm, vb))
print(f"唯一输入变体: {len(all_inputs)}")
for vk, cls, nm, vb in all_inputs:
    for sk, sf in schemes:
        for bk in BASIS:
            h = sf(vb, bk)
            if h in targets:
                hits.append((hex(h), targets[h], nm, vk, sk, hex(bk)))
print(f"命中 {len(hits)}")
for x in hits[:30]: print("  HIT:", x)

# ---------- 3. 如果 fnv1a 结构成立，做“剥素数”看 X = h/P 是否像 (prev ^ char)*? ----------
print("\n--- 剥素数: X = h * P^-1, 观察 X 低 8 位与末字符假设 ---")
# 对 FNV-1a: h = (Y ^ c)*P → Y = X ^ c, Y 应为合法中间态(任意)。
# 但若 poly(h=h*P+c): h = Y*P + c → c = h mod P? 不可行(mod 2^64)。
# 检查 h mod P 是否小 (poly 结构 h = ... mod 2^64 无此性质; 但若全程 mod P 则 h < P)
cnt_modP = sum(1 for t in targets if t < P)
print(f"h < P 的个数: {cnt_modP}/{len(targets)} (若全程 mod P 应为全部)")

# ---------- 4. 双 hash 拼接验证: 低32 = fnv1a32(name), 高32 = ? ----------
def fnv1a32(data):
    h = 0x811C9DC5
    for c in data:
        h ^= c; h = (h * 0x01000193) & 0xFFFFFFFF
    return h
lo_match = 0
lo_map = {}
for t, cls in targets.items():
    lo = t & 0xFFFFFFFF
    lo_map[lo] = cls
print("\n--- 若低32位是某 32bit hash, 检查高32位与低32位的相关性 ---")
# hi/lo 比值签名再确认
sig = 0
for t in targets:
    hi = t >> 32; lo = t & 0xFFFFFFFF
    if lo and 435 * (hi // 256) < (1 << 32):
        # 检查 t 是否 = δ*P 形式本身(首字段也可能是 δ*P+base)
        pass
# 直接: 全部值能否写成 base + Σ δ_i P^k? 检验 h*P^-1 的低位是否 ASCII 化
print("X=h/P 的低字节分布 (若 poly/fnv1a 且末字符 ASCII, X 低位应有结构):")
lb = Counter((t * Pinv) % 256 for t in targets)
print("  top10:", lb.most_common(10))
lb8 = Counter(t & 0xFF for t in targets)
print("h 本身低字节 top10:", lb8.most_common(10))
