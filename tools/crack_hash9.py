# -*- coding: utf-8 -*-
# crack_hash9.py — 用大 δ 差值对直接检验"poly/多重乘"深层结构
# 已证事实链:
#   1) 56 个类内相邻差 Δ 精确 = δ*P (P=0x100000001B3), δ∈[-9,9]
#   2) 全部 δ 都是合法 ASCII 差
#   3) Δ/δ = P 精确 → 不是 FNV(异或后乘), 是【先乘后加/异或?
#      注意: FNV-1a 中 h=(prev^c)*P。若 c 改变: Δ=((prev^c2)-(prev^c1))*P。
#      prev^c2 - prev^c1 一般是大数, 但当 prev 低位为 0 且 c 小时 = c2-c1!
#      prev 低 8 位全 0 的概率 1/256 — 不可能 56 对都是。
#   4) 但 FNV-1 (先乘后异或): h = prev*P ^ c → Δ = (y2*P^c2)-(y1*P^c1) 无代数性。
# 本脚本: 对【所有】类内差值 (不只小的), 检验 Δ*P^{-k} 对 k=1..16 的 "δ*P^k"
#   结构 (差异在第 L-k 字符处)。统计各 k 命中数 → 定位字符串差异位置分布。
import re
from collections import defaultdict, Counter

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

byclass = defaultdict(list)
for ln, h, cls in recs: byclass[cls].append((ln, h))
for c in byclass: byclass[c].sort()

kcount = Counter()
delta_hist = Counter()
total = 0
examples = defaultdict(list)
for cls, lst in byclass.items():
    for i in range(len(lst)-1):
        D = lst[i+1][1] - lst[i][1]
        total += 1
        d = D
        for k in range(0, 17):
            # d 应 = δ * P^k, |δ|<=127
            dd = d
            if dd < (1 << 63):
                if dd < 128:
                    kcount[k] += 1
                    delta_hist[dd] += 1
                    if k >= 1 and len(examples[k]) < 3:
                        examples[k].append((cls, hex(lst[i][1]), hex(lst[i+1][1]), dd, k))
                    break
            else:
                if dd >= M64 - 128:
                    kcount[k] += 1
                    delta_hist[dd - M64] += 1
                    if k >= 1 and len(examples[k]) < 3:
                        examples[k].append((cls, hex(lst[i][1]), hex(lst[i+1][1]), dd - M64, k))
                    break
            d = (d * Pinv) % M64
print(f"总类内差 {total}")
print("Δ = δ*P^k 的 k 分布:", dict(sorted(kcount.items())))
print("δ 直方图:", sorted(delta_hist.items()))
for k in sorted(examples):
    print(f"k={k} 示例:")
    for e in examples[k]: print("   ", e)

# 差值比检验: Δ2/Δ1 = P^j 对同类不同对之间
print("\n同类内差值互为 P 的幂次关系检验:")
relcnt = Counter()
for cls, lst in byclass.items():
    Ds = [lst[i+1][1] - lst[i][1] for i in range(len(lst)-1)]
    for a in range(len(Ds)):
        for b in range(len(Ds)):
            if a == b: continue
            r = (Ds[b] * pow(Ds[a] % M64, -1, M64)) % M64 if Ds[a] % 2 else 0
            if r:
                # r 是否 = P^j 小 j?
                v = r
                for j in range(1, 17):
                    v = (v * Pinv) % M64
                    if v < 128:
                        relcnt[j] += 1
                        break
                    if v > M64 - 128:
                        relcnt[-j] += 1
                        break
print("比值 = ±P^j 分布:", dict(sorted(relcnt.items(), key=lambda x: -abs(x[0]))))
