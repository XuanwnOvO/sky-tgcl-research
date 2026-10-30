import struct, re
# 关键突破：len22 记录 = name\0 + u32（04/4a/44）→ 尾部 u32 是"下一条记录长度"？不对，那是 BstNode_34452280x 同族。
# 观察 len22 尾 u32: 0x04, 0x4a, 0x44 → 疑为"属性块字节数"或"子节点数"。
# 更强假设：记录 = name\0 | u32 payloadLen | payload。验证：
#   len22 记录: name(19)\0 占 19，尾 u32=4 → 19+4=23 ≠22。差 1。
#   再看：name 18 chars + \0 =19; len22-19=3 剩 04 00 00 → 若 u24?
# 另一假设：记录 = name\0 | u8 0x04? no len22: 19+3。
# len23: name(19)\0 + 00 06 00 00 00 → 5B: u8 f=0 | u32 len=6 → 总长 19+1+4+6=30≠23
# 试：记录 = name\0 | varint? 00 06 00 = 24bit 0x000600?
# 看 len24: name(19)\0? "BstNode_3538681860"=18ch+\0=19, 剩 00 04 00 00 00 = 5B
# len22: name 17ch? "BstNode_344522804"=17ch+\0=18, 剩 04 00 00 00 = 4B ✓ → name 长度可变（数字位数），剩余 = payload
# len22 剩 4B: 04 00 00 00 = u32 4
# len23 剩 5B: 00 06 00 00 00
# len24 剩 5B: 00 04 00 00 00
# len25 剩 6B: 00 01 0a 00 00 00
# len26 剩 7B: 00 00 80 3f 06 00 00 00 → 8B 实际 (18+8=26) "BstNode_344523063"=17ch+1=18 ✓
#   → 剩 00 00 80 3f (float 1.0!) + 06 00 00 00
# len27 剩 7B: 00 00 00 00 09 00 00 00 (8B): u32 0 + u32 9
# 结论成形：payload 尾部有 u32 N（可能是"下一字段数/子数"），前面是字段数据
# len22: 字段数据=空, N=4? 但 len22 剩 4B 只有 04 00 00 00 → 若最后 u32 是 N，字段数据 = 空 ✓
# len26: 字段数据 = float 1.0, N=6
# len24: 字段数据 = 00 (u8), N=4
# len25: 字段数据 = 00 01? N=0x0a=10? "00 01 0a 00 00 00" → f8=0x00,f16=0x0001? 混乱
# 用首条 42B 验证：BstNode_2310602845(18ch)+\0=19, 剩 23B:
#   00 ed 2c 00 00 | 00 00 00 00 | 01 00 | ff ff ff ff | ee 2c 00 00 | 01 00 00 00
#   = u8 0 | u32 0x2ced | u32 0 | u16 1 | i32 -1 | u32 0x2cee | u32 1
#   若尾部 u32=1 是"子节点数1"？ 0x2cee=0x2ced+1 = 子节点文件序号!
# 系统性验证：解析所有记录，检查"尾部 u32"与下一记录关系
seg = open(r'd:\新建文件夹\LightEncounters\Children of the Light\Levels\Dawn\Objects.level.bin','rb').read()[91988:]
pos = [m.end() for m in re.finditer(rb'BstNode_\d{9,10}\x00', seg)]
starts = [m.start() for m in re.finditer(rb'BstNode_\d{9,10}\x00', seg)]
lens = [starts[i+1]-starts[i] for i in range(len(starts)-1)] + [len(seg)-starts[-1]]
# 尾 u32 分布 vs 记录长度
nxt = []
bad = 0
for i in range(len(starts)-1):
    L = lens[i]
    if L >= 4:
        tail, = struct.unpack_from('<I', seg, starts[i]+L-4)
        nxt.append(tail)
print('tail u32 sample:', nxt[:30])
print('tail==childIdx+1 pattern?', sum(1 for t in nxt if t < 15000)/len(nxt))
# 长度直方按尾值 <50 归纳：尾 u32 疑为"属性字段数"
from collections import Counter
print('tail dist:', Counter(t for t in nxt if t<20).most_common(15))
