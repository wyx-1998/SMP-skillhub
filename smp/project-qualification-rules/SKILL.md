---
name: project-qualification-rules
description: 工程资质识别。
requires:
  - smp-root-rules
  - smp-ocr-rules

---

# 工程资质材料识别

> OCR → 查下表分类 → 按字段提取 → 输出 → 保存。

## 分类

OCR 获取文本后，按下表匹配确定 entityCode：

| 文档类型               | entityCode                                 |
| ---------------------- | ------------------------------------------ |
| 法人授权委托书         | `EpibolyAuthorizLetterApply`               |
| 承诺书                 | `EpibolyPromiseLetterApply`                |
| 安全协议               | `EpibolySafeAgreementApply`                |
| 项目负责人管理资质     | `EpibolyPmCertifApply`                     |
| 项目安全保证金         | `EpibolyProjectSafetyDepositApply`         |
| 项目经济合同           | `EpibolyFilesApply` / `project_contract`   |
| 四措一案               | `EpibolyFilesApply` / `construction_plan`  |
| 施工方案               | `EpibolyFilesApply` / `construction_plan2` |
| 应急预案               | `EpibolyFilesApply` / `emergency_plan`     |
| 其他审核文件（工程侧） | `EpibolyFilesApply` / `project_other`      |

未命中兜底 `EpibolyFilesApply` / `project_other`。

## 提取

以目标实体的字段为 OCR 提取目标，逐字段抽取。

## 输出

组装 `<RESULT_JSON>`。`summary`：1.识别成功 / 2.识别失败 / 3.不支持的类型。`data`：OCR 提取的业务字段对象数组，失败 `[]`。

## 保存

用户确认后，遵守 `smp-root-rules`。
- **务必删除脏数据**
- **务必检查要保存的内容是否完整！**
- **一份文件内若识别出多个证件，实现 1对多的记录效果**