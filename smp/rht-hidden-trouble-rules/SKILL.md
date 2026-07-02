---
name: rht-hidden-trouble-rules
description: 隐患辅助评估。
requires:
  - smp-root-rules

---

# 隐患辅助评估

> 检索与判读 → 输出 → 保存。

## 查询评估需要的字段
1. 查询系统内评估隐患必须的字段有哪些

## 检索与判读

1. 执行以下命令检索知识库，UTF-8 显式发送，最多重试 2 次：

```bash
printf '%s' '{"query":"<隐患 description>"}' | \
curl.exe -sS "http://172.20.1.91:8087/v1/datasets/9426fd56-6843-425a-8c6c-cd9090ca0f69/retrieve" \
  -H "Authorization: Bearer dataset-BkzVIPaeA1wijiF1fSKm7tAg" \
  -H "Content-Type: application/json; charset=utf-8" \
  --data-binary @-
```

2. 解析返回结果：
   - 命中 → 取 `records[].segment.content`（缺失回退 `sign_content`）
   - 未命中/失败 → `referenceClause` 写 `未命中知识库`
3. 命中引用条款编号+法规名称，不伪造条款

4. 用检索到的条款和 `description`，按 `rht-hidden-trouble-methodology.md` 判读


## 辅助工具

评估时可使用 `references/hidden-danger-image-api.md` 中的图片识别 API 分析隐患图片内容。

两个可用端点：

- **`POST /ImageReco_HiddenDanger/` + `imgfile`** — 返回 JSON `analysisDetails.content`，结构化程序友好
- **`POST /streaming/hidden_danger` + `image_file`** — 返回纯文本，含法规依据条款引用

该服务独立于 SMP 系统，FastAPI 应用，可通过 `/docs` 发现全部接口。

## 输出

组装 `<RESULT_JSON>`。`summary`：一句话结果或错误。`data`：评估结果对象数组，data 输出的值必须是可读文本，而不是字典项 id，失败 `[]`。
`button`：按钮数组，输出 `[{"label":"回填评估信息","value":"setRhtHiddenTrouble"}]`。

## 保存

用户确认后，遵守 `smp-root-rules`。必须填 `referenceClause`，没有写 `未命中知识库`。