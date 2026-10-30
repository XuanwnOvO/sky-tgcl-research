import json, collections

# ===== 1. Constellations.json =====
d = json.load(open(r'Children of the Light\Resources\Constellations.json', encoding='utf-8'))
print('=== Constellations.json ===')
print('total nodes:', len(d))
print('types:', dict(collections.Counter(x['item_type'] for x in d)))
print('constellations:', dict(collections.Counter(x['name'] for x in d)))
print('seasons:', dict(collections.Counter(x.get('season','') for x in d)))
items = [x for x in d if x['item_type'] != 'dummy']
print('unlock items:', len(items))
for x in items[:12]:
    print(' ', x['name'], '|', x['item_name'], '|', x['item_type'], '| id=', x['unlockid'])

# 每星座统计
per = collections.defaultdict(list)
for x in items:
    per[x['name']].append(x['item_name'] + ':' + x['item_type'])
for k in sorted(per):
    print(k, len(per[k]), 'items')

# ===== 2. CompressDictionary.zst =====
print('\n=== CompressDictionary.zst ===')
raw = open(r'Children of the Light\Resources\CompressDictionary.zst','rb').read()
print('size:', len(raw), 'magic:', raw[:4].hex())
# zstd frame magic = 28 b5 2f fd
if raw[:4] == bytes([0x28,0xb5,0x2f,0xfd]):
    print('standard zstd frame')
else:
    print('NOT zstd frame — raw dictionary? first bytes:', raw[:32])
