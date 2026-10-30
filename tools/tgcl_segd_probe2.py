# -*- coding: utf-8 -*-
"""segD 记录序言探测: 遍历各 xoff 假设, 统计是否所有记录的 id/长度/序号能无碰撞解析到 END"""
import re, struct
from collections import Counter

P = r"Children of the Light\Levels\Dawn\Objects.level.bin"
data = open(P, "rb").read()
o1, o2, o3, o4, o5 = struct.unpack_from("<5I", data, 24)
c1, c2, c3, c4 = struct.unpack_from("<4I", data, 8)
SEG_D, END = o4, o5

pat = re.compile(rb"BstNode_(\d+)\x00")
nodes = [(m.start(), int(m.group(1))) for m in pat.finditer(data, SEG_D)]
print("nodes:", len(nodes), "first off:", hex(nodes[0][0]), "segD:", hex(SEG_D))

# 第一个记录: 打印 SEG_D..first+16 完整字节
s0 = nodes[0][0]
print("bytes SEG_D..first+24:", data[SEG_D:s0+24].hex(' '))

# 各候选序言字段位置 (相对记录名起点 rec = 节点名起点):
# 检查 "名字前 4B" 和 "名字后 4B" 的值分布
pre4 = Counter(data[n-4:n] for n, _ in nodes)
print("pre4 top:", pre4.most_common(6))
pre4v = Counter(struct.unpack_from("<I", data, n-4)[0] for n,_ in nodes)
print("pre4 as u32 top:", pre4v.most_common(8), "distinct:", len(pre4v))
post4 = Counter(struct.unpack_from("<I", data, n+13)[0] if n+17<=END else -1 for n,_ in nodes)
print("post4(as u32 after name) distinct:", len(post4), "top:", post4.most_common(8))

# 节点间距
gaps = Counter(nodes[i+1][0]-nodes[i][0] for i in range(len(nodes)-1))
print("gap top:", gaps.most_common(12), "min gap:", min(gaps))

# 检查每个记录名后第一个 u32 是否等于下一个记录名前某个位置 -> 尝试: L = 名后u32, rec_end = nameStart+? 
# 名字起点到名字结束(含\0) = nlen; payloadLen = 名后u32?; rec_end = post + 4 + L
ok = 0; bad = 0; badex = []
for i, (n, nid) in enumerate(nodes):
    L = struct.unpack_from("<I", data, n + 13)[0]
    end = n + 13 + L
    nn = nodes[i+1][0] if i+1 < len(nodes) else END - 4
    if end == nn: ok += 1
    else:
        bad += 1
        if len(badex) < 10: badex.append((nid, L, end-nn))
print("hypothesis [name][u32 L][payload L]: exact next:", ok, "bad:", bad, "badex:", badex)
