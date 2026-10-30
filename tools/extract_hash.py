import re

# 提取全部 hex 字段名及其所属类
lines = open(r'd:\新建文件夹\LightEncounters\dump.cs', encoding='utf-8').read().split('\n')
out = []
cls = None
for ln in lines:
    m = re.match(r'internal class (\w+) :  // 0x([0-9a-f]+)', ln)
    if m:
        cls = (m.group(1), m.group(2))
    m2 = re.match(r'\tpublic \S+\?? ([0-9A-F]{16}); // (0x[0-9a-f]+)', ln)
    if m2 and cls:
        out.append((cls[0], cls[1], m2.group(1), m2.group(2)))

print('total hex fields:', len(out))
classes = {}
for c, cra, name, off in out:
    classes.setdefault(c, (cra, []))[1].append((name, off))
for c, (cra, flds) in sorted(classes.items()):
    print(c, cra, len(flds), flds[0])
