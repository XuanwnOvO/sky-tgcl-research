import re, sys
data = open(r'D:\新建文件夹\cfxfmpk\libGame.so','rb').read()
strs = [s.decode() for s in re.findall(rb'[\x20-\x7e]{5,80}', data)]
keys = ['engine', 'gameworld', 'skynet', 'debughud', 'eventbarn', 'avatarbarn', 'tweak', 'hotal', 'loade']
hits = {}
for s in strs:
    ls = s.lower()
    for k in keys:
        if k in ls:
            hits.setdefault(k, []).append(s)
            break
with open('lua_bind_hits.txt', 'w', encoding='utf-8') as f:
    for k, v in hits.items():
        f.write(f'== {k} ({len(v)})\n')
        for s in v[:200]:
            f.write(s + '\n')
print('done', {k: len(v) for k, v in hits.items()})
