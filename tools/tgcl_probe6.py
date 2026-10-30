# -*- coding: utf-8 -*-
# tgcl_probe6.py: segD 属性结构验证
import struct, collections

path = r"Children of the Light/Levels/Dawn/Objects.level.bin"
d = open(path, "rb").read()
o = struct.unpack_from("<5I", d, 24)
o3, o4, o5 = o[2], o[3], o[4]
segC = d[o3:o4]; segD = d[o4:o5]

names = {}
i = 0
while True:
    e = segC.find(b"\x00", i)
    if e < 0: break
    names[i] = segC[i:e].decode(); i = e + 1

allu = struct.unpack_from(f"<{len(segD)//4}I", segD, 0)
# segD 里有没有 BstNode_ 名？统计
b = segD.count(b"BstNode_")
print("BstNode_ occurrences in segD:", b)

# u32==起点 的位置分布：是否聚集（属性块）？
pos = [j for j, u in enumerate(allu) if u in names]
gaps = collections.Counter(pos[k+1]-pos[k] for k in range(len(pos)-1))
print("gap between key-u32 positions, top10:", gaps.most_common(10))

# 看一个连续片段：找 pos 中连续 gap==1 的最长区段
best = (0, 0); cur = 1; s0 = pos[0]
for k in range(1, len(pos)):
    if pos[k] == pos[k-1] + 1: cur += 1
    else:
        if cur > best[1]: best = (pos[k-cur], cur)
        cur = 1
if cur > best[1]: best = (pos[len(pos)-cur], cur)
st, ln = best
print(f"longest consecutive run: {ln} u32s starting at byte {st*4}")
for j in range(st, min(st+ln, st+40)):
    print(f"  [{j*4}] {allu[j]:10d} -> {names.get(allu[j], '(val)')}")

# 后续 u32 是否为值/继续串？打印该区段前 60 个 u32
print("\ncontext:")
for j in range(max(0, st-4), min(st+ln+10, len(allu))):
    v = allu[j]
    tag = names.get(v)
    if tag is None:
        f = struct.unpack_from("<f", segD, j*4)[0]
        tag = f"num {v} / float {f:.4g}" if abs(f) < 1e6 and abs(f) > 1e-4 or f == 0 else f"num {v}"
    print(f"  [{j*4}] {v:10d}  {tag}")
