import subprocess, json, time
prog = r'd:\新建文件夹\LightEncounters\type_scan_prog.json'
for i in range(200):
    r = subprocess.run(['py', r'd:\新建文件夹\LightEncounters\tools\ida_run.py'],
                       capture_output=True, text=True, timeout=300)
    out = r.stdout
    if 'done=True' in out:
        print(out.strip())
        break
    if i % 10 == 0:
        print(out.strip(), flush=True)
else:
    print('max iters reached')
