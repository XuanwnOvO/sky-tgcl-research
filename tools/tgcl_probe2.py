# -*- coding: utf-8 -*-
# tgcl_probe2.py: 精确对齐测试
import struct, re, collections

path = r"Children of the Light/Levels/Dawn/Objects.level.bin"
d = open(path, "rb").read()
c1, c2, c3, c4 = struct.unpack_from("<4I", d, 8)
o = struct.unpack_from("<5I", d, 24)
o1, o2, o3, o4, o5 = o
segA = d[o1:o2]; segB = d[o2:o3]; segC = d[o3:o4]; segD = d[o4:o5]

# 解析 segC 字符串表
starts = set(); table = []  # (start, name)
i = 0
while i < len(segC):
    e = segC.find(b"\x00", i)
    if e < 0: break
    table.append((i, segC[i:e].decode()))
    starts.add(i)
    i = e + 1
print("segC strings:", len(table))

def back_str(u):
    """ref 可能指向串内部：回退到上一个 NUL 后取串"""
    if u >= len(segC): return None
    s = segC.rfind(b"\x00", 0, u) + 1
    e = segC.find(b"\x00", u)
    if e < 0 or e - s > 200: return None
    t = segC[s:e]
    return t.decode() if t and all(32 <= b < 127 for b in t) else None

# --- segB: 哪个字段精确指向字符串起点 ---
print("\n=== segB fields: exact string-start match (offset base = segC) ===")
for idx in range(4):
    exact = 0; inside = 0; tot = 0
    for r in range(c2):
        v = struct.unpack_from("<I", segB, r*16 + idx*4)[0]
        tot += 1
        if v in starts: exact += 1
        elif back_str(v): inside += 1
    print(f" field{idx}: exact {exact}/{tot}, inside-only {inside}")
# 完整行视图：打印前 12 行 (field0,field1->name,field2,field3)
print("sample rows:")
for r in range(12):
    f = struct.unpack_from("<4I", segB, r*16)
    n = back_str(f[1])
    n2 = back_str(f[0])
    print(f"  row{r}: {f[0]:6d}({n2}) {f[1]:6d}({n}) type={f[2]} f3={f[3]}")

# 也测试 offset base = o2 (segB 起点，相对整个文件)? segB 内数值域 [0,lenC)
# 试试 base = o3 - 44 (即相对 o1)? 不重要，segC 已 100% exact 即可。

# --- segA ---
print("\n=== segA 12B rows ===")
for idx in range(3):
    exact = sum(1 for r in range(c1)
                if struct.unpack_from("<I", segA, r*12+idx*4)[0] in starts)
    print(f" field{idx}: exact string-start {exact}/{c1}")
for r in range(10):
    f = struct.unpack_from("<3I", segA, r*12)
    print(f"  row{r}: {f[0]:6d}({back_str(f[0])}) {f[1]:6d}({back_str(f[1])}) {f[2]:6d}({back_str(f[2])})")

# --- segD refs ---
print("\n=== segD ref semantics ===")
# 收集 payload 模式 u32 count + count*u32 ref
refs = []
i = 0
name_re = re.compile(rb"BstNode_(\d+)\x00")
while True:
    m = name_re.search(segD, i)
    if not m: break
    p = m.end()
    # payload 后有 u32 seq；常见 payload = u32 count + refs。尝试多种跳法：
    # 直接把名字后 4 字节当 count
    if p + 4 <= len(segD):
        cnt = struct.unpack_from("<I", segD, p)[0]
        if 0 < cnt < 64 and p + 4 + 4*cnt + 4 <= len(segD):
            refs += list(struct.unpack_from(f"<{cnt}I", segD, p+4))
            i = p + 4 + 4*cnt
            continue
    i = m.end()
print("collected refs:", len(refs))
inC = [u for u in refs if u < len(segC)]
exact = sum(1 for u in inC if u in starts)
inside = sum(1 for u in inC if u not in starts and back_str(u))
print(f"refs <lenC: {len(inC)}/{len(refs)}; exact start {exact} ({100*exact/max(1,len(inC)):.1f}%), inside {inside}")
samp = inC[::max(1,len(inC)//20)][:20]
for u in samp: print(f"  {u:6d} -> {back_str(u)!r}")

# ref 分布是否均匀 mod4（若为偏移应几乎全 mod4==0）
mod4 = collections.Counter(u % 4 for u in inC)
print("mod4 dist of refs<lenC:", dict(mod4))
mod4b = collections.Counter(u % 4 for u in [struct.unpack_from('<I', segB, r*16+4)[0] for r in range(c2)])
print("mod4 dist of segB field1:", dict(mod4b))
