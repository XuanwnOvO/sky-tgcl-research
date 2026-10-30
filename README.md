# sky-tgcl-research

《光·遇》(Sky: Children of the Light) 国服 Android 客户端**静态逆向研究**的完整方法记录与工具集。44 批次分析日志、TGCL 场景图格式全解、自研关卡数据导出器。

> ⚠️ 仅供学习研究使用。不含任何游戏本体文件、解包资源或衍生二进制。

## 核心成果

### 1. TGCL 格式 100% 破解（`Objects.level.bin` 场景序列化格式）

44B 头 + 五段布局：

| 段 | 内容 |
|---|---|
| segA | 组件类型表：`u32 nameOff / schemaStart / propCount` ×12B |
| segB | 属性 schema 表：`(a, keyOff→segC, type, e)` ×16B |
| segC | 全局字符串池（NUL 分隔，100% 可读） |
| segD | 记录链：`[u32 V][BstNode_<id>\0][payload][next V]` |

- **V 局部性定理**：记录种类由 payload 模板（长度+固定字节签名）定义，V 是每关独立索引，不可跨关
- 引用体系：rec-index（记录数组下标），对象组 = `id>>8`，值不内联
- **BST = Behavior Stream Tree**；`bstGuid` 是运行时对象 ↔ 关卡记录的桥

### 2. 终局导出器 `tools/tgcl_final_export3.py`

按模板+结构启发判读（bigblock → transform 49B → component_slot → fixed），四关验证全绿：nextV 链 100%、NaN 0、ref_in_range 93-98%。导出 JSON 含 components/slots/transforms/clusters/groups。

### 3. 明文层全收割

- 148 个 Lua（unluac）、50 张 JSON 定义表（WorldQuestDefs/NpcDefs/OutfitDefs…含 Netease 特调表）
- 22 棵明文行为树（含 TGC 官方图编辑器坐标）
- Vars 调参字典、Hot-Date 热更机制、LevelSelect 路由表

## 仓库结构

- `玩法与社交类硬分析指南.md` —— **主文档，44 批全记录**（Barn 体系/RPC 注册/hash 机制/TGCL/货币/成就/社交玩法）
- `tools/` —— 207 个分析脚本（终局主力 `tgcl_final_export3.py`）
- `tgcl_final3_*.json` —— 四关终局导出产物
- `光遇引擎字段清单.md` / `光遇引擎类与方法清单.md` / `光遇逆向收官速查表.md` —— 专项索引

## 遗留工作

1. IDA 反汇编精读 `BstNode::Deserialize`（搜 `"BstNode_"` 字符串引用）→ 点名 V=9/14/391B 头部
2. 运行时 hook：`DevHost::Listen`、`sub_3361078` hash 算法、`word_4D265FC` 调试位
3. 远程资源 `remotelist.bin`（子关卡 .level 的玩法逻辑所在）
