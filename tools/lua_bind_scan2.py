import re
data = open(r'd:\新建文件夹\LightEncounters\bootloader\libBootloader.so', 'rb').read()
strs = set(re.findall(rb'[\x20-\x7e]{4,100}', data))
print('total strings:', len(strs))
# 已确认存在的绑定名 —— 找它们同属一张表的“邻居”
anchors = ['skyNetClient', 'eventBarn', 'debugHud', 'avatarBarn', 'SendCommandResponse', 'SendCommandResponseJson']
anchor_set = set(strs)
# 对每个锚，输出所有字符串，便于人工看注册表邻居
out = open(r'd:\新建文件夹\LightEncounters\lua_bind_full.txt', 'w', encoding='utf-8')
out.write('== ALL strings sorted ==\n')
# 打印锚点相邻的字符串（按排序近似）
sl = sorted(strs)
for a in anchors:
    ab = a.encode()
    idx = next((i for i, s in enumerate(sl) if s == ab or ab in s), None)
    if idx is None:
        out.write(f'-- {a}: NOT FOUND\n'); continue
    lo, hi = max(0, idx - 60), min(len(sl), idx + 60)
    out.write(f'\n== {a} (idx {idx}) neighbors ==\n')
    for s in sl[lo:hi]:
        out.write(s.decode() + '\n')
out.close()
print('done')
