import re, struct

b = open(r'Children of the Light\Levels\Dawn\Objects.level.bin','rb').read()

# 解析 BstNode 实例区 @91988:
# 记录格式: u32 ? | name (NUL 结尾) | u32 len | u32 ? | u32 hasParent | u32 parentIdx ...
ea = 91988 + 4  # skip 00000000
recs = []
for i in range(3):
    start = ea
    nul = b.index(b'\x00', ea)
    name = b[ea:nul].decode()
    ea = nul + 1
    if ea % 4: ea += 4 - ea % 4
    u = struct.unpack_from('<6I', b, ea)
    print(name, '->', [hex(x) for x in u])
    # 尝试步进: 参照下一条 BstNode 的间隔
    nxt = b.find(b'BstNode_', ea)
    print('  gap to next:', nxt - ea, 'raw:', b[ea:ea+40].hex())
    ea = nxt
