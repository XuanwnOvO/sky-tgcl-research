import re, struct
data = open(r'd:\新建文件夹\LightEncounters\bootloader\libBootloader.so','rb').read()

# 找 DevHost 相关引用的 VA/RVA 上下文
def find_all(needle):
    out=[]; i=0
    while True:
        i = data.find(needle, i)
        if i < 0: return out
        out.append(i); i += 1
    return out

# 文件偏移 -> ELF VA：假设典型布局，用 .rodata 段. 直接找引用：在 .text 段中搜 ADRP+ADD 对是复杂的，
# 简化：打印每个关键字符串的文件偏移与前后 64 字节内的邻近字符串
for needle in [b'Received DevHost lua command: ', b'Received lua command: ', b'skynetpassword', b'debug> ', b'DevHost::ConnectRemote', b'gm_ban_chat', b'gm_message', b'NoClip', b'open_console']:
    for off in find_all(needle):
        lo, hi = max(0,off-150), off+150
        ctx = re.findall(rb'[\x20-\x7e]{4,80}', data[lo:hi])
        print(f'--- {needle.decode()} @ file 0x{off:x}')
        for c in ctx: print('   ', c.decode())
