#!/bin/bash
# 向量搜索 CLI 使用範例

# === 生成嵌入 ===

# 為所有內容生成嵌入（需確認成本）
python generate_embeddings.py --provider gemini

# 自動確認（用於自動化）
python generate_embeddings.py --provider gemini --yes

# 只處理論文
python generate_embeddings.py --papers-only --limit 10

# 只處理 Zettelkasten
python generate_embeddings.py --zettel-only

# 使用 Ollama（免費但較慢）
python generate_embeddings.py --provider ollama

# 查看統計
python generate_embeddings.py --stats

# === 語義搜索 ===

# 搜索論文
python kb_manage.py semantic-search "深度學習應用" --type papers --limit 5

# 搜索 Zettelkasten 卡片
python kb_manage.py semantic-search "認知科學" --type zettel --limit 3

# 搜索所有類型
python kb_manage.py semantic-search "機器學習" --type all

# 使用 Ollama
python kb_manage.py semantic-search "AI研究" --provider ollama

# 顯示詳細信息
python kb_manage.py semantic-search "語言學" --verbose

# === 尋找相似內容 ===

# 尋找與論文相似的論文
python kb_manage.py similar 14 --limit 5

# 尋找與卡片相似的卡片
python kb_manage.py similar zettel_CogSci-20251029-001 --limit 3

# === 混合搜索 ===

# 結合全文搜索和語義搜索
python kb_manage.py hybrid-search "machine learning" --limit 10

# 使用 Ollama
python kb_manage.py hybrid-search "深度學習" --provider ollama
