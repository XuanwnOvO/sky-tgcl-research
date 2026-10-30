# -*- coding: utf-8 -*-
# crack_hash3.py — 研究《光·遇》dump.cs 脱敏字段名 (16 hex) 的生成机制
import re, sys
from math import gcd

M64 = (1 << 64) - 1

# ---------- 数据读取 ----------
pairs = []  # (lineno, hex, classname)
with open(r'd:\新建文件夹\LightEncounters\hex_ctx.txt', 'r', encoding='utf-8', errors='replace') as f:
    for line in f:
        m = re.match(r'\s*(\d+)\s+([0-9A-Fa-f]{16})\s*->\s*class\s+(\S+)', line)
        if m:
            pairs.append((int(m.group(1)), m.group(2).upper(), m.group(3)))
print(f"[load] hex_ctx.txt: {len(pairs)} 条 (lineno, hex, class)")

names = set()
try:
    with open(r'd:\新建文件夹\LightEncounters\reg_all.txt', 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            m = re.search(r"name='([^']+)'", line)
            if m:
                names.add(m.group(1))
except FileNotFoundError:
    print("[warn] reg_all.txt 未找到")
print(f"[load] reg_all.txt: {len(names)} 个明文名")

# ---------- 基础 hash ----------
def fnv1a64(b):
    h = 0xCBF29CE484222325
    for c in b:
        h ^= c; h = (h * 0x100000001B3) & M64
    return h
def fnv1_64(b):
    h = 0xCBF29CE484222325
    for c in b:
        h = (h * 0x100000001B3) & M64; h ^= c
    return h
def fnv1a32(b):
    h = 0x811C9DC5
    for c in b:
        h ^= c; h = (h * 0x01000193) & 0xFFFFFFFF
    return h

# ---------- SipHash-2-4 纯 python ----------
def _sipround(v0, v1, v2, v3):
    v0 = (v0 + v1) & M64; v1 = ((v1 << 13) | (v1 >> 51)) & M64
    v1 ^= v0; v0 = ((v0 << 32) | (v0 >> 32)) & M64
    v2 = (v2 + v3) & M64; v3 = ((v3 << 16) | (v3 >> 48)) & M64
    v3 ^= v2
    v0 = (v0 + v3) & M64; v3 = ((v3 << 21) | (v3 >> 43)) & M64
    v3 ^= v0
    v2 = (v2 + v1) & M64; v1 = ((v1 << 17) | (v1 >> 47)) & M64
    v1 ^= v2; v2 = ((v2 << 32) | (v2 >> 32)) & M64
    return v0, v1, v2, v3

def siphash24(data, key=b'\x00'*16):
    k0 = int.from_bytes(key[0:8], 'little')
    k1 = int.from_bytes(key[8:16], 'little')
    v0 = k0 ^ 0x736F6D6570736575
    v1 = k1 ^ 0x646F72616E646F6D
    v2 = k0 ^ 0x6C7967656E657261
    v3 = k1 ^ 0x7465646279746573
    n = len(data)
    for i in range(n // 8):
        m = int.from_bytes(data[i*8:(i+1)*8], 'little')
        v3 ^= m
        for _ in range(2): v0, v1, v2, v3 = _sipround(v0, v1, v2, v3)
        v0 ^= m
    lb = (n & 0xFF) << 56
    tail = data[(n // 8) * 8:]
    lb |= int.from_bytes(tail, 'little')
    v3 ^= lb
    for _ in range(2): v0, v1, v2, v3 = _sipround(v0, v1, v2, v3)
    v0 ^= lb
    v2 ^= 0xFF
    for _ in range(4): v0, v1, v2, v3 = _sipround(v0, v1, v2, v3)
    return (v0 ^ v1 ^ v2 ^ v3) & M64

# ---------- 第 2 步: 类名+字段名组合 hash ----------
# 从 hex_ctx 的上下文无法得到明文字段名（已脱敏），因此组合测试思路：
# 用明文名集合中的短名（如 showIcon 等）配合已知类名，尝试命中 hex 值。
# 由于我们不知道每个字段原名的对应关系，先对「每个类名 × 每个明文名」的所有组合
# 做 FNV-1a64/FNV-1 64 查表——若任何一个组合命中已知 hex，即证明是组合 hash。
targets = {h: cls for _, h, cls in pairs}
hits = []
combos = 0
if names:
    for h, cls in targets.items():
        for base in (cls, cls.lower(), cls.upper()):
            for nm in names:
                for nmv in {nm, nm.lower(), nm.upper()}:
                    for sep in ('.', '_', ''):
                        for order in (base + sep + nmv, nmv + sep + base):
                            combos += 1
                            s = order.encode()
                            if fnv1a64(s) == int(h, 16) or fnv1_64(s) == int(h, 16):
                                hits.append((h, cls, nm, order))
print(f"[step2] 组合 hash 测试: {combos} 次组合, 命中 {len(hits)}")
for x in hits[:20]:
    print("  HIT:", x)

# ---------- 第 3 步: SipHash ----------
if names:
    sip_hits = []
    for h, cls in targets.items():
        t = int(h, 16)
        for nm in names:
            if siphash24(nm.encode()) == t or siphash24((cls + '.' + nm).encode()) == t:
                sip_hits.append((h, cls, nm))
    print(f"[step3] SipHash-2-4 (key=0): 命中 {len(sip_hits)}")
    for x in sip_hits[:20]: print("  HIT:", x)
else:
    print("[step3] 无明文名，跳过 SipHash")

# ---------- 第 4 步: FNV 位数混淆 ----------
if names:
    mix_hits = []
    for h, cls in targets.items():
        t = int(h, 16)
        for nm in names:
            s = nm.encode()
            a = fnv1a32(s); b = fnv1a32(s + b'\x00')
            cands = {
                'fnv32x2': (a << 32) | fnv1a32(s[::-1]),
                'fnv32x2_null': (a << 32) | b,
                'fnv1a64_xorshift': (fnv1a64(s) ^ (fnv1a64(s) >> 32)) & M64,
                'fnv1a64_plus_hi': ((fnv1a64(s) >> 32) ^ fnv1a64(s)) & M64,
            }
            for k, v in cands.items():
                if v == t:
                    mix_hits.append((h, cls, nm, k))
    print(f"[step4] FNV 位数混淆: 命中 {len(mix_hits)}")
    for x in mix_hits[:20]: print("  HIT:", x)
else:
    print("[step4] 无明文名，跳过")

# ---------- 第 5 步: 结构分析（核心） ----------
print("\n========== 结构分析: hex 是否为 计数器×常数 式可逆 ID ==========")
# 按类分组
byclass = {}
for ln, h, cls in pairs:
    byclass.setdefault(cls, []).append((ln, int(h, 16)))

# 5a: 逐字段差分 gcd 分析
print("\n--- 5a: 全局相邻（按文件出现顺序）差值 ---")
allvals = [(ln, v, cls) for ln, h, cls in pairs for v in [int(h, 16)]]
diffs = [allvals[i+1][1] - allvals[i][1] for i in range(len(allvals) - 1)]
g_hi = 0; g_lo = 0
for d in diffs:
    g_hi = gcd(g_hi, (d >> 32) & 0xFFFFFFFF if d >= 0 else -(d >> 32))
    g_lo = gcd(g_lo, d & 0xFFFFFFFF if d >= 0 else -d)
print(f"全局差值数量 {len(diffs)}, 高32位差 gcd={g_hi:#x}, 低32位差 gcd={g_lo:#x}")

print("\n--- 5b: 类内差分（高低 32 位分别） ---")
for cls, lst in byclass.items():
    if len(lst) < 2: continue
    lst.sort()
    print(f"\nclass {cls} ({len(lst)} 个字段):")
    prev = None
    his, los = [], []
    for ln, v in lst:
        hi, lo = v >> 32, v & M64 >> 0
        hi &= 0xFFFFFFFF
        lo = v & 0xFFFFFFFF
        print(f"  line {ln:6d}  hi={hi:08X}  lo={lo:08X}", end='')
        if prev is not None:
            dh = hi - prev[0]; dl = lo - prev[1]
            print(f"   d_hi={dh:+08X} d_lo={dl:+08X}  (d64={v - prev[2]:+#018x})", end='')
        print()
        prev = (hi, lo, v)
    # 拟合 h = a*i + b mod 2^64：a 取相邻差（若一致则线性可逆）
    ds = [lst[i+1][1] - lst[i][1] for i in range(len(lst)-1)]
    g = 0
    for d in ds: g = gcd(g, d if d >= 0 else -d)
    print(f"  类内 64bit 差值 gcd = {g:#x}" if g else "  类内差值无公共因子")
    # 检查是否 a*const 形式：全部相邻差是否相等
    if len(set(ds)) == 1:
        print(f"  !! 等差: a = {ds[0]:#x} -> h(i) = h0 + a*i 可逆, i = (h - h0)/a")
    else:
        # 检查差值之间是否也等差（二次）
        d2 = [ds[i+1] - ds[i] for i in range(len(ds)-1)]
        if len(set(d2)) == 1:
            print(f"  !! 二阶等差: 一阶差 {ds[0]:#x}, 二阶差 {d2[0]:#x} -> h(i)=h0+a*i+b*i(i-1)/2 可逆")

# 5c: 高32位与低32位是否各自是 常数×counter
print("\n--- 5c: 高/低 32 位独立线性检验 ---")
for cls, lst in byclass.items():
    if len(lst) < 3: continue
    lst.sort()
    his = [(v >> 32) & 0xFFFFFFFF for _, v in lst]
    los = [v & 0xFFFFFFFF for _, v in lst]
    for tag, arr in (('hi', his), ('lo', los)):
        ds = [arr[i+1] - arr[i] for i in range(len(arr)-1)]
        if len(set(ds)) == 1:
            print(f"  {cls}.{tag}: 等差 a={ds[0]:#010x} 首项={arr[0]:#010x}")

# 5d: 全局：所有 516 个值按出现顺序，检验是否存在 全局等差/等比结构
print("\n--- 5d: 全局线性 / 常数因子检验 ---")
gall = 0
for d in diffs: gall = gcd(gall, d if d >= 0 else -d)
print(f"全部相邻差值 gcd = {gall:#x}")
if gall:
    print(f"  -> 若为线性 ID，步长可能是 {gall} 的因子；检验值/步长是否为小整数:")
    sample = allvals[:10]
    for ln, v, cls in sample:
        q = v // gall if gall else 0
        print(f"    {v:#018x} / step = {q}")

# 5e: 检查高低两半是否含共同基数（如时间戳）
print("\n--- 5e: 高半/低半内部结构（BindMobileMenu 样例深挖） ---")
lst = sorted(byclass.get('BindMobileMenu', []))
for ln, v in lst:
    hi = (v >> 32) & 0xFFFFFFFF; lo = v & 0xFFFFFFFF
    print(f"  hi={hi:08X} ({hi})  lo={lo:08X} ({lo})")
# 尝试 v = a * i + b：用前两个差求出候选 a，再验证第三个
if len(lst) >= 3:
    a_cand = lst[1][1] - lst[0][1]
    ok = all((lst[i+1][1] - lst[i][1]) == a_cand for i in range(len(lst)-1))
    print(f"  BindMobileMenu 全等差? {ok}  (a_cand={a_cand:#x})")
    # 检查 a 是否为 small counter * const: a 的因子
    x = a_cand
    fac = []
    p = 2
    while p * p <= x and p < 100000:
        while x % p == 0: fac.append(p); x //= p
        p += 1
    if x > 1: fac.append(x)
    print(f"  a 的因子分解: {fac}")

# 5f: 十六进制字符串是否可能由两个字段拼接（高32位来自另一 hash/序号）
print("\n--- 5f: 高低两半独立出现频率 ---")
from collections import Counter
hi_c = Counter((v >> 32) & 0xFFFFFFFF for _, h, cls in pairs for v in [int(h,16)])
lo_c = Counter(int(h,16) & 0xFFFFFFFF for _, h, cls in pairs)
dup_hi = [(k, c) for k, c in hi_c.items() if c > 1]
dup_lo = [(k, c) for k, c in lo_c.items() if c > 1]
print(f"高32位重复值: {len(dup_hi)} 个 (示例 {sorted(dup_hi, key=lambda x:-x[1])[:5]})")
print(f"低32位重复值: {len(dup_lo)} 个 (示例 {sorted(dup_lo, key=lambda x:-x[1])[:5]})")

# ---------- 第 6 步: 结论辅助 ----------
print("\n========== 结论辅助 ==========")
# 检验"随机 hash"假设：相邻字段差值应均匀分布；检验"线性 ID"假设：差值应集中
small = sum(1 for d in diffs if abs(d) < (1 << 40))
print(f"相邻差值 |d| < 2^40 的比例: {small}/{len(diffs)}  "
      f"(若为随机 hash，期望约 {len(diffs)*(2**40/2**64):.2f})")

# 检验文件顺序 vs 数值顺序相关性 (Spearman 简化: 比较两排序的一致率)
order_by_line = [v for _, v, _ in allvals]
order_by_val = sorted(order_by_line)
rank = {v: i for i, v in enumerate(order_by_val)}
same = sum(1 for i in range(len(order_by_line)-1)
           if rank[order_by_line[i]] < rank[order_by_line[i+1]])
print(f"出现顺序与数值顺序的单调一致率: {same}/{len(order_by_line)-1} = {same/(len(order_by_line)-1):.3f}")

# 类内检查
mono_total = mono_cls = 0
for cls, lst in byclass.items():
    if len(lst) < 2: continue
    lst.sort()
    vs = [v for _, v in lst]
    sv = sorted(vs)
    mono_total += 1
    if vs == sv: mono_cls += 1
print(f"类内数值升序的类: {mono_cls}/{mono_total}")
