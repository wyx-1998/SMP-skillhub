---
name: enterprise-qualification-mcp
description: 企业资质证照识别业务场景提示词。负责企业资质场景下的文档分类、实体映射、字段对应和场景专属约束；通用上传、字典、默认值规则继承系统级 skill。

---

# 企业资质材料识别

## 分层说明

- 本 skill 只描述企业资质识别场景自己的业务规则
- 本 skill 不重复定义系统级通用规则，只补充本场景自己的实体、字段和分类口径

## 目标

- 先通过 MCP 工具获取 epiboly 域实体定义、字段和关系，再进行识别
- 分类口径以 MCP 契约为准，不以历史样例为准
- 结构化文件按实体字段提取
- 纯附件类按场景映射直接入库

## 场景执行顺序

1. 识别文件属于企业资质场景的哪一类文档
2. 根据文档类型确定 `entityCode`
3. 调 MCP 获取真实字段定义
4. 按本场景字段对应规则组装识别结果
5. 对字典字段调用系统级字典查询规则
6. 对附件字段调用smp-attachment-rules进行处理
7. 按系统级默认值规则补齐缺失字段后保存

## 当前支持的文档类型与映射

### 专用证照与结构化文件

| 文档类型           | entityCode                       | 处理方式 | 场景说明                                |
| ------------------ | -------------------------------- | -------- | --------------------------------------- |
| 营业执照           | `EpibolyBusiLicenceApply`        | 结构化   | 字段以证照内容提取                      |
| 安全生产许可证     | `EpibolySafeLicenceApply`        | 结构化   | 字段以证照内容提取                      |
| 企业资质证书       | `EpibolyCertificateApply`        | 结构化   | `certificate_type` 由本场景字典规则决定 |
| 三位一体认证       | `EpibolyThreeinoneApply`         | 结构化   | `certificate_type` 由本场景字典规则决定 |
| 名称变更           | `EpibolyRenameApply`             | 结构化   | 原名称 / 新名称                         |
| 法人代表资质证书   | `EpibolyLegalPersonApply`        | 仅附件   | 仅保存图片                              |
| 爆破作业单位许可证 | `EpibolyBlastOperationUnitApply` | 结构化   | 图片数组 + 有效期                       |
| 安全员证书         | `EpibolySafeOfficerApply`        | 结构化   | 人员姓名、证书编号等                    |
| 单位负责人安全证   | `EpibolyFilesApply`              | 结构化   | `type = responsible_certif`             |
| 安全管理人员安全证 | `EpibolyFilesApply`              | 结构化   | `type = safe_certif`                    |
| 技术人员资格证     | `EpibolyFilesApply`              | 结构化   | `type = technician_certif`              |

### 纯附件类

| 文档类型           | entityCode                 | 处理方式 | 场景说明                     |
| ------------------ | -------------------------- | -------- | ---------------------------- |
| 近三年安全绩效证明 | `EpibolyFilesApply`        | 纯附件   | `type = performance`         |
| 安全管理网络图     | `EpibolyFilesApply`        | 纯附件   | `type = safe_net`            |
| 安全生产管理制度   | `EpibolyFilesApply`        | 纯附件   | `type = safe_system`         |
| 安全操作规程       | `EpibolyFilesApply`        | 纯附件   | `type = safe_operate_rule`   |
| 安全生产责任制     | `EpibolyFilesApply`        | 纯附件   | `type = safe_responsibility` |
| 其它审核文件       | `EpibolyOtherExamineApply` | 纯附件   | 兜底分类                     |

## 分类规则

- 先按正文关键词分类；正文没有有效关键词时按文件名分类
- `技术资格证书` / `技术人员资格证` 归 `EpibolyFilesApply`
- `安全员证书` 归 `EpibolySafeOfficerApply`
- `单位负责人安全证`、`安全管理人员安全证`、`技术人员资格证` 归 `EpibolyFilesApply`
- `企业资质证书`、`三位一体认证`、`名称变更`、`营业执照`、`安全生产许可证`、`爆破作业单位许可证` 按专用实体归类
- 文件名命中 `近三年安全绩效证明`、`安全管理网络图`、`安全生产管理制度`、`安全操作规程`、`安全生产责任制` 时归对应 `EpibolyFilesApply`
- 以上都未命中的附件统一归 `其它审核文件`

## 场景字段对应规则

### 1. 通用关联字段

- 主单据关联字段必须按目标实体 与主实体 的真实字段名写入，不硬编码历史字段名
- 若目标实体同时存在主单据 ID、单位 ID、项目 ID 等关联字段，也必须按目标实体真实字段名一并写入

### 2. 场景固定类型字段

- `EpibolyFilesApply.type` 必须按文档类型固定写入：
  - `performance`
  - `responsible_certif`
  - `technician_certif`
  - `safe_certif`
  - `safe_net`
  - `safe_system`
  - `safe_operate_rule`
  - `safe_responsibility`

### 3. 场景专用字段

- `安全生产许可证` 页面还要写入 `certificateOrg`、`permissionCode`、`effectiveBegin`、`effectiveEnd`
- `爆破作业单位许可证` 需要图片数组与有效期
- `法人代表资质证书` 只保存附件，不做结构化字段提取
- 纯附件类只保存实体 JSON 中的名称字段和 `file`

### 4. 场景字典字段

- 企业资质证书、三位一体认证中承载“证书类型”语义的字段，必须按目标实体中带 `codeListKey` 的真实字段写入
- 其它由实体定义标记为字典 / 枚举的字段，同样走系统级字典查询规则

### 5. 场景附件字段

- 所有证照图片、扫描件、证明材料、纯附件类文件，都必须落到实体实际附件字段
- `EpibolyFilesApply`、`EpibolyLegalPersonApply`、`EpibolyBlastOperationUnitApply`、`EpibolyOtherExamineApply` 涉及的附件字段，均先上传再写入

## 保存前场景检查点

每个文件在调用 保存 前，至少输出：

- `entityCode`
- 文档分类结果
- 场景固定字段（如 `type`）是否已正确确定
- 场景专用字段是否已提取
- 关联字段是否已补齐
- 当前文件属于结构化还是纯附件类

## 输出要求

### 识别总览

- 处理文件数
- 识别成功
- 失败
- 不支持
- 待确认

### 识别结果

每类按以下结构输出：

```text
【entityCode】【实体名称】— 成功 / 待确认 / 失败

| 字段 | 提取值 | 状态 |
|------|--------|------|
| xxx（必填） | — | 缺失 |
| yyy | zzz | 正常 |
```

### 结果要求

- 结构化类型必须列出提取字段与缺失字段
- 存在缺失字段的结构化类型必须单独列出 `待确认字段`
- 纯附件类型必须明确标注“仅附件类，不做结构化字段提取”
- 纯附件类型识别成功时，仍应计入 recognized，不要和 failed 混淆
- 失败项必须写清阶段、原因和建议动作
- 不支持项必须写清文件后缀和原因
- summary 口径必须与正文统计一致

### 常见场景错误

#### 1. 实体类型错误

- **错误**：营业执照保存到 `EpibolyOtherExamineApply`
- **正确**：营业执照保存到 `EpibolyBusiLicenceApply`

#### 2. 固定类型值错误

- **错误**：技术人员资格证未写 `type` 或写错 `type`
- **正确**：按文档类型写入固定 `type = technician_certif`

#### 3. 关联字段缺失

- **错误**：保存时未提供 `epiboly_base_applyid`
- **正确**：同时提供 `epiboly_base_applyid` 和 `epiboly_baseid`