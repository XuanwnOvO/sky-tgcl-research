# -*- coding: utf-8 -*-
# Resources JSON 定义表全景扫描：每张表的顶层键/条数/样例
import os, json, collections
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Resources"
for f in sorted(os.listdir(root)):
    if not f.endswith(".json"): continue
    p = os.path.join(root, f)
    try:
        data = json.load(open(p, encoding="utf-8"))
    except Exception as e:
        print(f"{f:36} 解析失败: {e}"); continue
    sz = os.path.getsize(p)
    if isinstance(data, list):
        n = len(data)
        keys = sorted(set(k for row in data[:50] if isinstance(row, dict) for k in row))
        print(f"{f:36} list n={n:<6} {sz/1e3:>7.0f}KB keys={keys[:8]}")
        if n and isinstance(data[0], dict):
            print("      样例:", json.dumps(data[0], ensure_ascii=False)[:220])
    elif isinstance(data, dict):
        print(f"{f:36} dict  keys={len(data):<5} {sz/1e3:>7.0f}KB top={list(data)[:6]}")
        k0 = list(data)[0]
        v0 = data[k0]
        print("      样例:", json.dumps({k0: v0}, ensure_ascii=False)[:220])
    print()
