# -*- coding: utf-8 -*-
# tgcl_probe1.py: 检查 segB/segC 头部内容与 ref 指向
import struct, sys, collections, re

path = r"Children of the Light/Levels/Dawn/Objects.level.bin"
d = open(path, "rb").read()
magic, ver, c1, c2, c3, c4 = d[:4], *struct.unpack_from("<5I", d, 4)
o = struct.unpack_from("<5I", d, 24)
print("magic", magic, "ver", ver, "counts", c1, c2, c3, c4)
print("offsets", o)
o1, o2, o3, o4, o5 = o
segA = d[o1:o2]; segB = d[o2:o3]; segC = d[o3:o4]; segD = d[o4:o5]
print("sizes A,B,C,D:", len(segA), len(segB), len(segC), len(segD))

def hexdump(buf, n=200, base=0):
    for i in range(0, min(n, len(buf)), 16):
        chunk = buf[i:i+16]
        hx = " ".join(f"{b:02x}" for b in chunk)
        asc = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(f"{base+i:08x}  {hx:<48}  {asc}")

print("\n=== segB head 200 ===")
hexdump(segB, 200, o2)
print("\n=== segC head 200 ===")
hexdump(segC, 200, o3)
print("\n=== segC tail 200 ===")
hexdump(segC[-200:], 200, o3+len(segC)-200)

# segC 中可打印 NUL 串统计
strs = [s for s in segC.split(b"\x00") if s]
readable = [s for s in strs if all(32 <= b < 127 for b in s)]
print(f"\nsegC strings: total {len(strs)}, readable {len(readable)} ({100*len(readable)/max(1,len(strs)):.1f}%)")
print("sample segC strings:", [s.decode() for s in readable[:40]])

# 收集 segD 中的 ref（payload u32 count + count*u32 ref 简化扫描：直接所有 u32 in range）
refs = collections.Counter()
i = o4
bst = re.compile(rb"BstNode_(\d+)\x00")
# 收集所有出现的 u32 值在 [0, len(segC)) 或 [0, len(segB))
allu32 = struct.unpack_from(f"<{len(segD)//4}I", segD, 0)
inC = [u for u in allu32 if u < len(segC)]
inB = [u for u in allu32 if u < len(segB)]
print(f"\nsegD u32 count={len(allu32)}, <segC size: {len(inC)}, <segB size: {len(inB)}")

def read_cstr(buf, u):
    e = buf.find(b"\x00", u)
    if e < 0 or e - u > 200 or e - u == 0: return None
    s = buf[u:e]
    return s if all(32 <= b < 127 for b in s) else None

# 抽样 segD 中的 u32 < len(segC)，作为 segC 偏移读串
samp = inC[::max(1, len(inC)//500)][:500]
hit = sum(1 for u in samp if read_cstr(segC, u))
print(f"sampled {len(samp)} refs(<segC size) as segC offset -> readable str: {hit} ({100*hit/max(1,len(samp)):.1f}%)")
ex = [(u, read_cstr(segC, u)) for u in samp if read_cstr(segC, u)][:15]
for u, s in ex: print(f"  ref={u} (abs {o3+u}) -> {s!r}")

# segB 行字段作为 segC 偏移测试
print("\n=== segB row tests ===")
row0 = struct.unpack_from("<4I", segB, 0)
print("row0 u32s:", [hex(x) for x in row0])
for idx in range(4):
    hits = 0; tot = 0
    for r in range(c2):
        v = struct.unpack_from("<I", segB, r*16 + idx*4)[0]
        if v < len(segC):
            tot += 1
            if read_cstr(segC, v): hits += 1
    print(f" field{idx}: <lenC {tot}/{c2}, readable {hits} ({100*hits/max(1,tot):.1f}%)")

# 对比：segB 字段 + 偏移基准 segC vs 全文件
for idx in range(4):
    hits = 0; tot = 0
    for r in range(200):
        v = struct.unpack_from("<I", segB, r*16 + idx*4)[0]
        if v < o3:
            tot += 1
            if read_cstr(d, v): hits += 1
    print(f" field{idx} as ABS file offset: <o3 {tot}/200, readable {hits}")

# segA 行测试: 12B 行, 3 个 u32? 检查各 u32 作为 segC 偏移
print("\n=== segA row tests (12B rows, n=%d) ===" % (len(segA)//12))
for idx in range(3):
    hits = 0; tot = 0
    for r in range(len(segA)//12):
        v = struct.unpack_from("<I", segA, r*12 + idx*4)[0]
        if v < len(segC):
            tot += 1
            if read_cstr(segC, v): hits += 1
    print(f" field{idx}: <lenC {tot}/{len(segA)//12}, readable {hits} ({100*hits/max(1,tot):.1f}%)")
# 6B 行 (u32,u16) 视角：u32 field
hits = 0; tot = 0
n6 = len(segA)//6
for r in range(n6):
    v = struct.unpack_from("<I", segA, r*6)[0]
    if v < len(segC):
        tot += 1
        if read_cstr(segC, v): hits += 1
print(f" 6B-row u32: <lenC {tot}/{n6}, readable {hits}")
