# -*- coding: utf-8 -*-
"""segD 终判: rec = [u32 V][name][payload ...]. 关键问题: payload 界限 = ? 打印前几条记录全字节, 观察 payload 结尾"""
import re, struct
from collections import Counter, defaultdict

P = r"Children of the Light\Levels\Dawn\Objects.level.bin"
data = open(P, "rb").read()
o1, o2, o3, o4, o5 = struct.unpack_from("<5I", data, 24)
c1, c2, c3, c4 = struct.unpack_from("<4I", data, 8)
SEG_D, END = o4, o5

schema = {}
for i in range(c1):
    no, ss, pc = struct.unpack_from("<3I", data, o1 + i*12)
    schema[i] = (data[no:data.find(b"\x00", no)].decode("latin1"), pc)
rows = []
for i in range(c2):
    a, ko, t, e = struct.unpack_from("<4I", data, o2 + i*16)
    rows.append((a, data[ko:data.find(b"\x00", ko)].decode("latin1"), t, e))

pat = re.compile(rb"BstNode_(\d+)\x00")
nodes = [(m.start(), int(m.group(1))) for m in pat.finditer(data, SEG_D)]
Vs = [struct.unpack_from("<I", data, n-4)[0] for n,_ in nodes]

# 打印前 6 条记录的完整字节（到下一节点名前）
for i in range(6):
    n, nid = nodes[i]
    nxt = nodes[i+1][0]
    print(f"\n=== rec{i} id={nid} V={Vs[i]} span={nxt-n} ===")
    print(data[n-4:nxt].hex(' '))

# 记录 span 与 segB 行 (a,key,t,e) 联系: V 是 payload 内的第几个字段?
# 尝试: payload = [u32 e? ...] 找 V 值在 payload 内? 检查 gap 中是否包含下一记录的 V
# 观察: V=0 rec 的 payload: "00 ed 2c 00 00 00 00 00 00 01 00 ff ff ff ff ee 2c 00 00 01 00 00 00"
# 0x2ced = 11469 -> 疑似到 segD 内偏移 or 节点数?  打印 0x2ced 附近含义
print("\nc3 =", c3, " c4 =", c4)
# 0x2ced=11469 < 11501 (BstNode 数) !  0x2cee=11470, 0x2cee? V=1 rec
for i in range(1, 6):
    n, nid = nodes[i]
    e0 = struct.unpack_from("<I", data, n)[0]  # 名后? 不对, n 是名字起点, 名字 "BstNode_.."
    # 名后 2B? 直接 hex 已打印

# 11569? 检查所有记录的 名后前2B 组成 u16?
# 观察 rec0 payload 前 3B: 00 ed 2c -> 不对齐. 也许 payload 从 名后 +1B? "00" 结尾后有 ed 2c 00 00
# 其实 V0 rec: name 含 \0 到 offset n+13.  之后: 00 ed 2c 00 00 00 00 00 00 01 00 ff ff ff ff ee 2c 00 00 01 00 00 00
# 若 payload 起始 = n+14 (跳过1B), 则 u32@n+14 = 0x00002ced = 11469 = 一个节点序号!
# 验证: 名后 1B 再 u32, 记录该值分布
vals1 = Counter()
for n, nid in nodes:
    vals1[struct.unpack_from("<I", data, n+14)[0]] += 1
print("\n[u32 @ name_end+1] distinct:", len(vals1), "top:", vals1.most_common(6))
vals0 = Counter()
for n, nid in nodes:
    vals0[struct.unpack_from("<I", data, n+13)[0]] += 1
print("[u32 @ name_end+0] distinct:", len(vals0), "top:", vals0.most_common(6))
