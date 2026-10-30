import json, re
# 最终合并：局部类型消歧 mixed + 枚举识别 + 方法参数 -> 最终文档与数据
ts = json.load(open(r'd:\新建文件夹\LightEncounters\type_scan.json'))
ls = json.load(open(r'd:\新建文件夹\LightEncounters\local_type_scan.json'))
ag = json.load(open(r'd:\新建文件夹\LightEncounters\argn_scan.json'))

WN = {'B':'byte/bool','H':'short','W':'int32','X':'ptr/int64','S':'float','D':'double','Q':'vec4/16B'}

def infer(widths):
    tot = sum(widths.values())
    if not tot: return None
    w, c = max(widths.items(), key=lambda kv: kv[1])
    if tot and c / tot >= 0.6: return WN.get(w, w)
    return None

# 读字段表
tools = []
cur = None
for l in open(r'd:\新建文件夹\LightEncounters\fields_clean.txt', encoding='utf-8'):
    l = l.rstrip('\n')
    m = re.match(r'^### (0x[0-9a-f]+) (\S+)', l)
    if m:
        cur = (m.group(1), m.group(2), [])
        tools.append(cur)
    elif l.startswith('  +') and cur:
        p = l[3:].split(None, 1)
        cur[2].append((int(p[0]), p[1].strip() if len(p) > 1 else '?'))

# 方法名表（调用点 -> 名字）
meth = {}
for l in open(r'd:\新建文件夹\LightEncounters\tool_registry_scan_full.txt'):
    p = l.rstrip('\n').split('\t')
    if len(p) >= 3: meth[p[0].lower()] = p[2]

resolved = 0; typed = 0; enum_cnt = 0
out = open(r'd:\新建文件夹\LightEncounters\fields_typed.txt', 'w', encoding='utf-8')
for site, tool, fields in tools:
    out.write('### %s %s\n' % (site, tool))
    for o, n in sorted(fields):
        t = '?'
        if re.match(r'^k[A-Z]', n):
            t = 'enum-const'; enum_cnt += 1
        else:
            # 先试局部
            w = ls.get('%s|%d' % (site, o))
            t = infer(w) if w else None
            if not t:
                t = infer(ts.get(str(o), {}))
            if t: typed += 1
            else: t = '?'
        out.write('  +%-6d %-10s %s\n' % (o, t, n))
out.close()

# 方法参数表
ma = open(r'd:\新建文件夹\LightEncounters\methods_args.txt', 'w', encoding='utf-8')
for k, v in sorted(ag.items(), key=lambda kv: int(kv[0], 16)):
    ma.write('%s\t%s\t%d\tsub_%s\n' % (k, meth.get(k, '?'), v['args'], v['fn']))
ma.close()
print('fields typed:', typed, '/', sum(len(f) for _,_,f in tools), ' enum:', enum_cnt, ' methods w/args:', len(ag))
