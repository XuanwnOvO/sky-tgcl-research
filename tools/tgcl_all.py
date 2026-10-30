import struct, re, math
# 收尾验证：35B/42B 模板字段未完全定（A 混有非指针值 → 有些 35B 其实是别的模板混入长度巧合）
# 用模板共同点收口：所有记录尾部 4B 在 0..5000 小值域（节点序/子链），记录定界= BstNode_ 锚定 100% 可行。
# 产出最终汇总 + 全关卡批量统计（所有 118 个 Objects.level.bin 的节点数/大小）
import os
root = r'd:\新建文件夹\LightEncounters\Children of the Light\Levels'
rows=[]
for lv in sorted(os.listdir(root)):
    p = os.path.join(root, lv, 'Objects.level.bin')
    if not os.path.exists(p): continue
    d = open(p,'rb').read()
    if d[:4]!=b'TGCL': rows.append((lv,'NO TGCL',0,0)); continue
    c = struct.unpack_from('<4I', d, 8)
    offs = struct.unpack_from('<5I', d, 24)
    n = len(re.findall(rb'BstNode_\d{9,10}\x00', d[offs[3]:]))
    rows.append((lv, len(d), n, c))
print(f'{"level":40s} {"size":>9s} {"nodes":>6s} counts')
for lv,sz,n,c in rows:
    print(f'{lv:40s} {sz:9d} {n:6d} {c}')
print('total levels:', len(rows), 'total nodes:', sum(r[2] for r in rows if isinstance(r[2],int)))
