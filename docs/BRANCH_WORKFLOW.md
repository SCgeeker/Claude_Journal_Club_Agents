# 雙分支工作流程指南

## 📋 分支概覽

```
main (公開)                develop (私人)
    │                          │
    ├─ 核心功能                ├─ 完整功能
    ├─ 通用文檔                ├─ 私人workflow
    ├─ 公開示例                ├─ SciMaker整合
    └─ MIT License             ├─ 知識庫數據
                               └─ 實驗功能
```

---

## 🚀 初始設置

### Windows用戶
```cmd
setup_branches.bat
```

### Linux/Mac用戶
```bash
bash setup_branches.sh
```

### 手動設置
```bash
# 1. 初始化並創建develop分支
git init
git checkout -b develop
git add .
git commit -m "feat: Full development version"

# 2. 創建main分支
git checkout -b main
# 清理私人內容（見下方清單）
git add .
git commit -m "feat: Public release v0.4.0"

# 3. 設置遠端
git remote add origin https://github.com/YOUR_USERNAME/knowledge-production-system.git

# 4. 推送分支
git push -u origin main
git checkout develop
git push -u origin develop  # 可選
```

---

## 🔄 日常工作流程

### 1. 在develop分支開發

```bash
# 確保在develop分支
git checkout develop

# 正常開發
# - 修改代碼
# - 測試功能
# - 提交更改

git add .
git commit -m "feat: 新增XXX功能"
git push origin develop  # 如果有推送develop分支
```

### 2. 準備公開發布

```bash
# 切換到main分支
git checkout main

# 選擇性合併develop的提交（cherry-pick）
git cherry-pick <commit-hash>

# 或手動複製特定文件
git checkout develop -- src/generators/new_feature.py
git checkout develop -- templates/new_template.jinja2

# 確保移除私人內容
# 檢查並提交
git add .
git commit -m "feat: 新增XXX功能（公開版）"
git push origin main
```

### 3. 快速發布腳本

```bash
# 創建 scripts/publish_to_main.sh
#!/bin/bash
git checkout main
git cherry-pick develop~5..develop  # 合併最近5個提交
# 檢查並清理私人內容
git push origin main
git checkout develop
```

---

## 🧹 main分支需要移除的內容

### 自動移除（setup腳本已處理）
```
knowledge_base/papers/*.md          # 您的論文筆記
knowledge_base/metadata/*            # 元數據
output/*.pptx                        # 生成的簡報
output/*.md                          # 生成的筆記
output/zettel_*/                     # Zettelkasten輸出
```

### 需要編輯的文件
```
CLAUDE.md                            # 移除私人路徑引用
  - 移除：D:\Apps\LLM\SciMaker
  - 移除：D:\core\research\Program_verse
  - 保留：技術設計和使用說明

README.md                            # 使用README_PUBLIC.md
  - 不提及SciMaker逆向工程
  - 使用通用示例
```

### 完全移除的文件（可選）
```
.claude/agents/                      # 如包含私人workflow
PRIVATE_NOTES.md                     # 個人筆記
DEVELOPMENT_LOG.md                   # 開發日誌
```

---

## 📊 分支對比

| 項目 | main (公開) | develop (私人) |
|------|------------|---------------|
| **核心代碼** | ✅ 完整 | ✅ 完整 |
| **文檔** | 通用版 | 完整版 + 私人筆記 |
| **知識庫數據** | ❌ 空（僅結構） | ✅ 完整 |
| **輸出示例** | 公開論文示例 | 您的實際輸出 |
| **API密鑰** | ❌ 僅.env.example | 實際.env |
| **SciMaker引用** | ❌ 移除 | ✅ 保留 |
| **測試數據** | 公開數據 | 私人數據 |

---

## 🔐 安全檢查清單

發布到main前必須檢查：

```bash
# 1. 檢查API密鑰
git checkout main
grep -r "sk-\|API_KEY" . --exclude-dir=.git --exclude=".env.example"

# 2. 檢查私人路徑
grep -r "D:\\Apps\|Program_verse\|SciMaker" . --exclude-dir=.git

# 3. 檢查個人信息
grep -r "Sau-Chin\|your-email" . --exclude-dir=.git

# 4. 檢查知識庫數據
ls knowledge_base/papers/  # 應該只有.gitkeep
ls output/                 # 應該只有.gitkeep或公開示例

# 5. 確認.gitignore
git status --ignored
```

---

## 💡 最佳實踐

### ✅ 推薦做法

1. **develop分支**：
   - 日常開發、實驗、測試
   - 包含您的實際使用數據
   - 可以推送到私人遠端（或不推送）

2. **main分支**：
   - 僅包含可公開的代碼和文檔
   - 定期從develop cherry-pick穩定功能
   - 每次發布前執行安全檢查

3. **提交訊息**：
   - develop: 詳細記錄開發過程
   - main: 精煉的功能說明

### ❌ 避免做法

1. ❌ 直接在main分支開發
2. ❌ 自動合併develop到main（可能包含私人數據）
3. ❌ 在main分支提交包含私人路徑的代碼
4. ❌ 將.env文件提交到任何分支

---

## 🔄 同步策略

### 方案A：雙向同步（謹慎）
```bash
# develop → main（選擇性）
git checkout main
git cherry-pick <develop的特定commit>

# main → develop（公開改進）
git checkout develop
git merge main  # 安全，公開內容合併回私人
```

### 方案B：單向發布（推薦）
```bash
# 僅 develop → main（手動選擇）
# 不合併main回develop
# develop保持完整功能，main僅發布穩定版本
```

---

## 📝 示例工作流

### 新功能開發
```bash
# 1. 在develop開發
git checkout develop
# ... 開發新功能 ...
git commit -m "feat: 新增Zettelkasten改進"
git push origin develop

# 2. 測試穩定後，發布到main
git checkout main
git checkout develop -- src/generators/zettel_maker.py
git checkout develop -- templates/prompts/zettelkasten_template.jinja2

# 3. 移除develop分支特定的私人內容
# 編輯文件，移除私人引用

# 4. 提交到main
git commit -m "feat: Zettelkasten核心概念原文擷取功能"
git push origin main
```

### 緊急修復
```bash
# 1. 在main修復（公開問題）
git checkout main
# ... 修復 ...
git commit -m "fix: 修復Markdown模板錯誤"
git push origin main

# 2. 合併回develop
git checkout develop
git cherry-pick main~1  # 或 git merge main
```

---

## 🎯 總結

**develop分支**：您的完整工作環境
**main分支**：對外展示的精選版本

記住：**develop → main 需謹慎選擇，main → develop 可安全合併**
