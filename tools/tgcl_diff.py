import re, struct
def parse(path):
    d = open(path,'rb').read()
    assert d[:4]==b'TGCL', d[:8]
    ver, = struct.unpack_from('<I', d, 4)
    c = struct.unpack_from('<4I', d, 8)
    off = struct.unpack_from('<5I', d, 24)
    return ver, c, off, d

a = parse(r'd:\新建文件夹\LightEncounters\Children of the Light\Levels\Dawn\Objects.level.bin')
b = parse(r'd:\新建文件夹\LightEncounters\Children of the Light\Levels\DuskGraveyard\Objects.level.bin')
print('Dawn ver', a[0], 'counts', a[1], 'offs', a[2], 'size', len(a[3]))
print('Isle ver', b[0], 'counts', b[1], 'offs', b[2], 'size', len(b[3]))

# 节点区起点 off[3]；先解头部已知段，然后逐记录扫
def walk(d, node_off, filesize):
    i = node_off
    recs=[]
    n=0
    while i < filesize - 20 and n < 20000:
        # name = NUL-terminated
        j = d.find(b'\x00', i)
        if j < 0 or j - i > 80: break
        name = d[i:j]
        if not name or not all(32 <= ch < 127 for ch in name): break
        p = j+1
        selfIdx, u, = struct.unpack_from('<II', d, p)
        depth, = struct.unpack_from('<H', d, p+8)
        parent, = struct.unpack_from('<i', d, p+10)
        nxt, = struct.unpack_from('<I', d, p+14)
        recs.append((name.decode(), selfIdx, depth, parent, nxt, i, p+18))
        i = p+18 + 0  # 属性块长度未知——先统计同 depth 下记录间隔
        n+=1
        # 猜测下一记录位置：找下一个可打印名
    return recs

ra = walk(a[3], a[2][3], len(a[3]))
print('Dawn records head-parsed:', len(ra))
for r in ra[:8]: print(r)
