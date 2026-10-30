import struct, re
# 尾 u32 是全局递增序号（1,2,3,...节点号）→ 与 seg3 键名字典对应？
# 序号 1..N 正好可作 seg2 表索引。每条记录 = name\0 | 数据... | u32 seq
# 长度分布最常见 72/391/35 → 数据部分类型固定模板。
# 若尾 u32=seq，则记录数据 = name 之后到尾 4B 之间。
# 35B 记录: name(19B for 18ch+\0) + 数据 12B + seq 4B。dump 几条 35B 和 72B、391B：
seg = open(r'd:\新建文件夹\LightEncounters\Children of the Light\Levels\Dawn\Objects.level.bin','rb').read()[91988:]
starts = [m.start() for m in re.finditer(rb'BstNode_\d{9,10}\x00', seg)]
lens = [starts[i+1]-starts[i] for i in range(len(starts)-1)] + [len(seg)-starts[-1]]
def show(target, n=3):
    k=0
    for i,L in enumerate(lens):
        if L==target:
            rec = seg[starts[i]:starts[i]+L]
            seq, = struct.unpack_from('<I', rec, L-4)
            print(f'--- len {L} seq {seq}: {rec.hex(" ")}')
            print('   ', repr(rec))
            k+=1
            if k>=n: break
show(35); show(72); show(391); show(51)
