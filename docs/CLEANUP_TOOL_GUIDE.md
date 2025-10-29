# 檔案清理工具使用指南

## 概述

工作階段清理工具 (`cleanup_session.py`) 是一個自動整理和清理工作過程產生文件的實用工具。它可以：

- ✅ 自動整理 PDF 分析 JSON 文件
- ✅ 自動整理簡報文件（PPTX/Markdown）
- ✅ 自動整理 Zettelkasten 筆記資料夾
- ✅ 清理臨時文件和緩存
- ✅ 生成清理報告
- ✅ 自動備份資料庫

## 快速開始

### 1. 乾跑模式（推薦第一次使用）

```bash
# 查看會做什麼，不實際執行
python cleanup_session.py
```

### 2. 實際執行清理

```bash
# 需要手動確認
python cleanup_session.py --execute

# 自動模式（不需確認）
python cleanup_session.py --auto
```

## 完整使用範例

### 基本使用

```bash
# 1. 乾跑模式 - 查看會做什麼
python cleanup_session.py

# 2. 執行清理並手動確認
python cleanup_session.py --execute

# 3. 自動執行（推薦）
python cleanup_session.py --auto
```

### 進階選項

```bash
# 指定工作階段類型
python cleanup_session.py --session batch --execute

# 不自動備份資料庫
python cleanup_session.py --execute --no-backup

# 指定報告輸出路徑
python cleanup_session.py --execute --report my_cleanup_report.md

# 使用自訂規則文件
python cleanup_session.py --execute --rules custom_rules.yaml
```

## 整理規則

清理工具遵循 `src/utils/cleanup_rules.yaml` 中定義的規則：

### 輸出文件組織

| 類型 | 來源模式 | 目標位置 |
|------|----------|----------|
| PDF 分析 JSON | `*_analysis.json` | `output/paper_analysis/` |
| 簡報文件 | `*.pptx`, `*_slides.md` | `output/slides/` |
| Zettelkasten | `zettel_*_YYYYMMDD/` | `output/zettelkasten_notes/` |

### 臨時文件清理

| 類型 | 模式 | 條件 |
|------|------|------|
| 批次腳本 | `batch_*.py`, `process_*.bat` | 存在 >1 小時 |
| 日誌緩存 | `*.log`, `*.tmp`, `__pycache__/` | 存在 >24 小時 |
| 空白文件 | 所有文件 | 大小 <100 bytes |

### 安全保護

以下文件類型**絕對不會被刪除**：

- ✅ Python 源碼（除臨時批次腳本）
- ✅ Markdown 文件（除舊報告）
- ✅ YAML/JSON 配置文件
- ✅ requirements.txt
- ✅ .git/ 目錄
- ✅ knowledge_base/ 目錄
- ✅ src/, templates/, config/ 目錄

## 工作流程範例

### 場景 1：批次處理論文後整理

```bash
# 1. 批次處理 15 篇論文
python batch_process.py --folder "D:\pdfs\new_papers"

# 2. 批次完成後整理文件
python cleanup_session.py --session batch --auto

# 輸出:
# ✅ 整理文件: 45 個
#    • 15 個 JSON 分析文件 → output/paper_analysis/
#    • 15 個 Zettelkasten 資料夾 → output/zettelkasten_notes/
#    • 刪除 2 個臨時批次腳本
# 📄 報告: FILE_CLEANUP_REPORT_20251029_1530.md
```

### 場景 2：生成簡報後整理

```bash
# 1. 生成多個簡報
python make_slides.py "主題1" --pdf paper1.pdf --style modern_academic
python make_slides.py "主題2" --pdf paper2.pdf --style zettelkasten

# 2. 整理生成的文件
python cleanup_session.py --session generation --auto

# 輸出:
# ✅ 整理文件: 4 個
#    • 2 個 PPTX 文件 → output/slides/
#    • 2 個 Zettelkasten 資料夾 → output/zettelkasten_notes/
```

### 場景 3：定期維護

```bash
# 每週或每月執行一次
python cleanup_session.py --auto

# 清理所有累積的臨時文件和緩存
```

## 清理報告

每次執行清理（非乾跑模式）都會生成報告，包含：

### 報告結構

```markdown
# 檔案清理報告 (2025-10-29)

## 清理執行摘要
- ✅ 整理文件: 45 個
- 🗑️  刪除文件: 3 個
- 💾 節省空間: 1.2 MB
- 📦 備份創建: knowledge_base/backups/index_20251029_1530.db

## 執行的整理動作
### 1. PDF 分析結果
- 15 個 JSON 文件移動到 output/paper_analysis/

### 2. Zettelkasten 原子筆記
- 15 個資料夾移動到 output/zettelkasten_notes/

## 清理的臨時文件
- batch_temp.py
- process_failed.bat
- *.log

## 清理後狀態
- 📚 知識庫論文: 44 篇
- 🗂️  Zettelkasten 資料夾: 48 個
- 📊 簡報文件: 6 個
```

### 報告保存

