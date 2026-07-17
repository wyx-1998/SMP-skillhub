---
name: project-qualification-mcp
description: 工程资质识别业务场景提示词。负责工程资质场景下的文档分类、实体映射、字段对应和场景专属约束；通用上传、字典、默认值规则继承系统级 skill。

---

# 工程资质材料识别

## 分层说明

- 本 skill 只描述工程资质识别场景自己的业务规则
- 本 skill 不重复定义系统级通用规则，只补充本场景自己的实体、字段和分类口径

## 目标

- 先通过 MCP 工具获取 epiboly 域实体定义、字段和关系，再进行识别
- 分类口径以 MCP 契约为准，不以历史样例为准
- 结构化文件按实体字段提取
- 纯附件类按场景映射直接入库

## 场景执行顺序

1. 识别文件属于工程资质场景的哪一类文档
2. 根据文档类型确定 `entityCode`
3. 调 mcp 工具 获取真实字段定义
4. 按本场景字段对应规则组装识别结果
5. 对字典字段调用系统级字典查询规则
6. 对附件字段调用系统级附件上传规则
7. 按系统级默认值规则补齐缺失字段后保存

## 文档类型与映射

| 文档类型           | entityCode                         | 处理方式 | 场景说明                         |
| ------------------ | ---------------------------------- | -------- | -------------------------------- |
| 法人授权委托书     | `EpibolyAuthorizLetterApply`       | 结构化   | 代理人、授权人、有效期、授权方式 |
| 安全协议           | `EpibolySafeAgreementApply`        | 结构化   | 协议名称、有效期                 |
| 项目负责人管理资质 | `EpibolyPmCertifApply`             | 结构化   | 人员姓名、证书编号、有效期       |
| 项目安全保证金     | `EpibolyProjectSafetyDepositApply` | 结构化   | 保证金金额、缴纳日期、凭证图片   |
| 承诺书             | `EpibolyPromiseLetterApply`        | 纯附件   | 仅附件                           |
| 项目经济合同       | `EpibolyFilesApply`                | 纯附件   | `type = project_contract`        |
| 四措一案           | `EpibolyFilesApply`                | 纯附件   | `type = construction_plan`       |
| 施工方案           | `EpibolyFilesApply`                | 纯附件   | `type = construction_plan2`      |
| 应急预案           | `EpibolyFilesApply`                | 纯附件   | `type = emergency_plan`          |
| 其他审核文件       | `EpibolyFilesApply`                | 纯附件   | `type = project_other`，兜底分类 |

## 分类规则

- 先按正文关键词分类；正文没有有效关键词时按文件名分类
- 命中 `授权人`、`代理人`、`有效期` 的归 `法人授权委托书`
- 只体现承诺内容和签章的归 `承诺书`
- 文件名命中 `四措一案` 的归 `四措一案`
- 文件名命中 `施工方案` 的归 `施工方案`
- 文件名命中 `应急预案` 的归 `应急预案`
- 以上都未命中的工程附件统一归 `其他审核文件`

## 场景字段对应规则

### 1. 通用关联字段

- 所有子表记录都必须写入 `epiboly_base_applyid` 和 `epiboly_baseid`
- 非 `EpibolyFilesApply` 子表同样必须写入主单据关联字段

### 2. 场景固定类型字段

- `EpibolyFilesApply.type` 必须按文档类型固定写入：
  - `project_contract`
  - `construction_plan`
  - `construction_plan2`
  - `emergency_plan`
  - `project_other`

### 3. 场景专用字段

- `法人授权委托书` 需要提取代理人、授权人、有效期、授权方式
- `安全协议` 需要提取协议名称、有效期
- `项目负责人管理资质` 需要提取人员姓名、证书编号、有效期
- `项目安全保证金` 需要提取保证金金额、缴纳日期、凭证图片
- `承诺书` 只保存附件，不做结构化字段提取
- 纯附件类只保存实体 JSON 中的名称字段和 `file`

### 4. 场景字典字段

- 本场景中若 `MCP 工具` 返回字典 / 枚举字段，按系统级字典查询规则处理
- 未命中时默认值仍取对应字典第一项 `dkey`

### 5. 场景附件字段

- 承诺书、项目经济合同、四措一案、施工方案、应急预案、其他审核文件的附件都必须落到实体实际附件字段
- 项目安全保证金中的凭证图片属于附件字段，必须先上传再写入

## 保存前场景检查点

每个文件在调用 `保存` 前，至少输出：

- `entityCode`
- 文档分类结果
- 场景固定字段（如 `type`）是否已正确确定
- 场景专用字段是否已提取
- 关联字段是否已补齐
- 当前文件属于结构化还是纯附件类

## 违规场景判定

出现以下任一情况，视为场景规则未满足：

- 文档分类和实体映射不一致
- `EpibolyFilesApply.type` 未按本场景固定值写入
- 结构化文档漏提取本场景要求的关键字段
- 纯附件类误走结构化字段提取

## 常见场景错误

#### 1. 附件类落错实体

- **错误**：项目经济合同保存到 `EpibolyOtherExamineApply`
- **正确**：项目经济合同保存到 `EpibolyFilesApply` 且 `type = project_contract`

#### 2. 固定类型值错误

- **错误**：四措一案写成 `construction_plan2`
- **正确**：四措一案固定为 `construction_plan`

#### 3. 结构化与纯附件混淆

- **错误**：承诺书按结构化字段抽取后保存
- **正确**：承诺书仅保存附件

#### 4. 关联字段缺失

- **错误**：保存时未提供 `epiboly_base_applyid`
- **正确**：同时提供 `epiboly_base_applyid` 和 `epiboly_baseid`