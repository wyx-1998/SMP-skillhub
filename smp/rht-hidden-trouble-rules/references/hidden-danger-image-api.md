# 隐患图片识别 API

> 独立于 SMP 系统的隐患图片识别服务，可辅助评估时分析隐患图片内容。

## 服务地址

```
http://101.204.230.42:2044
```

是 FastAPI 应用，可通过 `/docs`（Swagger UI）或 `/openapi.json` 发现全部接口。
若已知路径返回 404，优先检查这两个端点。

## 接口

### 端点一：`/ImageReco_HiddenDanger/` POST（推荐 — 结构化 JSON）

返回 JSON，`analysisDetails.content[]` 含每项的 `description` + `request`，干净无重复。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `imgfile` | binary (file) | 是 | 隐患图片（.jpg/.png 等） |

```bash
curl -X POST http://101.204.230.42:2044/ImageReco_HiddenDanger/ \
  -F "imgfile=@/path/to/image.png" \
  --connect-timeout 30 --max-time 120
```

响应格式：

```json
{
  "name": "文件名",
  "analysisDetails": {
    "content": [
      {"description": "隐患描述", "request": "整改建议"},
      ...
    ],
    "no_split": "汇总文本（无隐患时为'图片中没有安全隐患。'）",
    "time_consuming": 5.09
  }
}
```

### 端点二：`/streaming/hidden_danger` POST（含法规依据）

返回纯文本，每条带隐患依据国标/行标引用（如 GB 30871-2022 第8.2.7条），但重复项较多。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `image_file` | binary (file) | 是 | 隐患图片（.jpg/.png 等） |

```bash
curl -X POST http://101.204.230.42:2044/streaming/hidden_danger \
  -F "image_file=@/path/to/image.png" \
  --connect-timeout 30 --max-time 120
```

响应格式：

```
1.<隐患描述>。整改措施：<整改建议>。
隐患依据：《标准名称》（GB/T XXXX-XXXX）第X.X.X条。
```

### 端点三：`/streaming/hidden_danger_knowledge_base` POST

识别隐患图片并关联知识库检索。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `image_file` | binary (file) | 是 | 隐患图片 |
| `pdf_id_list` | array[string] | 是 | 知识库 PDF ID 列表 |

### 其他可用端点（来自 /openapi.json）

- `/streaming/certificate` POST — 证书识别
- `/streaming/images_texts_chat` POST — 图文对话

## 服务诊断

调用前用快速探针确认存活，避免等 120s 超时：

```bash
# 快速存活检测
STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 http://101.204.230.42:2044/)
case "$STATUS" in
  000) echo "服务无响应（TCP通但应用层挂）" ;;
  200|405) echo "服务正常" ;;
  404) echo "端点不存在 — 检查 /docs 或 /openapi.json" ;;
  *) echo "状态码 $STATUS" ;;
esac
```

常见状态：

| 现象 | 诊断 | 处理 |
|------|------|------|
| curl 返回 000 / Empty reply / Broken pipe | 服务应用层挂了 | 联系运维重启，或等一会重试 |
| HTTP 404 | 路径不对 | 用 /docs 或 /openapi.json 发现正确路径 |
| HTTP 200 | 正常 | 继续按照下述接口文档调用 |

## 选择建议

| 需求 | 推荐端点 |
|------|---------|
| 程序化处理（需要干净结构化数据） | `/ImageReco_HiddenDanger/` + `imgfile` |
| 追溯法规依据（需要标准条款引用） | `/streaming/hidden_danger` + `image_file` |
