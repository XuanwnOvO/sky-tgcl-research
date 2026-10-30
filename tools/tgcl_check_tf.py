# -*- coding: utf-8 -*-
# 检查 tgcl_final3_Dawn.json 中 transform 的 scale/pos 解码质量
import json, math, collections

d = json.load(open(r"d:\新建文件夹\LightEncounters\tgcl_final3_Dawn.json", encoding="utf-8"))
tfs = d["transforms"]
print("transform 总数:", len(tfs))

vals = [v for t in tfs for v in t["scale"] + t["pos4"]]
print("None/NaN/Inf 数:", sum(1 for v in vals if v is None or not math.isfinite(v)))

print("\n前 8 条样本:")
for t in tfs[:8]:
    print(f"  rec={t['rec']:>5} V={t['V']} scale={t['scale']} pos4={t['pos4']}")

c = collections.Counter(tuple(t["scale"]) for t in tfs)
print("\nscale 众数 top5:", c.most_common(5))

for i in range(4):
    vs = [t["pos4"][i] for t in tfs]
    print(f"pos4[{i}]: min={min(vs):.3f} max={max(vs):.3f} 样本={[round(x,2) for x in vs[:5]]}")

mags = [math.sqrt(sum(t["pos4"][k] ** 2 for k in range(3))) for t in tfs]
pct = 100 * sum(1 for m in mags if 0.99 < m < 1.01) / len(mags)
print(f"pos4[0:3] 模长: min={min(mags):.3f} max={max(mags):.3f} ≈1 占比={pct:.0f}%")

# 与源数据交叉验证：直接重读 rec payload，比对 JSON 里的字段
import re, struct, os
lv = "Dawn"
dd = open(os.path.join(r"d:\新建文件夹\LightEncounters\Children of the Light\Levels", lv, "Objects.level.bin"), "rb").read()
o4 = struct.unpack_from("<5I", dd, 24)[3]
seg = dd[o4:]
ms = list(re.finditer(rb"BstNode_(\d+)\x00", seg))
mismatch = 0
checked = 0
for t in tfs[:200]:
    m = ms[t["rec"]]
    a = m.start()
    e = ms[t["rec"] + 1].start() if t["rec"] + 1 < len(ms) else len(seg)
    body = seg[a:e - 4]
    hl = m.end() - m.start()
    p = body[hl:]
    if len(p) != 49:
        mismatch += 1; continue
    sc = struct.unpack_from("<3f", p, 1)
    po = struct.unpack_from("<4f", p, 21)
    checked += 1
    js = t["scale"]; jp = t["pos4"]
    if (any(abs(sc[k] - js[k]) > 0.001 for k in range(3)) or
            any(abs(po[k] - jp[k]) > 0.01 for k in range(4))):
        mismatch += 1
print(f"\n交叉验证（重读 payload vs JSON）: 不一致 {mismatch}/{checked}")
