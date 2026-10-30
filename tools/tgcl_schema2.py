import struct, re, os
from collections import Counter
root = r'd:\新建文件夹\LightEncounters\Children of the Light\Levels'
d = open(os.path.join(root,'Dawn','Objects.level.bin'),'rb').read()
o1,o2,o3,o4,o5 = struct.unpack_from('<5I', d, 24)
seg2 = d[o2:o3]; seg3 = d[o3:o4]
# schema 全表导出: c 字段 = 类型枚举
types = Counter()
rows=[]
n = len(seg2)//16
for k in range(n):
    a,b,c,e = struct.unpack_from('<4I', seg2, k*16)
    nm = seg3[b:b+48].split(b'\x00')[0].decode('latin1') if b < len(seg3) else '?'
    types[c]+=1
    rows.append((k,a,c,e,nm))
print('c(type) 分布:', types.most_common())
out = open(r'd:\新建文件夹\LightEncounters\tgcl_schema.txt','w',encoding='utf-8')
for k,a,c,e,nm in rows:
    out.write(f'{k}\t{a}\t{c}\t{e}\t{nm}\n')
out.close()
print('saved tgcl_schema.txt rows', n)
# 抽样看 type=4 (string?) 名字特征
s4 = [r for r in rows if r[2]==4][:15]
print('type4:', [r[4] for r in s4])
s1 = [r for r in rows if r[2]==1][:15]
print('type1:', [r[4] for r in s1])
s0 = [r for r in rows if r[2]==0][:15]
print('type0:', [r[4] for r in s0])
