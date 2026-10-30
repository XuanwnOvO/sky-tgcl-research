import re

txt = open(r'd:\新建文件夹\LightEncounters\reg_all.txt', encoding='utf-8').read()
pairs = []
for ln in txt.split('\n'):
    m = re.match(r"call@([0-9a-f\-]+)\s+name='([^']*)'", ln)
    if m:
        addr = m.group(1).replace('-', '')
        pairs.append((addr, m.group(2)))

out = open(r'd:\新建文件夹\LightEncounters\reg_named.txt', 'w', encoding='utf-8')
out.write('total named: %d\n' % len(pairs))

# 分类
cats = {
    'RPC': [], 'Event': [], 'Barn': [], 'Resource': [], 'Request(无Event后缀)': [],
    'UI/Menu': [], '其他': []
}
for a, n in pairs:
    if 'Rpc' in n: cats['RPC'].append((a, n))
    elif n.endswith('Event'): cats['Event'].append((a, n))
    elif 'Barn' in n: cats['Barn'].append((a, n))
    elif 'Resource' in n: cats['Resource'].append((a, n))
    elif 'Request' in n: cats['Request(无Event后缀)'].append((a, n))
    elif 'Menu' in n or 'Ui' in n or 'UI' in n or 'Button' in n: cats['UI/Menu'].append((a, n))
    else: cats['其他'].append((a, n))

for c, lst in cats.items():
    out.write('\n######## %s: %d ########\n' % (c, len(lst)))
    for a, n in sorted(lst, key=lambda x: x[1]):
        out.write('%s  %s\n' % (a, n))

out.close()
print('ok', {c: len(l) for c, l in cats.items()})
