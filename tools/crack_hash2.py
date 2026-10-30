import re

names = set()
for ln in open(r'd:\新建文件夹\LightEncounters\reg_all.txt', encoding='utf-8'):
    m = re.search(r"name='([^']+)'", ln)
    if m and m.group(1):
        names.add(m.group(1))

txt = open(r'd:\新建文件夹\LightEncounters\dump.cs', encoding='utf-8').read()
hexvals = {int(m.group(1), 16) for m in re.finditer(r'\b([0-9A-F]{16})\b', txt)}
M = 0xFFFFFFFFFFFFFFFF

def rot(x, n): return ((x << n) | (x >> (64 - n))) & M

def fnv1a64(s, seed):
    h = seed
    for b in s:
        h ^= b; h = (h * 0x100000001B3) & M
    return h

def fnv164(s, seed):
    h = seed
    for b in s:
        h = (h * 0x100000001B3) & M; h ^= b
    return h

# 1) seed 爆破：对短 seed 空间（常见 seed 0x811C9DC5, 0, 1, 0x9E3779B97F4A7C15...）＋明文小写/大写/带尾部\0
seeds = [0, 1, 0x811C9DC5, 0x9E3779B97F4A7C15, 0xCBF29CE484222325, 0x5A17, 0xDEADBEEF, 0x1234567,
         0x1000193, 0x1505, 0x01935, 0x19283746]
hits_total = 0
for seed in seeds:
    for tag, prep in [('lower', lambda b: b.lower()), ('upper', lambda b: b.upper()),
                      ('nul', lambda b: b + b'\0')]:
        pass  # prep 在字节层做
    for prep_name in ('id', 'lower', 'upper', 'nul'):
        hits = 0; ex = []
        for nm in names:
            b = nm.encode()
            if prep_name == 'lower': b = b.lower()
            elif prep_name == 'upper': b = b.upper()
            elif prep_name == 'nul': b = b + b'\0'
            if fnv1a64(b, seed) in hexvals or fnv164(b, seed) in hexvals:
                hits += 1
                if len(ex) < 2: ex.append(nm)
        if hits:
            print('seed %x %s fnv hits=%d %s' % (seed, prep_name, hits, ex))
            hits_total += hits
print('fnv variant total:', hits_total)

# 2) 反转序（大端解释）fnv1a
hits = 0; ex = []
for nm in names:
    b = nm.encode()
    h = 0
    for by in b[::-1]:
        h ^= by; h = (h * 0x100000001B3) & M
    if h in hexvals:
        hits += 1; ex.append(nm)
print('fnv1a reversed:', hits, ex)

# 3) 每字符累加位置混合（类似 Java 31/37 基）
for base in (31, 33, 37, 131, 1313, 65599, 0x100000001B3):
    for prep_name in ('id', 'lower'):
        hits = 0; ex = []
        for nm in names:
            b = nm.encode()
            if prep_name == 'lower': b = b.lower()
            h = 0
            for by in b:
                h = (h * base + by) & M
            if h in hexvals:
                hits += 1
                if len(ex) < 2: ex.append(nm)
        if hits:
            print('poly base %x %s: %d %s' % (base, prep_name, hits, ex))

# 4) CRC64 ECMA / ISO
def make_crc64(poly, init, xorout, rev):
    tab = []
    for i in range(256):
        c = i if rev else (i << 56) & M
        for _ in range(8):
            if rev: c = (c >> 1) ^ poly if c & 1 else c >> 1
            else: c = ((c << 1) & M) ^ poly if c & (1 << 63) else (c << 1) & M
        tab.append(c)
    def crc(s):
        c = init
        for by in s.encode():
            if rev: c = tab[(c ^ by) & 0xFF] ^ (c >> 8)
            else: c = tab[((c >> 56) ^ by) & 0xFF] ^ ((c << 8) & M)
        return c ^ xorout
    return crc

for pn, poly in [('ecma', 0xC96C5795D7870F42), ('iso', 0xD800000000000000 if True else 0)]:
    crc = make_crc64(poly, M, 0, True)
    hits = 0; ex = []
    for nm in names:
        if crc(nm) in hexvals:
            hits += 1; ex.append(nm)
    print('crc64 %s: %d %s' % (pn, hits, ex[:2]))

# 5)CityHash/xxh 变体太大，先看 hex 字段是否其实不是 hash——抽样看它们所在类
# hexvals 抽 5 个，在 dump.cs 找上下文
out = open(r'd:\新建文件夹\LightEncounters\hex_ctx.txt', 'w', encoding='utf-8')
lines = txt.split('\n')
cls = None
found = 0
for i, ln in enumerate(lines):
    m2 = re.search(r'\b([0-9A-F]{16})\b', ln)
    if m2:
        # 向上找类名
        c = None
        for j in range(i, max(0, i-30), -1):
            mm = re.match(r'internal class (\w+) :  // 0x([0-9a-f]+)', lines[j])
            if mm:
                c = (mm.group(1), mm.group(2)); break
        if found < 25:
            out.write('%s %s -> class %s %s\n' % (i, m2.group(1), c[0] if c else '?', ln.strip()[:80]))
        found += 1
out.write('total: %d\n' % found)
out.close()
print('hex ctx done, total', found)
