#!/bin/bash
# 批次處理器 CLI 使用範例

# 批次處理資料夾中的所有PDF
python batch_process.py --folder "D:\pdfs\mental_simulation"

# 批次處理並加入知識庫
python batch_process.py --folder "D:\pdfs" --domain CogSci --add-to-kb

# 批次處理並生成 Zettelkasten
python batch_process.py --folder "D:\pdfs" --domain CogSci --generate-zettel

# 完整處理（知識庫 + Zettelkasten）
python batch_process.py --folder "D:\pdfs" --domain CogSci --add-to-kb --generate-zettel --workers 4

# 指定特定文件
python batch_process.py --files paper1.pdf paper2.pdf --add-to-kb
