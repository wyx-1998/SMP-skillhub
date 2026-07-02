---
name: smp-root-rules
description: SMP MCP 系统级根规则。定义统一调用顺序、字段契约、上下文透传和保存门禁。
priority: 1
children:
  - smp-ocr-rules
---

# SMP MCP 系统级根规则

> 子 skill 只引用本文件，不重复定义通用规则。缺字段、缺关系、缺 where 条件就停，不要猜。

## 1. 统一输出契约

所有 skill 最终输出使用同一格式，只允许这 3 个顶层字段：`summary`、`data`、`button`。

```text
<RESULT_JSON>
{
  "summary": "一句话结果或错误",
  "data": [{"字段code值": "值"}],
  "button": [{"label": "按钮名称", "value": "前端按钮key"}]
}
</RESULT_JSON>
```

- `summary`：skill执行结果。
- `data`：JSON 数组，元素为业务字段对象；失败或空结果时为 `[]`。
- `button`：JSON 数组，数组元素是 JSON 对象，只能包含 `label` 和 `value`；没有按钮时返回 `[]`。
- 只允许这 3 个字段，不得输出任何其他顶层字段。
- 标签必须存在，标签外不写正文。

## 2. 通用前置顺序

| 顺序 | skill | 约束 |
|------|------|------|
| 1 | `smp-root-rules` | 先读根规则 |
| 2 | `smp-ocr-rules` | 需要 OCR 时先加载 |
| 3 | 业务场景 skill | 再进入具体业务流程 |

**没按顺序，不要执行 `save` / `remove` / `execute`。**

## 3. 保存门禁

先输出 `<RESULT_JSON>`，用户确认后，再执行 `save` / `remove` / `execute`。

`save` 前按顺序检查：

1. `getEntity(entityCode)` 获取实体定义
2. 同一主单据下有旧记录 → 先删旧（需保留历史时按业务指定处理）
3. 子实体外键已按 `relations.children.<childName>.foreignKey` 注入
4. 所有必填字段有值，不放实体 JSON 没有的字段
5. 字段值明确，不伪造。仅 `fallback` 字段可用默认值，默认值不补 `required`
6. 没有空记录或重复记录

### 附件

附件字段先带文件内容和元数据；save 时只传 `[{"id":"xxx","name":"xxx.pdf"}]`。不补路径或内容。

## 4. 查询规则

1. `getData` 前先 `getEntity`
2. 带 `codeListKey` 的字段，取 `dictOptions` 中的值
3. where 条件用以下格式，不省略任何字段：

```json
{"field":"字段名","opt":"=","value":"值","assemble":"and"}
```

| 字段 | 值 |
|------|------|
| `field` | `getEntity` 返回的字段名 |
| `opt` | `=` `like` `>` `<` `>=` `<=` `!=` `in` `notIn` |
| `value` | 匹配值 |
| `assemble` | `and` / `or`；单条件固定 `"and"` |

## 5. 上下文透传

`save` / `remove` / `execute` 的 `context` 只透传：

```json
{
  "userCtx": {},
  "dataCtx": {},
  "webCtx": {},
  "extCtx": {}
}
```