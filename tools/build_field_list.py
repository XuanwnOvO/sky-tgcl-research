import re
# 生成带类型列的《光遇引擎字段清单.md》（覆盖旧版，保留头部说明并扩展）
tools = []
cur = None
for l in open(r'd:\新建文件夹\LightEncounters\fields_typed.txt', encoding='utf-8'):
    l = l.rstrip('\n')
    m = re.match(r'^### (0x[0-9a-f]+) (\S+)', l)
    if m:
        cur = (m.group(1), m.group(2), [])
        tools.append(cur)
    elif l.startswith('  +') and cur:
        p = l[3:].split(None, 2)
        cur[2].append((int(p[0]), p[1] if len(p) > 1 else '?', p[2] if len(p) > 2 else ''))

lines = [
    '# 光·遇 引擎字段清单（属性注册 + 类型推断 dump）',
    '',
    '> 来源：工具注册 desc 结构体中的字段表。每个工具（类）注册时在 desc 里填入',
    '> `{int offset/ID, const char* name}` 对（指令模式 `MOV Wn,#imm` + `ADRL Xm,aStr` + `STP`）。',
    '> **类型列**来自全 .text 段内存访问宽度统计（LDRB=byte、LDR W=int32、LDR X=ptr/int64、',
    '> LDR S=float、LDR D=double、LDR Q=vec4/16B），按"同偏移所有访问的主导宽度（≥60%）"推断。',
    '> 与《光遇引擎类与方法清单.md》通过工具注册名关联。',
    '',
    '> **使用注意**：',
    '> 1. 偏移语义分两档——**小值（≤ 数千）大概率是对象实例内成员偏移**，可直接用于内存读写（GG）；',
    '>    +1/+2/+3/+4 这类极小值多为枚举常量（k*State_*）或标志，不是偏移（其"类型"无意义）。',
    '> 2. 类型按**全局同偏移**统计——不同类共用同一偏移时会互相污染（显示 mixed）。',
    '>    显示 `float`/`ptr/int64`/`byte/bool` 的为单一宽度主导，可信；',
    '>    `mixed?B...Q...S...` 表示该偏移被多种宽度的类共用，需实测或回 IDA 复核。',
    '> 3. 扫描窗口是"上一个调用点 → 本调用点"，超长初始化基本块内可能混入邻近工具的字段，',
    '>    与工具名不符的条目需回 IDA 复核。',
    '> 4. **AvatarBarn / 部分 Barn 管理器没有字段注册**（desc 为空）——槽布局见',
    '>    《AvatarBarn全体玩家列表指南.md》（63 槽 × 69008B）。字段清单与槽位指南互补。',
    '',
    '## 总览',
    '',
    '- 工具（类）含字段注册：%d 个' % len(tools),
    '- 字段总数：%d 个' % sum(len(f) for _, _, f in tools),
    '- 已推断类型（单一宽度主导）：%d 个' % sum(1 for _, _, fs in tools for _, t, _ in fs if t not in ('?', 'enum-const')),
    '- 枚举常量字段（k* 前缀，非偏移）：%d 个' % sum(1 for _, _, fs in tools for _, t, _ in fs if t == 'enum-const'),
    '- 已解析方法 fn + 参数个数：%d 个（见 methods_args.txt）' % 1339,
    '',
]
n = 0
for site, tool, fields in tools:
    lines.append('## %s（%s）' % (tool, site))
    lines.append('')
    lines.append('| 偏移 | 推断类型 | 字段名 |')
    lines.append('|---|---|---|')
    for o, t, name in sorted(fields):
        lines.append('| +%-6d | %s | %s |' % (o, t, name))
    lines.append('')
open(r'd:\新建文件夹\LightEncounters\光遇引擎字段清单.md', 'w', encoding='utf-8').write('\n'.join(lines))
print('written, tools:', len(tools))
