# -*- coding: utf-8 -*-
# tgcl_probe5.py: 复合值假设 + ref->segB 行映射
import struct, re, collections

path = r"Children of the Light/Levels/Dawn/Objects.level.bin"
d = open(path, "rb").read()
o = struct.unpack_from("<5I", d, 24)
o1, o2, o3, o4, o5 = o
segB = d[o2:o3]; segC = d[o3:o4]; segD = d[o4:o5]

starts = []
i = 0
while True:
    e = segC.find(b"\x00", i)
    if e < 0: break
    starts.append(i); i = e + 1
NS = len(starts)

# 收集 refs 同 probe2/3
name_re = re.compile(rb"BstNode_(\d+)\x00")
refs = []; i = 0
while True:
    m = name_re.search(segD, i)
    if not m: break
    p = m.end()
    cnt = struct.unpack_from("<I", segD, p)[0]
    if 0 < cnt < 64 and p+4+4*cnt+4 <= len(segD):
        refs += list(struct.unpack_from(f"<{cnt}I", segD, p+4))
        i = p+4+4*cnt
        continue
    i = m.end()
print("refs:", len(refs), "unique:", len(set(refs)))

# 假设1: ref = idx*4 (索引*4)? 即 ref//4 < NS
q = [u for u in refs if u % 4 == 0 and u//4 < NS]
print(f"ref%4==0 且 ref//4<{NS}: {len(q)}/{len(refs)}")
# 假设2: ref = idx*8?
q8 = [u for u in refs if u % 8 == 0 and u//8 < NS]
print(f"ref%8==0 且 ref//8<{NS}: {len(q8)}/{len(refs)}")

# segB field1 精确命中全部串起点 → segB keyOff 是相对 segC 的偏移(实锤)
# segD ref 若也相对 segC 但指向任意类型数据（数字/浮点），无法用可读性验证。
# 改为验证：segD ref 是否为 segB 行索引? c2=3239 行,行号*16 < 51824 → ref<51824 全域可能!
inB = [u for u in refs if u < 51824 and u % 16 == 0]
print(f"ref%16==0 且 <lenB: {len(inB)}/{len(refs)} ({100*len(inB)/max(1,len(refs)):.1f}%)")
# 精确行命中：ref/16 < c2 且 ref%16==0 → 与 c2 行对应
rows = set(u//16 for u in inB)
print(f"distinct row candidates: {len(rows)}/{len(segB)//16}")
# 检查这些行是否恰为 schema 表中该 type 相关行? 打印样例行内容
for u in inB[:10]:
    r = u//16
    f = struct.unpack_from("<4I", segB, r*16)
    name = segC[f[1]:segC.find(b'\x00', f[1])].decode()
    print(f"  ref={u} row={r}: off={f[0]} key={name} type={f[2]} f3={f[3]}")

# 假设3: segD payload 中名字后面的 count 实际是字段,ref 序列假设错误。
# 直接统计: segD 中 u32 值 == 某 segC 起点的频率
sc = set(starts)
allu = struct.unpack_from(f"<{len(segD)//4}I", segD, 0)
hit = sum(1 for u in allu if u in sc)
print(f"\nsegD all-u32 in segC-starts: {hit}/{len(allu)} ({100*hit/len(allu):.2f}%)")
# 按对齐到 payload 起点测试？先做 4 字节滑动 vs 均匀基线 2542/2^32
