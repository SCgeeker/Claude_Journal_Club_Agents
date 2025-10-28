# Knowledge Base Management Command

管理知識庫：查看統計、搜索論文、創建主題、建立關聯等操作。

## 任務說明

當用戶執行 `/kb-manage <subcommand>` 時，使用 `kb_manage.py` 腳本執行知識庫管理操作。

## 執行步驟

請使用Bash工具執行以下命令：

```bash
cd D:\core\research\claude_lit_workflow
python kb_manage.py {子命令} {參數}
```

## 可用子命令

### 1. stats - 查看統計
顯示知識庫的統計信息（論文數、主題數、引用數）

**用法**：
```bash
/kb-manage stats
```

**執行**：
```bash
python kb_manage.py stats
```

### 2. list - 列出論文
列出知識庫中的所有論文

**用法**：
```bash
/kb-manage list [--limit N]
```

**執行**：
```bash
python kb_manage.py list
python kb_manage.py list --limit 10
```

### 3. search - 搜索論文
全文搜索論文內容

**用法**：
```bash
/kb-manage search "關鍵詞" [--limit N]
```

**執行**：
```bash
python kb_manage.py search "deep learning"
python kb_manage.py search "AI cognitive science" --limit 5
```

### 4. show - 顯示詳情
顯示特定論文的詳細信息

**用法**：
```bash
/kb-manage show <paper_id>
```

**執行**：
```bash
python kb_manage.py show 1
```

### 5. add-topic - 創建主題
創建新的主題標籤

**用法**：
```bash
/kb-manage add-topic "主題名稱" [-d "描述"]
```

**執行**：
```bash
python kb_manage.py add-topic "AI與認知科學" -d "人工智能在認知科學研究中的應用與批判"
python kb_manage.py add-topic "研究方法論"
```

### 6. link - 連結論文與主題
將論文連結到主題

**用法**：
```bash
/kb-manage link <paper_id> <topic_id> [--relevance 0-1]
```

**執行**：
```bash
python kb_manage.py link 1 1
python kb_manage.py link 1 1 --relevance 0.95
```

### 7. topic-papers - 按主題查看論文
查看特定主題下的所有論文

**用法**：
```bash
/kb-manage topic-papers "主題名稱"
```

**執行**：
```bash
python kb_manage.py topic-papers "AI與認知科學"
```

### 8. cite - 添加引用關係
記錄論文之間的引用關係

**用法**：
```bash
/kb-manage cite <source_id> <target_id> [--type TYPE]
```

**執行**：
```bash
python kb_manage.py cite 1 2
python kb_manage.py cite 1 2 --type "extends"
```

## 常見使用場景

### 場景1: 查看知識庫狀態
```
用戶: /kb-manage stats
執行: python kb_manage.py stats
```

### 場景2: 搜索相關論文
```
用戶: /kb-manage search "deep learning medical"
執行: python kb_manage.py search "deep learning medical"
```

### 場景3: 組織論文主題
```
步驟1: 創建主題
用戶: /kb-manage add-topic "深度學習應用" -d "深度學習在各領域的應用研究"
執行: python kb_manage.py add-topic "深度學習應用" -d "深度學習在各領域的應用研究"

步驟2: 連結論文
用戶: /kb-manage link 1 1
執行: python kb_manage.py link 1 1
```

### 場景4: 建立文獻網絡
```
用戶: /kb-manage cite 1 2
執行: python kb_manage.py cite 1 2
說明: 表示論文1引用了論文2
```

## 完整工作流示例

```bash
# 1. 添加論文到知識庫
/analyze-paper paper.pdf --add-to-kb

# 2. 查看知識庫統計
/kb-manage stats

# 3. 創建主題標籤
/kb-manage add-topic "AI倫理" -d "人工智能的倫理問題研究"

# 4. 連結論文到主題
/kb-manage link 1 1

# 5. 搜索相關論文
/kb-manage search "AI ethics"

# 6. 查看主題下的論文
/kb-manage topic-papers "AI倫理"
```

## 輸出示例

### stats 命令輸出
```
============================================================
📊 知識庫統計
============================================================
論文總數: 15
主題總數: 3
引用總數: 8
============================================================
```

### search 命令輸出
```
============================================================
🔍 搜索: 'deep learning'
============================================================

找到 5 個結果:

1. [ID: 3] Deep Learning for Medical Image Analysis
   作者: John Smith, Jane Doe
   年份: 2024
   摘要: This paper presents a novel deep learning approach...

2. [ID: 7] Applications of Deep Learning in NLP
   作者: Bob Johnson
   年份: 2023
   ...

============================================================
```

### list 命令輸出
```
============================================================
📄 論文列表 (最多 50 篇)
============================================================

[ID: 1] TICS2778No.ofPages13
  作者: Cognitive Sciences, J.Crockett
  年份: 未知
  時間: 2025-10-27 13:30:31

[ID: 2] Deep Learning for Medical Diagnosis
  作者: John Smith, Jane Doe, Bob Johnson
  年份: 2024
  關鍵詞: deep learning, medical imaging, diagnosis
  時間: 2025-10-27 14:15:22

============================================================
```

## 參數說明

- `<paper_id>`: 論文的數字ID
- `<topic_id>`: 主題的數字ID
- `--limit N`: 限制返回結果數量（默認：list=50, search=10）
- `--relevance`: 相關度評分（0.0-1.0，默認：1.0）
- `--type`: 引用類型（默認："cites"）

## 提示

1. 使用 `stats` 命令快速了解知識庫規模
2. 使用 `search` 命令進行全文搜索，支援中英文
3. 定期使用 `add-topic` 組織論文，便於後續查找
4. 使用 `cite` 命令記錄論文引用關係，構建知識網絡

## 相關命令

- `/analyze-paper` - 分析論文並加入知識庫
- 查看 `QUICKSTART.md` 了解完整使用流程