- 預設保存到根目錄：`FILE_CLEANUP_REPORT_YYYYMMDD_HHMMSS.md`
- 自動保留最新 5 份報告
- 舊報告自動歸檔到 `docs/cleanup_history/`

## 自訂清理規則

### 編輯規則文件

```bash
# 編輯 src/utils/cleanup_rules.yaml
vim src/utils/cleanup_rules.yaml
```

### 規則範例

```yaml
# 添加新的整理規則
output_organization:
  my_custom_files:
    patterns:
      - "my_pattern_*.txt"
    destination: "output/my_folder/"
    action: "move"
    description: "我的自訂文件"

# 添加新的清理規則
temp_files:
  my_temp_files:
    patterns:
      - "temp_*.dat"
    action: "delete"
    description: "我的臨時文件"
    conditions:
      min_age_hours: 24
```

## 命令行參數

| 參數 | 說明 | 範例 |
|------|------|------|
| `--execute` | 實際執行清理 | `--execute` |
| `--auto` | 自動模式（不需確認） | `--auto` |
| `--session TYPE` | 工作階段類型 | `--session batch` |
| `--no-backup` | 不自動備份資料庫 | `--no-backup` |
| `--report PATH` | 指定報告路徑 | `--report my_report.md` |
| `--rules PATH` | 使用自訂規則 | `--rules custom.yaml` |

### 工作階段類型

- `auto` - 自動檢測（預設）
- `batch` - 批次處理
- `analysis` - 論文分析
- `generation` - 簡報/筆記生成

## 故障排除

### 問題 1：找不到規則文件

```bash
# 確認規則文件存在
ls src/utils/cleanup_rules.yaml

# 使用自訂規則
python cleanup_session.py --rules path/to/rules.yaml
```

### 問題 2：誤刪文件

**不用擔心！** 清理工具有多重保護：

1. ✅ 預設為乾跑模式
2. ✅ 自動備份資料庫
3. ✅ 保護關鍵文件類型
4. ✅ 需要手動確認（除非使用 `--auto`）

```bash
# 從備份恢復
cp knowledge_base/backups/index_LATEST.db knowledge_base/index.db
```

### 問題 3：權限錯誤

```bash
# Windows: 以管理員身份運行
# 或確保有寫入權限
```

## Python API 使用

```python
from src.utils import SessionOrganizer

# 創建整理器
organizer = SessionOrganizer(
    dry_run=False,        # False = 實際執行
    auto_backup=True      # 自動備份
)

# 執行清理
report = organizer.organize_session(session_type='batch')

# 保存報告
report_path = organizer.save_report()

print(f"整理完成: {report.total_moved} 個文件")
print(f"刪除: {report.total_deleted} 個文件")
print(f"節省空間: {report.space_saved_readable()}")
```

## 最佳實踐

### 1. 先乾跑再執行

```bash
# 第一次使用時，先查看會做什麼
python cleanup_session.py

# 確認無誤後再執行
python cleanup_session.py --auto
```

### 2. 定期維護

```bash
# 每週執行一次清理
# 可以設置 cron job 或 Windows 排程任務
```

### 3. 檢查清理報告

```bash
# 清理後查看報告
cat FILE_CLEANUP_REPORT_*.md | tail -n 50
```

### 4. 保留備份

```bash
# 定期檢查備份
ls knowledge_base/backups/

# 手動創建重要時刻的備份
cp knowledge_base/index.db knowledge_base/backups/index_before_major_cleanup.db
```

## 整合到工作流程

### 在批次處理後自動清理

編輯 `batch_process.py`，在結尾添加：

```python
# 批次處理完成後
if input("是否整理產生的文件？[Y/n] ").lower() != 'n':
    from src.utils import SessionOrganizer
    organizer = SessionOrganizer(dry_run=False)
    organizer.organize_session(session_type='batch')
    organizer.save_report()
```

### Git 提交前清理

```bash
# 在 .git/hooks/pre-commit 中添加
python cleanup_session.py --auto --no-backup
```

## 技術細節

- **語言**: Python 3.10+
- **依賴**: PyYAML, pathlib（標準庫）
- **配置**: YAML 格式
- **報告**: Markdown 格式
- **備份**: 自動增量備份

## 版本歷史

- **v1.0.0** (2025-10-29) - 初始版本
  - 基本整理功能
  - 安全保護機制
  - 自動備份
  - Markdown 報告

## 相關文檔

- [AGENT_SKILL_DESIGN.md](../AGENT_SKILL_DESIGN.md) - Agent & Skill 架構設計
- [FILE_CLEANUP_REPORT_20251029.md](../FILE_CLEANUP_REPORT_20251029.md) - 清理報告範例
- [cleanup_rules.yaml](../src/utils/cleanup_rules.yaml) - 清理規則配置

## 支援與反饋

如有問題或建議，請在專案中留言或更新 AGENT_SKILL_DESIGN.md 的用戶反饋區。

---

**工具版本**: v1.0.0
**最後更新**: 2025-10-29
**維護者**: Claude Code Agent
