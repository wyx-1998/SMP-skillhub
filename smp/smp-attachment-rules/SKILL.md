---
name: smp-attachment-rules
description: 系统级附件上传规则。负责所有场景的文件上传、上传结果格式和附件字段保存约束。本 skill 为 smp-root-rules 的子 skill，执行前必须先加载 smp-root-rules。
requires:
  - smp-root-rules

---

# 系统级附件上传规则

> **⚡ 前置依赖：本 skill 是 `smp-root-rules` 的子 skill。执行本 skill 前，必须先加载 `smp-root-rules` 的全部内容。`smp-root-rules` 中的保存规则、默认值规则、失败判定为本 skill 的上位规则，发生冲突时以 `smp-root-rules` 为准。**

---

## 适用范围

- 任何业务场景中，只要字段承载文件、图片、PDF、扫描件、压缩包、凭证或附件，就适用本 skill
- 本 skill 只负责通用上传契约，不负责业务场景本身的分类和实体路由
- `bizType` 必须取实际保存目标的 `entityCode`
- `fieldType` 必须取目标实体 `getEntity` 中实际承载附件的字段名
- 若保存目标是主实体下的子实体，则按子实体自己的 `entityCode` 和附件字段上传，不按主实体上传

## 不可跳过规则

- 只要目标字段承载文件、图片、PDF、扫描件、压缩包、凭证，就必须先上传
- 未上传成功前，不得直接调用 `save`（详见 `smp-root-rules` 保存前置门禁）
- 保存时附件字段只能写上传成功返回的 `[{id,name}]` 或 `null`
- 不得把本地路径、原文件名、OCR 文本、Base64 原文直接写入附件字段（详见 `smp-root-rules` 失败条件）
- 当前运行环境若无法发 HTTP、缺少 token / companyId 或 token 过期，必须停止保存并明确报错

## 前置条件

- API 地址：`http://172.20.7.243:8000/smp-api`
- 认证：`Authorization: Sys <JWT_TOKEN>`，token 使用统一认证，调用前检查 `exp` 是否过期
- 额外头：`Cookie: user=<用户名>; token=<JWT>`、`companyId: <公司ID>`

## 入参

| 参数            | 必填 | 说明                                                         |
| --------------- | ---- | ------------------------------------------------------------ |
| `file`          | 是   | 文件二进制内容                                               |
| `fileName`      | 是   | 文件名                                                       |
| `fileSize`      | 是   | 文件大小（字节）                                             |
| `bizType`       | 是   | 业务类型，如 `EpibolyProjectPlanInfo`                        |
| `fieldType`     | 是   | 实体 JSON 中承载附件的字段名，如 `filePlan`                  |
| `refId`         | 否   | 关联记录 ID，无则传 `"null"`                                 |
| `uploadPath`    | 否   | 上传路径，无则传 `"undefined"`                               |
| `attaType`      | 否   | 附件类型，默认空                                             |
| `memo`          | 否   | 备注，默认空                                                 |
| `customDirPath` | 否   | 自定义目录，默认空                                           |
| `dataList`      | 否   | 默认 `[{"id":null,"attaType":"","memo":"","name":"","createName":"","createTime":""}]` |

## 文件校验

- 文件名长度 ≤ 100
- 后缀必须在允许列表内（默认 `.jpg,.jpeg,.png,.pdf,.doc,.docx,.xls,.xlsx`）
- 文件大小 < 50 MB

## HTTP 请求

### 图片文件（后缀 .jpg / .jpeg / .png）

图片统一走压缩上传接口：

```http
POST http://172.20.7.243:8000/smp-api/atta/uploadWithCompress
Content-Type: multipart/form-data; boundary=<BOUNDARY>
Authorization: Sys <JWT_TOKEN>
Cookie: user=<用户名>; token=<JWT_TOKEN>
companyId: <公司ID>

--<BOUNDARY>
Content-Disposition: form-data; name="file"; filename="xxx.png"
Content-Type: image/png

<文件二进制>
--<BOUNDARY>
Content-Disposition: form-data; name="bizType"

EpibolyProjectPlanInfo
--<BOUNDARY>
Content-Disposition: form-data; name="fieldType"

filePlan
...其他字段...
--<BOUNDARY>--
```

### 非图片文件（后缀 .pdf / .doc / .docx / .xls / .xlsx）

非图片文件走普通上传接口：

```http
POST http://172.20.7.243:8000/smp-api/atta/upload
Content-Type: multipart/form-data; boundary=<BOUNDARY>
Authorization: Sys <JWT_TOKEN>
Cookie: user=<用户名>; token=<JWT_TOKEN>
companyId: <公司ID>

--<BOUNDARY>
Content-Disposition: form-data; name="file"; filename="xxx.docx"
Content-Type: application/octet-stream

<文件二进制>
--<BOUNDARY>
Content-Disposition: form-data; name="bizType"

EpibolyProjectPlanInfo
--<BOUNDARY>
Content-Disposition: form-data; name="fieldType"

filePlan
...其他字段...
--<BOUNDARY>--
```

> **路由规则**：根据文件后缀选择端点。`.jpg/.jpeg/.png` → `uploadWithCompress`，其余 → `upload`。两个端点的入参、出参格式完全一致。

## 出参

```json
{"code": 10000, "rows": [{"id": "xxx", "name": "xxx.jpg"}]}
```

- `code == 10000` 为成功
- 取 `rows` 中的每条 `{ id, name }`

## 通用保存规则

保存到实体对应的附件字段，格式（与 `smp-root-rules` 保存规则一致）：

```json
[{"id":"...","name":"..."}]
```

- 有上传结果时必须写上传结果
- 本次输入本就没有该字段附件时存 `null`
- 不得把空字符串、原文件名或临时路径当成附件值

## 通用输出检查点

每次上传完成后，至少输出：

- 字段名
- 文件名
- `bizType`
- `fieldType`
- 上传是否成功
- 返回的 `rows[*].{id,name}`
- 当前字段是否已满足 `smp-root-rules` 保存条件

## 失败判定

出现以下任一情况，视为本步骤失败（与 `smp-root-rules` 失败条件一致）：

- 未上传就直接构造附件字段保存值
- 上传失败后仍继续调用 `save`
- 保存值不是接口返回的 `[{id,name}]`
- 多附件字段漏传任一文件