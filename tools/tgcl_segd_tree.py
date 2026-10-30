# -*- coding: utf-8 -*-
"""segD 树结构标定：BstNode 全集定界 + 嵌套树 + 子块长度验证 + 组件索引型复查"""
import re, struct, sys
from collections import Counter, defaultdict

P = r"Children of the Light\Levels\Dawn\Objects.level.bin"
data = open(P, "rb").read()
print("filesize", len(data))
cnt = struct.unpack_from("<4I", data, 0)
offs = struct.unpack_from("<5I", data, 16)
print("counts", cnt, "offsets", offs)
SEG_D = offs[4]          # 91988
END = len(data)

# --- 1. BstNode 全集（含短 id）---
pat = re.compile(rb"BstNode_(\d+)\x00")
all_nodes = [(m.start(), int(m.group(1))) for m in pat.finditer(data)]
print("total BstNode occurrences in file:", len(all_nodes))
in_segd = [(o, i) for o, i in all_nodes if SEG_D <= o < END]
print("  within segD:", len(in_segd))
ids = [i for _, i in in_segd]
print("  unique ids:", len(set(ids)), "id range:", min(ids), "-", max(ids))
len_hist = Counter(len(str(i)) for i in ids)
print("  id digit-length hist:", dict(sorted(len_hist.items())))

# 记录按节点名起点定界：record span = node_name_start -> next_node_name_start（初版，含尾部 seq 问题稍后处理）
spans = []
for k in range(len(in_segd)):
    s = in_segd[k][0]
    e = in_segd[k+1][0] if k+1 < len(in_segd) else END
    spans.append((s, e, in_segd[k][1]))
# 尾部 u32 seq 假设：最后 4B
tail = struct.unpack_from("<I", data, END-4)[0]
print("tail u32 (before last4):", struct.unpack_from("<I", data, END-8)[0], " last4:", tail)

# --- 2. 树构建：短 id 节点在长 id payload 内 ---
# 一个 span 若包含另一个 span 的起点 -> 嵌套
parent = {}
tops = []
order = sorted(range(len(spans)), key=lambda k: (spans[k][0], -spans[k][1]))
stack = []
for k in order:
    s, e, nid = spans[k]
    while stack and spans[stack[-1]][1] <= s:
        stack.pop()
    if stack:
        parent[k] = stack[-1]
    else:
        tops.append(k)
    stack.append(k)
print("top-level records:", len(tops), "nested:", len(parent))
depth = Counter()
for k in range(len(spans)):
    d, cur = 0, k
    while cur in parent:
        cur = parent[cur]; d += 1
    depth[d] += 1
print("depth hist:", dict(sorted(depth.items())))

# 嵌套对样本：child 相对 parent 起点的偏移
ex = [(spans[p][2], spans[c][2], c - p) for p, c in list(parent.items())[:15]]
for pid, cid, rel in ex:
    print(f"  parent BstNode_{pid} -> child BstNode_{cid} rel_off_from_parent_payloadname={rel}")

# --- 3. 107B LevelMesh 样本：0x14=20 子块长验证 ---
# 找包含 "BstNode_973" 的记录，检查头三 u32 与子块长度
target = data.find(b"BstNode_973\x00")
print("\nBstNode_973 first occurrence at", target, "in segD:", SEG_D <= target < END)
# 它所在的父记录头
# 父记录 = 最近一个其 span 覆盖 target 的记录
# 打印 target 前 32B
print("ctx before:", data[target-24:target].hex(" "))
name_len = len(b"BstNode_973\x00")  # 12
# 假设头: u32 X, u32 Y, u32 sublen, 然后 name+payload
hdr_off = target - 12
X, Y, SUBLEN = struct.unpack_from("<3I", data, hdr_off)
print(f"hdr u32s before name: X={X} (0x{X:x}) Y={Y} (0x{Y:x}) SUBLEN={SUBLEN} (0x{SUBLEN:x})")
# name_end = target + name_len; child payload = 从 X? 从 Y? 试着看 name 后的结构
after = target + name_len
print("after name 48B:", data[after:after+48].hex(" "))

