#!/bin/bash
# 質量檢查器 CLI 使用範例

# 檢查所有論文
python check_quality.py

# 檢查特定論文
python check_quality.py --paper-id 27

# 生成詳細報告
python check_quality.py --detail comprehensive --output quality_report.txt

# 僅顯示有嚴重問題的論文
python check_quality.py --critical-only

# 檢測重複論文（相似度 >= 85%）
python check_quality.py --detect-duplicates --threshold 0.85

# JSON格式輸出
python check_quality.py --format json --output quality_report.json
