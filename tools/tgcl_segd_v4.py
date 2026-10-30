# -*- coding: utf-8 -*-
"""segD v4: rec = [u32 V][name + payload][u32 nextV]. 下一层: payload 是否以 1B 长度+尾部字节开始
   关键: 名字尾 '2310602845\0' 之后跟 00 -- 名字真正的 \0 被吞了? 试 name 不含 \0:
   name='2310602845' 10B. V=0, 然后名字从 n+4 开始. re match start n 就是 'BstNode_' 起.
   实际: rec0 V=0 @n-4, name@n .. n+13 = 'BstNode_2310602845\0'? BstNode_=8 + 10 + \0 = 19B -> n+19.
   n+13 是错的! BstNode_ 是 8 字符, id 是 10 位: 8+10+1=19. 我上面用 n+13 少了 6B -> payload 首部其实是名字残余!
   真正 name end = n + 8 + len(str(id)) + 1. 重算."""
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

recs = []
for i, (n, nid) in enumerate(nodes):
    V = struct.unpack_from("<I", data, n-4)[0]
    ne = n + 8 + len(str(nid)) + 1
    nxt = nodes[i+1][0] if i+1 < len(nodes) else END - 4
    tailV = struct.unpack_from("<I", data, nxt-4)[0]
    recs.append((n, nid, V, ne, nxt, tailV))
    assert data[n-4:n][0] == len(str(nid)) or True
print("sample:", [(r[1], r[2], r[5]) for r in recs[:8]])
# tail==next V 已证. payload = [ne, nxt-4)
plens = Counter(r[4]-r[3]-4 for r in recs)
print("payload len top:", plens.most_common(12), "min:", min(plens))

# payload 首 u32 < 261 -> 组件索引?
comp = Counter(); bycomp = defaultdict(list)
for n, nid, V, ne, nxt, tailV in recs:
    pl = nxt - ne - 4
    if pl >= 4:
        f = struct.unpack_from("<I", data, ne)[0]
        if f < c1:
            comp[schema[f][0]] += 1
            bycomp[schema[f][0]].append((pl, schema[f][1], V))
print("comp-index count:", sum(comp.values()), "top:", comp.most_common(12))
for cn in ["Marker","AudioMixToHaptics","IfEnabled","LevelMesh","CandleObject"]:
    if cn in bycomp:
        L = bycomp[cn]
        print(cn, "n=", len(L), "plens:", sorted(set(x[0] for x in L))[:15], "propCounts:", sorted(set(x[1] for x in L)))

# Marker 完整样本
for n, nid, V, ne, nxt, tailV in recs:
    pl = nxt - ne - 4
    if pl >= 4 and struct.unpack_from("<I", data, ne)[0] < c1 and schema[struct.unpack_from('<I',data,ne)[0]][0]=="Marker":
        print("Marker rec: V=%d plen=%d payload=%s" % (V, pl, data[ne:nxt-4].hex(' ')))
        break
# AudioMixToHaptics
for n, nid, V, ne, nxt, tailV in recs:
    pl = nxt - ne - 4
    if pl >= 4 and struct.unpack_from("<I", data, ne)[0] < c1 and schema[struct.unpack_from('<I',data,ne)[0]][0]=="AudioMixToHaptics":
        print("AMTH rec: V=%d plen=%d payload=%s" % (V, pl, data[ne:nxt-4].hex(' ')))
        break
# LevelMesh 各长度一个样本
shown = set()
for n, nid, V, ne, nxt, tailV in recs:
    pl = nxt - ne - 4
    if pl >= 4 and struct.unpack_from("<I", data, ne)[0] < c1 and schema[struct.unpack_from('<I',data,ne)[0]][0]=="LevelMesh":
        if pl not in shown:
            shown.add(pl)
            print("LevelMesh plen=%d payload=%s" % (pl, data[ne:nxt-4].hex(' ')))
        if len(shown) >= 6: break

# 尾部 u32 (nextV) 前面是否有固定字段: payload 末 8B 检查 -> 打印 comp 记录末 12B
endpat = Counter()
for n, nid, V, ne, nxt, tailV in recs:
    pl = nxt - ne - 4
    if pl >= 4 and struct.unpack_from("<I", data, ne)[0] < c1:
        endpat[data[nxt-8:nxt-4].hex()] += 1
print("comp rec last-8B(top):", endpat.most_common(6))
