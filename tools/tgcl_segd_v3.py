# -*- coding: utf-8 -*-
"""segD 终判 v3: rec = [u32 V][name][1B][u32? ...]; 末尾 3u32 = (compIdx, ?, nextSeq)?; 寻找起止规则"""
import re, struct
from collections import Counter, defaultdict

P = r"Children of the Light\Levels\Dawn\Objects.level.bin"
data = open(P, "rb").read()
o1, o2, o3, o4, o5 = struct.unpack_from("<5I", data, 24)
c1, c2, c3, c4 = struct.unpack_from("<4I", data, 8)
SEG_D, END = o4, o5

schema = {}
for i in range(c1):
    no, ss, pc = struct.unpack_from("<3I", data, o1 + i*12)
    schema[i] = (data[no:data.find(b"\x00", no)].decode("latin1"), pc)
rows = []
for i in range(c2):
    a, ko, t, e = struct.unpack_from("<4I", data, o2 + i*16)
    rows.append((a, data[ko:data.find(b"\x00", ko)].decode("latin1"), t, e))

pat = re.compile(rb"BstNode_(\d+)\x00")
nodes = [(m.start(), int(m.group(1))) for m in pat.finditer(data, SEG_D)]
Vs = [struct.unpack_from("<I", data, n-4)[0] for n,_ in nodes]

# 检查每条记录末尾 4B (next-4 处 u32) 是否等于下一记录的 V
match_next = 0
for i in range(len(nodes)-1):
    n, nid = nodes[i]; nxt = nodes[i+1][0]
    tail = struct.unpack_from("<I", data, nxt-4)[0]
    if tail == Vs[i+1]: match_next += 1
tail_last = struct.unpack_from("<I", data, END-4)[0]
print("tail4 == next V:", match_next, "/", len(nodes)-1, " last tail:", tail_last)

# 所以 rec = [u32 V][name][payload][u32 nextV]; 且 V=自己序号.
# payload 长度 = next - (name_end). 
# 检查: 尾部 3u32 结构: (compIdx, A, nextSeq)?  rec0 末尾: 01 00 00 00 | ee 2c 00 00 | 01 00 00 00
# rec0: V=0, name, payload: 00 ed 2c 00 00 00 00 00 00 01 00 ff ff ff ff? no——让我按 tail 切:
# rec0: V=0 (4B) name(18+1=19B) payload = 42-4-19-4 = 15B, tail4 = nextV=1
# payload: 00 ed 2c 00 00 00 00 00 00 01 00 ff ff ff ff -> 0x2ced=11469 节点引用
print()
for i in range(8):
    n, nid = nodes[i]; nxt = nodes[i+1][0]
    pl = nxt - (n+13) - 4
    pay = data[n+13:n+13+pl]
    tailV = struct.unpack_from("<I", data, nxt-4)[0]
    print(f"rec{i} V={Vs[i]} id={nid} plen={pl} payload={pay.hex(' ')} nextV={tailV}")

# plen 分布 & 末尾固定模式检查: 记录 payload 尾部常见 "01 00 00 00"? 
# 检查 payload 尾 u32 值分布
tailu = Counter()
for i in range(len(nodes)-1):
    n, nid = nodes[i]; nxt = nodes[i+1][0]
    pl = nxt - (n+13) - 4
    if pl >= 4:
        tailu[struct.unpack_from("<I", data, n+13+pl-4)[0]] += 1
print("payload tail u32 top:", tailu.most_common(10))

# 之前"组件索引 3789"来自旧定界 (span 到下一名字起点)。现在检查 payload 首 u32 <261:
firstu = Counter(); pl_by_comp = defaultdict(list)
for i in range(len(nodes)-1):
    n, nid = nodes[i]; nxt = nodes[i+1][0]
    pl = nxt - (n+13) - 4
    if pl < 4: continue
    f = struct.unpack_from("<I", data, n+13)[0]
    if f < c1:
        firstu[schema[f][0]] += 1
        pl_by_comp[schema[f][0]].append((pl, schema[f][1], Vs[i]))
print("payload first<261 count:", sum(firstu.values()), "top:", firstu.most_common(10))
for cn in ["Marker","AudioMixToHaptics","IfEnabled","LevelMesh"]:
    if cn in pl_by_comp:
        L = pl_by_comp[cn]
        print(cn, "n=",len(L), "plens:", sorted(set(x[0] for x in L))[:15], "pcs:", sorted(set(x[1] for x in L)))
# Marker 样本完整
for i in range(len(nodes)-1):
    n, nid = nodes[i]; nxt = nodes[i+1][0]
    pl = nxt - (n+13) - 4
    f = struct.unpack_from("<I", data, n+13)[0] if pl>=4 else -1
    if 0 <= f < c1 and schema[f][0]=="Marker":
        print("Marker full:", data[n-4:nxt].hex(' '))
        break
