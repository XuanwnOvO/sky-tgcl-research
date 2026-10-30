# -*- coding: utf-8 -*-
"""segD v54: V=0 的 b@14 u16 都是 xx xx 的高值? 63487=0xF7FF, 52223=0xCBFF... 
全部是 0x??FF 模式! = [u8 high][0xFF]. 即 byte15=? byte14=u8N.
读 p[14] 与 p[15]: 样例1: ee 2c → 14=0xee? 不对样例1 p[14:16]=ee 2c=0x2cee.
p[15] 是 00 (u32@14 之前算出 0x2cee). 
上面 u16@14 显示 63487 等 → p[15]=0xFF? 混乱, 直接 dump p[13:19].
等下 19B payload 索引 0..18. u16@14 = p[14:16], 还有 p[16:19] 3B.
样例1 p = 00 ed 2c | 00 00 00 00 00 | 00 01 00 | ff ff ff ff | ee 2c 00 00
分解: [00][u16 A][u8?][...]  
A=0x2ced=11501, 然后 5B 0, 然后 00 01 00, ff*4, ee 2c 00 00 = 0x2cee=11502.
样例3: A=11523, 中间 p[5]=01, p[9]=01, ff*4, 尾 0x03ec=1004.
样例 (344523086): 00 e9 02 ... 尾 7b 2d = 0x2d7b=11643.
=> 结构猜测: [00][u32 start][u32 ?][01 00][u32 -1][u32 end]? 
样例1: start=0x2ced? 但 A 只有 u16...
真正的分解: p[0]=00, p[1:5]=u32(0x2ced), p[5:9]=u32(0), p[9]=01, p[10]=00, p[11:15]=-1, p[15:19]=u32(0x2cee)
→ [00][u32 11501][u32 0][b9=1][b10=0][u32 -1][u32 11502]
样例3: [00][11523][u32@5=1][b9=1][b10=1][u32 -1][u32 1004]
=> 尾 u32 = ? 样例1 11502=start+1; 样例3 1004. 
啊! 【尾 u32 = BST 子节点范围】? 11501..11502 = 记录 index 区间 (1-based)!
V=0 = BST 内部节点声明子树 index 区间!
样例3 start=11523?? > 11501. 矛盾. 除非不是 index.
换: u32@1 可能是【字符串池偏移/其它】.
算了, 证据不足. 用另一个决定性方法: 看 V=0 记录的名字 id! 2310602845 vs 其它. 
其实关键问题不在这. 回到主线: 需要最终结论. 已有足够证据输出:
1. 结构: [u32 V][BstNode_id][payload][u32 nextV], V-chain 11500/11500
2. type 编码: 从组件值块可以推导...
做最后一个脚本: 用 AudioMixToHaptics (5条, 88B) 和 schema props 推 type 宽度.
props: autoStart(1),enable(1),mixChannel(4),fadeInSeconds(4),intensity(4)
但值可能是引用. DialogHintTimed 160条 plen=16 = compIdx+3 refs.
type 4 (float) 值在 V=20 (346条 83B) 中出现内联: transform...
其实 V=20 = 固定 83B 模板 = LevelMesh 的 transform 存储块.
最后验证: V=20 83B 恰好 = transform 的内联编码? 83 = 1 + ...?"""
