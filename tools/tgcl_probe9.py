# -*- coding: utf-8 -*-
# tgcl_probe9.py: segA field1/field2 是否为 segB 行索引/区间
import struct, collections

path = r"Children of the Light/Levels/Dawn/Objects.level.bin"
d = open(path, "rb").read()
o = struct.unpack_from("<5I", d, 24)
o1, o2, o3, o4, o5 = o
segA = d[o1:o2]; segB = d[o2:o3]; segC = d[o3:o4]
c2 = len(segB)//16

starts = []
i = 0
while True:
    e = segC.find(b"\x00", i)
    if e < 0: break
    starts.append(i); i = e + 1
names = {s: segC[s:segC.find(b'\x00', s)].decode() for s in starts}

rows = []
for r in range(len(segA)//12):
    a, b_, c = struct.unpack_from("<3I", segA, r*12)
    rows.append((a, b_, c, names.get(a, "?")))

# field1/field2 值域
f1 = [r[1] for r in rows]; f2 = [r[2] for r in rows]
print("field1 range:", min(f1), max(f1), " distinct:", len(set(f1)))
print("field2 range:", min(f2), max(f2), " distinct:", len(set(f2)))
# field2 是否递增（区间端点）?
inc2 = all(f2[k] <= f2[k+1] for k in range(len(f2)-1))
print("field2 nondecreasing:", inc2)
# field2 - field1 关系
print("f2-f1 top:", collections.Counter(f2[k]-f1[k] for k in range(len(rows))).most_common(5))
# 若 field2 是 segB 行索引：field2 < c2 且递增 → 每个组件占 schema 连续区间
print("field2 < c2:", sum(1 for v in f2 if v < c2), "/", len(f2))
# 按 field2 排序打印样例（组件 -> schema 区间）
for k in range(0, len(rows), 20):
    a, b_, c, nm = rows[k]
    print(f"  comp[{k}] {nm}: f1={b_} f2={c}")
# 对一个组件，读 segB[f1..f2] 行看键名是否合理
a, b_, c, nm = rows[2]  # LevelMesh
print(f"\n{nm} schema rows f1..f2 = {b_}..{c}:")
for r in range(b_, min(c, b_+15)):
    fa, fb, ft, fe = struct.unpack_from("<4I", segB, r*16)
    print(f"   key={names.get(fb,'?')} off={fa} type={ft} f3={fe}")
