# -*- coding: utf-8 -*-
# tgcl_probe8.py: 解码 key 值编码 (idx<<8|flag 等)
import struct, collections

path = r"Children of the Light/Levels/Dawn/Objects.level.bin"
d = open(path, "rb").read()
o = struct.unpack_from("<5I", d, 24)
o3, o4 = o[2], o[3]
segC = d[o3:o4]; segD = d[o4:o[4+1]] if False else d[o[3]:o[4]]
segD = d[o[3]:o[4]]
# 重取正确段
o1, o2, o3, o4, o5 = o
segB = d[o2:o3]; segC = d[o3:o4]; segD = d[o4:o5]

starts = []
i = 0
while True:
    e = segC.find(b"\x00", i)
    if e < 0: break
    starts.append(i); i = e + 1
names = {s: segC[s:segC.find(b'\x00', s)].decode() for s in starts}
start_set = starts  # list
start_set = set(starts)
NS = len(starts)

# 收集 segD 中命中起点的 u32 值(排除0)
allu = struct.unpack_from(f"<{len(segD)//4}I", segD, 0)
hits = [u for u in allu if u in start_set and u != 0]
print("nonzero exact hits:", len(hits))
vals = sorted(set(hits))
print("distinct hit values:", len(vals))
print("sample:", vals[:40])

# 假设 u = idx*k + r? 检查 hits/4, hits/8
for k in (1, 2, 4, 8, 16):
    ok = sum(1 for u in hits if u % k == 0 and u//k in start_set)
    print(f" u/{k} also a start: {ok}/{len(hits)}")

# 检查 hits 值域 vs NS=2542：值最大？
print("max hit:", max(hits), "NS:", NS)
# 若编码为 idx<<N | flag，则 u>>N 应 < NS 且 u>>N 大量重复
for N in (7, 8, 9, 10, 12):
    idxs = collections.Counter(u >> N for u in hits)
    inr = sum(1 for idx in idxs if idx < NS)
    print(f" u>>{N}: distinct {len(idxs)}, idx<NS {inr}/{len(idxs)}, top {idxs.most_common(5)}")

# 对照 segB: segB 的 keyOff(field1) 也全部命中起点——那些偏移是真实偏移。
# 也许 segD 命中只是"值恰好落在偏移值域"? 值域 0..36988 全部? 检查 hits 是否也大量命中非起点
# 随机 32 位不可能命中；但若这些 u32 本身是小值(0..~2542*16)，命中起点概率 = 2542/36988≈6.9%
# 反过来：segD 里 u32 < 36988 的比例
small = [u for u in allu if u < 36988]
print(f"\nu32 < 36988: {len(small)}/{len(allu)} ({100*len(small)/len(allu):.2f}%)")
# 若小值 u32 中命中起点比例 ~6.9% 且起点均匀 → 说明只是小值巧合, 不是 key
hs = sum(1 for u in small if u in start_set)
print(f"among small, exact start hit: {hs} ({100*hs/max(1,len(small)):.2f}%)  [random baseline {100*len(starts)/36988:.2f}%]")
# 看小值分布
buckets = collections.Counter(u // 1000 for u in small)
print("small value //1000 top:", buckets.most_common(10))
