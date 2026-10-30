import struct, re, os, math
from collections import Counter, defaultdict
root = r'd:\新建文件夹\LightEncounters\Children of the Light\Levels'

def load(lv):
    d = open(os.path.join(root, lv, 'Objects.level.bin'),'rb').read()
    assert d[:4]==b'TGCL'
    c = struct.unpack_from('<4I', d, 8)
    o1,o2,o3,o4,o5 = struct.unpack_from('<5I', d, 24)
    return d, (o1,o2,o3,o4,o5), c

# 步骤1: 建立跨关卡模板库 — (记录长度) → 记录数/关卡。同一模板在不同关卡应同构
tmpl_map = defaultdict(lambda: defaultdict(int))  # len -> level -> count
lvls = ['Dawn','DuskGraveyard','MainStreet','Prairie_Island','CandleSpace','Night_PaintedWorld',
        'Event_DaysOfMischief','SunsetColosseum','Dawn_TrialsEarth','TGCOffice']
recs_by = defaultdict(list)  # len -> [(lv, bytes)]
for lv in lvls:
    d, offs, c = load(lv)
    seg = d[offs[3]:]
    starts = [m.start() for m in re.finditer(rb'BstNode_\d{9,10}\x00', seg)]
    lens = [starts[i+1]-starts[i] for i in range(len(starts)-1)] + [len(seg)-starts[-1]]
    for i,L in enumerate(lens):
        tmpl_map[L][lv]+=1
        if len(recs_by[L])<40: recs_by[L].append((lv, seg[starts[i]:starts[i]+L]))
# 跨关卡同构验证：长度出现于 ≥3 关卡 → 通用模板
common = sorted([L for L,m in tmpl_map.items() if len(m)>=3 and sum(m.values())>=50], key=lambda L:-sum(tmpl_map[L].values()))
print('通用模板 (>=3 关卡, >=50 条):', [(L, sum(tmpl_map[L].values())) for L in common[:25]])

# 步骤2: 对每个通用模板生成"字段语义标注"：逐4B窗口分类 float-plausible / u32-small / ptr-to-seg3
def classify(L):
    out=[]
    for off in range(19, L-4, 4):
        ivs=[]; fvs=[]
        for lv, r in recs_by[L][:30]:
            if len(r) < off+4: break
            iv, = struct.unpack_from('<I', r, off)
            fv, = struct.unpack_from('<f', r, off)
            ivs.append(iv); fvs.append(fv)
        if not ivs: break
        uni = len(set(ivs))
        f_ok = sum(1 for v in fvs if (abs(v)<1e6 and (abs(v)>1e-8 or v==0)) or v==0)
        tag = 'F' if f_ok/len(fvs)>0.8 else ('U' if max(ivs)<5000 else 'H')
        out.append((off-19, tag, uni, round(fvs[0],4) if tag=='F' else ivs[0]))
    return out
report = open(r'd:\新建文件夹\LightEncounters\tgcl_templates.txt','w',encoding='utf-8')
for L in common[:25]:
    report.write(f'\n=== template {L}B ({sum(tmpl_map[L].values())} recs, levels {len(tmpl_map[L])}) ===\n')
    for row in classify(L):
        report.write(f'  +{row[0]:4d} {row[1]} uniq={row[2]:5d} v={row[3]}\n')
report.close()
print('tgcl_templates.txt written')
# 步骤3: 模板→schema 关联验证。72B transform 模板的节点应引用 type64 schema 行。
# 用节点 payload 中 u32 值 < schema 行数 且命中键名的比例来验证挂接:
d, offs, c = load('Dawn')
seg3 = d[offs[2]:offs[3]]
seg = d[offs[3]:]
starts = [m.start() for m in re.finditer(rb'BstNode_\d{9,10}\x00', seg)]
lens = [starts[i+1]-starts[i] for i in range(len(starts)-1)] + [len(seg)-starts[-1]]
hit=miss=0
for i,L in enumerate(lens[:3000]):
    r = seg[starts[i]:starts[i]+L]
    for off in range(19, L-4, 4):
        v, = struct.unpack_from('<I', r, off)
        if v < len(seg3) and v>0:
            b = seg3[v]
            if 97<=b<=122 or 65<=b<=90: hit+=1
            else: miss+=1
print('payload u32 → seg3 键名命中:', hit, '未命中:', miss)
