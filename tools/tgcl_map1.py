# -*- coding: utf-8 -*-
# 探索：segD 中 BstNode 值块如何对应 segA 组件？
# BstNode_<id> 的 id 可能 = 组件类型 id 或节点实例 id。
# 实验：统计 id 前缀分布，看是否有 261 个不同 id（=组件表）还是海量（=实例）
import os, re, struct, collections
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"
lv = 'Dawn'
d = open(os.path.join(root, lv, 'Objects.level.bin'), 'rb').read()
o1, o2, o3, o4, o5 = struct.unpack_from('<5I', d, 24)
seg = d[o4:]
ms = list(re.finditer(rb'BstNode_(\d{9,10})\x00', seg))
ids = [m.group(1).decode() for m in ms]
print("节点数:", len(ids), "唯一 id:", len(set(ids)))
# id 长度分布
print("id 长度分布:", collections.Counter(len(i) for i in ids).most_common(5))
# 前 20 个 id
print("前 20 id:", ids[:20])
# segA 里 nameOff→类名，类名数量
segC = d[o3:o4]
segA = d[o1:o2]
def s3(u):
    e = segC.find(b'\x00', u)
    return segC[u:e].decode('utf-8', 'replace')
comps = []
for i in range(261):
    a, st, pc = struct.unpack_from('<3I', segA, i*12)
    comps.append(s3(a))
print("组件前 20:", comps[:20])
print("唯一组件名:", len(set(comps)))
# id 数值范围
ival = [int(i) for i in ids]
print("id min/max:", min(ival), max(ival))
