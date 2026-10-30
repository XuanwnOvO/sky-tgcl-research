# -*- coding: utf-8 -*-
# 关键发现！LevelMesh 值块 107B 里有内嵌 "BstNode_973\0"！
# 这说明 segD 是【嵌套树】：BstNode_<大id> 里面再嵌 BstNode_<小id>?
# 不对——外层正则只匹配 \d{9,10}，内嵌是 BstNode_973（3位）→ 我们漏了子节点！
# 重新定界：BstNode_\d+ 任意长度
import os, re, struct, collections
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"
lv = 'Dawn'
d = open(os.path.join(root, lv, 'Objects.level.bin'), 'rb').read()
o1, o2, o3, o4, o5 = struct.unpack_from('<5I', d, 24)
seg = d[o4:]
ms = list(re.finditer(rb'BstNode_(\d+)\x00', seg))
print("全部 BstNode 数:", len(ms), "唯一 id:", len(set(m.group(1) for m in ms)))
lens = collections.Counter(len(m.group(1)) for m in ms)
print("id 位数分布:", lens.most_common(12))
# 大 id 节点 payload 首 u32<261 的还成立吗
segC = d[o3:o4]
def s3(u):
    e = segC.find(b'\x00', u)
    return segC[u:e].decode('utf-8', 'replace')
segA = d[o1:o2]
comps = [s3(struct.unpack_from('<I', segA, i*12)[0]) for i in range(261)]
first = collections.Counter()
nest = 0
for i, m in enumerate(ms):
    a, hl = m.start(), m.end()-m.start()
    e = ms[i+1].start() if i+1 < len(ms) else len(seg)
    body = seg[a+hl:e-4]
    if len(body) < 4: continue
    u = struct.unpack_from('<I', body, 0)[0]
    if u < 261: first[comps[u]] += 1
    elif b'BstNode_' in body: nest += 1
print("首u32<261:", sum(first.values()), "含嵌套BstNode:", nest)
print(first.most_common(12))
