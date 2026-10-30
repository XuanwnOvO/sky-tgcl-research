import struct, re, os
root = r'd:\新建文件夹\LightEncounters\Children of the Light\Levels'
d = open(os.path.join(root,'Dawn','Objects.level.bin'),'rb').read()
o1,o2,o3,o4,o5 = struct.unpack_from('<5I', d, 24)
seg1 = d[o1:o2]; seg3 = d[o3:o4]
# 明确了：seg1 是 (u32, u32) 交替 = (offA, offB)，其中名字是**共享后缀**结构:
# 'toCurrentTargetTransform' = off 20+? seg3[20]='toCurre...' 但 off 对 (7,20): seg3[7..20)='eventN\0gotoCurre'
# 真相: seg1 = [u32 x][u32 y] 对，x 是名字 off（完整 NUL 结尾名），y 是下一相关 off 或哈希。
# 看 (off=36515→'IfEnabled', 0), (off=7→''(seg3[7]=\0?), 17920)...
# seg3[7]=0x00 → 名空。但 seg3[20]='toCurre' 是 'gotoCurrentTargetTransform' 的中段 → off 指到串中间 = 子串表！
# 结论修正: seg1 = 压缩字符串表（串共享去重，条目指向子串）。真正名字 = seg2 schema 的 b 字段已完美解析（3239 键全名）。
# seg1 的角色: 783 项指向这些键的中缀/后缀 → 去重字符串池的索引块。
# 够了——不需要更多。TGCL 全部 4 段语义已定。最终验证: 写一个最小完整解析器验证全流程:
d2 = open(os.path.join(root,'DuskGraveyard','Objects.level.bin'),'rb').read()
o1b,o2b,o3b,o4b,o5b = struct.unpack_from('<5I', d2, 24)
s2b = d2[o2b:o3b]; s3b = d2[o3b:o4b]
n2 = len(s2b)//16
rows=[]
for k in range(n2):
    a,b,c,e = struct.unpack_from('<4I', s2b, k*16)
    nm = s3b[b:b+48].split(b'\x00')[0].decode('latin1') if b < len(s3b) else '?'
    rows.append((k,a,c,nm))
from collections import Counter
print('DuskGraveyard schema:', len(rows), 'types:', Counter(r[2] for r in rows))
print('sample:', rows[:8])
