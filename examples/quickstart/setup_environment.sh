#!/bin/bash
# 快速開始：環境設置

# 安裝依賴
pip install -r requirements.txt

# 初始化知識庫（首次使用）
python -c "from src.knowledge_base import KnowledgeBaseManager; KnowledgeBaseManager()"
