import struct
# 解 seg4 节点记录：name NUL | 之后 u32 序号结构。逐记录推进需要知道变长属性块大小。
# 策略：利用记录间的索引连续性。记录头假定: name\0 | u32 idx | u32 ? | u16 depth | i32 parent | u32 next
# 第一条: BstNode_2310602845\0 然后 00 ed 2c 00 00 | 00 00 00 00 | 01 00 | ff ff ff ff | ee 2c 00 00 | 01 00 00 00
# 注意 "01 00 00 00" 后直接跟下一个名字 → 说明第一条的属性块为 0 或结构不同。
# 第二条: BstNode_2819097706\0 01 00 00 d6 1e 00 00 00 6a 04 08 a8 | MemAp18Misfit5\0...
# 猜：name\0 | u32 idx | [若 flag 字节非0: 变长 payload] ？
# 另一种切法：name\0 | u32 fieldA | u8 flag | payload...

def recs(d, start, end):
    i = start
    out=[]
    while i < end:
        j = d.find(b'\x00', i)
        if j<0 or j-i>64: break
        name = d[i:j]
        if not name.startswith(b'BstNode'): 
            # prefab 名？跳过看下一段
            out.append(('NAME?', name.decode('latin1'), i)); i = j+1; continue
        p = j+1
        idx, = struct.unpack_from('<I', d, p)
        out.append(('BST', name.decode(), idx, i))
        i = p+4
    return out

d = open(r'd:\新建文件夹\LightEncounters\Children of the Light\Levels\Dawn\Objects.level.bin','rb').read()
o4 = 91988; o5 = len(d)
r = recs(d, o4+4, min(o4+2000, o5))
for x in r[:30]: print(x)
