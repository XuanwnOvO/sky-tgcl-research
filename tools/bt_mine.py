# -*- coding: utf-8 -*-
# BehaviorTrees 全量节点类型统计 + 图编辑器坐标确认
import os, json, collections
root = r"d:\新建文件夹\LightEncounters\Children of the Light\Resources\BehaviorTrees"
nt = collections.Counter()
pp = collections.Counter()
for f in sorted(os.listdir(root)):
    bt = json.load(open(os.path.join(root, f), encoding="utf-8"))
    def walk(n):
        if not isinstance(n, dict): return
        nt[n.get("type", "?")] += 1
        for c in n.get("children", []): walk(c)
        if "child" in n: walk(n["child"])
    walk(bt.get("root", {}))
    # position 字段确认（图编辑器坐标）
    def haspos(n):
        if not isinstance(n, dict): return False
        if "position" in n: return True
        return any(haspos(c) for c in n.get("children", [])) or ("child" in n and haspos(n["child"]))
    if haspos(bt.get("root", {})): pp[f] += 1
print("节点类型统计（全部 22 棵树）:")
for t, c in nt.most_common(40):
    print(f"  {c:>4}  {t}")
print("\n含 position(编辑器坐标) 的树:", len(pp), "/", len(os.listdir(root)))
