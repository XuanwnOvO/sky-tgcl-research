import struct, re, os
root = r'd:\新建文件夹\LightEncounters\Children of the Light\Levels'
d = open(os.path.join(root,'Dawn','Objects.level.bin'),'rb').read()
o1,o2,o3,o4,o5 = struct.unpack_from('<5I', d, 24)
seg1 = d[o1:o2]; seg3 = d[o3:o4]
# seg1 = [u32 len][u32 off] 对! (7,17920)(7,20)... len=7 → seg3[17920:17920+7]?
seg3v = lambda off, ln: seg3[off:off+ln]
for ln, off in [(7,17920),(7,20),(13636,27)]:
    print(ln, off, seg3v(off, ln)[:40])
# len=7 off=20 → seg3[20:27]:
print('seg3[20:27]:', seg3[20:27])
# 若 len 是字符串长: seg3[17920:17927]:
print('seg3[17920:17927]:', seg3[17920:17927])
# 对调: [off][len]? 头 36515,0 → off=36515 len=0? 'IfEnabled' 在 36515-9? seg3[36515:] len 473
# 更可能: seg1 = (hash/nameOff, something) 的哈希表。0x8ea3=36515: seg3[36515-9:36515]?
print('seg3[36506:36530]:', seg3[36506:36530])
# 好吧 36515 处是什么:
print('seg3[36515:36540]:', seg3[36515:36540])
