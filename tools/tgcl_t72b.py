import struct, re
# len72 更合理模板：flag(1) | pos 3f (12) | pad u32 (4) | quat 4f (16) | ... 再校验:
# 72B 数据总长 = 72-4(seq) = 68 → name 后 payload 68B: flag1 + 67
# 试着按: flag | pos(3f) | u32 0 | quat(4f, 后 3 分量? (0.0489,-0.586,0.0355)+w?) | 
#  72B 模板实测字段假设: [01][pos 3f][u32 0][quat 4f][3f][u32 0] = 1+12+4+16+12+4=49 ≠67
# 重新切 72B 原始: 01 | 30 11 f6 40 | 59 fd 05 41 | 34 11 f6 40 | 00 00 00 00 | 13 45 48 3d | 0f 0a 16 bf | cc 44 11 3d | 80 d8 4e 3f | d1 81 a2 42 | f2 bf 0a 41 | e9 a1 c1 43 | 00 00 00 00 | seq
#   = flag | pos(7.69,8.37,7.69) | u32 0 | quat(0.0489,-0.586,0.0355, 3.3e5?) 不对 0x424ea2d8=51.66 万?
#   80 d8 4e 3f = 0.819; d1 81 a2 42=81.25; f2 bf 0a 41=8.67; e9 a1 c1 43=387.26
# 交替假设: flag | pos(3f) | u32 0 | euler/quat 前 3f = (0.0489,-0.586,0.0355) w=? | scale? (0.819,81.25,8.67) | (387.26,0,0)?
# 更可能: quat = (0.0489,-0.586,0.0355,0.819)! → 0x3f4ed880=0.8192 ✓ 单位四元数! 
# 然后 (81.25,8.67,387.26) = 第二位置/worldPos? 00 00 00 00 尾
# 所以 len72: flag | pos(3f) | u32 0 | quat(4f) | pos2(3f) | u32 0 | seq = 1+12+4+16+12+4+4=53? name 后 68B 才对——上面漏算:
# 1+12+4+16+12+4 = 49, +4 seq = 53, +19 name = 72 ✓✓✓ 完全吻合!
# 验证所有 72B 记录：flag∈{0,1}, pos 有限 float, quat 单位长度
seg = open(r'd:\新建文件夹\LightEncounters\Children of the Light\Levels\Dawn\Objects.level.bin','rb').read()[91988:]
starts = [m.start() for m in re.finditer(rb'BstNode_\d{9,10}\x00', seg)]
lens = [starts[i+1]-starts[i] for i in range(len(starts)-1)] + [len(seg)-starts[-1]]
import math
ok=bad=0
for i,L in enumerate(lens):
    if L==72:
        rec = seg[starts[i]:starts[i]+L]
        flag = rec[19]
        pos = struct.unpack_from('<3f', rec, 20)
        z, = struct.unpack_from('<I', rec, 32)
        quat = struct.unpack_from('<4f', rec, 36)
        pos2 = struct.unpack_from('<3f', rec, 52)
        m = math.sqrt(sum(q*q for q in quat))
        if flag in (0,1) and m>0.9 and m<1.1 and all(abs(v)<1e6 for v in pos): ok+=1
        else: bad+=1
print('len72 as [flag|pos|0|quat|pos2|0|seq]:', ok, 'ok /', bad, 'bad')
# 51B 模板: 00 | ff*8 | 00 | u32 idx | 01 | ff*4 | float(2.0) | ff*4 | seq = 1+8+1+4+1+4+4+4+4=31? 51-19=32-4=28 数据? 
# 51: name19 + 28 data + 4 seq.  data: 00 ff ff ff ff ff ff ff ff 00 f7 2c 00 00 01 00 ff ff ff ff 00 00 00 40 ff ff ff ff
#   = u8 0 | i32 -1 | i64 -1 | u8 0 | u32 0x2cf7(11511) | u8 1 | i32 -1 | float 2.0 | i32 -1
#   11511 = c3=14651? no. 0x2cf7 正好是 Dawn 头 c 数值域。它是 引用另一节点/资源 ID
# 输出 72B 模板的一段汇总统计完事
