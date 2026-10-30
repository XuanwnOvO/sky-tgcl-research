import struct, re
# seq 不全局连续但局部递增 → 尾 u32 是"同级兄弟/子链序号"（prev 分析里看到 1,2,3..,6,7,6,8..），
# 更像 "childIndex 或链表 next 计数"。无论语义，定界方案已被 BstNode_ 锚定法独立解决。
# 最后一验：391B 模板在两个关卡都出现（Dawn 1029 / DuskGraveyard 505），73/178/173 族是 DuskGraveyard 特有 → 模板按节点类型。
# 输出最终结构报告数据: Dawn 72B 模板统计 + 35B 模板复验
seg = open(r'd:\新建文件夹\LightEncounters\Children of the Light\Levels\Dawn\Objects.level.bin','rb').read()[91988:]
starts = [m.start() for m in re.finditer(rb'BstNode_\d{9,10}\x00', seg)]
lens = [starts[i+1]-starts[i] for i in range(len(starts)-1)] + [len(seg)-starts[-1]]
import math
# 35B 模板: 00 | u32 A | 00 | 01 | u32 hash | 00 | seq  (A 递增?)
vals=[]
for i,L in enumerate(lens):
    if L==35:
        rec = seg[starts[i]:starts[i]+L]
        A, = struct.unpack_from('<I', rec, 20)
        h = rec[25:29].hex()
        vals.append(A)
print('35B A field sample:', vals[:12], '...递增?', all(vals[i]<vals[i+1] for i in range(11)))
print('A range:', min(vals), max(vals))
# 全部记录的 seq 尾值范围
seqs = [struct.unpack_from('<I', seg, starts[i]+lens[i]-4)[0] for i in range(len(lens))]
print('seq max', max(seqs), '== c4 42919?', max(seqs)==42919)
# 42B (Dawn 首条类型) 数量 191: 结构 = 00 | u32 idA | u32 parent | u16 n | i32 -1 | u32 idA+1 | u32 cnt
ok=0
for i,L in enumerate(lens):
    if L==42:
        rec = seg[starts[i]:starts[i]+L]
        idA, = struct.unpack_from('<I', rec, 20)
        par, = struct.unpack_from('<i', rec, 24)
        if par == -1: ok+=1
print('42B 中 parent=-1 占比:', ok, '/', sum(1 for L in lens if L==42))
