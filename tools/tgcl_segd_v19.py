# -*- coding: utf-8 -*-
"""segD v19: 意外发现: 0x2ced=11469 处有个 BstNode_2310602845?? 那不是 rec0.
   看: V0 payload '00 ed 2c 00 00' = 0x2ced=11469 -> SEG_D+11469 = ? 0x16758+? 不对:
   SEG_D=0x16754. SEG_D+11469 = 0x19541. 检查那里是什么.
   另外发现 rec0 payload 首 1B=00 + u32 偏移(未对齐!) —— payload 可能不是 4 对齐流!
   payload 首字节可能是 1B 标志, 后接未对齐 u32 偏移.
   检查: SEG_D+0x2ced 处内容."""
import re, struct, bisect
from collections import Counter

P = r"Children of the Light\Levels\Dawn\Objects.level.bin"
data = open(P, "rb").read()
o1, o2, o3, o4, o5 = struct.unpack_from("<5I", data, 24)
c1, c2, c3, c4 = struct.unpack_from("<4I", data, 8)
SEG_D, END = o4, o5
segC = data[o3:o4]
def s3(u):
    e = segC.find(b"\x00", u); return segC[u:e].decode()
comps = [s3(struct.unpack_from('<I', data, o1+i*12)[0]) for i in range(c1)]

pat = re.compile(rb"BstNode_(\d+)\x00")
nodes = [(m.start(), int(m.group(1))) for m in pat.finditer(data, SEG_D)]
recs = []
for i, (n, nid) in enumerate(nodes):
    V = struct.unpack_from("<I", data, n-4)[0]
    ne = n + 8 + len(str(nid)) + 1
    nxt = nodes[i+1][0] if i+1 < len(nodes) else END - 4
    recs.append((n, nid, V, ne, nxt))
relmap = {}
for r in recs: relmap[(r[0]-4)-SEG_D] = r[1]

# 0x2ced = 11469 处
a = SEG_D + 0x2ced
print("SEG_D+0x2ced =", hex(a), "bytes:", data[a-8:a+24].hex(' '))
# rel 0x2ced -> 若是记录起点, V=? 
for u in [0x2ced, 0x2cee, 0x2cec]:
    if u in relmap: print(f"rel {hex(u)} -> BstNode_{relmap[u]}")
# 也许偏移含义 = 记录起点+1 (名字首字符 'B' 位置) 或 +0x?
# relmap 检查附近
for d in range(-8, 9):
    if 0x2ced+d in relmap:
        print("near:", hex(0x2ced+d), "->", relmap[0x2ced+d])

# 107B 案例: BstNode_973 是一条完整记录 (V=20, span=99). 
# 它的 payload 首 1B=00 后 u32 ff ff ff ff, '00 00 a0 41' = 80.0f...
# V=20 记录 (346条) 可能 = Transform!  72B transform?
t20 = [r for r in recs if r[2]==20][:4]
for n,nid,V,ne,nxt in t20:
    print(f"\nV20 id={nid} plen={nxt-ne-4} payload={data[ne:nxt-4].hex(' ')}")

# BstNode_973 所在父记录(107B LevelMesh): 其实是 rec V=20 id=973? 
# 107B 块 = 12B(hdr) + ... 回看原始 107B 样本: '29160000 c11f0000 14000000 4273744e...' 
# = u32 0x1629=5673? 现在重新解读: 那是 [prev payload tail][V=20][name BstNode_973\0][payload 87B][nextV]
# 验证: 0x14=20 = V 字段, 0x1629/0x1fc1 是前一条记录的 tail. 
print("\nBstNode_973 rec:", [r for r in recs if r[1]==973])
r973 = [r for r in recs if r[1]==973][0]
print("V=", r973[2], "payload:", data[r973[3]:r973[4]-4].hex(' '))
