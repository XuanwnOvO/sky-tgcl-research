import struct
# 关键观察：11493 个 BstNode 记录（头 count c3=14651 是别的）。
# 记录1 (42B): name\0 | 00 | ed 2c 00 00 | 00 00 00 00 | 01 00 | ff ff ff ff | ee 2c 00 00 | 01 00 00 00
#   假设: name\0 | u8 flags=0 | u32 idA=0x2ced(11437) | u32 idB=0 | u16 n1=1 | u32 parent=-1 | u32 idA_next=0x2cee | u32 n2=1
#   → 树结构：当前节点 fileIdx=11437，parent=-1（根），下一个兄弟编号 11438
# 记录2: name\0 | 01 | 00 00 d6 1e ... → flags=1 后跟 payload（含 prefab 名 "MemAp18Misfit5"）
# 验证思路：从记录1格式假设出发做解析器，payload 长度未知——但可以用 "下一记录的 idA 递增" 特性?
# 更直接: 用 diff —— 同样 dump DuskGraveyard 头两条
import sys
def head_dump(path, n=400):
    d = open(path,'rb').read()
    o4, = struct.unpack_from('<I', d, 36)
    seg = d[o4:o4+n]
    pos = [m for m in range(len(seg)) if seg.startswith(b'BstNode_', m)]
    print(path.split('\\')[-2], 'first BstNode@', o4, 'recs at', pos[:5])
    a,b = pos[0], pos[1]
    print(seg[a:b].hex(' ')); print(repr(seg[a:b]))
    c = pos[2] if len(pos)>2 else len(seg)
    print(seg[b:c].hex(' ')); print(repr(seg[b:c]))

head_dump(r'd:\新建文件夹\LightEncounters\Children of the Light\Levels\DuskGraveyard\Objects.level.bin')
