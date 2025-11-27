#!/bin/bash
# 快速開始：環境設置

# 方式 1：使用 uv（推薦）
uv sync

# 方式 2：使用 pip（傳統方式）
# pip install -r requirements.txt

# 驗證安裝
uv run kb stats
