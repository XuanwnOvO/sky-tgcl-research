# -*- coding: utf-8 -*-
# tgcl_probe7.py: 排除 0 后的 key 分布 + segD 是否 = 对象属性流
import struct, collections

path = r"Children of the Light/Levels/Dawn/Objects.level.bin"
d = open(path, "rb").read()
o = struct.unpack_from("<5I", d, 24)
o3, o4, o5 = o[2], o[3], o[4]
segC = d[o3:o4]; segD = d[o4:o5]

names = {}
i = 0
while True:
    e = segC.find(b"\x00", i)
    if e < 0: break
    names[i] = segC[i:e].decode(); i = e + 1
starts = set(names) - {0}

allu = struct.unpack_from(f"<{len(segD)//4}I", segD, 0)
pos = [j for j, u in enumerate(allu) if u in starts]
print(f"nonzero key hits: {len(pos)}/{len(allu)} ({100*len(pos)/len(allu):.2f}%)")
gaps = collections.Counter(pos[k+1]-pos[k] for k in range(len(pos)-1))
print("gaps top12:", gaps.most_common(12))

# 检验模式 [key, type?, val...]：对 gap==2 的对，看中间 u32 值域
mid = collections.Counter()
for k in range(len(pos)-1):
    if pos[k+1]-pos[k] == 2:
        mid[allu[pos[k]+1] // 100] += 1
print("gap-2 middle u32 //100 top:", mid.most_common(8))

# 展示几个连续命中上下文（非零键）
shown = 0
k = 0
while shown < 5 and k < len(pos)-1:
    if pos[k+1]-pos[k] <= 6:
        a, b_ = pos[k], pos[k+1]
        ctx = []
        for j in range(max(0,a-3), min(b_+3, len(allu))):
            v = allu[j]
            t = names.get(v)
            if t is None:
                f = struct.unpack_from("<f", d, o4+j*4)[0]
                t = f"{v} (f={f:.4g})"
            ctx.append(f"[{j*4}]{v}:{t}")
        print("\n".join("  "+c for c in ctx)); print("---")
        shown += 1
        k += 2
    else:
        k += 1

# BstNode_ 名字是对象分隔？统计名字后紧跟 4B 内是否为 u32==某key起点
import re
name_re = re.compile(rb"BstNode_\d+\x00")
ms = list(name_re.finditer(segD))
after = collections.Counter()
for m in ms[:4000]:
    p = m.end()
    if p % 1 == 0:
        # 名字结束位置未必 4 对齐，测试其后 0..3 字节滑窗
        for off in range(4):
            if p+off+4 <= len(segD):
                v = struct.unpack_from("<I", segD, p+off)[0]
                if v in starts: after[off] += 1
print("u32-in-starts within 4B after name, by offset:", dict(after), "of", len(ms))
