# -*- coding: utf-8 -*-
# 重要观察：Marker 值块 24B = 6×u32（值全是 0x600-0x27d0 范围的小 u32）
# 假设：值块其实不是属性值！这些小 u32 更像 "子节点 id 列表" 或 事件引用。
# 而 AudioMixToHaptics 84B = 21×u32 全是小值。
# 新假设：segD = 事件/连接表！BstNode_<id> 的值块 = 该节点的事件连线（u32 = 另一节点表索引？）
# 检查：值块里的 u32 是否能对上其他 BstNode 的 id 低 32 位 / 或事件字符串 hash
import os, re, struct, collections
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"
lv = 'Dawn'
d = open(os.path.join(root, lv, 'Objects.level.bin'), 'rb').read()
o1, o2, o3, o4, o5 = struct.unpack_from('<5I', d, 24)
segC = d[o3:o4]
seg = d[o4:]
ms = list(re.finditer(rb'BstNode_(\d{9,10})\x00', seg))
# 全部值块 u32 值域
vals = collections.Counter()
maxv = 0
for i, m in enumerate(ms):
    a, hl = m.start(), m.end()-m.start()
    e = ms[i+1].start() if i+1 < len(ms) else len(seg)
    body = seg[a+hl:e-4]
    if len(body) < 4: continue
    u = struct.unpack_from('<I', body, 0)[0]
    if u >= 261: continue
    for k in range(4, len(body)-3, 4):
        v = struct.unpack_from('<I', body, k)[0]
        vals[v] += 1
        maxv = max(maxv, v)
print("组件索引型块里的 u32 总数:", sum(vals.values()), "max:", maxv)
print("值域分布: <261:", sum(v for k,v in vals.items() if k<261),
      "<3239:", sum(v for k,v in vals.items() if k<3239),
      "<14651:", sum(v for k,v in vals.items() if k<14651),
      "<42919:", sum(v for k,v in vals.items() if k<42919))
# 是否 < 11194 (节点数)?  是否是节点序号？
print("<11194:", sum(v for k,v in vals.items() if k<11194))
# top 值
print("top:", vals.most_common(10))
