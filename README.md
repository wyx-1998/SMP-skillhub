# SMP-skillhub

SMP 系统 Skill 资源仓库，集中存放面向 OCR、资质材料识别、隐患图像识别、隐患辅助评估和法规知识库问答的规则与技能包。仓库内每个 skill 都通过 `SKILL.md` 定义能力边界、依赖关系和输出规范。

## 仓库结构

```text
.
├── legal-regulation-kb/
│   └── SKILL.md
└── smp/
    ├── DESCRIPTION.md
    ├── enterprise-qualification-rules.zip
    ├── hidden-danger-recognition.zip
    ├── project-qualification-rules.zip
    ├── rht-hidden-trouble-rules.zip
    ├── smp-ocr-rules.zip
    └── smp-root-rules.zip
```

## 技能包说明

| 路径 / 技能 | 作用 | 依赖 |
| --- | --- | --- |
| `smp-root-rules` | SMP 系统级根规则，统一输出契约、上下文透传、保存门禁 | - |
| `smp-ocr-rules` | 图片 OCR 识别，只负责识别，不负责保存 | `smp-root-rules` |
| `enterprise-qualification-rules` | 企业资质材料识别 | `smp-root-rules`、`smp-ocr-rules` |
| `project-qualification-rules` | 工程资质材料识别 | `smp-root-rules`、`smp-ocr-rules` |
| `hidden-danger-recognition` | 安全隐患图像识别 | `smp-root-rules` |
| `rht-hidden-trouble-rules` | 隐患辅助评估与知识库判读 | `smp-root-rules` |
| `legal-regulation-kb` | 法规/合规知识库检索与问答 | - |

## 使用方式

1. 先加载 `smp-root-rules`，确认统一输出格式和保存门禁。
2. 如需图片识别，先加载 `smp-ocr-rules`。
3. 再按业务场景选择对应 skill。
4. 所有输出遵循 `<RESULT_JSON>`：`summary`、`data`、`button`。
5. 需要保存前，先完成识别/判读并等待用户确认。

## 输出约定

- `summary`：一句话结果或错误说明。
- `data`：业务字段数组；失败或无结果时返回 `[]`。
- `button`：仅包含 `label` 和 `value` 的按钮数组；没有按钮时返回 `[]`。
- 附件保存时只传 `id` 与 `name`，不补路径或内容。
- 识别/判读结果不确定时，不要臆测，直接返回不足以判断或继续追问。

## 维护建议

如需新增 skill：

- 复用 `smp-root-rules` 的统一契约。
- 先明确依赖关系，再补充 `SKILL.md`。
- 尽量保持目录命名与能力名称一致，方便检索与维护。

## 说明

本仓库当前以技能规则文件为主，适合直接作为 SMP 系统的 skill 资源包使用。
