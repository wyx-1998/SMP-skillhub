---
name: enterprise-qualification-rules
description: 企业资质识别。
requires:
  - smp-root-rules
  - smp-ocr-rules

---

# 企业资质材料识别

> OCR → 查下表分类 → 按字段提取 → 输出 → 保存。

## 分类

OCR 获取文本后，按下表匹配确定 entityCode：

| 文档类型           | entityCode                                  |
| ------------------ | ------------------------------------------- |
| 营业执照           | `EpibolyBusiLicenceApply`                   |
| 安全生产许可证     | `EpibolySafeLicenceApply`                   |
| 企业资质证书       | `EpibolyCertificateApply`                   |
| 法人代表资质证书   | `EpibolyLegalPersonApply`                   |
| 爆破作业单位许可证 | `EpibolyBlastOperationUnitApply`            |
| 安全员证书         | `EpibolySafeOfficerApply`                   |
| 三位一体认证       | `EpibolyThreeinoneApply`                    |
| 其它审核文件       | `EpibolyOtherExamineApply`                  |
| 近三年安全绩效证明 | `EpibolyFilesApply` / `performance`         |
| 单位负责人安全证   | `EpibolyFilesApply` / `responsible_certif`  |
| 技术人员资格证     | `EpibolyFilesApply` / `technician_certif`   |
| 安全管理人员安全证 | `EpibolyFilesApply` / `safe_certif`         |
| 安全管理网络图     | `EpibolyFilesApply` / `safe_net`            |
| 安全生产管理制度   | `EpibolyFilesApply` / `safe_system`         |
| 安全操作规程       | `EpibolyFilesApply` / `safe_operate_rule`   |
| 安全生产责任制     | `EpibolyFilesApply` / `safe_responsibility` |

未命中兜底 `EpibolyOtherExamineApply`。

## 提取

以目标实体的字段为 OCR 提取目标，逐字段抽取。

## 输出

组装 `<RESULT_JSON>`。`summary`：1.识别成功 / 2.识别失败 / 3.不支持的类型。`data`：OCR 提取的业务字段对象数组，失败 `[]`。

## 保存

- **务必删除脏数据**
- **务必检查要保存的内容是否完整！**
- **一份文件内若识别出多个证件，实现 1对多的记录效果**

用户确认后，遵守 `smp-root-rules`。
