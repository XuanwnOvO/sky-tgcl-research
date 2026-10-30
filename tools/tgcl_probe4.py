# -*- coding: utf-8 -*-
# tgcl_probe4.py: 精确观察 segD 节点结构
import struct, re, collections

path = r"Children of the Light/Levels/Dawn/Objects.level.bin"
d = open(path, "rb").read()
o = struct.unpack_from("<5I", d, 24)
o1, o2, o3, o4, o5 = o
segC = d[o3:o4]; segD = d[o4:o5]
strs = [s for s in segC.split(b"\x00") if s]
starts = {}
i = 0
while i < len(segC):
    e = segC.find(b"\x00", i)
    if e < 0: break
    starts[i] = segC[i:e].decode()
    i = e + 1

name_re = re.compile(rb"BstNode_(\d+)\x00")
nodes = [(m.start(), m.end(), int(m.group(1))) for m in name_re.finditer(segD)]
print("nodes:", len(nodes))

def hexdump(buf, base, n=96):
    for j in range(0, min(n, len(buf)), 16):
        c = buf[j:j+16]
        hx = " ".join(f"{b:02x}" for b in c)
        asc = "".join(chr(b) if 32 <= b < 127 else "." for b in c)
        print(f"  {base+j:08x}  {hx:<48}  {asc}")

# 打印前 6 个节点的完整区域（到下一个节点名）
for k in range(6):
    st, en, nid = nodes[k]
    nxt = nodes[k+1][0] if k+1 < len(nodes) else len(segD)
    print(f"\nNode {nid} @ {st} (payload len {nxt-en})")
    hexdump(segD[en:nxt], en, 120)

# 统计每个节点 payload 开头 u32（候选 count/字段）分布
first_u32 = collections.Counter()
for k in range(len(nodes)):
    en = nodes[k][1]
    if en+4 <= len(segD):
        first_u32[struct.unpack_from("<I", segD, en)[0]] += 1
print("\nfirst-u32-after-name top20:", first_u32.most_common(20))

# 也许每个节点固定结构：u32 A, u32 count, refs...？测试: 在 payload 中找 u32==starts 索引
# 构建 segC 字符串索引映射
idx_by_start = {s: n for n, (s, _) in enumerate(sorted(starts.items()))}
# 观察节点内是否有 u32 < 2542（字符串索引）
small = collections.Counter()
tot = 0
for st, en, nid in nodes[:2000]:
    nxt = nodes[[x[0] for x in nodes].index(st)+1][0] if nodes.index((st,en,nid)) < len(nodes)-1 else len(segD)
for k in range(2000):
    en = nodes[k][1]
    nxt = nodes[k+1][0] if k+1 < len(nodes) else len(segD)
    pay = segD[en:nxt]
    n_u = len(pay)//4
    for j in range(n_u):
        v = struct.unpack_from("<I", pay, j*4)[0]
        tot += 1
        if v < 2542: small[v % 256] += 1
print(f"\nsegD payload u32 total {tot}, <2542: {sum(small.values())} ({100*sum(small.values())/max(1,tot):.2f}%)")
