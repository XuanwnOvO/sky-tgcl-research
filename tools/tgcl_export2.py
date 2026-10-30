# -*- coding: utf-8 -*-
# TGCL 解析器 v2：payload = [变长区]。引用型记录 = u32 count + count×u32(seg3偏移)
import os, re, struct, json, sys, collections
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"

def parse(lv):
    d = open(os.path.join(root, lv, 'Objects.level.bin'), 'rb').read()
    ver, c1, c2, c3, c4 = struct.unpack_from('<5I', d, 4)
    o1, o2, o3, o4, o5 = struct.unpack_from('<5I', d, 24)
    strpool = d[o2:o3]
    slen = len(strpool)
    def s3(u):
        if u is None or u >= slen: return None
        z = strpool.find(b'\x00', u)
        return strpool[u:z if z >= 0 else slen].decode('utf-8', 'replace')
    seg = d[o3:]
    ms = list(re.finditer(rb'BstNode_(\d{9,10})\x00', seg))
    nodes = []
    kinds = collections.Counter()
    for i, m in enumerate(ms):
        a, hl = m.start(), m.end()-m.start()
        e = ms[i+1].start() if i+1 < len(ms) else len(seg)
        body = seg[a+hl:e-4]
        seq = struct.unpack_from('<I', seg, e-4)[0]
        nid = m.group(0)[:-1].decode()
        n = len(body)
        kind = None; parsed = None
        if n >= 4 and n % 4 == 0:
            c = struct.unpack_from('<I', body, 0)[0]
            if c == n//4 - 1:
                kind = f'ref{c}'
                parsed = [s3(u) for u in struct.unpack_from(f'<{c}I', body, 4)] if c else []
        if kind is None:
            f0 = struct.unpack_from('<I', body, 0)[0] if n >= 4 else 0
            f0f = struct.unpack_from('<f', body, 0)[0] if n >= 4 else 0
            if f0 == 0: kind = 'flag0'
            elif f0 == 0xFFFFFFFF: kind = 'sentinel-1'
            elif abs(f0f) < 1e6 and (f0f == 0 or abs(f0f) > 1e-3): kind = f'float-head({f0f:.3g})'
            else: kind = f'other({f0:#x})'
            parsed = None
        kinds[kind] += 1
        nodes.append({'id': nid, 'seq': seq, 'kind': kind, 'refs': parsed})
    return {'ver': ver, 'nodes': len(nodes), 'kinds': dict(kinds.most_common(20)), 'nodes_list': nodes}

if __name__ == '__main__':
    lv = sys.argv[1] if len(sys.argv) > 1 else 'Dawn'
    r = parse(lv)
    print(f"{lv}: nodes={r['nodes']}")
    for k, v in r['kinds'].items(): print(f"  {k}: {v}")
    # 展示前几个 ref 记录
    shown = 0
    for nd in r['nodes_list']:
        if nd['refs'] and shown < 5:
            print(" ", nd['id'], nd['kind'], nd['refs'][:6], '...' if len(nd['refs'])>6 else '')
            shown += 1
