import struct
d = open(r'd:\新建文件夹\LightEncounters\Children of the Light\Levels\Dawn\Objects.level.bin','rb').read()
o4 = 91988; o5 = len(d)
seg = d[o4:o5]
# 头 4 字节 00 00 00 00，然后记录：name\0 | 后续变长
# 记录1: name(19) \0 | 00 ed 2c 00 00(u32=0x2ced? no: 00 ed 2c 00 → little 0x002ced00? 试 u32@19=0x002ced00)
# 更合理: name\0 | u32 idx=0x00002ced? 不对
# 试: name\0 | u8 f=0x00 | u32 0x2ced = 11437 ... c2=3239? c3=14651?
# counts=(261,3239,14651,42919)。0x2ced=11437, 0x2cee=11438 相邻！→ 是下一记录的 fileIdx 连续编号?
# 记录1 tail: 00 | ed 2c 00 00(0x2ced=11437) | 00 00 00 00 | 01 00 | ff ff ff ff | ee 2c 00 00(0x2cee) | 01 00 00 00
# 记录2: name\0(0) | 01 00 00 d6 1e 00 00 00 6a 04 08 a8 MemAp18Misfit5 \0 ...
# 试: name\0 | u8 flag | (flag==1: u32 ?=0x001ed6... 
# 记录2 tail: 01 | 00 00 d6 1e 00 00 00 | 6a | 04 | 08 | a8 | MemAp18Misfit5\0 | 00 00 ff ff ff ff | 00 | ef 2c 00 00(0x2cef!) ...
# 0x2cef 紧跟 0x2cee → 每记录尾部有一个 u32 "下一个节点编号"。
# 记录1 尾 01 00 00 00 也可能是 count。假设: name\0 | u8 depth | u32 curIdx | u32 parent | u16 ? | i32 child? ...
# 先统计：假设记录格式 name\0 | u8 depth | u32 idx，扫描全 seg 看连续性
i=4; recs=[]
prev=None
while i < len(seg):
    j = seg.find(b'\x00', i)
    if j<0: break
    name = seg[i:j]
    if not name.startswith(b'BstNode'):
        break
    p=j+1
    depth = seg[p]; idx, = struct.unpack_from('<I', seg, p+1)
    recs.append((name.decode(), depth, idx, i))
    # 找下一个 BstNode_
    k = seg.find(b'BstNode_', p+5)
    if k<0: break
    i = k
print('count:', len(recs))
for r in recs[:10]: print(r)
print('...')
for r in recs[-3:]: print(r)
# depth 分布
from collections import Counter
print(Counter(r[1] for r in recs))
# idx 连续性
idxs=[r[2] for r in recs]
print('idx monotonic?', all(idxs[i]<=idxs[i+1] for i in range(len(idxs)-1)), 'min', min(idxs), 'max', max(idxs), 'c3=',14651)
