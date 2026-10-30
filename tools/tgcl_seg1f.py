import struct, re, os
root = r'd:\新建文件夹\LightEncounters\Children of the Light\Levels'
d = open(os.path.join(root,'Dawn','Objects.level.bin'),'rb').read()
o1,o2,o3,o4,o5 = struct.unpack_from('<5I', d, 24)
seg1 = d[o1:o2]; seg3 = d[o3:o4]
# 8B 步长错。seg1 783 u32 = 可能是 (off,len) 交替但步长 8 从 off=0 开始才对：
# 头: 36515,0,7,17920,7,20,13636,27,61,30298,88,7,...
# 若条目 = (off,plen): (36515,0)='IfEnabled'; (7,17920)? off=7 plen=17920 不可能(len>off)
# 若条目 = (plen,off): (36515,7)? 36515 超界。 
# 头可能是表头: [n=36515?][0] 然后条目 (7,17920)(7,20)... 但 (7,17920) off=17920 plen=7 → seg3[17913:17920]='Npc_Mem'? 上面显示 'eEvent '
# 试 (plen, off): plen=7, off=17920 → prefix=seg3[17920-7:17920]... 同。
# 换思路: 条目 = (off, N)  其中名字 = seg3[off:off+N]（定长截断）: (7,17920) → seg3[7:14]:
print('seg3[7:14]:', seg3[7:14])
print('seg3[20:27]:', seg3[20:27])
print('seg3[27:27+13636?]:', seg3[27:40])
# (7,20): off=20 len=7 'toCurre' 不完整名。 
# 也许 seg1 783 u32 就是 783 个偏移（交错含义不同），两个相邻 u32 一个是 offset 一个是 count
# 头 36515 落在 seg3 → seg1[0] 也是 off。 (36515, 0, 7, 17920): (off=36515) 'IfEnabled'
# (off=7, ...) seg3[7:]='toCurrentTargetTransform...'! seg3 头部:
print('seg3[0:80]:', seg3[0:80])
# → off=7 起正好 'toCurrentTargetTransform'! 名=从 off 到 NUL: 'toCurrentTargetTransform' ✓✓
# 那 (17920)='Npc_MemoryPose' ✓ (20)='TargetTransform'? seg3[20:26]... 上面 seg3[20:27]='toCurre' 因为 20 在 'toCurrent' 内
# 所以 seg1 = 纯 u32 偏移表（含头 2 个：n=36515? 0=?）。 783 个偏移全部解名:
names=[]
for k in range(len(seg1)//4):
    off, = struct.unpack_from('<I', seg1, k*4)
    if off >= len(seg3): names.append(''); continue
    names.append(seg3[off:off+64].split(b'\x00')[0].decode('latin1'))
print(len(names))
print([n for n in names[:40]])
# 头 0 → 空。 36515 → 'IfEnabled' 是第一条。那 783 个名字是什么表？组件类名+键名混合？
print('sample names:', names[1:20])
