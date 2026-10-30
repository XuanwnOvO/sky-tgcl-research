import struct, re
# 391B data 结构（这条样本）：0..63B = 交替 (float, u32 0)×8 → 8 个 float 属性!
# 64: 1.0 2.0 2.0 | 0 | ... 0 ... | 2.0 2.0 | 0 | 0.125 | 0 | 1.0 2.0 | 0.5 | 1.0 | ...
# 192 处出现 1.074e8 = u32 位模式 (0x4A0C3622 等被当 float) → 中段有 u32 字段!
# 数据不是纯 float——是混合。用 ida 思路：391 模板 = TGC "BoxShape/Mesh" 节点定长组件。
# 这一步已足够产出结构结论：定界方案已实锤（尾部 seq u32），72B transform 模板 98.9% 命中。
# 391B 模板做成字段图留待 IDA 交叉验证（BstNode::Deserialize）。
# 汇总全模板长度族 → 输出报告
from collections import Counter
seg = open(r'd:\新建文件夹\LightEncounters\Children of the Light\Levels\Dawn\Objects.level.bin','rb').read()[91988:]
starts = [m.start() for m in re.finditer(rb'BstNode_\d{9,10}\x00', seg)]
lens = [starts[i+1]-starts[i] for i in range(len(starts)-1)] + [len(seg)-starts[-1]]
c = Counter(lens)
print('记录数', len(lens))
print('模板长度族 (top 30):', c.most_common(30))
# seq 连续性验证
seqs = [struct.unpack_from('<I', seg, starts[i]+lens[i]-4)[0] for i in range(len(lens))]
print('seq 是否 1..N 连续:', seqs == list(range(1, len(seqs)+1)), 'max', max(seqs))
# DuskGraveyard 交叉验证
seg2 = open(r'd:\新建文件夹\LightEncounters\Children of the Light\Levels\DuskGraveyard\Objects.level.bin','rb').read()[55373:]
s2 = [m.start() for m in re.finditer(rb'BstNode_\d{9,10}\x00', seg2)]
l2 = [s2[i+1]-s2[i] for i in range(len(s2)-1)] + [len(seg2)-s2[-1]]
sq2 = [struct.unpack_from('<I', seg2, s2[i]+l2[i]-4)[0] for i in range(len(l2))]
print('DuskGraveyard 记录', len(l2), 'seq 连续:', sq2 == list(range(1, len(sq2)+1)))
c2 = Counter(l2)
print('DuskGraveyard 模板族 top15:', c2.most_common(15))
