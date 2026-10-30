import struct, re, os
root = r'd:\新建文件夹\LightEncounters\Children of the Light\Levels'
# type 语义定案: 0=引用/对象(复合), 1=bool, 4=float, 16=?, 64=?
# 16 与 64: 看名字:
d = open(os.path.join(root,'Dawn','Objects.level.bin'),'rb').read()
o1,o2,o3,o4,o5 = struct.unpack_from('<5I', d, 24)
seg2 = d[o2:o3]; seg3 = d[o3:o4]
rows=[]
for k in range(len(seg2)//16):
    a,b,c,e = struct.unpack_from('<4I', seg2, k*16)
    nm = seg3[b:b+48].split(b'\x00')[0].decode('latin1')
    rows.append((k,a,c,e,nm))
print('type16:', [r[4] for r in rows if r[2]==16][:25])
print('type64:', [r[4] for r in rows if r[2]==64][:25])
# a 字段 uniq? e 字段?
from collections import Counter
print('a vals:', Counter(r[1] for r in rows).most_common(5))
print('e vals:', Counter(r[3] for r in rows).most_common(8))
# 剩余谜团: seg1 (44..3176, 3132B) 高熵。看内容:
seg1 = d[o1:o2]
print('seg1 head:', seg1[:64].hex(' '))
print('seg1 ascii:', seg1[:80])
# 熵估计
from collections import Counter as C2
cnt = C2(seg1)
import math
H = -sum(v/len(seg1)*math.log2(v/len(seg1)) for v in cnt.values())
print('seg1 entropy bits/byte:', round(H,2))
