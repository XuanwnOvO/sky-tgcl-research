import subprocess
for i in range(20):
    r = subprocess.run(['py', r'd:\新建文件夹\LightEncounters\tools\ida_run.py'],
                       capture_output=True, text=True, timeout=600)
    out = r.stdout
    if 'progress: 3215' in out:
        print(out.strip()); break
    print(out.strip(), flush=True)
else:
    print('max iters')
