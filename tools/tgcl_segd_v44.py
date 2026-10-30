# -*- coding: utf-8 -*-
"""segD v44: V=4 u16@9 常量聚集 (0xC9BE=51646 x306!). 这些像 id 高位!
对象 id 形如 3384673xxx -> /65536? 3384673323>>16 = 51646 = 0xC9BE! 
=> V=4 记录 = 【对象组链接】: u16@9 = 对象 id 高 16 位!
3384673323>>16=51646 ✓ (u16@9=0xC9BE)
验证: V=4 记录的 u32@8 = (u16@9<<16)|byte8? 13221381=0xC9C005 = 51648*256+5 → 
其实是 u24@8 = id>>8 的低 3 字节? 3384673323>>8 = 13221380 = 0xC9C004!
样本2 u32@8 bytes = 04 be c9 00 → u24 = 0xC9BE04 = 13221380? 
p[8]=0x04, p[9]=0xBE, p[10]=0xC9 → u24 LE = 0xC9BE04 = 13221380 = id>>8 ✓✓✓
=> V=4 payload: 00 [u16A] 00 00 00 [flag] [b7] [u24 objId>>8] 00
验证所有 798 条: u24@8 == 某记录 id >> 8?"""
import re, struct
from collections import Counter

P = r"Children of the Light\Levels\Dawn\Objects.level.bin"
data = open(P, "rb").read()
o1, o2, o3, o4, o5 = struct.unpack_from("<5I", data, 24)
c1, c2, c3, c4 = struct.unpack_from("<4I", data, 8)

pat = re.compile(rb"BstNode_(\d+)\x00")
nodes = [(m.start(), int(m.group(1))) for m in pat.finditer(data, o4)]
recs = []
for i, (n, nid) in enumerate(nodes):
    V = struct.unpack_from("<I", data, n-4)[0]
    ne = n + 8 + len(str(nid)) + 1
    nxt = nodes[i+1][0] if i+1 < len(nodes) else o5 - 4
    recs.append((n, nid, V, ne, nxt))
ids = set(r[1] for r in recs)
idhi = Counter(r[1] >> 8 for r in recs)

v4 = [(nid, data[ne:nxt-4]) for (n, nid, V, ne, nxt) in recs if V == 4]
ok = 0; hi_ok = 0
tgt = Counter()
for nid, p in v4:
    u24 = p[8] | (p[9] << 8) | (p[10] << 16)
    if u24 in idhi: hi_ok += 1
    # 精确 id 匹配: u24 = id>>8, 且 byte8..10 之外无更多信息 → 匹配 id>>8
print(f"V=4 u24@8 == 某id>>8: {hi_ok}/{len(v4)}")
# u16@1 是否也是 id>>16? 
h16 = 0
for nid, p in v4:
    A = struct.unpack_from("<H", p, 1)[0]
    # 检查 A 是否 == 某id>>16
    pass
# 统计 u16@1 分布特征
As = Counter(struct.unpack_from("<H", p, 1)[0] for nid, p in v4)
print("u16@1 distinct:", len(As), "top:", As.most_common(5))
# 与 V=7 组件值块记录的邻近关系: V=4 记录的 id>>8 组是否包含组件值块?
