import struct, re
# 结构已明朗：记录 = BstNode_xxx\0 | [data...] | u32 seq（全局节点序号）
# len35 模板: 00 | u32 ptr?(0x2cf0,0xf34,0x1692 疑为 seg 内偏移/索引) | 00 | 01 | 4B hash?(9a 01 d7 6d) | 00 | seq
#   实际: 00 f0 2c 00 00 00 01 9a 01 d7 6d 00 → f0 2c 00 00=0x2cf0(11440) 序号类; 01; 9a 01 d7 6d=哈希/引用; 00
# len72: 01 | 3 floats (pos) | 00 00 00 00 | 4x3 floats? (quat+更多) | 00 00 00 00 | seq
# len391: 00 | 00000000 | 3f.. float pos? | 三元组+quat+scale(3x 0x4040=3.0?) | ... | seq
#   len391 明确有: pos(12B) | quat(16B: 00 00 80 3f 00 00 00 40 00 00 00 40 00..) | ff ff ff ff | u32 (591/200/655)
#   网格/材质参数一大块 + 尾部 "0a/06 00 00 00" 前有 u32 5 + 01/03 + 2 floats
# len51: 00 | ffffffff ffffffff | 00 | u32 0x2cf7 | 01 | ff ff ff ff | u32 0x40000000(2.0f!) | ff ff ff ff | seq
#   → ff ff ff ff = -1 引用哨兵
# 固定模板不是统一结构，但 len72 与 len391 是 transform 节点两种精度的模板。
# 结论层检验：把 72B 模板按 [u8 flag][12B pos][16B quat][12B scale][4B] 试试:
rec = bytes.fromhex('01'+'3011f64059fd05413411f640'+'00000000'+'1345483d0f0a16bfcc44113d80d84e3fd181a242'+'f2bf0a41e9a1c143'+'00000000')
import struct as s
flag = rec[0]
pos = s.unpack_from('<3f', rec, 1)
print('flag', flag, 'pos', pos)
off = 13
q = s.unpack_from('<4f', rec, off); print('q?', q); off+=16
v2 = s.unpack_from('<3f', rec, off); print('v2?', v2); off+=12
v3 = s.unpack_from('<2f', rec, off); print('v3?', v3)
# len72 全模板数值合理性打印
