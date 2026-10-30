import os, re, struct, collections
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"
LVLS = sorted(os.listdir(root))
TARGET = [71, 51, 47, 43, 41, 37, 34, 27, 26, 31, 39, 59, 64, 53, 55]

def proc(lv):
    d = open(os.path.join(root, lv, 'Objects.level.bin'), 'rb').read()
    offs = struct.unpack_from('<5I', d, 24)
    s1, s2, s3, s4, s5 = offs
    seg = d[s3:]
    out = [(m.start()+s3, m.end()-m.start()) for m in re.finditer(rb'BstNode_(\d{9,10})\x00', seg)]
    res = collections.defaultdict(list)
    for i, (a, hl) in enumerate(out):
        e = out[i+1][0] if i+1 < len(out) else s3+len(seg)
        L = e - a
        if L in TARGET and len(res[L]) < 4:
            res[L].append((a, hl))
    return d, res

samples = collections.defaultdict(list)
used = 0
for lv in LVLS:
    d, res = proc(lv)
    for L in TARGET:
        for a, hl in res[L]:
            samples[L].append((lv, d[a+hl:a+L]))  # payload incl trailing seq? exclude seq
    used += 1
    if used >= 6: break

for L in TARGET:
    print(f"===== {L}B =====")
    for lv, p in samples[L][:4]:
        body = p[:-4]  # drop seq
        hx = body.hex()
        asc = ''.join(chr(b) if 32 <= b < 127 else '.' for b in body)
        print(f" [{lv}] {hx}")
        print(f"        {asc}")
