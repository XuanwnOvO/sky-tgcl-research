# -*- coding: utf-8 -*-
# IDA headless 脚本：定位 BstNode 相关符号/函数，导出反汇编与字符串交叉引用
import json, os
import idaapi, idautils, idc, ida_name, ida_funcs, ida_xref

OUT = r"d:\新建文件夹\LightEncounters\ida_out"
os.makedirs(OUT, exist_ok=True)
idc.auto_wait()

report = {"names": [], "funcs_of_interest": {}}

# ① 全局名字里含 BstNode 的
for ea, name in idautils.Names():
    if "BstNode" in name or "bstnode" in name.lower():
        report["names"].append([hex(ea), name])

# ② 每个匹配名字 → 函数边界 + 前几个调用者
for ea, name in idautils.Names():
    if "Deserialize" in name and ("Bst" in name or "Node" in name):
        f = ida_funcs.get_func(ea)
        if f:
            callers = []
            for xr in idautils.XrefsTo(f.start_ea):
                callers.append([hex(xr.frm), idc.get_func_name(xr.frm)])
            report["funcs_of_interest"][name] = {
                "start": hex(f.start_ea), "end": hex(f.end_ea),
                "size": f.end_ea - f.start_ea, "callers": callers[:20]}

json.dump(report, open(os.path.join(OUT, "bstnode_index.json"), "w"), indent=1)
print("names:", len(report["names"]))
print(json.dumps(report["funcs_of_interest"], indent=1)[:3000])
idc.qexit(0)
