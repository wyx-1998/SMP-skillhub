---
name: vision-ocr
description: "并行 Vision OCR 工具 - 调用本地 Qwen3.5-35b 模型识别图片/文档"
version: 1.0.0
author: User
license: MIT
platforms: [macos, linux]
metadata:
  hermes:
    tags: [OCR, Vision, Image-Recognition, Document-Extraction, Qwen3.5]
    related_skills: [markitdown-docs, ocr-and-documents]
---


## Reference material

- See `references/pdf_ocr_workflow.md` for the session-proven PDF -> image -> OCR flow and the common 400 error signature.


## 工具位置

**脚本路径**: `./scripts/vision_ocr.py`（技能目录下的主脚本）

**模型配置**:
- 模型: `qwen3.5-35b`
- 服务端: `http://172.20.1.91:3333/v1`
- 并行数: 4

## 使用方法

### 基本用法

```bash
# 单张图片
python ./scripts/vision_ocr.py image.jpg

# 多张图片
python ./scripts/vision_ocr.py image1.jpg image2.jpg image3.jpg

# 指定问题
python ./scripts/vision_ocr.py document.jpg --question "请识别这份文档的类型，并提取全部信息"

# 使用通配符
python ./scripts/vision_ocr.py "*.jpg" --question "识别图片中的所有文字内容"

# 中文路径
python ./scripts/vision_ocr.py "/Users/wangyuxing/Desktop/中建材/扫描件/合同.jpg"
```

### 支持的文件格式

- **图片**: `.jpg`, `.jpeg`, `.png`, `.gif`
- **文档**: `.pdf` (需要服务端支持 PDF 解析)

⚠️ **注意**: 对于电子版 PDF（非扫描件），推荐使用 `markitdown-docs` 技能，效果更佳。

### PDF 扫描件处理（重要）

vision-ocr 服务端**不支持直接传入 PDF 文件**（会返回 HTTP 400: "cannot identify image file"）。对于扫描件 PDF，必须先转为图片再 OCR：

```python
import fitz  # pymupdf
import os

doc = fitz.open("/path/to/scanned.pdf")
os.makedirs("/tmp/pdf_images", exist_ok=True)
for i, page in enumerate(doc):
    pix = page.get_pixmap()
    pix.save(f"/tmp/pdf_images/{filename}_{{i+1}}.jpg")
```

然后对生成的图片调用 vision-ocr：
```bash
python ./scripts/vision_ocr.py /tmp/pdf_images/*.jpg --question "识别所有的内容"
```

**注意**：对于页数较多的 PDF（>10 页），建议分批处理以避免超时。

### 输出格式

工具会输出：
1. 进度信息（准备分析的图片数量、问题、并行数）
2. 每张图的分析结果（成功/失败状态）
3. 统计信息（成功数、失败数、总数）
4. JSON 格式结果（便于程序调用）

### 示例输出

```
📸 准备分析 3 张图片...
📝 问题：请识别这份文档的类型
⚡ 并行数：4
------------------------------------------------------------

✅ 合同.jpg
这是一份劳动合同，包含以下关键信息：
- 甲方：某某公司
- 乙方：张三
- 合同期限：2024 年 1 月 1 日至 2025 年 12 月 31 日
...

✅ 发票.png
这是一张增值税发票，包含：
- 发票号码：12345678
- 金额：¥1,234.56
...

============================================================
完成：2 成功，1 失败，总计 3

--- JSON 结果 ---
[
  {
    "success": true,
    "file": "合同.jpg",
    "analysis": "这是一份劳动合同..."
  },
  ...
]
```

## 常见问题

## 常见问题

### 1. PDF 文件返回 HTTP 400

```
HTTP 400: "cannot identify image file"
```

**原因**: vision-ocr 服务端不支持 PDF 格式直接传入。
**解决**: 先用 pymupdf (fitz) 将 PDF 转为图片，再对图片执行 OCR。参见上方「PDF 扫描件处理」。

**批量 PDF 转换示例**：
```python
import fitz
import os

os.makedirs('/tmp/smp_ocr', exist_ok=True)
pdf_files = ['安全制度.pdf', '安全操作规程.pdf']

for pdf in pdf_files:
    if os.path.exists(pdf):
        doc = fitz.open(pdf)
        base_name = pdf.replace('.pdf', '')
        for i, page in enumerate(doc):
            pix = page.get_pixmap()
            output_path = f'/tmp/smp_ocr/{base_name}_page{i+1}.jpg'
            pix.save(output_path)
        doc.close()
```

### 2. 文件名包含特殊字符（空格、连字符、中文）

**问题**: 文件名包含空格、连字符（-）、中文时，shell 会错误解析。

**解决**: 必须用双引号包裹文件路径：
```bash
# ❌ 错误：会被解析为多个参数
python vision_ocr.py /tmp/技术人员 - 副本_page1.jpg

# ✅ 正确：用双引号包裹
python vision_ocr.py "/tmp/技术人员 - 副本_page1.jpg"

# ✅ 多个文件也要分别包裹
python vision_ocr.py "/tmp/file 1.jpg" "/tmp/file-2.jpg"
```

