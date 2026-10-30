import re

# 第一步：建立明文名集合（reg_named）与 hex 字段集合（dump.cs）
names = set()
for ln in open(r'd:\新建文件夹\LightEncounters\reg_all.txt', encoding='utf-8'):
    m = re.search(r"name='([^']+)'", ln)
    if m and m.group(1):
        names.add(m.group(1))
print('names:', len(names))

hexes = set()
txt = open(r'd:\新建文件夹\LightEncounters\dump.cs', encoding='utf-8').read()
for m in re.finditer(r'\b([0-9A-F]{16})\b', txt):
    hexes.add(m.group(1))
print('hex fields:', len(hexes))

# 候选算法
def fnv1a64(s, seed=0xCBF29CE484222325):
    h = seed
    for b in s.encode():
        h ^= b
        h = (h * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return h

def fnv164(s, seed=0xCBF29CE484222325):
    h = seed
    for b in s.encode():
        h = (h * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
        h ^= b
    return h

def djb2(s):
    h = 5381
    for b in s.encode():
        h = ((h * 33) + b) & 0xFFFFFFFFFFFFFFFF
    return h

def sdbm(s):
    h = 0
    for b in s.encode():
        h = (b + (h << 6) + (h << 16) - h) & 0xFFFFFFFFFFFFFFFF
    return h

def elf(s):
    h = 0
    for b in s.encode():
        h = (h << 4) + b
        g = h & 0xF000000000000000
        if g: h ^= g >> 24
        h &= ~g & 0xFFFFFFFFFFFFFFFF
    return h

def rot(x, n):
    return ((x << n) | (x >> (64 - n))) & 0xFFFFFFFFFFFFFFFF

def murmur3_x64_88(s, seed=0):
    # murmur3 x64 88
    data = s.encode()
    n = len(data)
    h1 = seed
    h2 = seed
    c1, c2 = 0x87c37b91114253d5, 0x4cf5ad432745937f
    i = 0
    while n - i >= 16:
        k1 = int.from_bytes(data[i:i+8], 'little')
        k2 = int.from_bytes(data[i+8:i+16], 'little')
        k1 = (k1 * c1) & M; k1 = rot(k1, 31); k1 = (k1 * c2) & M; h1 ^= k1
        h1 = rot(h1, 27); h1 = (h1 + h2) & M; h1 = (h1 * 5 + 0x52dce729) & M
        k2 = (k2 * c2) & M; k2 = rot(k2, 33); k2 = (k2 * c1) & M; h2 ^= k2
        h2 = rot(h2, 31); h2 = (h2 + h1) & M; h2 = (h2 * 5 + 0x38495ab5) & M
        i += 16
    tail = data[i:]
    k1 = k2 = 0
    for j in range(len(tail) - 1, -1, -1):
        if j >= 8:
            k2 = (k2 << 8) | tail[j]
        else:
            k1 = (k1 << 8) | tail[j]
    if len(tail) > 8:
        k2 = (k2 * c2) & M; k2 = rot(k2, 33); k2 = (k2 * c1) & M; h2 ^= k2
    if len(tail) > 0:
        k1 = (k1 * c1) & M; k1 = rot(k1, 31); k1 = (k1 * c2) & M; h1 ^= k1
    h = (h1 ^ h2) & M
    h = (h ^ n) & M
    h ^= h >> 33; h = (h * 0xff51afd7ed558ccd) & M; h ^= h >> 33
    h = (h * 0xc4ceb9fe1a85ec53) & M; h ^= h >> 33
    return h

M = 0xFFFFFFFFFFFFFFFF

def xxh64(s, seed=0):
    data = s.encode()
    P1, P2, P3, P4, P5 = 11400714785074694791, 14029467366897019727, 1609587929392839161, 9650029242287828579, 2870177450012600261
    M = 0xFFFFFFFFFFFFFFFF
    n = len(data)
    if n >= 32:
        v1 = (seed + P1 + P2) & M
        v2 = (seed + P2) & M
        v3 = seed & M
        v4 = (seed - P1) & M
        i = 0
        while n - i >= 32:
            for vi in range(4):
                k = int.from_bytes(data[i:i+8], 'little')
                v = [v1, v2, v3, v4][vi]
                v = (v + k * P2) & M
                v = rot(v, 31)
                v = (v * P1) & M
                if vi == 0: v1 = v
                elif vi == 1: v2 = v
                elif vi == 2: v3 = v
                else: v4 = v
                i += 8
        h = (rot(v1, 1) + rot(v2, 7) + rot(v3, 12) + rot(v4, 18)) & M
        for v in (v1, v2, v3, v4):
            v = (v * P2 + P4) & M
            v = rot(v, 31)
            h = (h ^ (v * P1)) & M
            h = ((h << 27) | (h >> 37)) & M
            h = (h * P4 + P5) & M
    else:
        h = (seed + P5) & M
        i = 0
    h = (h + n) & M
    while n - i >= 8:
        k = int.from_bytes(data[i:i+8], 'little')
        v = (h ^ (k * P2)) & M
        v = rot(v, 31)
        h = ((v * P1) ^ (v * P2 * 0)) & M
        h = (h ^ ((rot(v, 31) * P1))) & M
        h = rot(h, 27)
        h = (h * P1 + P4) & M
        i += 8
    if n - i >= 4:
        h = (h ^ (int.from_bytes(data[i:i+4], 'little') * P1)) & M
        h = rot(h, 23)
        h = (h * P2 + P3) & M
        i += 4
    while i < n:
        h = (h ^ (data[i] * P5)) & M
        h = rot(h, 11)
        h = (h * P1) & M
        i += 1
    h ^= h >> 33; h = (h * P2) & M; h ^= h >> 29; h = (h * P3) & M; h ^= h >> 32
    return h

algos = [('fnv1a', fnv1a64), ('fnv1', fnv164), ('djb2', djb2), ('sdbm', sdbm), ('elf', elf),
         ('murmur3_88', murmur3_x64_88), ('xxh64', xxh64)]

hexvals = {int(h, 16) for h in hexes}
print('hex vals:', len(hexvals))

for aname, fn in algos:
    hits = 0
    examples = []
    for nm in names:
        v = fn(nm)
        if v in hexvals:
            hits += 1
            if len(examples) < 3: examples.append((nm, hex(v)))
    print('%s: %d hits %s' % (aname, hits, examples))
