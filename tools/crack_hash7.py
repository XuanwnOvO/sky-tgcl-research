# -*- coding: utf-8 -*-
# crack_hash7.py — 验证 h = Σ c_i * P^(L-i) mod 2^64 (Rabin-Karp 无模滚动)
#                  并爆破恢复原始字段名
from collections import defaultdict
import re, itertools

M64 = 1 << 64
P = 0x100000001B3

def rk(s, basis=0):
    h = basis
    for c in s:
        h = (h * P + c) % M64
    return h

def rk_l2r(s, basis=0):
    """另一种方向: h = Σ c_i P^{i-1} (先出现的字符乘低次幂)"""
    h = basis
    pw = 1
    for c in s:
        h = (h + c * pw) % M64
        pw = (pw * P) % M64
    return h

# ---------- 载入 ----------
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
print(f"[load] {len(targets)} 个唯一脱敏值")

# ---------- 验证模型: 用 reg_all.txt 明文名 ----------
names = set()
with open(r'd:\新建文件夹\LightEncounters\reg_all.txt', 'r', encoding='utf-8', errors='replace') as f:
    for line in f:
        m = re.search(r"name='([^']+)'", line)
        if m: names.add(m.group(1))
print(f"[load] {len(names)} 个明文名")

hits = []
for nm in names:
    s = nm.encode()
    for tag, fn in (('l2r', rk), ('r2l', rk_l2r)):
        for b in (0, 0xCBF29CE484222325):
            h = fn(s, b)
            if h in targets:
                hits.append((hex(h), targets[h], nm, tag, hex(b)))
print(f"\n[验证] 纯 Rabin-Karp P=0x100000001B3 直接命中: {len(hits)}")
for x in hits[:40]: print("  HIT:", x)

# 若直接不命中，尝试小变体: 首字符basis=ord(c0), 或字符集为可见ASCII+小写化
if not hits:
    print("\n[变体] lower / 去下划线 / basis=ord(first):")
    h2s = []
    for nm in names:
        for v in (nm.lower(), nm.replace('_', ''), nm.lower().replace(' ', '')):
            s = v.encode()
            h = rk(s, 0)
            if h in targets: h2s.append((hex(h), targets[h], v))
            h = rk(s, 0xCBF29CE484222325)
            if h in targets: h2s.append((hex(h), targets[h], v))
    print(f"  命中 {len(h2s)}")
    for x in h2s[:20]: print("  HIT:", x)

# ---------- 逆向: 模型若真, 可从 h 直接解名字 ----------
# h = Σ c_i P^{L-i} mod 2^64。未知 L。对每个 h, 从 L=2..16 枚举末字符 DFS。
# 由于 mod 2^64 截断, 每个 c 候选需满足 (h - c) ≡ prev*P → prev=(h-c)/P 整除性?
# mod 2^64 下 P 奇 → 总可除, 无法剪枝。但字符范围 32..126 限制, 
# L 固定时解空间 95^L —— 需更好的剪枝: 高位匹配。
# 改进: h = c1*P^{L-1} + ...。P^{L-1} 的最高位决定 c1 贡献的高位。逐字符从首位解:
# 对固定 L, c1 ≈ h / P^{L-1} (mod 2^64 近似不成立)。
# 替代: 前缀搜索。由 δ 分析知道相邻名共享前缀。用已知明文名做前缀树 + 
#   分支限界: 逐字符扩展 prefix, 计算剩余长度可能范围。
# 简化: 先解决"小 δ 相邻对"已给出相同 L 与共享前缀 —— 
#   对每个连通分量, h_i = base + Σ (字符差) P^k, 字符差 ∈ [-95,95]。
print("\n[逆向] 基于滚动模型的受约束恢复(演示单个类):")
def solve_last(h, L):
    """给定 L, 枚举所有满足 h=Σ c_i P^{L-i} 的字符串 (DFS, 逐位定末字符)"""
    sols = []
    cset = range(32, 127)
    # 从末字符往前: (h - c_L) = prev * P → prev = (h-c_L)*Pinv
    Pinv = pow(P, -1, M64)
    def dfs(val, depth, acc):
        if depth == 0:
            if val == 0:
                sols.append(bytes(reversed(acc)))
            return
        for c in cset:
            prev = ((val - c) * Pinv) % M64
            # 剪枝: prev 的高位应小于 127*P^{depth-1}+...
            acc.append(c)
            dfs(prev, depth-1, acc)
            acc.pop()
    dfs(h, L, [])
    return sols

# 先小规模验证求解器: 求一个已知 h 的所有 (L<=3) 解, 看是否恰好唯一且合理
demo = sorted(targets)[0]
for L in (2, 3):
    sols = solve_last(demo, L)
    printable = [s for s in sols if all(32 <= b < 127 for b in s)]
    print(f"  h={demo:#018x} L={L}: {len(sols)} 个解, 可打印 {len(printable)}: "
          f"{[s.decode() for s in printable[:5]]}")

# 对小 δ 相邻对验证: 差 = (c2-c1)*P^0? 已证 Δ=δ*P 精确 →
# 若 h = Σ c P^(L-i), 则相邻只差末字符: Δ = c2-c1 (不乘P!) 
# 而我们观测 Δ = δ*P → 说明变化发生在倒数第二字符位置之前 → L>=2 且前缀至少保留1字符乘P。
# 即: h2 - h1 = (y*P + c2) - (y*P + c1)? 不, 前缀hash相同 y, h = y*P + c:
#   Δ = c2 - c1。可我们观测 Δ = δ*P。矛盾! → 模型应为 h = y + c*P? 
#   即 h = Σ c_i P^{i-1} (r2l)。那么 Δ(末字符) = (c2-c1)*P^{L-1}。
#   观测 Δ = δ*P → L-1 = 1?? 或 δ = (c2-c1)*P^{L-2}。若 L-2=0 → L=2。
#   但 δ 最大 9 → 只有当 P^{L-2} 整除差且商小。多数类内差 'big' → L 不同或前缀不同。
# 结论方向: h = r2l 滚动 h = h + c*P^i, 且相邻同长度名 → Δ=(c2-c1)*P^{L-1}
#   检验: Δ / P^{L-1} 是否小整数 (对未知 L, 试 L=1..16)
print("\n[方向检验] Δ = (c2-c1)*P^(L-1):")
byclass = defaultdict(list)
for ln, h, cls in recs: byclass[cls].append((ln, h))
for c in byclass: byclass[c].sort()
cands = defaultdict(int)
for cls, lst in byclass.items():
    for i in range(len(lst)-1):
        D = lst[i+1][1] - lst[i][1]
        for L in range(1, 20):
            pk = pow(P, L-1, M64)
            try:
                inv = pow(pk, -1, M64)
            except ValueError:
                continue
            d = (D * inv) % M64
            if d < 128 or d >= M64 - 128:
                cands[L] += 1
print("  各 L 命中数:", dict(sorted(cands.items())))
