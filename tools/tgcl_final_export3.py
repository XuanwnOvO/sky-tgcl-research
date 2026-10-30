# -*- coding: utf-8 -*-
# TGCL 终局导出器 v3（按方案修正）：
#  1) 种类键 = plen + 跨关固定字节签名（V 仅作每关局部索引，导出 V→种类映射）
#  2) transform 判读 = 72B 模板簇整簇签名匹配（不再用 scale 浮点启发）
#  3) 先扫全关建 plen→(固定字节掩码, 众数 V)，再按掩码判读
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
        V = struct.unpack_from('<I', seg, a-4)[0]  # V 在名字前 4B
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
    return d, counts, comps, recs, groups

def byte_mask(samples):
    """返回固定字节掩码（本簇内恒定的字节=True）"""
    n = len(samples[0])
    return bytes(all(s[i] == samples[0][i] for s in samples) for i in range(n))

def match_mask(p, mask, tmpl):
    return len(p) == len(mask) and all(p[i] == tmpl[i] for i in range(len(p)) if mask[i])

def decode(lv, out_json=None):
    d, counts, comps, recs, groups = parse(lv)
    info = {'level': lv, 'records': len(recs), 'object_groups': len(groups)}

    # ---- 第一步：每关内按 plen 聚簇，建 plen→(掩码, 模板, 众数V) 映射 ----
    by_plen = collections.defaultdict(list)
    for r in recs:
        by_plen[r['plen']].append(r)
    clusters = {}
    for plen, rs in by_plen.items():
        if len(rs) < 5:   # 太少的簇不建模板
            continue
        masks = byte_mask([r['payload'] for r in rs])
        modeV = collections.Counter(r['V'] for r in rs).most_common(1)[0][0]
        clusters[plen] = {'mask': masks, 'tmpl': rs[0]['payload'],
                          'fixed': sum(masks), 'modeV': modeV, 'n': len(rs)}

    # ---- 第二步：种类判读 ----
    # transform: 72B 簇（跨关签名 100% 恒定，见 tgcl_sig.py）
    # bigblock : 384/391/368B 簇
    # slot     : 首 u32 < 组件数 且后续引用大多 < 记录数
    # 其余     : 按 plen 簇标记为 fixed_<plen>
    nrec = len(recs)
    kind_of = {}
    transforms = []
    for r in recs:
        pl, p = r['plen'], r['payload']
        if pl in (368, 384, 391):
            kind_of[r['idx']] = 'bigblock'
            continue
        c = clusters.get(pl)
        if pl == 49 and c and match_mask(p, c['mask'], c['tmpl']):
            # 变换块：01 + scale12(0..12) + 8B + pos16(21..37) + tail12（第十八节 49B 模板）
            # 排除：内嵌可打印 ASCII 串≥4B（如 "ap28_hint_fly"）的参数块；
            #       scale 含 0 分量（正常变换块 scale 极少为 0）
            has_str = re.search(rb'[\x20-\x7e]{4,}', p) is not None
            try:
                sc = struct.unpack_from('<3f', p, 1)
                if (not has_str and all(x == x and abs(x) < 1e6 and x != 0.0 for x in sc)):
                    kind_of[r['idx']] = 'transform'
                    pos = struct.unpack_from('<4f', p, 21)
                    transforms.append({'rec': r['idx'], 'id': r['id'], 'V': r['V'],
                                       'scale': [round(x, 3) for x in sc],
                                       'pos4': [round(x, 2) for x in pos]})
                    continue
            except Exception:
                pass
        # 组件槽启发式
        if pl >= 8:
            ci = struct.unpack_from('<I', p, 0)[0]
            refs = [struct.unpack_from('<I', p, k)[0] for k in range(4, pl-3, 4)]
            if ci < counts[0] and refs:
                inr = sum(1 for u in refs if u < nrec or u == 0xFFFFFFFF)
                if inr / len(refs) >= 0.6:
                    kind_of[r['idx']] = 'component_slot'
                    r['slot'] = (ci, refs)
                    continue
        kind_of[r['idx']] = f'fixed_{pl}' if c else 'variable'

    kind_cnt = collections.Counter(kind_of.values())
    info['kind_dist'] = dict(kind_cnt.most_common(20))
    # V→种类映射（每关局部）
    v2k = collections.defaultdict(collections.Counter)
    for r in recs:
        v2k[r['V']][kind_of[r['idx']]] += 1
    info['V_to_kind'] = {str(v): dict(c.most_common(2)) for v, c in sorted(v2k.items())}

    # 组件槽展开
    slots = []
    for r in recs:
        if kind_of[r['idx']] != 'component_slot': continue
        ci, refs = r['slot']
        comp = comps[ci] if ci < len(comps) else None
        slots.append({'rec': r['idx'], 'id': r['id'], 'group': r['id'] >> 8, 'V': r['V'],
                      'comp': comp['name'] if comp else ci, 'refs': refs})
    tot = sum(len(s['refs']) for s in slots)
    hit = sum(1 for s in slots for u in s['refs'] if u < nrec or u == 0xFFFFFFFF)
    info['component_slots'] = len(slots)
    info['ref_in_range'] = f"{hit}/{tot} = {hit*100//max(tot,1)}%"
    info['transform_count'] = len(transforms)
    nn = sum(1 for t in transforms if any(v is None for v in t['scale']+t['pos4']))
    info['transform_nan'] = f"{nn}/{len(transforms)}"
    info['transform_samples'] = transforms[:5]
    info['slot_samples'] = slots[:5]

    if out_json:
        full = {'meta': info, 'components': comps, 'slots': slots,
                'transforms': transforms,
                'clusters': {str(k): {'n': v['n'], 'fixed': v['fixed'], 'modeV': v['modeV']}
                             for k, v in sorted(clusters.items())},
                'groups': {str(g): idxs for g, idxs in list(groups.items())[:50]}}
        with open(out_json, 'w', encoding='utf-8') as f:
            json.dump(full, f, ensure_ascii=False)
    return info

if __name__ == '__main__':
    lvs = sys.argv[1:] or ['Dawn', 'CandleSpace', 'DuskGraveyard', 'RainForest']
    for lv in lvs:
        out = r'd:\新建文件夹\LightEncounters\tgcl_final3_%s.json' % lv
        info = decode(lv, out)
        print(json.dumps(info, ensure_ascii=False, indent=1)[:2200])
        print("JSON →", out, "\n")
