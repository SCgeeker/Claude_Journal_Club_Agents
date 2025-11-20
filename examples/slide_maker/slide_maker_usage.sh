#!/bin/bash
# 投影片生成器使用範例

# === 基本用法 ===

# 從主題生成投影片
python make_slides.py "深度學習應用" --style modern_academic --slides 15

# 從PDF直接生成（快速模式）
python make_slides.py "論文摘要" --pdf paper.pdf --style research_methods

# 從PDF分析後生成（知識驅動模式，推薦）
python make_slides.py "論文摘要" --pdf paper.pdf --analyze-first --style literature_review

# 從知識庫已有論文生成（重用模式）
python make_slides.py "論文簡報" --from-kb 1 --style modern_academic

# === 使用不同的 LLM 後端 ===

# 使用Google Gemini（更快）
python make_slides.py "AI研究" --pdf paper.pdf --llm-provider google --model gemini-2.0-flash-exp

# 使用OpenAI
python make_slides.py "機器學習" --pdf paper.pdf --llm-provider openai --model gpt-4

# 使用Anthropic Claude
python make_slides.py "認知科學" --pdf paper.pdf --llm-provider anthropic --model claude-3-haiku

# 使用本地Ollama
python make_slides.py "語言學" --pdf paper.pdf --llm-provider ollama --model gemma2:latest

# === 自定義格式和風格 ===

# 生成雙語投影片
python make_slides.py "機器學習入門" --style teaching --language bilingual --slides 20

# 生成詳細內容
python make_slides.py "研究方法" --pdf paper.pdf --style research_methods --detail detailed

# 生成英文投影片
python make_slides.py "Deep Learning" --pdf paper.pdf --language english --slides 25

# === 自定義輸出路徑 ===

# 指定輸出文件名
python make_slides.py "主題" --pdf paper.pdf --output "output/my_presentation.pptx"
