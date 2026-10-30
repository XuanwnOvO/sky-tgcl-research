# -*- coding: utf-8 -*-
"""segD 终判: rec = [u32 seq][name][payload]; V=seq 递增?  尝试 V = seq 与文件序对照"""
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
print("nodes:", len(nodes), "c4 =", c4)

# 每记录: pre4 u32 = V. 检查 V 是否 0..N-1 严格递增
Vs = [struct.unpack_from("<I", data, n-4)[0] for n,_ in nodes]
inc = sum(1 for i in range(1, len(Vs)) if Vs[i] == Vs[i-1] + 1)
print("V strictly+1 steps:", inc, "/", len(Vs)-1, " V[0..10]:", Vs[:11], " V[-5:]:", Vs[-5:])
# 名后首 u32?
post = [struct.unpack_from("<I", data, n+13)[0] for n,_ in nodes]
# 检查 V=0/1/2... 与文件序差: 打印 V 序列前 30
print("V min/max:", min(Vs), max(Vs))
# gap 之间字节: gap=391 的记录, payload 是啥
# 先看 V 与 next-V 差
diffs = Counter(Vs[i+1]-Vs[i] for i in range(len(Vs)-1))
print("V diff hist:", diffs.most_common(8))

# 若 rec = [u32 V][name][payload (gap-13-V-4)]: V=0 时 gap-13-4=29-13-4=12? gap29 -> payload 12B?
# V=0 rec gap=29: payload = 29-13-4-4 = 8? 打印 V=0 rec 完整 29+4B
for i,(n,nid) in enumerate(nodes):
    if Vs[i]==0:
        nxt = nodes[i+1][0]
        print("V0 full rec:", data[n-4:nxt].hex(' '), "len", nxt-n+4)
        break

# 假设: [u32 V][name][u32 ?][payload...]  V=字段值. 看名后 4B 与下一记录 pre-8 对齐
# 直接解析尝试: walk: at pos: read u32 V; name until 0; then payload until next node pre4 - 4
# 统计 payload 首 u32<261 -> 组件
comp = Counter(); plens = defaultdict(list)
for i,(n,nid) in enumerate(nodes):
    nxt = nodes[i+1][0] if i+1 < len(nodes) else END - 4
    ps = n + 13
    pe = nxt - 4
    if pe < ps: continue
    pl = pe - ps
    f = struct.unpack_from("<I", data, ps)[0] if pl >= 4 else None
    if f is not None and f < c1:
        comp[schema[f][0]] += 1
        plens[schema[f][0]].append((pl, schema[f][1]))
print("comp-index records (payload after name, until next-4):", sum(comp.values()), "top:", comp.most_common(10))
for cname in ["Marker", "AudioMixToHaptics", "IfEnabled", "LevelMesh", "Transform"]:
    if cname in plens:
        L = plens[cname]
        print(cname, "n=", len(L), "payloadlens:", sorted(set(x[0] for x in L))[:15], "propCounts:", sorted(set(x[1] for x in L)))

# Marker 样本完整 dump
for i,(n,nid) in enumerate(nodes):
    nxt = nodes[i+1][0] if i+1 < len(nodes) else END - 4
    ps = n + 13; pe = nxt - 4
    f = struct.unpack_from("<I", data, ps)[0] if pe-ps >= 4 else -1
    if 0 <= f < c1 and schema[f][0] == "Marker" and pe-ps == 24:
        print("Marker rec:", data[n-4:nxt].hex(' '))
        break

# 检查名后 payload 首 u32 是组件时, pre4(V) 与 c2/rows 关系: V 是否 = segB row index?
# V max? 
vset = set(Vs)
print("V in segB-row-range [0,3239):", sum(1 for v in Vs if v < c2), "/", len(Vs))
