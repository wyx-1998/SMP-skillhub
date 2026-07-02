---
name: smp-ocr-rules
description: OCR 识别工具。
requires:
  - smp-root-rules

---

# OCR 识别工具

> 只做 OCR，不做保存。缺文件就停。

## 输入

- `question` 必填，默认：`请识别这份文档的类型，并提取关键信息`
- 支持 `.jpg` `.jpeg` `.png` `.gif`，文件必须存在可读
- 只支持图片，不处理 PDF
- 提示词写清：OCR 用文件内容；save 时附件只传 `[{"id":"...","name":"..."}]`

## 工具

```yaml
ocr_vision:
  input:
    filepath: string   # 必填，图片本地路径
    question: string   # 必填
    max_tokens: int    # 可选，默认 2048
  output:
    success: bool
    file: string
    analysis: string
    error: string
```

## 失败

- HTTP 非 200 → `success=false`
- 异常 → `success=false`，`error` 为异常信息
- 无有效文件 → 直接退出

## 并行

多文件并行，默认 `max_workers=4`。`ThreadPoolExecutor` + `as_completed`。单文件失败不影响其他。

## 输出

`summary`：一句话 OCR 结果或错误。`data`：OCR 结果数组，失败时为 `[]`。其余遵守 `smp-root-rules`。