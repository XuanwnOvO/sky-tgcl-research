# V -> payload size 关联性检验：若每个 V 在单关内对应固定 payload 长度，
# 说明 V 是“记录种类码”（长度由种类决定）；若长度发散，V 另有语义。
import re, struct, sys, collections, os

LEVELS = ["Dawn", "CandleSpace", "DuskGraveyard", "RainForest"]

def parse(level):
    p = os.path.join(r"d:\新建文件夹\LightEncounters\Children of the Light\Levels", lv, "Objects.level.bin")
    data = open(p, "rb").read()
    o1,o2,o3,o4,o5 = struct.unpack_from("<5I", data, 24)
    seg = data[o4:]  # segD 到文件尾
    ms = list(re.finditer(rb'BstNode_(\d+)\x00', seg))
    out = []
    for i, m in enumerate(ms):
        a = m.start()
        e = ms[i+1].start() if i+1 < len(ms) else len(seg)
        V = struct.unpack_from('<I', seg, a-4)[0]
        size = e - a          # 名字+payload+尾u32（不含前导V）
        out.append((V, size))
    return out

for lv in LEVELS:
    recs = parse(lv)
    byV = collections.defaultdict(list)
    for V, s in recs:
        byV[V].append(s)
    print(f"\n=== {lv}  ({len(recs)} recs) ===")
    print(f"{'V':>4} {'n':>6} {'size min':>9} {'max':>9} {'众数':>8} {'纯度':>6}")
    for V in sorted(byV, key=lambda v: -len(byV[v]))[:12]:
        ss = byV[V]
        cnt = collections.Counter(ss)
        mode, mc = cnt.most_common(1)[0]
        print(f"{V:>4} {len(ss):>6} {min(ss):>9} {max(ss):>9} {mode:>8} {mc/len(ss)*100:>5.0f}%")
