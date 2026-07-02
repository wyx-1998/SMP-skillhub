---
name: hidden-danger-recognition
description: 安全隐患图像识别。
requires:
  - smp-root-rules

---

# 安全隐患图像识别

> 文件校验 → 接口识别 → 解析结果 → 输出。只识别，不保存。

## 文件校验

| 校验项 | 规则                     |
| ------ | ------------------------ |
| 路径   | 文件必须存在且可读       |
| 后缀   | 仅 `.jpg` `.jpeg` `.png` |
| 大小   | 大于 0 字节              |

校验失败就停。

## 工具

```yaml
hidden_danger_detect:
  input:
    filepath: string   # 必填，图片绝对路径
    timeout: int       # 可选，默认 120s
  output:
    success: bool
    items: array
      - description: string   # 隐患描述
        request: string        # 整改建议
        standard: string       # 法规依据（国标/行标引用），可能为空
    error: string
```

## 服务状态检测（前置）

发起大文件上传前先用小请求探测服务器是否存活，避免浪费 120s 等待。

```bash
# 基础生存检测：TCP 可达且返回了 HTTP 响应（非空）
curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 --max-time 10 http://<host>:<port>/ 2>&1

# 如果返回 "000" → TCP 通但应用层无响应（服务挂了或重启中）
# 如果返回 "200"/"405" → 服务正常
# 如果返回 "404" → 端点可能已迁移，用 /docs 或 /openapi.json 发现
```

也可以用技能自带的检测脚本（需先 `chmod +x`）：

```bash
bash scripts/check-server.sh http://101.204.230.42:2044
```

预期输出说明：

| 输出前缀 | 含义 | 下一步 |
|---------|------|--------|
| `ALIVE` | 服务正常运行 | 继续上传 |
| `WARN` | TCP 通但 HTTP 无响应 | 等一会重试，或联系运维重启服务 |
| `INFO` | 端点 404 / 其他状态码 | 用端点发现技巧找到正确路径 |
| `FAIL` | 服务完全不可用 | 停止，报告用户 |

## 端点发现技巧

如果已知端点返回 404，或需要查找可用接口，探测 FastAPI 文档端点：

```bash
# 检查 Swagger 文档
curl -s http://<host>:<port>/docs | head -5

# 获取 OpenAPI 规范，列出所有可用端点
curl -s http://<host>:<port>/openapi.json | python3 -c "
import json, sys
d = json.load(sys.stdin)
for path, methods in d.get('paths', {}).items():
    for method, info in methods.items():
        print(f'{method.upper():7s} {path}  — {info.get(\"summary\",\"\")}')
"
```

若 OpenAPI 文档也无法获取（空响应），则服务应用层已停止响应，需联系运维重启。

此技巧适用于任何 FastAPI 服务。

## 请求

### 端点一：`/ImageReco_HiddenDanger/`（推荐 — 结构化 JSON）

返回结构化的 `analysisDetails.content` 数组，每项含 `description` + `request`，干净无重复。

```bash
curl -X POST http://101.204.230.42:2044/ImageReco_HiddenDanger/ \
  -F "imgfile=@<文件路径>" \
  --connect-timeout 30 \
  --max-time 120
```

### 端点二：`/streaming/hidden_danger`（含法规依据）

返回纯文本，每条带隐患依据国标/行标引用，但重复项较多。

```bash
curl -X POST http://101.204.230.42:2044/streaming/hidden_danger \
  -F "image_file=@<文件路径>" \
  --connect-timeout 30 \
  --max-time 120
```

**选择建议：** 需要机器处理 → 用端点一（JSON 直接解析）；需要追溯法规依据 → 用端点二（含标准条款）。

### 带知识库的识别端点

额外支持 `pdf_id_list` 参数，将识别结果与知识库文档关联：

```bash
curl -X POST http://101.204.230.42:2044/streaming/hidden_danger_knowledge_base \
  -F "image_file=@<文件路径>" \
  -F 'pdf_id_list=["doc_id_1","doc_id_2"]' \
  --connect-timeout 30 \
  --max-time 120
```

## 结果解析

| 条件 | 处理 |
|------|------|
| HTTP 非 200 | 返回错误 |
| 200 响应为 JSON（端点一/旧版） | 取 `analysisDetails.content` 数组 |
| 200 响应无隐患（JSON 中 `no_split` 含关键词） | 返回空结果 `summary: "未识别到安全隐患"` |
| 200 响应为纯文本编号列表（端点二） | `data` = 逐项拆解为数组 |

### 格式一：JSON（端点一 `/ImageReco_HiddenDanger/`）

```json
{
  "name": "文件名",
  "analysisDetails": {
    "description": "",
    "no_split": "汇总文本（可能为空）",
    "content": [
      {"description": "隐患描述", "request": "整改建议"},
      ...
    ],
    "time_consuming": 5.09
  }
}
```

`data` = `content` 数组。`no_split` 若含"没有安全隐患"则无结果。

### 格式二：纯文本（端点二 `/streaming/hidden_danger`）

每项格式如下：

```
<序号>.<隐患描述>。整改措施：<整改建议>。
隐患依据：<国家标准/行业标准>第<条号>条。<条文内容>。
```

示例：

```
1.管道未固定，存在跌落风险。整改措施：固定管道。
隐患依据：《固定式升降工作平台》（JB/T 11169-2011）第5.5.2条。
2.地面上有散落的物品和杂物，可能会造成滑倒或绊倒。整改措施：清扫地面，确保整洁。
隐患依据：《危险化学品企业特殊作业安全规范》（GB 30871-2022）第8.2.7条。
```

### 已知问题

- **重复项较多**（端点二）：同一张图可能产出大量相似项，输出时需要去重或汇总。
- **文本截断**（端点二）：响应可能被后端截断，接收时要判断是否完整。
- 端点一 JSON 输出干净无重复，推荐程序化使用。

### 纯文本→结构化（端点二专用）

```python
import re

def parse_hidden_danger_response(text: str) -> list[dict]:
    """将纯文本响应解析为结构化列表"""
    items = []
    pattern = re.compile(
        r'(?P<num>\d+)\.(?P<desc>.+?)整改措施：(?P<request>.+?)(?:隐患依据：(?P<standard>.+?))?(?=\d+\.|$)',
        re.DOTALL
    )
    for m in pattern.finditer(text):
        items.append({
            "description": m.group("desc").strip().rstrip("。"),
            "request": m.group("request").strip().rstrip("。"),
            "standard": m.group("standard").strip().rstrip("。") if m.group("standard") else ""
        })
    return items
```

## 输出

`summary`：识别结果摘要（首项描述或错误信息）。`data`：结构化数组 `[{description, request}]`（纯文本解析后），失败时为 `[]`。`standard` 字段（法规依据）存在时保留在 data 中。

`button`：按钮数组，输出 `[{"label":"去随手拍登记","value":"setDescription"}]`。

其余遵守 `smp-root-rules`。