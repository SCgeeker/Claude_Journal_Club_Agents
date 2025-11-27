#!/bin/bash
# 快速開始：基本使用

# 分析單篇論文
uv run analyze paper.pdf

# 分析並加入知識庫
uv run analyze paper.pdf --add-to-kb

# 生成投影片
uv run slides "論文主題" --pdf paper.pdf --style modern_academic

# 知識庫查詢
uv run kb list
uv run kb search "關鍵詞"
