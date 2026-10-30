# -*- coding: utf-8 -*-
# TGCL 终局导出器：记录链 → 对象组 → 组件槽 → 引用解链，整关 dump JSON
import os, re, struct, json, collections, sys
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"

def parse(lv):
    d = open(os.path.join(root, lv, 'Objects.level.bin'), 'rb').read()
    counts = struct.unpack_from('<4I', d, 8)
    o1, o2, o3, o4, o5 = struct.unpack_from('<5I', d, 24)
    segC = d[o3:o4]
    def s3(u):
        if u is None or u >= len(segC): return None
        e = segC.find(b'\x00', u)
        return segC[u:e].decode('utf-8', 'replace')
    segA = d[o1:o2]
    comps = []
    for i in range(counts[0]):
        a, st, pc = struct.unpack_from('<3I', segA, i*12)
        comps.append({'name': s3(a), 'schemaStart': st, 'propCount': pc})
    segB = d[o2:o3]
    for c in comps:
        c['props'] = [{'a': a, 'key': s3(ko), 'type': t, 'e': e}
                      for a, ko, t, e in (struct.unpack_from('<4I', segB, j*16)
                                          for j in range(c['schemaStart'], c['schemaStart']+c['propCount']))]
    seg = d[o4:]
    ms = list(re.finditer(rb'BstNode_(\d+)\x00', seg))
    recs = []
    for i, m in enumerate(ms):
        a, hl = m.start(), m.end()-m.start()
        e = ms[i+1].start() if i+1 < len(ms) else len(seg)
        V = struct.unpack_from('<I', seg, a-4)[0]  # V 在名字前 4B（= 上条记录的尾 u32）
        body = seg[a:e-4]
        recs.append({'idx': i, 'V': V, 'id': int(m.group(1)),
                     'plen': len(body)-hl, 'payload': body[hl:]})
    # nextV 链验证：rec[i] 尾 u32 == rec[i+1] 的 V
    chain_ok = 0
    for i in range(len(recs)-1):
        tail = struct.unpack_from('<I', seg, ms[i+1].start()-4)[0]
        if tail == recs[i+1]['V']: chain_ok += 1
    print(f"nextV 链验证: {chain_ok}/{len(recs)-1}")
    # 对象组
    groups = collections.defaultdict(list)
    for r in recs:
        groups[r['id'] >> 8].append(r['idx'])
    return d, comps, recs, groups, s3

def decode(lv, out_json=None):
    d, comps, recs, groups, s3 = parse(lv)
    info = {
        'level': lv,
        'records': len(recs),
        'object_groups': len(groups),
        'V_dist': dict(collections.Counter(r['V'] for r in recs).most_common(15)),
    }
    # V=7 组件槽：compIdx + N×rec-index
    slots = []
    for r in recs:
        if r['V'] != 7: continue
        p = r['payload']
        if len(p) < 4: continue
        ci = struct.unpack_from('<I', p, 0)[0]
        refs = []
        for k in range(4, len(p)-3, 4):
            u = struct.unpack_from('<I', p, k)[0]
            refs.append(u)
        comp = comps[ci] if ci < len(comps) else None
        slots.append({'rec': r['idx'], 'id': r['id'], 'group': r['id']>>8,
                      'comp': comp['name'] if comp else ci,
                      'keys': [pr['key'] for pr in comp['props']] if comp else [],
                      'refs': refs})
    info['component_slots'] = len(slots)
    # 验证 rec-index：引用 < len(recs) 比例
    tot = hit = 0
    for s in slots:
        for u in s['refs']:
            tot += 1
            if u < len(recs): hit += 1
    info['ref_in_range'] = f"{hit}/{tot} = {hit*100//max(tot,1)}%"
    # V=6 变换块解码样本
    transforms = []
    for r in recs:
        if r['V'] != 6: continue
        p = r['payload']
        try:
            sc = struct.unpack_from('<3f', p, 1)
            pos = struct.unpack_from('<4f', p, 21)
            transforms.append({'rec': r['idx'], 'id': r['id'], 'scale': [round(x,3) for x in sc],
                               'pos4': [round(x,2) for x in pos]})
        except Exception:
            pass
    info['transform_records'] = len(transforms)
    info['transform_samples'] = transforms[:5]
    info['slot_samples'] = [{k: v for k, v in s.items() if k != 'keys'} for s in slots[:6]]
    if out_json:
        full = {'meta': info, 'components': comps, 'slots': slots,
                'records_V6': transforms,
                'groups': {str(g): idxs for g, idxs in list(groups.items())[:50]}}
        with open(out_json, 'w', encoding='utf-8') as f:
            json.dump(full, f, ensure_ascii=False)
    return info

if __name__ == '__main__':
    lv = sys.argv[1] if len(sys.argv) > 1 else 'Dawn'
    out = r'd:\新建文件夹\LightEncounters\tgcl_final_%s.json' % lv
    info = decode(lv, out)
    print(json.dumps(info, ensure_ascii=False, indent=1)[:3000])
    print("JSON →", out)
