#!/bin/bash
# 雙分支設置腳本

echo "🌳 Knowledge Production System - 雙分支設置"
echo "=========================================="

# 1. 初始化Git（如果還沒有）
if [ ! -d .git ]; then
    echo "📦 初始化Git倉庫..."
    git init
    echo "✅ Git倉庫已初始化"
fi

# 2. 確保.env在gitignore中
if ! grep -q "^\.env$" .gitignore; then
    echo ".env" >> .gitignore
    echo "✅ .env已加入.gitignore"
fi

# 3. 創建develop分支（私人開發）
echo ""
echo "🔧 創建develop分支（私人開發版本）..."
git checkout -b develop 2>/dev/null || git checkout develop

# 添加所有文件到develop
git add .
git commit -m "feat: Full development version with private workflows

- Complete Zettelkasten implementation
- Multi-LLM backend support
- 8 academic styles
- Knowledge base integration
- Private workflows and configurations
" 2>/dev/null || echo "ℹ️  No changes to commit in develop"

echo "✅ develop分支已創建（私人開發版本）"

# 4. 創建main分支（公開版本）
echo ""
echo "🌍 創建main分支（公開版本）..."
git checkout -b main 2>/dev/null || git checkout main

# 複製公開版本文件
if [ -f README_PUBLIC.md ]; then
    cp README_PUBLIC.md README.md
    echo "✅ 使用公開版README"
fi

# 合併公開版gitignore
if [ -f .gitignore_public ]; then
    cat .gitignore_public >> .gitignore
    echo "✅ 更新公開版.gitignore"
fi

# 移除私人內容
echo "🧹 清理私人內容..."

# 清空knowledge_base但保留結構
mkdir -p knowledge_base/papers knowledge_base/metadata
find knowledge_base/papers -type f -name "*.md" -delete 2>/dev/null
touch knowledge_base/papers/.gitkeep
touch knowledge_base/metadata/.gitkeep

# 清空output但保留結構
mkdir -p output
find output -type f \( -name "*.pptx" -o -name "*.md" -o -name "*.json" \) -delete 2>/dev/null
touch output/.gitkeep

echo "✅ 私人數據已清理"

# 提交公開版本
git add .
git commit -m "feat: Public release v0.4.0-alpha

Features:
- PDF literature analysis
- 8 academic presentation styles (PPTX + Markdown)
- Zettelkasten atomic note system
- Multi-LLM backend (Ollama/Gemini/OpenAI/Claude)
- Hybrid knowledge base management

Highlights:
- Direct quote extraction for core concepts
- AI/Human note separation
- Semantic ID format
- Mermaid concept network visualization
" 2>/dev/null || echo "ℹ️  No changes to commit in main"

echo "✅ main分支已創建（公開版本）"

# 5. 顯示分支狀態
echo ""
echo "📊 分支狀態："
git branch -v

echo ""
echo "✨ 設置完成！"
echo ""
echo "📋 下一步："
echo "1. 切換到main分支：git checkout main"
echo "2. 連接GitHub遠端："
echo "   git remote add origin https://github.com/YOUR_USERNAME/knowledge-production-system.git"
echo "3. 推送公開分支："
echo "   git push -u origin main"
echo "4. (可選) 推送私人分支："
echo "   git checkout develop"
echo "   git push -u origin develop"
echo ""
echo "💡 工作流程："
echo "- 日常開發在 develop 分支"
echo "- 公開發布時合併到 main 分支（手動選擇性合併）"
