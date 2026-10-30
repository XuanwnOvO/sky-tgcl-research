import struct, re, math
# anchor 没找到因为缩放可能不同 (3.0,3.0 是另一条)。改用 quat 锚：找 4f 单位四元数窗口。
# 391B 模板逐 4B float 视图直接看：
seg = open(r'd:\新建文件夹\LightEncounters\Children of the Light\Levels\Dawn\Objects.level.bin','rb').read()[91988:]
starts = [m.start() for m in re.finditer(rb'BstNode_\d{9,10}\x00', seg)]
lens = [starts[i+1]-starts[i] for i in range(len(starts)-1)] + [len(seg)-starts[-1]]
i391 = next(i for i,L in enumerate(lens) if L==391)
rec = seg[starts[i391]:starts[i391]+391]
data = rec[19:-4]
n = len(data)//4
fs = struct.unpack_from(f'<{n}f', data, 0)
for r in range(0, n, 4):
    row = fs[r:r+4]
    print(f'{r*4:4d}: ' + ' '.join(f'{v:12.4f}' if abs(v)<1e8 else f'{v:12.3e}' for v in row))
# 尾部 12B 不是 4 对齐的再单列
rem = len(data)%4
print('rem', rem, struct.unpack_from(f'<{rem}B', data, n*4))
