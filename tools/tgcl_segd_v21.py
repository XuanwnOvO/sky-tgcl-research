# -*- coding: utf-8 -*-
"""segD v21: 找 Marker 定义. segB 行 keyOff 可能为相对文件头(含offset)或段内.
dump 组件名池与 Marker 相关 segB 行, 并 dump 前几个组件名"""
import struct

data = open(r"Children of the Light\Levels\Dawn\Objects.level.bin", "rb").read()
def cstr(off):
    e = data.index(b"\0", off)
    return data[off:e].decode("utf-8", "replace")

# segA: 261 行 12B (nameOff, schemaStart, propCount)
names = []
for i in range(261):
    no, ss, pc = struct.unpack_from("<III", data, 44 + i * 12)
    names.append(cstr(no))
mk = [i for i, nm in enumerate(names) if "Marker" in nm]
print("含Marker的组件:", [(i, names[i]) for i in mk])
print("前10组件名:", names[:10])

# segB: keyOff 试 3 种基准: 绝对文件偏移 / 段内(减55000) / 减o1
# dump 前5行原始
for i in range(5):
    a, ko, tp, e = struct.unpack_from("<IIII", data, 3176 + i * 16)
    print("segB[0]", (a, ko, tp, e), "abs:", cstr(ko) if ko < len(data) else "?")
for i in range(3239):
    a, ko, tp, e = struct.unpack_from("<IIII", data, 3176 + i * 16)
    nm = cstr(ko)
    if "Marker" in nm or "marker" in nm:
        print("segB Marker 行:", i, (a, ko, tp, e), nm)

# schemaStart 区域解码: segA[i].schemaStart 指向 segB 行
mi = mk[0] if mk else None
if mi is not None:
    no, ss, pc = struct.unpack_from("<III", data, 44 + mi * 12)
    print(f"comp[{mi}]={names[mi]} propCount={pc} schemaStart={ss}")
    for p in range(pc):
        a, ko, tp, e = struct.unpack_from("<IIII", data, ss + p * 16)
        print(f"  prop{p}: a={a} key={cstr(ko)} type={tp} e={e}")
