import struct, re, os, math
from collections import defaultdict
root = r'd:\新建文件夹\LightEncounters\Children of the Light\Levels'
def load(lv):
    d = open(os.path.join(root, lv, 'Objects.level.bin'),'rb').read()
    c = struct.unpack_from('<4I', d, 8)
    offs = struct.unpack_from('<5I', d, 24)
    return d, offs, c
# 小模板族 26-71B 是最大宗。做逐字节特征提取定结构。拿 71B（与 72 差 1）与 51B（-1 结尾引用型）:
d, offs, c = load('Dawn')
seg3 = d[offs[2]:offs[3]]
seg = d[offs[3]:]
starts = [m.start() for m in re.finditer(rb'BstNode_\d{9,10}\x00', seg)]
lens = [starts[i+1]-starts[i] for i in range(len(starts)-1)] + [len(seg)-starts[-1]]
def show(L, n=3):
    k=0
    for i,Ln in enumerate(lens):
        if Ln==L:
            r = seg[starts[i]:starts[i]+Ln]
            print(f'--- {L}B:'); print(r.hex(' '))
            k+=1
            if k>=n: return
show(71); show(51); show(27); show(34)
