import struct, re
# TGCL transform 定界：策略——所有记录间用 "BstNode_" 或文件序号推进定界不可行时
# 用另一种线索：seg4 里 idA 递增序列。先收集 Dawn 的 idA 出现位置，得出每条记录长度
d = open(r'd:\新建文件夹\LightEncounters\Children of the Light\Levels\Dawn\Objects.level.bin','rb').read()
o4, o5 = 91988, len(d)
seg = d[o4:o5]
# 搜 seg4 内所有 BstNode_ 偏移
pos = [m.start() for m in re.finditer(rb'BstNode_\d{9,10}\x00', seg)]
print('nodes:', len(pos))
# 记录长度 = 下一个 pos - pos（最后一条到文件尾）
lens = [pos[i+1]-pos[i] for i in range(len(pos)-1)]
from collections import Counter
c = Counter(lens)
print('length distribution top20:', c.most_common(20))
print('min', min(lens), 'max', max(lens))
# 最短记录结构应为无 payload 的纯头，取出现最多的最短长度样本 dump
short = min(lens)
idxs = [i for i,l in enumerate(lens) if l == short][:3]
for i in idxs:
    print(f'--- rec len {short} @ {pos[i]}')
    print(seg[pos[i]:pos[i]+short].hex(' '))
    print(repr(seg[pos[i]:pos[i]+short]))
# 长度 42 的样本（Dawn 首条）在全部中分布如何
print('len42 count:', c.get(42,0))
# dump 一条 len=43 与 len=44 对比，找结构差
for L in sorted(c)[:6]:
    i = next(i for i,l in enumerate(lens) if l==L)
    print(f'--- len {L}:'); print(seg[pos[i]:pos[i]+L].hex(' '))
