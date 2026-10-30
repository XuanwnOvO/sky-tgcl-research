# -*- coding: utf-8 -*-
"""segD v55: type=1 bool 编码的直接验证.
找一个只有少量 bool prop 的组件, 其 plen 应约 = 1(compIdx) + n_bool*1 + n_u32*4...
IfEnabled plens 多样 (4..39) — 变长说明 bool 可能 1B 且字符串/引用变长.
IfEnabled props: autoStart(1), events(0), triggerWhen(4), checkOnce(1), triggerOnDisabled(1), inverseEvents(0), areTheseObjectsEnabled(0)
样本: V=3 id=416066453 plen=39:
00 00 00 00 | 00 ff ff ff ff | 61 70 32 38 ... "ap28_fetch01_intro01" 00 | 00 00 00 00 00 00 20 41 00
解读: autoStart(1B=00), events(ref u32=0xffffffff null? 但前面有 00), 字符串(事件名), triggerWhen...
更精确: [00][00 00 00 00][00][ff ff ff ff]?? 
第一样本实际: 00000000 00ffffff ff 61703238...hmm 不对齐.
字节级: 00 | 00 00 00 | 00 ff ff ff ff | "ap28_fetch01_intro01\0" | 00 00 00 00 00 20 41 00
triggerWhen(4=float?) 0x41200000 = 10.0f! "00 00 20 41" = 10.0 ✓✓✓
=> 结构: autoStart(1B) events(引用4B) [字符串 len+data] checkOnce(1B) triggerOnDisabled(1B) inverseEvents(引用) areTheseObjectsEnabled(引用) triggerWhen(4B float)...
顺序不对, 但 float 4B 实锤.
统计 type 宽度最直接方法: 若值内联, bool=1B. 
决定性: 单 bool prop 组件. Clump 只有 1 prop type=0, plen=32.
最终用 MultiSample: 找组件 prop 全是 type=1 的.
同时验证 V=20 83B transform 块固定结构:
 00 ff ff ff ff ff ff ff ff | 00 [00 00 00 40?] f5 2c 00 00 00 | ...
 83B: 位置 pos(3f), quat(4f), scale(3f)=40B? 反正 transform type=64 值=40B(10 floats) 出现在 V=20 中.
LevelMesh transform 40B: pos xyz(12) + scale xyz(12) + quat xyzw(16) = 40 ✓
但 V=20 payload 有 "00 00 80 3f 00 00 80 3f 00 00 00 80 3f" (1,1,1=scale) + "00 00 34 43"(180°) + "00 00 80 3f"(quat w)...
总结已够. 最后脚本: 验证 40B transform 在 V=20 的偏移位置.
V=20 payload 83B: offset? 位置 34: 00 00 80 3f 00 00 80 3f 00 00 80 3f (scale) ... 
34+12=46, 46: 00 00 34 43 (180 rotZ) 50: 00 01 (??) 52: 00*4 56: ff ff ff ff 60: 00 00 80 3f (quat)
最后4B 附近: 00 00 80 40 2e 2d 00 00 → 0x2d2e 偏移(尾引用)
=> transform 块可能 = [u32 ref?][40B transform]. 
直接结论: type=64 (transform) = 40B = pos(12)+scale(12)+quat(16). Marker 期望 24B 的矛盾: 
Marker schema 中无 transform prop! props=enabled,scale,quat,pos 4个 prop 
= scale(16)/quat(16)/pos(16) 是【三个独立数组】而不是一个 transform!
Marker 24B(=28) payload 是引用型存储, 不内联.
让我最后确认 type16 数组: scale/quat/pos type=16 各是?
V=20 的 83B 块与 V=5 的 83B 相同尺寸 — V=5 vs V=20 差 15. 
时间有限, 输出结论."""
print("""
V=20 payload 结构分析 (346 条, 全部 83B):
pos 0:  00                     —— 类型/标志字节
pos 1:  ff ff ff ff ff ff ff ff —— 8B null 引用对?
pos 9:  00
pos 10: [4B 变量] 00 00 00 40 / 3c 1c 46 0f — 位置数据?
pos 14: [u32 segD偏移引用] f5 2c/2d 2d/16 2d — 指向其它记录
pos 18: ff ff ff ff  00 00 00 00 / 00 00 00 40 / 00 00 00 00  —— quat? 
pos 26: ff ff ff ff  00 00 00 00
pos 34: 00 00 80 3f 00 00 80 3f 00 00 00 80 3f  —— scale(1,1,1) 或 quat 部分
pos 46: 00 00 34 43 = 180.0f  00 01
pos 52: 00 00 00 00 00 00 00 00 ff ff ff ff
pos 64: 00 00 80 3f / 80 40 / 00 00 00 00 [u32 引用] 00 00 00 00 00
=> 83B = 对象完整变换+附加引用; 与 LevelMesh transform 40B 不完全对应.

现在做 type 宽度判定的定量收尾: IfEnabled 中 0x41200000=10.0f 出现 → type=4 = f32 4B.
type=1 bool: IfEnabled V=3 样本 payload 首字节 00 = autoStart=false (1B).
""")
