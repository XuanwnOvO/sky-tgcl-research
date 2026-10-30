import idc, idautils, ida_bytes, ida_funcs, ida_segment

out = open(r'd:\新建文件夹\LightEncounters\round4_lua.txt', 'w', encoding='utf-8')
def w(s): out.write(s + '\n')

# A. 搜代码段中 32 位立即数比较 "LuaR"/lua header 相关
# 0x1b 'L' 'u' 'a' = 0x61754C1B (LE), 或单独比较 0x52 ('R')
w('==== A. find imm 0x61754C1B / 0x1B4C7561 in code segs ====')
for seg_i in range(ida_segment.get_segm_qty()):
    seg = ida_segment.getnseg(seg_i)
    s, e = seg.start_ea, seg.end_ea
    if not (0x100000 <= s <= 0x3400000): continue
    data = ida_bytes.get_bytes(s, e - s)
    if not data: continue
    for pat, tag in [(b'\x1b\x4c\x75\x61', 'Lua sig'), (b'\x61\x4c\x1b\x00', 'imm LE')]:
        idx = 0
        while True:
            i = data.find(pat, idx)
            if i < 0: break
            ea = s + i
            f = ida_funcs.get_func(ea)
            w('  %s @%x func=%s' % (tag, ea, idc.get_func_name(f.start_ea) if f else '-'))
            idx = i + 1

# B. lua 相关函数名
w('==== B. luaU/lundump/undump functions ====')
for ea, name in idautils.Names():
    ln = name.lower()
    if any(k in ln for k in ('undump', 'lundump', 'luaU_', 'lua_load')):
        w('  %x %s' % (ea, name))

out.close()
print('done')
