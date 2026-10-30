# -*- coding: utf-8 -*-
# crack_hash10.py — 定稿分析:
# 事实: 515 个类内差中 103 个 = δ(小整数, 无 P 因子), 42 个 = δ*P, 1 个 = δ*P²
#       δ ∈ [-9,9] 全部合法 ASCII 差; 且同类内不同差值之比 ±P^j 有 27 次
#       → hash 是【多项式滚动 h=h*P+c】, 且相邻名差异发生在末尾若干字符。
#       k=0 (Δ=δ 纯小整数) 意味着末字符不同且**无乘法作用于差** → 
#       poly 模型: Δ = (y*P+c2)-(y*P+c1) = c2-c1 → k=0 ✓
#       k=1: 倒数第二字符不同 (差 (a2-a1)*P) ✓
#       完美自洽! 之前 crack_hash8 的爆破失败是因为 basis/编码不对,
#       或名字不在 reg_all。现在直接用模型从 h 逆向恢复名字。
# poly: h_L = h_{L-1}*P + c_L。逆向: h_{L-1} = (h_L - c_L)/P。
# mod 2^64 无整除约束 → 需剪枝: 前缀值 h_{L-1} 必须能继续分解, 且整体字符可打印。
# 高效方法: 从末字符递推, 用"前缀 hash 高位边界"剪枝:
#   深度还剩 d 时, 前缀值 = Σ_{i<=d} c_i P^{d-i} ≤ 127*(P^d-1)/(P-1) < P^{d+1}/(P-1)*127
#   用 log2 界: 前缀值 < 2^{8d+7.1}。即 prev >> (8*d) 应为 0 或极小。
import re, sys
from collections import defaultdict

M64 = 1 << 64
P = 0x100000001B3
Pinv = pow(P, -1, M64)

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
targets = {h: cls for ln, h, cls in recs}

def recover(h, Lmin=2, Lmax=30, cmin=32, cmax=126, limit=50):
    """poly h=h*P+c, basis=0, 全 ASCII 可打印。返回 [(L, bytes)]"""
    sols = []
    def dfs(val, depth, acc):
        if len(sols) >= limit: return
        if depth == 0:
            if val == 0:
                s = bytes(reversed(acc))
                if all(cmin <= b <= cmax for b in s):
                    sols.append((len(s), s))
            return
        # 剪枝: 前缀值上界 ~ cmax * P^{depth-1} * P/(P-1) → 用 log2
        # prev = (val - c)*Pinv 需 < cmax*P^{depth-1}*P/(P-1) ≈ 2^{log2(cmax)+(depth)*log2(P)}
        # 粗剪枝: prev >> (log2P*(depth-1) + 7.1) == 0
        if depth > 1:
            shift = round(6.017 * (depth - 1)) + 7
        else:
            shift = 0
        for c in range(cmin, cmax+1):
            prev = ((val - c) * Pinv) % M64
            if depth > 1 and (prev >> shift) != 0:
                continue
            acc.append(c)
            dfs(prev, depth-1, acc)
            acc.pop()
    for L in range(Lmin, Lmax+1):
        dfs(h, L, [])
        if sols and L >= max(s[0] for s in sols):
            # 名字长度确定后再深一层确认无更长解 (简单起见: 找到即停, 因唯一 L)
            if sols: 
                # 继续检查 L+1 一层太贵; 由模型唯一长度, 直接停
                break
    return sols

print("[逆向恢复] 对全部 504 个唯一值尝试恢复 (L<=30):")
out = []
sys.setrecursionlimit(50000)
import time
t0 = time.time()
for idx, (h, cls) in enumerate(sorted(targets.items())):
    sols = recover(h)
    if sols:
        # 可能多解, 全列出
        strs = sorted(set(s.decode() for _, s in sols))
        out.append((hex(h), cls, strs))
        if idx < 20 or len(out) <= 5:
            print(f"  {hex(h)} [{cls}]: {strs[:6]}")
    else:
        out.append((hex(h), cls, None))
print(f"\n恢复成功 {sum(1 for _,_,s in out if s)}/{len(out)}  耗时 {time.time()-t0:.1f}s")

# 与 reg_all 名字交叉验证
names = set()
with open(r'd:\新建文件夹\LightEncounters\reg_all.txt', 'r', encoding='utf-8', errors='replace') as f:
    for line in f:
        m = re.search(r"name='([^']+)'", line)
        if m: names.add(m.group(1))
rec_ok = 0
for h, cls, strs in out:
    if strs and any(s in names for s in strs):
        rec_ok += 1
print(f"恢复结果中命中 reg_all 明文名的: {rec_ok}")
print("\n前 40 个恢复结果:")
for h, cls, strs in out:
    if strs:
        print(f"  {h} [{cls}]: {strs[:4]}")
