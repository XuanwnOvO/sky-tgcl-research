import struct, re, os
root = r'd:\新建文件夹\LightEncounters\Children of the Light\Levels'
d = open(os.path.join(root,'Dawn','Objects.level.bin'),'rb').read()
o1,o2,o3,o4,o5 = struct.unpack_from('<5I', d, 24)
seg1 = d[o1:o2]; seg3 = d[o3:o4]
# (7,17920)→'Npc_Mem' 7字符 ✓ (7,20)→'toCurre' 7字符 ✓ (13636,27)→'ntTargetTransform\x00' 18字符+1?
# 前缀偏移问题: 17920 处 'Npc_Mem' 是 'Npc_MemoryPose' 的前 7 字符 → len 不匹配名长，而 hash?
# 试 (len, off) 但名长≠7: 'Npc_MemoryPose'=15。或 (hash, off) 7=hash?
# 另一解: seg1 是 [str1][str2] 双字符串表：每个条目 (a, b) = (k前缀长, off)?
# 直接法: (13636,27): 27 起 = 'ntTargetTransform' — 之前 schema 名 'toCurrentTargetTransform' 子串!
#   27 指向 'ntTargetTransform' = toCurre(7) + ntTargetTransform → 拼接 = 'toCurrentTargetTransform'!
# → seg1 条目 = [u32 前缀长][u32 后缀偏移]，完整名 = seg3[前缀off : prefixLen] + seg3[off:]
# 36515 = 'IfEnabled' 完整名（前缀长 0? 头对 36515,0 → len=0? 但 36515 直接是 'IfEnabled')
# 验证: (0, 36515)? 头是 (36515, 0) 顺序。看 783 条逐条解析:
out=[]
for k in range(0, len(seg1)-4, 8):
    a,b = struct.unpack_from('<2I', seg1, k)
    # a=后缀off? b=前缀长?
    nm = seg3[a:a+60].split(b'\x00')[0].decode('latin1')
    out.append((a,b,nm))
print(out[:10])
# 而奇数位值小(0..136) = 前缀长, 前缀 = seg3[?]。前缀 off 在哪? 上一条目的 a!
# 若条目 = (off, prefixLen) 且名 = seg3[off - prefixLen : off] + seg3[off : until NUL]:
for a,b,nm in out[:10]:
    full = seg3[a-b:a+40].split(b'\x00')[0].decode('latin1')
    print(f'off={a} plen={b} short={nm!r} full={full!r}')
