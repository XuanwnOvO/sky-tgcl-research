import re
# 按 dnSpy 反编译格式生成（参考 com.je.skgame...cs）：
# 类: "internal class Name : <基类>" + "// Fields" + "// Methods"
# 字段: "public <Type> name; // 0x偏移"
# 枚举: "public const EnumName K = 值; // 0x0" + value__
# 方法: "public <Ret> Name(args); // 0xFnAddr"
CS = {'byte/bool':'System.Byte','short':'System.Int16','int32':'System.Int32',
      'ptr/int64':'System.Int64','float':'System.Single','double':'System.Double',
      'vec4/16B':'UnityEngine.Vector4'}
TN = {'byte/bool':'bool','short':'short','int32':'int','ptr/int64':'long',
      'float':'float','double':'double','vec4/16B':'Vector4'}

def sanitize(n):
    n = re.sub(r'[^A-Za-z0-9_]', '_', n)
    if not n or n[0].isdigit(): n = '_' + n
    return n

# 字段表
ts = {}; order = []
for l in open(r'd:\新建文件夹\LightEncounters\fields_typed.txt', encoding='utf-8'):
    l = l.rstrip('\n')
    m = re.match(r'^### (0x[0-9a-f]+) (\S+)', l)
    if m:
        order.append((m.group(1), m.group(2)))
        ts[m.group(1)] = []
    elif l.startswith('  +') and order:
        p = l[3:].split(None, 2)
        # fields_typed.txt 行: +<off十进制> <type> <name>
        off = int(p[0], 10)
        typ = p[1] if len(p) > 1 else '?'
        nam = p[2].strip() if len(p) > 2 else p[1]
        ts[order[-1][0]].append((off, nam, typ))

# 方法表
meth = {}
for l in open(r'd:\新建文件夹\LightEncounters\methods_args.txt', encoding='utf-8'):
    p = l.rstrip('\n').split('\t')
    if len(p) >= 4: meth[p[0]] = (p[1], int(p[2]), p[3])

# 全部注册点
all_sites = []
for l in open(r'd:\新建文件夹\LightEncounters\tool_registry_scan_full.txt', encoding='utf-8'):
    p = l.rstrip('\n').split('\t')
    if len(p) >= 3: all_sites.append((p[0], p[2]))

out = []
out.append('// libgame.so (TGC engine, Sky 光·遇 Android) - 静态逆向 dump')
out.append('// 格式仿 dnSpy C# 反编译；类名后 // 注册点RVA；字段后 // 0x对象内偏移；方法后 // 0x函数RVA')
out.append('// 类型为访问宽度推断，"var?" 表示未定')
out.append('')

field_sites = set(ts.keys())
done = set()
def emit(site, name):
    if site in done: return
    done.add(site)
    out.append('// libgame.so')
    m = meth.get(site)
    fields = sorted(ts.get(site, []))
    is_enum_only = fields and all(t == 'enum-const' for _, _, t in fields)
    kw = 'enum' if is_enum_only else 'class'
    out.append('internal %s %s :  // %s' % (kw, sanitize(name), site))
    out.append('{')
    if fields:
        out.append('\t// Fields')
        if is_enum_only:
            out.append('\tpublic System.Int32 value__; // 0x10')
            for o, n, t in fields:
                out.append('\tpublic const %s %s = %d; // 0x0' % (sanitize(name), n, o))
        else:
            for o, n, t in fields:
                tn = TN.get(t, 'var?')
                out.append('\tpublic %s %s; // 0x%x' % (tn, n, o))
    if m:
        if fields: out.append('')
        out.append('\t// Methods')
        args = ', '.join('System.Int64 arg%d' % i for i in range(max(0, m[1] - 1)))
        out.append('\tpublic System.Void %s(%s); // 0x%s' % (m[0] or sanitize(name), args, m[2].replace('sub_', '')))
    out.append('}')
    out.append('')

# 先输出有字段的（按注册点顺序），再输出其余
for site, name in all_sites:
    if site in field_sites: emit(site, name)
for site, name in all_sites:
    emit(site, name)

open(r'd:\新建文件夹\LightEncounters\dump.cs', 'w', encoding='utf-8').write('\n'.join(out))
print('written %d lines, %d classes' % (len(out), len(done)))
