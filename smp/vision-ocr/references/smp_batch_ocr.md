# SMP 企业资质材料批量 OCR 识别脚本

## 用途

一键完成以下操作：
1. 将 PDF 文件转换为图片
2. 对转换后的图片执行批量 OCR 识别
3. 输出识别结果到指定目录

## 使用方法

```bash
python ./scripts/smp_batch_ocr.py \
  --input-dir /Users/wangyuxing/Desktop/test/com3/danwei \
  --output-dir /tmp/smp_ocr \
  --question "请识别文档类型并提取关键信息"
```

## 参数说明

- `--input-dir`: 输入目录，包含原始图片和 PDF 文件
- `output-dir`: 输出目录，存放转换后的图片和 OCR 结果
- `--question`: OCR 问题模板（可选，默认识别文档类型和关键信息）

## 支持的文档类型

根据 `enterprise-qualification-rules` 规范：
- 营业执照
- 安全生产许可证
- 企业资质证书
- 三位一体认证
- 安全员证书
- 单位负责人安全证
- 安全管理人员安全证
- 技术人员资格证
- 安全生产管理制度
- 安全操作规程
- 安全管理网络图
- 其他审核文件

## 输出格式

```
/tmp/smp_ocr/
├── converted/           # PDF 转换后的图片
│   ├── 安全制度_page1.jpg
│   └── 技术人员 - 副本_page1.jpg
├── results/             # OCR 识别结果
│   ├── 安全制度_page1.json
│   └── 技术人员 - 副本_page1.json
└── summary.json         # 汇总结果
```

## 注意事项

1. PDF 必须先转换为图片才能进行 OCR
2. 文件名包含空格、连字符、中文时，必须用双引号包裹
3. 页数较多的 PDF（>10 页）建议分批处理
4. 识别结果需要按照 `enterprise-qualification-rules` 规范进行分类和字段提取
