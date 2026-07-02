# PDF 扫描件批量 OCR 处理工作流

## 问题背景

vision_ocr.py 服务端不支持直接传入 PDF 文件，会返回 HTTP 400: "cannot identify image file"。

## 解决方案

**两步走：PDF → 图片 → OCR**

### 1. PDF 转图片（使用 pymupdf/fitz）

```python
import fitz  # pymupdf
import os

def pdf_to_images(pdf_path, output_dir='/tmp/smp_ocr'):
    """将 PDF 文件转换为多页 JPG 图片"""
    os.makedirs(output_dir, exist_ok=True)
    
    doc = fitz.open(pdf_path)
    base_name = os.path.basename(pdf_path).replace('.pdf', '')
    
    print(f'处理 {pdf_path} ({len(doc)} 页)')
    
    for i, page in enumerate(doc):
        # 渲染为图片，分辨率 150 DPI 足够 OCR
        pix = page.get_pixmap(dpi=150)
        output_path = os.path.join(output_dir, f'{base_name}_page{i+1}.jpg')
        pix.save(output_path)
        print(f'  已保存：{output_path}')
    
    doc.close()
    return [os.path.join(output_dir, f'{base_name}_page{i+1}.jpg') for i in range(len(doc))]

# 批量处理多个 PDF
pdf_files = [
    '/Users/wangyuxing/Desktop/test/com3/danwei/安全制度.pdf',
    '/Users/wangyuxing/Desktop/test/com3/danwei/安全操作规程.pdf',
    '/Users/wangyuxing/Desktop/test/com3/danwei/技术人员 - 副本.pdf',
    '/Users/wangyuxing/Desktop/test/com3/danwei/陈燕萍安全员证.pdf'
]

all_images = []
for pdf in pdf_files:
    if os.path.exists(pdf):
        images = pdf_to_images(pdf)
        all_images.extend(images)

print(f'\n共转换 {len(all_images)} 张图片')
```

### 2. 对生成的图片执行 OCR

```bash
# 单张图片
python ./scripts/vision_ocr.py "/tmp/smp_ocr/安全制度_page1.jpg" \
  --question "请识别文档类型并提取关键信息"

# 多张图片（注意文件名包含空格/中文/连字符时要用双引号包裹）
python ./scripts/vision_ocr.py \
  "/tmp/smp_ocr/安全制度_page1.jpg" \
  "/tmp/smp_ocr/安全制度_page2.jpg" \
  "/tmp/smp_ocr/技术人员 - 副本_page1.jpg" \
  --question "请识别文档类型并提取关键信息"
```

### 3. 批量一键脚本

```python
#!/usr/bin/env python3
"""批量 PDF 转 OCR 一键脚本"""

import fitz
import os
import sys
import subprocess
import glob

def pdf_to_images(pdf_path, output_dir='/tmp/smp_ocr'):
    """将 PDF 文件转换为多页 JPG 图片"""
    os.makedirs(output_dir, exist_ok=True)
    
    doc = fitz.open(pdf_path)
    base_name = os.path.basename(pdf_path).replace('.pdf', '')
    
    images = []
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=150)
        output_path = os.path.join(output_dir, f'{base_name}_page{i+1}.jpg')
        pix.save(output_path)
        images.append(output_path)
    
    doc.close()
    return images

def main():
    if len(sys.argv) < 2:
        print('用法：python batch_pdf_ocr.py file1.pdf [file2.pdf ...]')
        sys.exit(1)
    
    pdf_files = []
    for arg in sys.argv[1:]:
        # 支持通配符
        matches = glob.glob(arg)
        if matches:
            pdf_files.extend(matches)
        elif os.path.exists(arg):
            pdf_files.append(arg)
        else:
            print(f'⚠️  未找到文件：{arg}')
    
    if not pdf_files:
        print('错误：没有有效的 PDF 文件')
        sys.exit(1)
    
    # 1. 转换 PDF 为图片
    all_images = []
    for pdf in pdf_files:
        print(f'\n📄 处理：{pdf}')
        images = pdf_to_images(pdf)
        all_images.extend(images)
    
    print(f'\n✅ 共转换 {len(all_images)} 张图片到 /tmp/smp_ocr/')
    
    # 2. 执行 OCR
    print(f'\n🔍 开始 OCR 识别...')
    cmd = ['python', os.path.join(script_dir, 'vision_ocr.py')]
    cmd.extend(all_images)
    cmd.extend(['--question', '请识别文档类型并提取关键信息'])
    
    result = subprocess.run(cmd)
    sys.exit(result.returncode)

if __name__ == '__main__':
    main()
```

## 注意事项

### 1. 文件名包含空格/特殊字符

**必须用双引号包裹文件路径**：

```bash
# ❌ 错误：会被解析为多个参数
python vision_ocr.py /tmp/技术人员 - 副本_page1.jpg

# ✅ 正确：用双引号包裹
python vision_ocr.py "/tmp/技术人员 - 副本_page1.jpg"

# ✅ 多个文件也要分别包裹
python vision_ocr.py \
  "/tmp/file 1.jpg" \
  "/tmp/file-2.jpg" \
  "/tmp/中文文件.jpg"
```

### 2. 依赖检查

确保已安装 pymupdf：

```bash
pip install pymupdf
```

### 3. 服务端配置

vision_ocr.py 默认使用：
- 模型：qwen3.5-35b
- 服务端：http://172.20.1.91:3333/v1
- 并行数：4

### 4. 多页 PDF 处理

- 每页会生成单独的图片文件
- OCR 时会分别识别每页
- 对于页数较多的 PDF（>10 页），建议分批处理以避免超时

## 典型应用场景

### SMP 企业资质材料识别

```bash
# 1. 批量转换 PDF
python ./scripts/batch_pdf_ocr.py \
  /Users/wangyuxing/Desktop/test/com3/danwei/*.pdf

# 2. 对生成的图片执行 OCR
python ./scripts/vision_ocr.py \
  "/tmp/smp_ocr/安全制度_page1.jpg" \
  "/tmp/smp_ocr/安全操作规程_page1.jpg" \
  "/tmp/smp_ocr/技术人员 - 副本_page1.jpg" \
  --question "请识别文档类型并提取关键信息"
```

## 输出示例

```
📸 准备分析 3 张图片...
📝 问题：请识别文档类型并提取关键信息
⚡ 并行数：4
------------------------------------------------------------

✅ 安全制度_page1.jpg
这是一份企业内部的**安全生产管理制度**文档。
以下是提取的关键信息：
...

✅ 安全操作规程_page1.jpg
### 文档类型识别
**企业安全管理标准/制度文件**
...

============================================================
完成：3 成功，0 失败，总计 3

--- JSON 结果 ---
[
  {"success": true, "file": "...", "analysis": "..."},
  ...
]
```
