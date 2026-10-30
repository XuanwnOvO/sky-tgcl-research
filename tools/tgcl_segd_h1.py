# -*- coding: utf-8 -*-
"""segD 记录格式终判: [u32 V][name\\0][payload V-?]. 假设 H1: rec = 4B V + name + (V) bytes payload"""
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
print("nodes:", len(nodes))

# H1
ok = bad = 0; badex = []
for i, (n, nid) in enumerate(nodes):
    V = struct.unpack_from("<I", data, n-4)[0]
    end = n + 13 + V
    nn = nodes[i+1][0] if i+1 < len(nodes) else END - 4
    if end == nn: ok += 1
    else:
        bad += 1
        if len(badex) < 12: badex.append((nid, V, end - nn))
print("H1 exact:", ok, "bad:", bad, "badex(off):", badex)

# H1 变体: 含 name 的总长
ok2 = 0
for i, (n, nid) in enumerate(nodes):
    V = struct.unpack_from("<I", data, n-4)[0]
    end = n - 4 + V
    nn = nodes[i+1][0] if i+1 < len(nodes) else END - 4
    if end == nn: ok2 += 1
print("H1b (V = 4B+name+payload) exact:", ok2)

# H2: V=0 时 payload=0? H1 bad 记录的 V=0 样本
if bad:
    shown = 0
    for i, (n, nid) in enumerate(nodes):
        V = struct.unpack_from("<I", data, n-4)[0]
        if V == 0:
            end = n + 13
            nn = nodes[i+1][0] if i+1 < len(nodes) else END - 4
            print(f"V=0 rec id={nid} end-nextgap={nn-end} nextbytes={data[n:n+40].hex(' ')}")
            shown += 1
            if shown >= 5: break

# H1 ok 记录上: V 与 payload 首 u32/组件
def parse_ok_records():
    recs = []
    for i, (n, nid) in enumerate(nodes):
        V = struct.unpack_from("<I", data, n-4)[0]
        end = n + 13 + V
        nn = nodes[i+1][0] if i+1 < len(nodes) else END - 4
        if end == nn and V >= 4:
            recs.append((n, nid, V))
    return recs
recs = parse_ok_records()
print("H1 ok with payload:", len(recs))
first = Counter()
for n, nid, V in recs:
    f = struct.unpack_from("<I", data, n+13)[0]
    first[f] += 1
print("payload-first-u32 top:", first.most_common(10), "distinct:", len(first))
compf = Counter(schema[f][0] for n,nid,V in recs if f < c1 for f in [struct.unpack_from('<I',data,n+13)[0]])
print("comp-index dist:", compf.most_common(10))

# X 字段 = pre-8 u32?
pre8 = Counter(struct.unpack_from("<I", data, n-8)[0] for n,_ in nodes)
print("pre8 distinct:", len(pre8), "top:", pre8.most_common(8))
# pre-12
pre12 = Counter(struct.unpack_from("<I", data, n-12)[0] for n,_ in nodes)
print("pre12 distinct:", len(pre12), "top:", pre12.most_common(8))
