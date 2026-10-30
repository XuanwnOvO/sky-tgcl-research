import re
d = open(r'd:\新建文件夹\LightEncounters\bootloader\libBootloader.so','rb').read()
ss = set(re.findall(rb'[\x20-\x7e]{6,120}', d))
# 所有含 {" 的 JSON 命令串
out = open(r'd:\新建文件夹\LightEncounters\json_cmds.txt','w',encoding='utf-8')
jsons = [s for s in ss if b'{' in s and b'"' in s]
jsons.sort()
for s in jsons:
    try: t = s.decode()
    except: continue
    if '"cmd"' in t or 'cmd' in t.lower():
        out.write(t+'\n')
# 另抓所有 "cmd":" 结构附近
for m in re.finditer(rb'\{"cmd":"[^"]{1,40}"', d):
    out.write(m.group().decode()+'\n')
out.close()
print('done')
# 也抓 SetSpeed 类似结构的完整串
for m in re.finditer(rb'\{"cmd"[^\x00]{0,80}', d):
    print(m.group().decode())
