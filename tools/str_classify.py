import re
data = open(r'd:\新建文件夹\LightEncounters\bootloader\libBootloader.so','rb').read()
strs = set(re.findall(rb'[\x20-\x7e]{4,120}', data))
sl = sorted(strs)
keys = {
 'cheat': rb'cheat', 'gm_': rb'\bgm[_A-Z]', 'admin': rb'admin', 'secret': rb'secret',
 'hidden': rb'hidden', 'backdoor': rb'backdoor|Backdoor', 'devonly': rb'devOnly|DevOnly|dev_only',
 'qa': rb'\bQA[A-Z_]', 'debug_cmd': rb'debug|Debug', 'password': rb'password|Password|passwd',
 'skynet': rb'skyNet|SkyNet|skynet', 'command': rb'[Cc]ommand', 'godmode': rb'god|God',
 'noclip': rb'noclip|NoClip|flyMode', 'console': rb'console|Console', 'freecam': rb'freecam|FreeCam|FreeCamera',
 'time_scale': rb'timeScale|time_scale|TimeScale', 'unlock': rb'[Uu]nlock[A-Z]', 'warp': rb'[Ww]arp',
 'coin_currency': rb'[Cc]andle|candles', 'heart': rb'[Hh]eart[s]?\b',
}
out = open(r'd:\新建文件夹\LightEncounters\strings_classified.txt','w',encoding='utf-8')
counts={}
for k,p in keys.items():
    r = re.compile(p)
    hits = [s.decode() for s in sl if r.search(s)]
    counts[k]=len(hits)
    out.write(f'\n== {k} ({len(hits)}) ==\n')
    for s in hits[:400]:
        out.write(s+'\n')
out.close()
print(counts)
