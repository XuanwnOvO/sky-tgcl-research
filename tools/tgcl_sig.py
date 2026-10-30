# 跨关卡同 plen 簇的字节签名一致性检验
# 对每个 plen 簇：按字节位统计各关样本的取值是否一致 → 得到“固定模板字节”掩码
import re, struct, os, collections
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Levels"
LEVELS = ["Dawn", "CandleSpace", "DuskGraveyard", "RainForest"]

def parse(lv):
    d = open(os.path.join(root, lv, 'Objects.level.bin'), 'rb').read()
    o1,o2,o3,o4,o5 = struct.unpack_from("<5I", d, 24)
    seg = d[o4:]
    ms = list(re.finditer(rb'BstNode_(\d+)\x00', seg))
    out = []
    for i, m in enumerate(ms):
        a = m.start()
        e = ms[i+1].start() if i+1 < len(ms) else len(seg)
        body = seg[a:e-4]
        hl = m.end()-m.start()
        out.append(body[hl:])  # payload only
    return out

# 关注的 plen（跨关同尺寸候选）：72, 391, 147, 51, 35, 106
TARGET = {72, 391, 147, 51, 35, 106, 78}
sig = collections.defaultdict(lambda: collections.defaultdict(list))
for lv in LEVELS:
    for pl in parse(lv):
        if len(pl) in TARGET:
            sig[len(pl)][lv].append(pl)

for plen in sorted(sig):
    print(f"\n--- payload len={plen} ---")
    lvls = list(sig[plen])
    n = min(len(v) for v in sig[plen].values())
    # 取各关前 n 个样本，逐字节比较跨关是否恒定
    fixed = 0
    masks = {}
    for L in lvls:
        arr = sig[plen][L][:n]
        mask = bytes(all(s[i]==arr[0][i] for s in arr) for i in range(plen))
        masks[L] = mask
    common = None
    for L in lvls:
        common = masks[L] if common is None else bytes(a&b for a,b in zip(common, masks[L]))
    fx = sum(common)
    print(f"levels={lvls} samples/lv={n} 恒定字节 {fx}/{plen} ({fx/plen*100:.0f}%)")
    # 打印 Dawn 样本的固定字节十六进制预览
    s0 = sig[plen[lvls.index(lvls[0])] if False else plen][lvls[0]][0]
    prev = ' '.join(f"{s0[i]:02x}" if common[i] else '..' for i in range(min(plen,64)))
    print(f"  {lvls[0]}样本(固定位): {prev}")
