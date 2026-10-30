import struct, re, math
# 72B 模板 98.9% 命中 → 结构实锤。现在攻 391B（最大模板 1029 条）:
# 391: name19 + data368 + seq4. 数据开头: 00 00000000 | 1f 2b 08 3f | 00000000 | d9 94 a3 3e | 00000000 | 22 36 0c bf | a8 21 75 41 | c2 6d 69 3f | 00000000 | 86 71 79 c1 | 33 89 06 c0 | a1 a4 cf 41 | 00000000 | 28 22 e3 43 | 82 f9 53 43 | 2c a3 77 c4 | 00 00 80 3f | 00 00 00 40 | 00 00 00 40 | 00000000 | ff ff ff ff | 59 02 00 00 ...
# 交替 float,0 结构! (f,0),(f,0),(f,0)... = 属性键值对? 6 对 float 后 quat-scale (1,3,3), u32 0, -1, u32 601(0x259)
# 猜: 391B = 属性对列表 [key u32? | float] × N + transform 尾块
# 数一下: data 368B。变换尾块从 '00 00 80 3f 00 00 00 40 00 00 00 40 00000000 ffffffff' 开始
# 之前 6 组 (float, u32 0): 1f2b083f=0.534, d994a33e=0.319, 22360cbf=-0.548, a8217541=15.32, c26d693f=0.913, 867179c1=-15.47, 338906c0=-2.10, a1a4cf41=25.9, 2822e343=455.2, 82f95343=3353.2, 2ca377c4=-977.9 → 11 floats 不是 6 组
# 直接输出 391B 前面为 (f,0) 交替多少个:
seg = open(r'd:\新建文件夹\LightEncounters\Children of the Light\Levels\Dawn\Objects.level.bin','rb').read()[91988:]
starts = [m.start() for m in re.finditer(rb'BstNode_\d{9,10}\x00', seg)]
lens = [starts[i+1]-starts[i] for i in range(len(starts)-1)] + [len(seg)-starts[-1]]
i391 = next(i for i,L in enumerate(lens) if L==391)
rec = seg[starts[i391]:starts[i391]+391]
data = rec[19:-4]
print('data len', len(data))
# 找 quat-scale 锚：连续 (1.0, 3.0, 3.0)
anchor = struct.pack('<3f', 1.0, 3.0, 3.0)
a = data.find(anchor)
print('anchor at', a)
# 锚前 16B 应是 quat（单位化验证）
if a>0:
    q = struct.unpack_from('<4f', data, a-16)
    print('quat before scale:', q, '|len|', math.sqrt(sum(x*x for x in q)))
    pos = struct.unpack_from('<3f', data, a-16-12-4)  # quat 前应有 u32 0 + pos
    print('pos guess:', pos)
# 锚后: u32 0, -1, u32 N, ... 数剩余字节
print('after anchor bytes:', len(data)-a-12)
tail = data[a+12:]
z, = struct.unpack_from('<I', tail, 0); m1, = struct.unpack_from('<i', tail, 4); n, = struct.unpack_from('<I', tail, 8)
print('tail: u32', z, 'i32', m1, 'u32', n)
# 头部: data[0]=flag, data[1..5] u32 0, 然后 float 对
hdr = struct.unpack_from('<I', data, 1)
print('hdr u32:', hdr)
# float 对区: 从 5 到 a-28
zone = data[5:a-28]
print('pre-transform zone len', len(zone))
fs = struct.unpack_from(f'<{len(zone)//4}f', zone, 0)
print('floats:', [round(f,3) for f in fs])
