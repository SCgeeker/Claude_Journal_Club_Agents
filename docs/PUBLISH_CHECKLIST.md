# GitHub雙分支發布檢查清單

## 📋 發布前準備

本文檔幫助您檢查專案是否已準備好發布到GitHub。

---

## ✅ 必須完成的項目

### 1. 安全檢查

- [ ] `.env` 文件包含實際API密鑰
- [ ] `.gitignore` 已包含 `.env` 和 `*.key`
- [ ] 確認知識庫中無私人論文筆記（或準備清理）
- [ ] 確認輸出目錄無私人簡報（或準備清理）
- [ ] `CLAUDE.md` 中無私人路徑引用（如 `D:\Apps\LLM\SciMaker`）

### 2. 文檔完整性

- [x] `README_PUBLIC.md` 已創建（將成為main分支的README.md）
- [x] `LICENSE` 文件已創建（MIT License）
- [x] `.env.example` 已創建
- [x] `BRANCH_WORKFLOW.md` 已創建（雙分支工作流指南）
- [ ] 根據實際情況更新 `README_PUBLIC.md` 中的GitHub用戶名

### 3. 分支設置腳本

- [x] `setup_branches.sh`（Linux/Mac）已創建
- [x] `setup_branches.bat`（Windows）已創建
- [ ] 選擇並執行對應的設置腳本

---

## 🚀 執行步驟

### Windows用戶

```cmd
# 1. 執行分支設置腳本
setup_branches.bat

# 2. 在GitHub創建新倉庫
# https://github.com/new
# 倉庫名稱建議：knowledge-production-system

# 3. 連接遠端倉庫（替換YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/knowledge-production-system.git

# 4. 推送公開分支
git checkout main
git push -u origin main

# 5. (可選) 推送私人開發分支
git checkout develop
git push -u origin develop
```

### Linux/Mac用戶

```bash
# 1. 執行分支設置腳本
bash setup_branches.sh

# 2. 在GitHub創建新倉庫
# https://github.com/new
# 倉庫名稱建議：knowledge-production-system

# 3. 連接遠端倉庫（替換YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/knowledge-production-system.git

# 4. 推送公開分支
git checkout main
git push -u origin main

# 5. (可選) 推送私人開發分支
git checkout develop
git push -u origin develop
```

---

## 🔍 發布後驗證

### 檢查GitHub倉庫

1. 訪問 `https://github.com/YOUR_USERNAME/knowledge-production-system`
2. 確認README.md正確顯示
3. 確認LICENSE文件存在
4. 確認.env文件**不存在**
5. 檢查 `knowledge_base/papers/` 目錄應該是空的（僅有.gitkeep）
6. 檢查 `output/` 目錄應該是空的（僅有.gitkeep）

### 測試克隆

```bash
# 克隆到臨時目錄測試
cd /tmp
git clone https://github.com/YOUR_USERNAME/knowledge-production-system.git test-clone
cd test-clone

# 檢查是否包含敏感信息
grep -r "sk-\|API_KEY" . --exclude-dir=.git --exclude=".env.example"
# 應該沒有任何結果

# 檢查私人路徑
grep -r "D:\\Apps\|Program_verse\|SciMaker" . --exclude-dir=.git
# 應該沒有任何結果
```

---

## 📊 分支狀態概覽

| 項目 | main (公開) | develop (私人) |
|------|------------|----------------|
| **核心代碼** | ✅ 完整 | ✅ 完整 |
| **文檔** | 公開版README | 完整版 + 私人筆記 |
| **知識庫數據** | ❌ 空（僅結構） | ✅ 完整 |
| **輸出示例** | ❌ 空（僅結構） | ✅ 實際輸出 |
| **API密鑰** | ❌ 僅.env.example | ✅ 實際.env |
| **私人路徑** | ❌ 已移除 | ✅ 保留 |

---

## 🛡️ 緊急修復

如果不小心提交了敏感信息：

```bash
# 1. 立即修改API密鑰（在雲端服務商處）

# 2. 從Git歷史中移除敏感文件
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# 3. 強制推送（警告：會改寫歷史）
git push origin --force --all

# 4. 通知協作者
```

---

## 📚 參考文檔

- [雙分支工作流程指南](BRANCH_WORKFLOW.md)
- [開發文檔](CLAUDE.md)
- [公開版README](README_PUBLIC.md)

---

## 💡 最佳實踐

### ✅ 推薦

1. **先在develop分支開發，測試穩定後再發布到main**
2. **使用cherry-pick選擇性合併提交到main**
3. **每次發布前運行安全檢查清單**
4. **保持main分支乾淨，僅包含可公開內容**
5. **定期備份develop分支到私人遠端**

### ❌ 避免

1. ❌ 直接在main分支開發
2. ❌ 自動合併develop到main（可能包含私人數據）
3. ❌ 將.env文件提交到任何分支
4. ❌ 在main分支提交私人論文筆記
5. ❌ 使用git add . 而不檢查暫存內容

---

**最後更新**：2025-10-28
**狀態**：準備就緒，等待執行