### 3. 文件不存在

```
⚠️  未找到文件：xxx.jpg
```

**解决**: 检查文件路径是否正确，支持绝对路径、相对路径和通配符。

### 2. 服务端不可用

```
HTTP 000: Connection refused
```

**解决**: 确认本地 Qwen3.5-35b 服务端是否运行在 `http://172.20.1.91:3333/v1`

### 3. 超时错误

```
HTTP 000: Read timed out
```

**解决**: 图片太大或网络慢，尝试减少并行数或单张处理。

## 与 markitdown 的区别

| 工具 | 适用场景 | 优势 |
|------|----------|------|
| **vision-ocr** | 图片、扫描件、截图 | 多模态理解，支持复杂布局 |
| **markitdown** | 电子版 PDF/DOCX/PPTX | 原生格式解析，保留结构 |
| **ocr-and-documents** | 批量 PDF 处理 | 专门针对 PDF 优化 |

## 使用建议

1. **图片/扫描件**: 优先使用 `vision-ocr`
2. **电子版文档**: 优先使用 `markitdown`
3. **混合场景**: 先用 `markitdown` 处理电子版，剩余用 `vision-ocr` 处理扫描件

## 脚本架构

技能包含两个脚本，自成体系可独立复制：

| 脚本 | 角色 | 定位方式 |
|------|------|----------|
| `scripts/vision_ocr.py` | 主 OCR 引擎 | 命令行直接调用 `python ./scripts/vision_ocr.py` |
| `scripts/batch_pdf_ocr.py` | PDF→图片→OCR 一键批处理 | 通过 `__file__` 自动定位同目录的 `vision_ocr.py` |

`batch_pdf_ocr.py` 使用 `os.path.dirname(os.path.abspath(__file__))` 动态解析兄弟脚本路径，因此两个脚本**必须保持在同一目录下**才可正常工作。

```bash
# ✅ 正确：从 skill 根目录调用
python ./scripts/batch_pdf_ocr.py *.pdf

# ✅ 也正确：直接进入 scripts/ 目录调用
cd scripts && python batch_pdf_ocr.py ../*.pdf
```

**移植时**：将 `scripts/` 整个目录复制过去即可，无需修改任何路径。

> 此架构避免了硬编码绝对路径，确保技能包可被复制到任意位置直接使用。

## 修改配置

如需修改模型配置，编辑脚本顶部的 `MODEL_CONFIG`：

```python
MODEL_CONFIG = {
    "model": "qwen3.5-35b",      # 模型名称
    "base_url": "http://172.20.1.91:3333/v1",  # 服务端地址
    "api_key": "sk-uSG...28B8",  # API Key
    "max_workers": 4              # 并行数
}
```

## 依赖

- Python 3.8+
- `requests` 库
- 本地 Qwen3.5-35b 多模态模型服务

## 快捷命令

```bash
# 创建别名（添加到 ~/.zshrc）
alias vision-ocr="python ./scripts/vision_ocr.py"

# 使用别名
vision-ocr image.jpg --question "识别内容"

# 批量 PDF 转 OCR（一键转换 PDF 并识别）
python ./scripts/batch_pdf_ocr.py *.pdf
```

## 实战案例：SMP 企业资质材料识别

**场景**: 批量识别企业资质证照（营业执照、安全生产许可证、各类证书等）

**步骤**:

1. **PDF 转图片**（vision-ocr 不支持直接传 PDF）：
```python
import fitz
import os

os.makedirs('/tmp/smp_ocr', exist_ok=True)
pdf_files = ['安全制度.pdf', '安全操作规程.pdf', '技术人员 - 副本.pdf']

for pdf in pdf_files:
    if os.path.exists(pdf):
        doc = fitz.open(pdf)
        base_name = pdf.replace('.pdf', '')
        print(f'处理 {pdf} ({len(doc)} 页)')
        for i, page in enumerate(doc):
            pix = page.get_pixmap()
            output_path = f'/tmp/smp_ocr/{base_name}_page{i+1}.jpg'
            pix.save(output_path)
        doc.close()
```

2. **批量 OCR 识别**（注意文件名包含空格/连字符/中文）：
```bash
# ✅ 正确：用双引号包裹每个文件
python ./scripts/vision_ocr.py \
  "/tmp/smp_ocr/安全制度_page1.jpg" \
  "/tmp/smp_ocr/技术人员 - 副本_page1.jpg" \
  --question "请识别文档类型并提取关键信息"
```

3. **按业务规范分类**（参考 `enterprise-qualification-rules` 技能）：
- 营业执照 → EpibolyBusiLicenceApply
- 安全生产许可证 → EpibolySafeLicenceApply
- 资质证书 → EpibolyCertificateApply / EpibolyThreeinoneApply
- 人员证书 → EpibolySafeOfficerApply / EpibolyFilesApply
- 制度文件 → EpibolyFilesApply (attachment_only)