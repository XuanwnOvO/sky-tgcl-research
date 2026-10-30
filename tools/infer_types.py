import json, re
# join 字段表 与 宽度统计 -> 推断类型
types = json.load(open(r'd:\新建文件夹\LightEncounters\type_scan.json'))

def infer(widths):
    total = sum(widths.values())
    # 取占主导的宽度（>=60%）
    w, c = max(widths.items(), key=lambda kv: kv[1])
    if c / total < 0.6: return 'mixed?' + ','.join('%s%d' % kv for kv in sorted(widths.items()))
    return {'B': 'byte/bool', 'H': 'short', 'W': 'int32/uint32/float-bits',
            'X': 'ptr/int64', 'S': 'float', 'D': 'double', 'Q': 'vec4/16B'}.get(w, w)

# 读字段表（clean）
tools = []
cur = None
for l in open(r'd:\新建文件夹\LightEncounters\fields_clean.txt', encoding='utf-8'):
    l = l.rstrip('\n')
    m = re.match(r'^### (0x[0-9a-f]+) (\S+)\s+\((\d+) fields\)', l)
    if m:
        cur = (m.group(1), m.group(2), [])
        tools.append(cur)
    elif l.startswith('  +') and cur:
        off, name = l[3:].split(None, 1)
        cur[2].append((int(off), name.strip()))

typed = 0
out = open(r'd:\新建文件夹\LightEncounters\fields_typed.txt', 'w', encoding='utf-8')
for site, tool, fields in tools:
    out.write('### %s %s\n' % (site, tool))
    for o, n in sorted(fields):
        w = types.get(str(o))
        t = infer(w) if w else '?'
        if w: typed += 1
        out.write('  +%-6d %-10s %s\n' % (o, t, n))
out.close()
print('fields typed:', typed, '/', sum(len(f) for _,_,f in tools))
