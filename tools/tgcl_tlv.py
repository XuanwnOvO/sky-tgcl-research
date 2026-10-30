import struct, re, os
root = r'd:\新建文件夹\LightEncounters\Children of the Light\Levels'
d = open(os.path.join(root,'Dawn','Objects.level.bin'),'rb').read()
o3, o4 = struct.unpack_from('<2I', d, 32)
keys = [k for k in d[o3:o4].split(b'\x00') if k]
seg = d[o4:]
starts = [m.start() for m in re.finditer(rb'BstNode_\d{9,10}\x00', seg)]
lens = [starts[i+1]-starts[i] for i in range(len(starts)-1)] + [len(seg)-starts[-1]]
# 188..264 是字节流不是 u32: 0x80000030,0x3f,0x4ccccd00... 错位了。
# 从 188 起按字节看: 30 00 00 00 80 | 3f 00 00 00 00 | e6 66 66 3f | 00 00 00 3e ...
# → 这是变长 TLV! [key LEB][tag?][value] 流。sample: 80 3f 后 = 1.0f 尾部 → value 是 f32 嵌在流中
# 猜 TLV: [u8/leb key][u8 type][val]? 解: 从 data184 起:
i391 = next(i for i,L in enumerate(lens) if L==391)
data = seg[starts[i391]:starts[i391]+lens[i391]][19:-4]
print('bytes 180..280:')
print(data[180:280].hex(' '))
# 也可看 391B 完整字节找 TLV 边界标记: 头 64B 是纯 float 块(无 0x80 高位字节?)
print('bytes 0..80:'); print(data[0:80].hex(' '))
print('bytes 264..368:'); print(data[264:].hex(' '))
