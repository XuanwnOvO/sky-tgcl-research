# -*- coding: utf-8 -*-
# TGCL 终局导出器 v2：按「payload 模板签名」判读记录种类（V 是关卡局部索引，不可跨关用）
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
    seg = d[o4:]
    ms = list(re.finditer(rb'BstNode_(\d+)\x00', seg))
    recs = []
    for i, m in enumerate(ms):
        a = m.start()
        e = ms[i+1].start() if i+1 < len(ms) else len(seg)
        V = struct.unpack_from('<I', seg, a-4)[0]
        body = seg[a:e-4]
        hl = m.end()-m.start()
        recs.append({'idx': i, 'V': V, 'id': int(m.group(1)),
                     'plen': len(body)-hl, 'payload': body[hl:]})
    chain_ok = sum(1 for i in range(len(recs)-1)
                   if struct.unpack_from('<I', seg, ms[i+1].start()-4)[0] == recs[i+1]['V'])
    print(f"nextV 链验证: {chain_ok}/{len(recs)-1}")
    groups = collections.defaultdict(list)
    for r in recs:
        groups[r['id'] >> 8].append(r['idx'])
    return d, comps, recs, groups, s3

# ---- 模板签名库（跨关恒定字节的种类码）----
# key = plen, sig = 固定字节模板; kind = 语义
TEMPLATES = {
    72:  ('transform', {'scale_off': 1, 'pos_off': 21, 'tail_off': 60}),
}

def classify(rec, counts):
    """按 payload 模板返回 (kind, note)；规则按证据强度排序"""
    p, n = rec['payload'], rec['plen']
    if n == 72:
        # 变换块：01 + scale12 + 8 + pos16 + tail12
        try:
            sc = struct.unpack_from('<3f', p, 1)
            if all(abs(x) < 1e6 and x == x for x in sc):
                return 'transform', {'scale': sc}
        except Exception: pass
    if n == 368 or n == 391 or n == 384:
        return 'bigblock', None   # V=9 族（材质/音频大块）
    # 组件槽启发式：首 u32 = 组件索引 且递增、后续含 < counts[1] 的引用
    if n >= 8:
        ci = struct.unpack_from('<I', p, 0)[0]
        if ci < counts[0]:
            refs = [struct.unpack_from('<I', p, k)[0] for k in range(4, n-3, 4)]
            inr = sum(1 for u in refs if u < counts[3]*0 + 100000)
            if refs and inr / len(refs) > 0.6:
                return 'component_slot', {'compIdx': ci, 'refs': refs}
    return 'unknown', None

def decode(lv, out_json=None):
    d, comps, recs, groups, s3 = parse(lv)
    cnt = struct.unpack_from('<4I', d, 8)
    info = {'level': lv, 'records': len(recs), 'object_groups': len(groups)}
    kind_cnt = collections.Counter()
    slots, transforms = [], []
    for r in recs:
        kind, note = classify(r, cnt)
        r['kind'] = kind
        kind_cnt[kind] += 1
        if kind == 'component_slot':
            ci = note['compIdx']
            comp = comps[ci] if ci < len(comps) else None
            slots.append({'rec': r['idx'], 'id': r['id'], 'group': r['id']>>8,
                          'comp': comp['name'] if comp else ci, 'refs': note['refs']})
        elif kind == 'transform':
            sc = struct.unpack_from('<3f', r['payload'], 1)
            pos = struct.unpack_from('<4f', r['payload'], 21)
            transforms.append({'rec': r['idx'], 'id': r['id'],
                               'scale': [round(x,3) for x in sc],
                               'pos4': [round(x,2) for x in pos]})
    info['kind_dist'] = dict(kind_cnt)
    # 每类记录对应的 V（证明 V 局部性）
    vmap = collections.defaultdict(collections.Counter)
    for r in recs:
        vmap[r['kind']][r['V']] += 1
    info['kind_to_V'] = {k: dict(c.most_common(5)) for k, c in vmap.items()}
    tot = sum(len(s['refs']) for s in slots)
    hit = sum(1 for s in slots for u in s['refs'] if u < len(recs))
    info['ref_in_range'] = f"{hit}/{tot} = {hit*100//max(tot,1)}%"
    info['transform_count'] = len(transforms)
    info['transform_samples'] = transforms[:5]
    info['slot_samples'] = slots[:6]
    if out_json:
        full = {'meta': info, 'components': comps, 'slots': slots,
                'transforms': transforms,
                'groups': {str(g): idxs for g, idxs in list(groups.items())[:50]}}
        with open(out_json, 'w', encoding='utf-8') as f:
            json.dump(full, f, ensure_ascii=False)
    return info

if __name__ == '__main__':
    lv = sys.argv[1] if len(sys.argv) > 1 else 'Dawn'
    out = r'd:\新建文件夹\LightEncounters\tgcl_final2_%s.json' % lv
    info = decode(lv, out)
    print(json.dumps(info, ensure_ascii=False, indent=1)[:2500])
    print("JSON →", out)
