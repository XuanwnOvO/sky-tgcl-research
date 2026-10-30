import os, re, struct, collections

root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"
LVLS = sorted(os.listdir(root))
TARGET = [71, 51, 39, 42, 47, 31, 43, 50, 38, 41, 53, 55, 59, 64, 37, 34, 27, 26]

def proc(lv):
    d = open(os.path.join(root, lv, 'Objects.level.bin'), 'rb').read()
    offs = struct.unpack_from('<5I', d, 24)
    s1, s2, s3, s4, s5 = offs
    strpool = d[s2:s3]
    slen = len(strpool)
    seg = d[s3:]
    out = []
    for m in re.finditer(rb'BstNode_(\d{9,10})\x00', seg):
        st = m.start()
        out.append((st + s3, m.end() - st))  # abs start, header len
    res = collections.defaultdict(list)
    for i, (absst, hl) in enumerate(out):
        absend = out[i+1][0] if i+1 < len(out) else s3 + len(seg)
        L = absend - absst
        if L in TARGET and len(res[L]) < 60:
            res[L].append((absst, hl))
    return d, strpool, slen, res

stats = collections.defaultdict(lambda: [0,0,0,0])  # nrec, u32tot, u32hit, ff
samples = collections.defaultdict(list)
used = 0
for lv in LVLS:
    try:
        d, strpool, slen, res = proc(lv)
    except Exception:
        continue
    for L in TARGET:
        for absst, hl in res[L][:25]:
            rec = d[absst:absst+L]
            payload = rec[hl:-4]
            stats[L][0] += 1
            info = []
            for j in range(0, len(payload)-3, 4):
                u = struct.unpack_from('<I', payload, j)[0]
                f = struct.unpack_from('<f', payload, j)[0]
                stats[L][1] += 1
                isoff = 0 < u < slen
                if isoff: stats[L][2] += 1
                if u == 0xFFFFFFFF: stats[L][3] += 1
                info.append((j, u, isoff, f))
            if len(samples[L]) < 3:
                samples[L].append((lv, info))
    used += 1
    if used >= 10: break

for L in TARGET:
    n, tot, hit, ff = stats[L]
    if n == 0:
        print(f"== {L}B: none"); continue
    print(f"== {L}B: {n} recs | u32 slots {tot} | seg3-hit {hit*100//max(tot,1)}% | ff {ff}")
    for lv, info in samples[L]:
        parts = []
        for j, u, isoff, f in info:
            if u == 0xFFFFFFFF: parts.append("ff")
            elif isoff:
                # extract string
                pass
            else:
                parts.append(f"{u:x}/f={f:.3g}" if abs(f) < 1e6 and (abs(f)>1e-3 or f==0) else f"{u:x}")
        print(f"   [{lv}] {' | '.join(parts)}")
