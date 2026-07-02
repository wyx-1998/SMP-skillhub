# SMP-skillhub

SMP 系统 Skill 仓库，用于沉淀 OCR、资质识别、隐患识别、隐患评估和法规知识库等场景的规则与实现。

仓库同时保留两种形态：

- **源码目录**：便于阅读、维护和二次开发
- **zip 包**：便于分发和导入到目标环境

## 目录结构

```text
.
├── legal-regulation-kb/
│   └── SKILL.md
└── smp/
    ├── DESCRIPTION.md
    ├── enterprise-qualification-rules/
    ├── enterprise-qualification-rules.zip
    ├── hidden-danger-recognition/
    ├── hidden-danger-recognition.zip
    ├── project-qualification-rules/
    ├── project-qualification-rules.zip
    ├── rht-hidden-trouble-rules/
    ├── rht-hidden-trouble-rules.zip
    ├── smp-ocr-rules/
    ├── smp-ocr-rules.zip
    ├── smp-root-rules/
    ├── smp-root-rules.zip
    └── vision-ocr/
```

## 技能一览

| 名称 | 位置 | 作用 |
| --- | --- | --- |
| `smp-root-rules` | `smp/smp-root-rules/`、`smp/smp-root-rules.zip` | 系统级根规则，统一输出契约、上下文透传和保存门禁 |
| `smp-ocr-rules` | `smp/smp-ocr-rules/`、`smp/smp-ocr-rules.zip` | 图片 OCR 识别，只做识别，不做保存 |
| `vision-ocr` | `smp/vision-ocr/` | 并行 OCR 工具实现，适合图片与扫描件处理 |
| `enterprise-qualification-rules` | `smp/enterprise-qualification-rules/`、`smp/enterprise-qualification-rules.zip` | 企业资质材料识别 |
| `project-qualification-rules` | `smp/project-qualification-rules/`、`smp/project-qualification-rules.zip` | 工程资质材料识别 |
| `hidden-danger-recognition` | `smp/hidden-danger-recognition/`、`smp/hidden-danger-recognition.zip` | 安全隐患图像识别，只识别不保存 |
| `rht-hidden-trouble-rules` | `smp/rht-hidden-trouble-rules/`、`smp/rht-hidden-trouble-rules.zip` | 隐患辅助评估与知识库判读 |
| `legal-regulation-kb` | `legal-regulation-kb/` | 法规/合规知识库检索与问答 |

## 推荐使用顺序

1. 先加载 `smp-root-rules`，确认统一输出格式和保存门禁。
2. 涉及图片识别时，再加载 `smp-ocr-rules` 或 `vision-ocr`。
3. 再进入具体业务 skill，例如资质识别、隐患识别或法规判读。
4. 所有输出都遵循 `<RESULT_JSON>`：`summary`、`data`、`button`。
5. 如果需要保存，先完成识别/判读并等待用户确认。

## 输出约定

- `summary`：一句话结果或错误说明。
- `data`：业务字段数组；无结果或失败时返回 `[]`。
- `button`：仅包含 `label` 和 `value`。
- 识别或判读不确定时，不要臆测，直接停下或继续追问。
- 附件保存时只传 `id` 与 `name`，不补路径或内容。

## 维护说明

- 新增 skill 时，优先复用 `smp-root-rules` 的统一契约。
- 目录命名尽量与技能名一致，方便检索与维护。
- 资源文件可放在 `references/`，脚本可放在 `scripts/`。
- `.DS_Store` 等系统文件不建议提交到仓库。

## 说明

本仓库适合直接作为 SMP 系统的 skill 资源包使用，也方便后续继续拆分、打包和发布。
