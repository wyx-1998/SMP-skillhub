#!/usr/bin/env python3
"""
并行 Vision OCR 工具 - 调用本地 Qwen3.5-35b 模型
支持多图并行识别，支持本地文件路径（包括中文路径）
"""

import sys
import os
import json
import base64
import requests
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

# 模型配置
MODEL_CONFIG = {
    "model": "qwen3.5-35b",
    "base_url": "http://172.20.1.91:3333/v1",
    "api_key": "sk-uSG0FeQmu39ZlB998b408eFf22Fa4d52B3F21759F86828B8",
    "max_workers": 4  # 并行数
}

def resolve_file_path(pattern: str) -> str:
    """使用 glob 解析文件路径（支持中文）"""
    matches = glob.glob(pattern)
    if matches:
        return matches[0]
    # 尝试直接路径
    if os.path.exists(pattern):
        return pattern
    return None

def encode_image_to_base64(filepath: str) -> tuple:
    """读取图片并转换为 base64，返回 (base64_str, mime_type)"""
    # 解析真实路径
    real_path = resolve_file_path(filepath)
    if not real_path:
        raise FileNotFoundError(f"文件不存在：{filepath}")
    
    with open(real_path, 'rb') as f:
        data = f.read()
    
    b64 = base64.b64encode(data).decode('utf-8')
    
    # 根据文件扩展名判断 MIME 类型
    ext = os.path.splitext(real_path)[1].lower()
    if ext == '.pdf':
        raise ValueError(f"不支持 PDF 文件：{real_path}")
    if ext in ['.jpg', '.jpeg']:
        mime = 'image/jpeg'
    elif ext == '.png':
        mime = 'image/png'
    elif ext == '.gif':
        mime = 'image/gif'
    else:
        mime = 'image/jpeg'  # 默认
    
    return b64, mime, real_path

def analyze_single_image(image_path: str, question: str) -> Dict[str, Any]:
    """分析单张图片"""
    try:
        # 编码图片
        b64, mime, real_path = encode_image_to_base64(image_path)
        
        # 构建请求 payload
        payload = {
            "model": MODEL_CONFIG["model"],
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime};base64,{b64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": question
                        }
                    ]
                }
            ],
            "max_tokens": 2048
        }
        
        # 发送请求
        response = requests.post(
            f"{MODEL_CONFIG['base_url']}/chat/completions",
            headers={
                "Authorization": f"Bearer {MODEL_CONFIG['api_key']}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=120
        )
        
        if response.status_code != 200:
            return {
                "success": False,
                "file": image_path,
                "error": f"HTTP {response.status_code}: {response.text[:200]}"
            }
        
        result = response.json()
        content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        return {
            "success": True,
            "file": image_path,
            "analysis": content
        }
        
    except Exception as e:
        return {
            "success": False,
            "file": image_path,
            "error": str(e)
        }

def analyze_images_parallel(image_paths: List[str], question: str, max_workers: int = None) -> List[Dict[str, Any]]:
    """并行分析多张图片"""
    if max_workers is None:
        max_workers = MODEL_CONFIG["max_workers"]
    
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_path = {
            executor.submit(analyze_single_image, path, question): path 
            for path in image_paths
        }
        
        # 收集结果
        for future in as_completed(future_to_path):
            result = future.result()
            results.append(result)
    
    return results

def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("用法：python vision_ocr.py <图片路径 1> [图片路径 2] ... --question <问题>")
        print("示例：python vision_ocr.py image1.jpg image2.jpg --question '请识别文档类型'")
        sys.exit(1)
    
    # 解析参数
    image_paths = []
    question = "请识别这份文档的类型，并提取关键信息。"
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--question' and i + 1 < len(sys.argv):
            question = sys.argv[i + 1]
            i += 2
        elif sys.argv[i].startswith('--'):
            i += 1
        else:
            # 使用 glob 解析路径（支持中文和通配符）
            matches = glob.glob(sys.argv[i])
            if matches:
                valid_matches = []
                for path in matches:
                    if os.path.splitext(path)[1].lower() == '.pdf':
                        print(f"⚠️  不支持 PDF 文件：{path}")
                    else:
                        valid_matches.append(path)
                image_paths.extend(valid_matches)
            elif os.path.exists(sys.argv[i]):
                ext = os.path.splitext(sys.argv[i])[1].lower()
                if ext == '.pdf':
                    print(f"⚠️  不支持 PDF 文件：{sys.argv[i]}")
                else:
                    image_paths.append(sys.argv[i])
            else:
                print(f"⚠️  未找到文件：{sys.argv[i]}")
            i += 1
    
    if not image_paths:
        print("错误：未指定有效的图片路径")
        sys.exit(1)
    
    print(f"📸 准备分析 {len(image_paths)} 张图片...")
    print(f"📝 问题：{question}")
    print(f"⚡ 并行数：{MODEL_CONFIG['max_workers']}")
    print("-" * 60)
    
    # 执行并行分析
    results = analyze_images_parallel(image_paths, question)
    
    # 输出结果
    success_count = 0
    fail_count = 0
    
    for r in results:
        if r["success"]:
            success_count += 1
            print(f"\n✅ {os.path.basename(r['file'])}")
            print(r['analysis'])
        else:
            fail_count += 1
            print(f"\n❌ {os.path.basename(r.get('file', 'unknown'))}")
            print(f"   错误：{r['error']}")
    
    print("\n" + "=" * 60)
    print(f"完成：{success_count} 成功, {fail_count} 失败, 总计 {len(results)}")
    
    # 返回 JSON 格式结果（便于程序调用）
    print("\n--- JSON 结果 ---")
    print(json.dumps(results, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
