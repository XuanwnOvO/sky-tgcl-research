# -*- coding: utf-8 -*-
# TGCL -> JSON 导出器：验证 TLV 解析器能否无损解析整关
import os, re, struct, json, sys, collections

root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"

def parse(lv):
    d = open(os.path.join(root, lv, 'Objects.level.bin'), 'rb').read()
    ver, c1, c2, c3, c4 = struct.unpack_from('<5I', d, 4)
    o1, o2, o3, o4, o5 = struct.unpack_from('<5I', d, 24)
    strpool = d[o2:o3]
    seg = d[o3:]
    starts = [(m.start()+o3, m.end()-m.start()) for m in re.finditer(rb'BstNode_(\d{9,10})\x00', seg)]
    nodes = []
    unk_types = collections.Counter()
    for i, (a, hl) in enumerate(starts):
        e = starts[i+1][0] if i+1 < len(starts) else o3 + len(seg)
        body = d[a+hl:e-4]
        nid = d[a:a+hl-1].decode()
        seq = struct.unpack_from('<I', d, e-4)[0]
        # TLV decode
        p = 0
        props = []
        ok = True
        while p < len(body):
            t = body[p]; p += 1
            if t == 0:  # inline string
                z = body.find(b'\x00', p)
                if z < 0: ok = False; unk_types[t] += 1; break
                props.append({'t': 'str', 'v': body[p:z].decode('utf-8', 'replace')})
                p = z + 1
            elif t == 1:  # transform 10 floats
                if p + 40 > len(body): ok = False; unk_types[t] += 1; break
                f = struct.unpack_from('<10f', body, p)
                props.append({'t': 'transform', 'scale': f[0:3], 'rot': f[3:7], 'pos': f[7:10]})
                p += 40
            elif 2 <= t <= 7:  # N refs
                n = t
                if p + 4*n > len(body): ok = False; unk_types[t] += 1; break
                refs = []
                for k in range(n):
                    u = struct.unpack_from('<I', body, p+4*k)[0]
                    s = strpool[u:strpool.find(b'\x00', u)].decode('utf-8', 'replace') if u < len(strpool) else None
                    refs.append({'off': u, 's': s})
                props.append({'t': f'ref{n}', 'refs': refs})
                p += 4*n
            else:
                unk_types[t] += 1
                ok = False
                break
        nodes.append({'id': nid, 'seq': seq, 'props': props, 'full': ok, 'raw': None if ok else body.hex()})
    return {'ver': ver, 'counts': [c1, c2, c3, c4], 'n_nodes': len(nodes),
            'full_pct': sum(1 for n in nodes if n['full'])*100//max(1, len(nodes)),
            'unk_types': dict(unk_types), 'nodes': nodes}

if __name__ == '__main__':
    lv = sys.argv[1] if len(sys.argv) > 1 else 'Dawn'
    r = parse(lv)
    print(f"{lv}: ver={r['ver']} nodes={r['n_nodes']} 完整TLV解析率={r['full_pct']}%")
    print("未知type字节:", r['unk_types'])
    out = os.path.join('..', 'tgcl_%s.json' % lv) if False else (r'd:\新建文件夹\LightEncounters\tgcl_%s.json' % lv)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(r, f, ensure_ascii=False, indent=1)
    # 抽样展示
    shown = 0
    for n in r['nodes']:
        if n['full'] and any(p['t'] == 'transform' for p in n['props']) and shown < 3:
            print(json.dumps(n, ensure_ascii=False)[:400]); shown += 1
