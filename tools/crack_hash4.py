# -*- coding: utf-8 -*-
# crack_hash4.py — 深挖: 多项式基数识别 / 乘法计数器 h = M*n mod 2^64
import re, sys
from math import gcd
from collections import Counter

M64 = 1 << 64
FILE = r'd:\新建文件夹\LightEncounters\dump.cs'

# ---------- 读取全部脱敏字段 ----------
recs = []  # (lineno, hex, cls)
cur_cls = '?'
with open(FILE, 'r', encoding='utf-8', errors='replace') as f:
    for ln, line in enumerate(f, 1):
        mc = re.match(r'\s*class\s+(\S+)', line)
        if mc:
            cur_cls = mc.group(1)
        for m in re.finditer(r'\b([0-9A-F]{16})\b', line):
            h = m.group(1)
            # 启发式：脱敏字段名出现在成员声明位置（排除纯偏移注释）
            if re.match(r'\s*(public|private|protected|internal).*\s' + h + r'\s*;', line):
                recs.append((ln, h, cur_cls))
print(f"[load] dump.cs: {len(recs)} 个脱敏字段")

byclass = {}
for ln, h, cls in recs:
    byclass.setdefault(cls, []).append((ln, int(h, 16)))
for c in byclass: byclass[c].sort()

# ---------- 收集所有类内相邻差值 ----------
diffs = []
for cls, lst in byclass.items():
    for i in range(len(lst) - 1):
        d = lst[i+1][1] - lst[i][1]
        diffs.append((cls, d, lst[i][0]))
sdiffs = sorted(set(abs(d) for _, d, _ in diffs))
print(f"[diffs] 类内相邻差值 {len(diffs)} 个, 绝对值去重 {len(sdiffs)} 个")
print("  最小的 10 个:", [hex(x) for x in sdiffs[:10]])

# ---------- 思路A: 差值整数 gcd → 公共乘数 M ----------
g = 0
for _, d, _ in diffs:
    g = gcd(g, abs(d))
