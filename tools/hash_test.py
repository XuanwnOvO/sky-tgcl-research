# 验证 hash 算法：已知 WerewolfGameTableRpc hash = 0xBBE28586E228DA28
# 候选：FNV-1a 64、FNV-1 64、xxhash64(seed0)、CRC64、djb2 等，对 "ConfirmDialog"/"activate_werewolfgame_bonfire" 等明文测试
# 同时测试大写/小写、类名前缀组合

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

tests = ['ConfirmDialog', 'activate_werewolfgame_bonfire', 'werewolfgame_leave',
         'werewolfgame_table_sharedspace_hint', 'WerewolfGameTableRpc', 'ui_nav_confirm']
target = 0xBBE28586E228DA28

for t in tests:
    for fn, nm in [(fnv1a64,'fnv1a'), (fnv164,'fnv1'), (djb2,'djb2'), (sdbm,'sdbm')]:
        v = fn(t)
        if v == target:
            print('HIT!', nm, t)
        # 也测试大写
        v2 = fn(t.upper())
        if v2 == target:
            print('HIT-upper!', nm, t)
print('done')
