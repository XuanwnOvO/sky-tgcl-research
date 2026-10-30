# -*- coding: utf-8 -*-
# crack_hash8.py — 基于 δ*P 结构 + ASCII δ 全部合法的事实
# 核心已证: 相邻名 hash 差 = δ*P, δ∈[-9,9] 全部为合法 ASCII 字符差
# 结论候选: hash = poly h=h*P+c, 且相邻对共享全部前缀(除末字符)
#           Δ = (y*P + c2) - (y*P + c1) = 0?? 不对。
# 正确推导: h_L = h_{L-1}*P + c_L。若两名字前缀完全相同 y_L:
#   Δ = c2 - c1 (不含 P)。但观测 Δ = δ*P。
# 若共享前缀为 y_{L-1} (倒数第二字符也相同, 只有末字符不同):
#   Δ = (y_{L-1}*P + c2) - (y_{L-1}*P + c1) = c2-c1。仍无 P!
# 出现 *P 的唯一方式: 前缀 hash 不同, 且 y2 - y1 = δ。
#   即 Δ = (y2 - y1)*P + (c2-c1) = δ*P → c2 = c1 且 y2-y1 = δ!
#   → 相邻字段名【末字符相同】, 差异在更前面!
# 与"字符串相似性"观测吻合: isEnabled1/isEnabled2 → 末字符是 '1'/'2'? 不, 那样末字符不同。
# 但观测 c2=c1 强制末字符相同。结合 δ 小: 差异也在最后几字符。
#   例: "xx_1a" vs "xx_2a"? 少见。更可能: 差异在倒数第二字符:
#   Δ = ((y'*P + a2)*P + c) - ((y'*P + a1)*P + c) = (a2-a1)*P → δ = a2-a1 ✓✓✓
# 即: 倒数第二字符不同, 末字符相同!  如 "on_1"/"on_2"? 末字符不同...
#   如 "itemA1" vs "itemB1"? 倒数第二字符 A/B 差 ±1? A→B 差1, δ=1,2,3 都有 → 合理!
#   如 "btn_l"/"btn_r" 差 6 ✓ (l=108,r=114)
# 由此模型完全确定: h = h*P + c (poly, Rabin-Karp), mod 2^64, 无 basis(或试两种)
# 直接爆破验证: 用 reg_all 名字 + 类名组合:
import re
from collections import defaultdict

M64 = 1 << 64
P = 0x100000001B3

def poly(s, basis=0):
    h = basis
    for c in s:
        h = (h * P + c) % M64
    return h

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

names = set()
with open(r'd:\新建文件夹\LightEncounters\reg_all.txt', 'r', encoding='utf-8', errors='replace') as f:
    for line in f:
        m = re.search(r"name='([^']+)'", line)
        if m: names.add(m.group(1))
print(f"[load] {len(targets)} 个目标, {len(names)} 个明文名")

# 大规模变体: 名字编码(UTF8/UTF16/加\0)、类名前后缀、大小写、basis 两种、加下划线/点
seen = set()
hit = []
inputs = []
for cls in set(targets.values()) | {''}:
    for nm in names:
        raws = [nm, nm.lower(), nm.upper()]
        if cls and cls != '?':
            raws += [f"{cls}.{nm}", f"{cls}_{nm}", f"{cls}{nm}", f"{nm}.{cls}", f"{nm}_{cls}",
                     f"{cls}.{nm.lower()}", f"{cls}_{nm.lower()}"]
        for r in raws:
            for enc, b in (('u8', r.encode()), ('u16', r.encode('utf-16-le')),
                           ('u8z', r.encode()+b'\x00'), ('u16z', r.encode('utf-16-le')+b'\x00\x00')):
                if b not in seen:
                    seen.add(b)
                    inputs.append((r, enc, b))
print(f"变体输入 {len(inputs)} 个, x2 basis")
for r, enc, b in inputs:
    for basis in (0, 0xCBF29CE484222325):
        h = poly(b, basis)
        if h in targets:
            hit.append((hex(h), targets[h], r, enc, hex(basis)))
print(f"poly P=FNV素数 命中 {len(hit)}")
for x in hit[:30]: print("  HIT:", x)

# 反向确认: 拿 poly 模型对每个 target 做"末字符枚举+前缀可打印性"恢复
# h_L = y*P + c → y = (h - c)/P, c∈ASCII. y 应继续可分解。
# 由于 mod 2^64, 从头解: 用高位约束。改为从 δ 对获取前缀 hash 再展开。
# 生成所有 target 的 (h mod P)? poly 模型无此性质。
# 实用恢复: 对每个 h, DFS L=4..20, 每层枚举 c∈[32,127], prev=(h-c)*Pinv,
#   剪枝: prev 的高 32 位 < 127 * P^{L-1-1} 的高位 + 少量。要求解唯一性。
def recover(h, Lmax=24, cmin=32, cmax=127):
    Pinv = pow(P, -1, M64)
    sols = []
    # (删除错误的上界预计算)
    def dfs(val, depth, acc):
        if depth == 0:
            if val == 0: sols.append(bytes(reversed(acc)))
            return
        # 剪枝: val - c 必须在合法前缀范围内: |val| 超界则 c 使 prev 过大
        for c in range(cmin, cmax+1):
            prev = ((val - c) * Pinv) % M64
            # prev 应 < 127*P^{depth-1} + slack → 用近似: prev >> (8*(depth-1)) 小
            acc.append(c)
            if depth > 1 and (prev >> (10*(depth-1))) > 300:
                acc.pop(); continue
            dfs(prev, depth-1, acc)
            acc.pop()
    for L in range(2, Lmax+1):
        dfs(h, L, [])
        if sols: break
    return sols

print("\n[恢复演示] 对 3 个 target 尝试唯一解恢复(深度<=6):")
import sys
sys.setrecursionlimit(10000)
for t in sorted(targets)[:3]:
    sols = recover(t, Lmax=6)
    pr = [s.decode('ascii', 'replace') for s in sols if all(32 <= b < 127 for b in s)]
    print(f"  {t:#018x} ({targets[t]}): {len(sols)} 解, 可打印: {pr[:6]}")
