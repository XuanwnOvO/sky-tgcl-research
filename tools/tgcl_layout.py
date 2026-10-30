# -*- coding: utf-8 -*-
# 五段布局总检：o1..o2 和 o2..o3 段到底是什么
import os, struct
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"
lv = 'Dawn'
d = open(os.path.join(root, lv, 'Objects.level.bin'), 'rb').read()
ver, c1, c2, c3, c4 = struct.unpack_from('<5I', d, 4)
o1, o2, o3, o4, o5 = struct.unpack_from('<5I', d, 24)
print(f"file={len(d)} ver={ver} counts={c1},{c2},{c3},{c4}")
print(f"o1={o1} o2={o2} o3={o3} o4={o4} o5={o5}")
print(f"segA(o1..o2)={o2-o1}B segB(o2..o3)={o3-o2}B segC(o3..o4)={o4-o3}B segD(o4..o5)={o5-o4}B segE(o5..end)={len(d)-o5}B")

# segA 前几行
print("\nsegA 头 64B:", d[o1:o1+64].hex())
print("segA as u32:", [hex(x) for x in struct.unpack_from('<8I', d, o1)])

# segB 12B 记录假设：count?
print("\nsegB 头 48B:", d[o2:o2+48].hex())
n12 = (o3-o2)/12
print(f"segB/12 = {n12}, /16 = {(o3-o2)/16}, /4 = {(o3-o2)/4}, counts c2={c2} c3={c3}")

# 若 segB 行 = (u32 a, u32 b, u32 c)，打印前 10 行
for i in range(8):
    a, b, c = struct.unpack_from('<3I', d, o2 + i*12)
    print(f"  row{i}: a={a:#x} b={b:#x} c={c:#x}")

# segB 内的 4B 值会不会是"行内偏移"：u=39 → row 3.25 不对齐；u=2042/4=510.5 也不对齐
# 也许 segB 是 (key u16, type u16, val u32)? 打印 bytes 视图
print("\nsegB row bytes 视图(前5行):")
for i in range(5):
    raw = d[o2+i*12: o2+i*12+12]
    print(f"  {raw.hex()}")
