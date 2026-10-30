import re, json
from collections import Counter

# 读取原始扫描
tools = []   # (site, tool_name, [(imm, field)])
cur = None
for l in open(r'd:\新建文件夹\LightEncounters\fields_scan.txt', encoding='utf-8'):
    l = l.rstrip('\n')
    m = re.match(r'^### (0x[0-9a-f]+) (\S+)\s+\((\d+) fields\)', l)
    if m:
        cur = (m.group(1), m.group(2), [])
        tools.append(cur)
    elif l.startswith('  +') and cur:
        off, name = l[3:].split('\t')[:2]
        cur[2].append((int(off), name))

# 过滤规则：
# 1. 偏移必须是合理结构体偏移: 0 < off <= 65536，且通常 4/8 对齐（放宽到任意，但排除超大值如 1e9）
# 2. 名字必须是合法标识符（snake_case 或 camelCase），排除 URL/格式串/哈希/带空格
ident = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
reserved_hint = (' ', '%', '/', ':', 'http', '\\', '"', "'", '.')

def is_field(off, name):
    if not (0 < off <= 65536): return False
    if not ident.match(name): return False
    if any(c in name for c in reserved_hint): return False
    # 排除明显枚举值/资源路径片段
    if name.startswith('kABTesting'): return False
    return True

out_tools = []
total = 0
noise = Counter()
for site, tool, fields in tools:
    keep = [(o, n) for o, n in fields if is_field(o, n)]
    for o, n in fields:
        if not is_field(o, n):
            if o > 65536: noise['imm too big'] += 1
            elif not ident.match(n): noise['not ident'] += 1
            else: noise['other'] += 1
    if keep:
        out_tools.append((site, tool, keep))
        total += len(keep)

print('tools kept:', len(out_tools), '/', len(tools))
print('fields kept:', total, '/', sum(len(f) for _,_,f in tools))
print('noise:', dict(noise))

with open(r'd:\新建文件夹\LightEncounters\fields_clean.txt', 'w', encoding='utf-8') as f:
    for site, tool, fields in out_tools:
        f.write('### %s %s  (%d fields)\n' % (site, tool, len(fields)))
        for o, n in sorted(fields):
            f.write('  +%-6d %s\n' % (o, n))
print('sample:')
for site, tool, fields in out_tools[:3]:
    print(site, tool, fields[:8])