# 统计：对每个嵌套 child，读取其名字前 12B 作为 (X,Y,SUBLEN)，验证 SUBLEN == (child span 从名字前?到结束) 长度候选
ok_sub = 0; bad = 0
samples = []
for c, p in parent.items():
    cs, ce, cid = spans[c]
    h = struct.unpack_from("<3I", data, cs-12)
    # 候选1: SUBLEN == ce - (cs-12+12)? 即 name后到记录尾
    cand = ce - cs
    cand2 = ce - (cs - 12)  # 含3u32头
    samples.append((h[2], cand, cand2, ce, cs))
for SUBLEN, cand, cand2, ce, cs in samples[:10]:
    print(f"  child: SUBLEN={SUBLEN} nameStart..end={cand} hdrStart..end={cand2}")
# 全局验证
m1 = sum(1 for SUBLEN, cand, cand2, ce, cs in samples if SUBLEN == cand)
m2 = sum(1 for SUBLEN, cand, cand2, ce, cs in samples if SUBLEN == cand2)
print(f"SUBLEN==nameStart..end: {m1}/{len(samples)}   SUBLEN==hdrStart..end: {m2}/{len(samples)}")

# --- 4. 父记录头三 u32 分析 ---
print("\ntop-level record headers (first u32s before name):")
for k in tops[:12]:
    s, e, nid = spans[k]
    print(f"  BstNode_{nid} span={e-s} hdr12={data[s-12:s].hex(' ')}")

# --- 5. 组件索引型记录复查：payload 首 u32 <261 ---
schema = {}
for i in range(cnt[0]):
    no, ss, pc = struct.unpack_from("<3I", data, offs[0] + i*12)
    e = data.find(b"\x00", no)
    schema[i] = (data[no:e].decode(), pc)
print("\nschema sample:", {i: schema[i] for i in [0,1,2]})

comp_hits = Counter()
rec_meta = []
for k, (s, e, nid) in enumerate(spans):
    # payload 起点 = 名字结束
    ps = s + len(b"BstNode_%d\x00" % nid)
    first = struct.unpack_from("<I", data, ps)[0] if ps+4 <= e else -1
    rec_meta.append((k, s, e, nid, ps, first))
    if 0 <= first < cnt[0]:
        comp_hits[schema[first][0]] += 1
print("component-index-like records:", sum(comp_hits.values()), "top:", comp_hits.most_common(8))

# 这些记录的长度分布 vs schema propCount
lens_by_comp = defaultdict(list)
for k, s, e, nid, ps, first in rec_meta:
    if 0 <= first < cnt[0]:
        lens_by_comp[schema[first][0]].append((e-s, e-ps, schema[first][1]))
for c in ["Marker", "IfEnabled", "LevelMesh", "AudioMixToHaptics"]:
    if c in lens_by_comp:
        L = lens_by_comp[c]
        print(c, "n=", len(L), "payloadlen(set):", sorted(set(x[1] for x in L))[:12], "propCounts:", sorted(set(x[2] for x in L)))

# Marker 24B 详细 dump
for k, s, e, nid, ps, first in rec_meta:
    if 0 <= first < cnt[0] and schema[first][0] == "Marker" and e-ps == 24:
        print("Marker 24B sample: name=BstNode_%d hdr12=%s payload=%s" % (nid, data[s-12:s].hex(' '), data[ps:e].hex(' ')))
        break

# --- 6. 检查组件索引型记录是否嵌套在别的记录内 ---
nest_among_comp = sum(1 for k, s, e, nid, ps, first in rec_meta if 0 <= first < cnt[0] and k in parent)
print("component-index-like records that are NESTED:", nest_among_comp, "/", sum(comp_hits.values()))

# --- 7. first u32 >= 261 的 top 记录：值域分析 ---
vals = Counter()
for k, s, e, nid, ps, first in rec_meta:
    if k not in parent and first >= cnt[0]:
        vals[first] += 1
print("top-level non-comp first-u32 distinct:", len(vals), "top10:", vals.most_common(10))
# 是否 first == 自身 id 或附近?
same = sum(1 for k, s, e, nid, ps, first in rec_meta if first == nid)
print("first_u32 == own node id:", same)
