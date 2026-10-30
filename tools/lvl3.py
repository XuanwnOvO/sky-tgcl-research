import struct

b = open(r'Children of the Light\Levels\Dawn\Objects.level.bin','rb').read()

# BstNode 记录: name NUL | u16 offset | u16 flags | u32 parentIdx | u32 ?(2C...) 
# BstNode_2819097706 -> "MemAp18Misfit5" (prefab 实例名)
# 后续记录间隔可变: 内含子字段。先统计记录数、找 transform 块模式 (1.0,1.0,1.0 scale + pos)
# 实际上更简单: 引擎里 Bst = "Behavior Stream Tree"? 值域 0x2ced 是子节点偏移

# 统计: 每条记录 = name + u16 len? 让我扫描所有 BstNode_ 的间隔分布
import re
pos = [m.start() for m in re.finditer(rb'BstNode_[0-9]+\x00', b)]
print('count:', len(pos))
gaps = [pos[i+1]-pos[i] for i in range(len(pos)-1)]
import collections
print('gap distribution top:', collections.Counter(gaps).most_common(10))

# BstNode_2310602845 记录后 22 字节就到下一条 → 头部结构 = name(16) + u32 idx + u16 + u16 + u32? 
# name 长度 = len('BstNode_2310602845')+1 = 19; 19+? = 22 → 后跟 u16? 
# 实测: name 结束@pos+19, gap=22 → 后跟 3 字节? 不对, name 19+pad2+1? 
# 看 0x2ced = u32 在 name 后。 而 BstNode_2819097706 后是 "d6 1e" u16=0x1ed6, "0000" u16, "6a04" u16, "08" ...
# 假设记录 = name | u16 name_len | u16 attr_count | u16 data_len | data
print(b[pos[1]:pos[1]+20])
