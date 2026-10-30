import os, subprocess, sys

ROOT = r"d:\新建文件夹\LightEncounters\Children of the Light"
OUT = r"d:\新建文件夹\LightEncounters\decompiled_lua"
CONV = r"d:\新建文件夹\LightEncounters\tools\tgc2std.py"
CP = r"D:\unluac_build\classes"
TMP = r"D:\tmp_luac"
os.makedirs(TMP, exist_ok=True)

ok = fail = 0
failed = []
for dirpath, dirs, files in os.walk(ROOT):
    for fn in files:
        if not fn.lower().endswith('.luac'):
            continue
        src = os.path.join(dirpath, fn)
        rel = os.path.relpath(src, ROOT)
        outlua = os.path.join(OUT, os.path.splitext(rel)[0] + '.lua')
        os.makedirs(os.path.dirname(outlua), exist_ok=True)
        tmp = os.path.join(TMP, f"{abs(hash(rel))}.luac")
        try:
            r = subprocess.run([sys.executable, CONV, src, tmp], capture_output=True, text=True)
            if r.returncode != 0:
                raise Exception('convert: ' + r.stderr.strip()[-200:])
            r = subprocess.run(['java', '-cp', CP, 'unluac.Main', tmp],
                               capture_output=True, text=True)
            if r.returncode != 0:
                raise Exception('unluac: ' + r.stderr.strip()[-200:])
            with open(outlua, 'w', encoding='utf-8') as f:
                f.write(r.stdout)
            ok += 1
        except Exception as e:
            fail += 1
            failed.append((rel, str(e)[:150]))
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)

print(f"OK {ok}, FAIL {fail}")
for rel, e in failed[:40]:
    print("FAIL", rel, "|", e)
