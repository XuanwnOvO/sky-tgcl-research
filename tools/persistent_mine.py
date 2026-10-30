# -*- coding: utf-8 -*-
import os, re, collections
s = open(os.path.join('decompiled_lua', 'Resources', 'Persistent.lua'), encoding='utf-8', errors='replace').read()
kinds = collections.Counter(re.findall(r'file\("([^"]+/)?', s))
print('file() 引用目录分布:', kinds.most_common(25))
rt = collections.Counter(re.findall(r'resource\("(\w+)"\)', s))
print('resource 类型:', rt.most_common(20))
ne = [l.strip() for l in s.split('\n') if 'NETEASE' in l.upper()]
print('NETEASE 行数:', len(ne))
print(ne[:8])
bl = re.findall(r'bundle\w*\("([^"]+)"\)', s)
print('bundle 定义数:', len(bl), bl[:10])
# 子关卡来源确认: AllLevelList / level() 列表
ll = re.findall(r'level\("([^"]+)"', s)
print('Persistent 内 level() 数:', len(ll))
# 92KB 主体是什么
lines = s.split('\n')
print('总行数:', len(lines))
print('中部样例:', lines[len(lines)//2][:200])
