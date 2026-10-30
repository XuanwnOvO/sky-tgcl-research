# -*- coding: utf-8 -*-
import re, collections

lines = [l.rstrip('\n') for l in open('tool_registry_scan_full.txt', encoding='utf-8', errors='replace') if l.strip()]
recs = []
for l in lines:
    parts = l.split('\t')
    if len(parts) >= 3:
        recs.append((parts[0].strip(), parts[2].strip(), parts[1].strip()))

# 分类规则：按前缀分组
RULES = [
    ('BT_',        '行为树（BT_*）'),
    ('AvatarBarn', 'Avatar / AvatarBarn'),
    ('Avatar',     'Avatar / AvatarBarn'),
    ('Account',    'Account 账号系统'),
    ('Camera',     'Camera 相机系统'),
    ('Quest',      'Quest 任务系统'),
    ('Social',     'Social 社交系统'),
    ('Npc_',       'NPC 系统（Npc_*）'),
    ('Rpc',        'RPC 网络调用'),
    ('Barn',       'Barn 管理器'),
    ('Sky',        'Sky* 游戏对象'),
    ('Level',      'Level 关卡系统'),
    ('Menu',       'Menu 菜单/UI'),
    ('Music',      'Music 音乐系统'),
    ('Audio',      'Audio 音频'),
    ('Cloud',      '云音乐 / 网易模块'),
    ('Lua',        'Lua 脚本'),
    ('lua_',       'Lua 脚本'),
    ('Vfs',        'Vfs 文件系统'),
    ('Job',        'Job 作业系统'),
    ('Heap',       'Heap 内存'),
    ('Shader',     'Shader 渲染'),
    ('Render',     '渲染（Render*）'),
    ('Module',     'Module 模块'),
    ('Network',    'Network 网络'),
    ('Net',        'Net 网络'),
    ('Item',       'Item 物品'),
    ('Map',        'Map 地图'),
    ('Player',     'Player 玩家'),
    ('Entity',     'Entity 实体'),
    ('System',     'System 系统'),
]

groups = collections.OrderedDict()
other = []
empty = []
for addr, name, kind in recs:
    if not name:
        empty.append(addr)
        continue
    entry = (addr, name, kind)
    for p, g in RULES:
        if name.startswith(p):
            groups.setdefault(g, []).append(entry)
            break
    else:
        # 后缀二次归类
        if name.endswith('Barn'):
            groups.setdefault('Barn 管理器', []).append(entry)
        elif 'RequestEvent' in name or name.endswith('Request'):
            groups.setdefault('服务器请求事件（*RequestEvent）', []).append(entry)
        elif 'Rpc' in name or name.endswith('Rpc'):
            groups.setdefault('RPC 网络调用', []).append(entry)
        elif name.endswith('Event'):
            groups.setdefault('事件（*Event）', []).append(entry)
        elif 'Menu' in name or 'Widget' in name or 'UI' in name:
            groups.setdefault('Menu 菜单/UI', []).append(entry)
        elif 'Editor' in name:
            groups.setdefault('Editor 编辑器', []).append(entry)
        else:
            groups.setdefault('游戏玩法对象 / 活动 / 节点', []).append(entry)

out = open('光遇引擎类与方法清单.md', 'w', encoding='utf-8')
w = out.write
w('# 光·遇 引擎类与方法清单（工具注册表 dump）\n\n')
w('> 来源：对 TGC 自研引擎 so 的工具注册系统批量扫描（静态 dump）。\n')
w('> 注册函数：`sub_3361078(desc, name, fn)`，全 so 共 %d 个调用点：静态字符串 %d（含寄存器中转），运行时构造 %d（XOR 加密/拼接，已忽略）。\n' % (len(recs), len(recs) - len(empty), len(empty)))
w('> 每条记录的"调用点地址"是该工具类的注册代码所在位置（so 内偏移，加基址即运行时地址），可作为逆向锚点。\n')
w('> 本文件即该引擎最接近 Unity dump.cs 的等价物。\n\n')

w('## 总览\n\n| 分组 | 数量 |\n|---|---|\n')
for g, lst in sorted(groups.items(), key=lambda kv: -len(kv[1])):
    w('| %s | %d |\n' % (g, len(lst)))
w('| 其他（未归类） | %d |\n\n' % len(other))

for g, lst in sorted(groups.items(), key=lambda kv: -len(kv[1])):
    w('## %s（%d）\n\n| 调用点地址 | 注册名 | 提取方式 |\n|---|---|---|\n' % (g, len(lst)))
    for addr, name, kind in lst:
        w('| %s | %s | %s |\n' % (addr, name, '直取' if kind == 'STATIC' else '寄存器中转'))
    w('\n')

w('## 其他（未归类，%d）\n\n| 调用点地址 | 注册名 |\n|---|---|\n' % len(other))
for addr, name in other:
    w('| %s | %s |\n' % (addr, name))
w('\n')

if empty:
    w('## 运行时构造名字的调用点（%d，XOR 加密/拼接，静态无法直接提取）\n\n' % len(empty))
    w(', '.join(empty))
    w('\n')

out.close()
print('done. groups:', {g: len(v) for g, v in groups.items()})
print('other:', len(other), 'empty:', len(empty))
