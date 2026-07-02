#!/usr/bin/env python3
"""
批量 PDF 转 OCR 一键脚本

用法:
    python batch_pdf_ocr.py file1.pdf [file2.pdf ...]
    python batch_pdf_ocr.py "*.pdf"  # 通配符

示例:
    python batch_pdf_ocr.py /path/to/安全制度.pdf /path/to/技术人员.pdf
    python batch_pdf_ocr.py "/Users/wangyuxing/Desktop/*.pdf"
"""

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
    
    print(f'\n📄 处理：{pdf_path} ({len(doc)} 页)')
    
    images = []
    for i, page in enumerate(doc):
        # 渲染为图片，150 DPI 足够 OCR
        pix = page.get_pixmap(dpi=150)
        output_path = os.path.join(output_dir, f'{base_name}_page{i+1}.jpg')
        pix.save(output_path)
        images.append(output_path)
        print(f'  ✅ {os.path.basename(output_path)}')
    
    doc.close()
    return images

def main():
    if len(sys.argv) < 2:
        print('用法：python batch_pdf_ocr.py file1.pdf [file2.pdf ...]')
        print('      python batch_pdf_ocr.py "*.pdf"  # 通配符')
        sys.exit(1)
    
    # 收集所有 PDF 文件
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
        print('\n❌ 错误：没有有效的 PDF 文件')
        sys.exit(1)
    
    print(f'\n📚 共找到 {len(pdf_files)} 个 PDF 文件')
    
    # 1. 转换 PDF 为图片
    all_images = []
    for pdf in pdf_files:
        images = pdf_to_images(pdf)
        all_images.extend(images)
    
    print(f'\n✅ 共转换 {len(all_images)} 张图片到 /tmp/smp_ocr/')
    
    # 2. 执行 OCR
    print(f'\n🔍 开始 OCR 识别...')
    print(f'⚡ 并行数：4')
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cmd = ['python', os.path.join(script_dir, 'vision_ocr.py')]
    cmd.extend(all_images)
    cmd.extend(['--question', '请识别文档类型并提取关键信息'])
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print(f'\n🎉 完成！所有文件已识别')
    else:
        print(f'\n⚠️  OCR 识别过程中出现错误')
    
    sys.exit(result.returncode)

if __name__ == '__main__':
    main()