print(f"\n[A] 全部类内差值的整数 gcd = {g:#x}")
if g > 1:
    qs = Counter(d // g for _, d, _ in diffs)
    print(f"    差值/g 的商分布(前10): {qs.most_common(10)}")

# 两两 gcd，找常见大公因子
pair_g = Counter()
dl = [abs(d) for _, d, _ in diffs]
for i in range(len(dl)):
    for j in range(i+1, len(dl)):
        gg = gcd(dl[i], dl[j])
        if gg > 1:
            pair_g[gg] += 1
print(f"    两两 gcd > 1 的组合: {len(pair_g)}; 最大几个: {[hex(x[0]) for x in pair_g.most_common(5)]}")

# ---------- 思路B: Δ = δ * R^k (多项式 hash 基数识别) ----------
BASES = {
    'FNV64prime': 0x100000001B3,
    'FNV32prime': 0x01000193,
    'djb2(33)': 33, 'sdbm(65599)': 65599, 'karp31': 31, 'x131': 131,
    'x37': 37, 'x17': 17, 'x1313': 1313, 'x5381': 5381,
    'golden64': 0x9E3779B97F4A7C15, 'golden32': 0x9E3779B1,
    'LCG64': 6364136223846793005, 'LCG64b': 2862933555777941757,
    '2^32': 1 << 32, '2^16': 1 << 16, '2^24': 1 << 24,
    'splitmixMul': 0xbf58476d1ce4e5b9, 'murmulC1_64': 0x87c37b91114253d5,
    'murmulC2_64': 0x4cf5ad432745937f,
}
print("\n[B] 检验 Δ = δ * R^k mod 2^64 (δ 为小整数 |δ|<2^24, k=0..32):")
found = []
for name, R in BASES.items():
    Rk = 1
    for k in range(0, 33):
        # δ = D * R^{-k} mod 2^64
        try:
            inv = pow(Rk, -1, M64)
        except ValueError:
            break
        cnt = 0
        for _, d, _ in diffs:
            delta = (d * inv) % M64
            if delta < (1 << 24) or delta >= M64 - (1 << 24):
                cnt += 1
        if cnt >= 2:
            found.append((cnt, name, k))
            print(f"    {name} k={k}: {cnt}/{len(diffs)} 个差值匹配小 δ")
        Rk = (Rk * R) % M64
if not found:
    print("    无任何基数匹配")

# ---------- 思路C: h = M * n mod 2^64 (乘法计数器) ----------
print("\n[C] 检验 h = M * n mod 2^64:")
vals = [v for _, h, cls in recs for v in [int(h, 16)]]
# 候选 M：从相邻差值及其小因子中取
candM = set()
for _, d, _ in diffs:
    ad = abs(d)
    candM.add(ad)
    # 也试 ad / 小商
    for q in range(2, 64):
        if ad % q == 0:
            candM.add(ad // q)
# 加上经典乘数
candM.update([0x9E3779B97F4A7C15, 6364136223846793005, 2862933555777941757,
              0xbf58476d1ce4e5b9, 0x94d049bb133111eb, 0x100000001B3])
hits = []
for M in candM:
    if M % 2 == 0:
        continue
    try:
        inv = pow(M, -1, M64)
    except ValueError:
        continue
    ns = [(v * inv) % M64 for v in vals]
    small = sum(1 for n in ns if n < (1 << 40))
    if small >= len(vals) // 2:
        hits.append((small, M, ns[:8]))
hits.sort(reverse=True)
for s, M, ns in hits[:5]:
    print(f"    M={M:#x}: {s}/{len(vals)} 个值反解出 n < 2^40, 示例 n={[hex(x) for x in ns]}")
if not hits:
    print("    无候选乘数使多数值反解为小 n")

# ---------- 思路D: 差值比值恒定? 检验 hi/lo 比例 ----------
print("\n[D] 类内差值 hi32/lo32 比值分布 (检测固定乘数结构):")
rats = []
for cls, d, ln in diffs:
    hi = (d >> 32) & 0xFFFFFFFF
    lo = d & 0xFFFFFFFF
    if lo and abs(d) < (1 << 62):
        rats.append(round(abs(hi) / abs(lo), 4))
rc = Counter(rats)
print(f"    最常见比值: {rc.most_common(8)}")

# 若比值集中在 ~r，则 D ≈ δ*(2^32 + r^{-1})... 反解: 试 C = 2^32 + c
# D = δ*C mod 2^64 → 对 D3、D4 联立: D4/D1 是否有理 → 用连分数找 C
print("\n[E] 连分数法: 假设 D = δ*C (整数), 从两个大差值求公共 C:")
big = sorted([abs(d) for _, d, _ in diffs], reverse=True)[:8]
print("    最大差值:", [hex(x) for x in big])
# 对每对 (D_i, D_j) 做辗转相除展开看商序列是否吻合小整数模式
from fractions import Fraction
for i in range(min(3, len(big))):
    for j in range(i+1, min(4, len(big))):
        a, b = big[i], big[j]
        qs = []
        while b and len(qs) < 8:
            qs.append(a // b); a, b = b, a % b
        print(f"    gcd展开 {hex(big[i])},{hex(big[j])}: 商={qs}, gcd={hex(big[i] if not b else a if False else gcd(big[i],big[j]))}")

# ---------- 思路F: 直接检验经典结构: h = (h_prev * P + c) 滚动? ----------
# 更强检验: 若是 FNV-1a 类, h = ((prefix_h ^ c)*P...), 对"只差末字符"的字段:
#   Δ = P * ((x ^ c2) - (x ^ c1)) —— 检验 Δ 是否 ≡ 0 mod P
P = 0x100000001B3
cntP = sum(1 for _, d, _ in diffs if d % P == 0)
print(f"\n[F] 类内差值被 FNV 素数 P={P:#x} 整除的个数: {cntP}/{len(diffs)}")
cntP2 = sum(1 for _, d, _ in diffs if d % 0x10000000193 == 0)
print(f"    被 0x10000000193 整除: {cntP2}")
# 高低 32 位分别整除检验
hiP = sum(1 for _, d, _ in diffs if ((d >> 32) & 0xFFFFFFFF) % 0x01000193 == 0 and (d>>32)&0xFFFFFFFF)
loP = sum(1 for _, d, _ in diffs if (d & 0xFFFFFFFF) % 0x01000193 == 0 and d & 0xFFFFFFFF)
print(f"    高32位被 FNV32 素数整除: {hiP}, 低32位: {loP}")

# ---------- 思路G: 把 16hex 当两个独立 32bit 值? 检验 hi、lo 是否各自满足 h=M*n ----------
print("\n[G] hi/lo 32 位各自 = M32 * n 检验 (取 lo 差值 gcd):")
glo = 0; ghi = 0
for _, d, _ in diffs:
    glo = gcd(glo, d & 0xFFFFFFFF)
    ghi = gcd(ghi, (d >> 32) & 0xFFFFFFFF)
print(f"    lo 差值 gcd = {glo:#x}, hi 差值 gcd = {ghi:#x}")
if glo:
    los = sorted(set(v & 0xFFFFFFFF for v in vals))
    inv = pow(glo, -1, 1 << 32) if glo % 2 else None
    if inv:
        ns = [(x * inv) % (1 << 32) for x in los]
        print(f"    lo/glo 反解 n 示例: {[hex(x) for x in ns[:10]]}")
