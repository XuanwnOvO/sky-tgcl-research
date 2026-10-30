# -*- coding: utf-8 -*-
# crack_hash6.py — δ 符号链诊断：还原滚动方向/字符序/最终操作
from collections import Counter, defaultdict

M64 = 1 << 64
P = 0x100000001B3
Pinv = pow(P, -1, M64)

# δ 查表: FNV-1a 末步 h=(prev^c)*P → Δ=(prev^c2)*P-(prev^c1)*P ≠ 小整数
# 但若 hash = poly: h = h*P + c (mod 2^64)，末步: Δ = (h1*P + c2) - (h0*P + c1)
#   其中 h0 = hash(去尾). Δ = P*(h0'-h0'') ... 复杂。
# 关键观察：Δ = δ*P 精确成立 → 末字符处理是 XOR 后乘，且 prev 相同!
# FNV-1a: Δ = ((y^c2)-(y^c1))*P，y=共同前缀hash。所以 δ = (y^c2)-(y^c1)
#   y 固定时 δ 由 (c1,c2) 决定 → 我们可以反解 y 的低位!
# δ = (y^c2) - (y^c1)。c 为 ASCII (32..127)。
# 取 δ=5, c2-c1... 枚举 y 的低位 8bit 与字符对，找一致解。
import re
recs = []
cur = '?'
with open(r'd:\新建文件夹\LightEncounters\dump.cs', 'r', encoding='utf-8', errors='replace') as f:
    for ln, line in enumerate(f, 1):
        mc = re.match(r'\s*class\s+(\S+)', line)
        if mc: cur = str(mc.group(1))
        for m in re.finditer(r'\b([0-9A-F]{16})\b', line):
            h = m.group(1)
            if re.match(r'\s*(public|private|protected|internal).*\s' + h + r'\s*;', line):
                recs.append((ln, int(h, 16), cur))

byclass = defaultdict(list)
for ln, h, cls in recs: byclass[cls].append((ln, h))
for c in byclass: byclass[c].sort()

pairs_small = []
for cls, lst in byclass.items():
    for i in range(len(lst)-1):
        D = lst[i+1][1] - lst[i][1]
        d = (D * Pinv) % M64
        if d < 256 or d >= M64 - 256:
            pairs_small.append((cls, lst[i][1], lst[i+1][1], d if d < (1<<63) else d - M64))

print(f"δ∈[-256,256] 的相邻对: {len(pairs_small)}")

# 假设 A: FNV-1a, y 为共同前缀 hash。δ = (y^c2)-(y^c1)
# y 的低 8 位 y0: (y^c) 的低 8 位 = y0^c. δ mod 256 = (y0^c2)-(y0^c1) mod 256
# 枚举 y0 ∈ [0,256), c1,c2 ∈ ASCII, 找满足所有观测 δ 的 y0 集合
obs = [(d % 256 if d >= 0 else -((-d) % 256)) for _, _, _, d in pairs_small]
cand_y0 = []
for y0 in range(256):
    ok = True
    for d in obs:
        found = False
        for c1 in range(32, 127):
            for c2 in range(32, 127):
                if ((y0 ^ c2) - (y0 ^ c1)) % 256 == d % 256:
                    found = True; break
            if found: break
        if not found: ok = False; break
    if ok: cand_y0.append(y0)
print(f"假设A(FNV-1a尾XOR) y 低8位候选: {cand_y0}")

# 假设 B: poly h=h*P+c: Δ = P*(h0-h0') + (c2-c1)? 不成立，因为 h0 不同。
#   实际: h2 = H(c2末), h1 = H(c1末), H = P^k*a + P^(k-1)*c2 + ... 
#   Δ = P^(k-1)*(c2-c1) → δ = (c2-c1)*P^{k-2}... 不一定是小整数，除非 k-2=0。
#   即若 δ = c2-c1 (k=2, 2字符名!) → 检查 δ 是否都落在 |c2-c1| 可达范围
print("\n假设B: δ 直接 = 字符差 (即名字只有2字符或前缀归零):")
for cls, h1, h2, d in pairs_small[:25]:
    print(f"  δ={d:4d}  {'=ASCII差?' if abs(d)<95 else ''}")

# 假设 C: 末字符先乘后异或 (fnv1): Δ = y*(P-1) + (c2-c1)... 
#   fnv1: h = prev*P ^ c → Δ = (prev2*P^c2)-(prev1*P^c1), prev 相同: 
#   Δ = prev*(P-P) ^... 不对, XOR 与乘不线性。跳过。

# 假设 D: h = (h + c) * P (滚动加): Δ = (c2-c1)*P → δ = c2-c1 纯字符差!
#   与假设B相同数学形式: δ = c2 - c1。检验所有 |δ|<256 的 δ 是否都是合法 ASCII 差且一致。
print("\n假设D检验: 若 δ=c2-c1, 每个观测 δ 应 ∈[-95,95]:")
viol = [d for _, _, _, d in pairs_small if abs(d) > 95]
print(f"  违例数: {len(viol)} / {len(pairs_small)}  违例δ: {viol[:10]}")

# 若假设D成立 → h = base + Σ c_i * P^(L-i) mod 2^64 = 多项式滚动(类似 Rabin-Karp 无 mod)
# 则对每个字段 h = ((...((0*P+c1)*P+c2)...)*P+cL)，末字符 c_L = 低字节参与最后一次乘
# 关键可验证预测: h mod P? h = Σ c_i P^(L-i) → h mod P = c_L (若全程无 mod 2^64 截断) 
# 但有截断，不成立。改验证: h * P^{-L} ≈ 名字数字。另一验证: 
#   h(c1..cL) = P*h(c1..c_{L-1}) + c_L 精确 mod 2^64。
# 由 δ=P*(c2-c1) 验证: Δ 精确 = δ*P 已证实!
# 那么从任意一个 h 反推: 若知道长度 L, h = Σ c_i P^{L-i} mod 2^64, 
#   c_L = ? 不可直接除。但 h_{L-1} = (h_L - c_L)/P, c_L ∈ ASCII:
print("\n--- 由 h=c 滚动模型, 枚举末字符恢复前缀链 ---")
def crack(h, L, cset=range(32,127)):
    """h = Σ c_i P^{L-i}; 递归枚举末字符"""
    if L == 0:
        return [] if h == 0 else None
    Pk = pow(P, L-1, M64)
    for c in cset:
        # h - c ≡ 0? 需 (h - c) * Pinv^{?} ... 直接: prev = (h - c)*Pinv
        prev = ((h - c) * Pinv) % M64
        r = crack(prev, L-1, cset)
        if r is not None:
            return r + [c]
    return None

# 但截断使 c 不唯一。测试: 对已知简单名验证。先对 δ 对:
# 若 h2-h1 = (c2-c1)*P, 则两名字长度相同且前缀 hash 相同。
# 检验相邻 δ 对的传递闭包: δ 链如 +2,+3,-5 是否构成小字符差链
print("δ 链示例 (同一类内连续):")
for cls, lst in byclass.items():
    ds = []
    for i in range(len(lst)-1):
        d = ((lst[i+1][1]-lst[i][1]) * Pinv) % M64
        d = d if d < (1<<63) else d - M64
        if abs(d) < 256: ds.append(d)
        else: ds.append(None)
    if sum(1 for x in ds if x is None) <= 1 and len(ds) >= 2:
        print(f"  {cls}: {ds}")

# 全局: 统计所有小 δ 值的直方图 → 应映射为字符差频度
sm = Counter(d for _,_,_,d in pairs_small)
print("\nδ 直方图:", sorted(sm.items()))
