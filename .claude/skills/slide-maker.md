# Slide Maker Skill

## 功能描述

基於Journal Club架構的多風格學術簡報生成器，支援8種學術風格、5種詳細程度、3種語言。

## 能力

- 🎨 **8種學術風格**：經典、現代、臨床、研究方法、文獻回顧、案例分析、教學導向、**Zettelkasten卡片盒**
- 📊 **5種詳細程度**：極簡、簡要、標準、詳細、完整
- 🌍 **3種語言模式**：中文、英文、中英雙語
- 🤖 **LLM平台整合**：支援Ollama、OpenAI、Google AI等（可擴展）
- 📄 **PDF整合**：可基於PDF論文內容生成簡報
- 💾 **PPTX輸出**：標準PowerPoint格式

## 基於Journal Club

此Skill完全基於SciMaker Journal Club的逆向工程成果：
- ✅ 22個原始prompt templates
- ✅ 8 × 5 × 3 = 120種組合（含Zettelkasten）
- ✅ 投影片解析邏輯（regex模式）
- ✅ PPTX生成流程
- ✅ 多LLM平台支援

## 使用方式

### 基本用法

```python
from src.generators import SlideMaker

# 初始化生成器
maker = SlideMaker()

# 生成投影片
result = maker.generate_slides(
    topic="深度學習在醫學影像中的應用",
    style="modern_academic",      # 現代學術風格
    detail_level="standard",       # 標準詳細程度
    language="chinese",            # 繁體中文
    slide_count=15,                # 15張投影片
    output_path="output/deep_learning_medical.pptx"
)

print(f"✅ 生成完成: {result['output_path']}")
print(f"投影片數: {result['slide_count']}")
```

### 基於PDF生成

```python
from src.generators import make_slides

# 便捷函數：基於PDF生成投影片
output_path = make_slides(
    topic="AI Surrogates研究評論",
    pdf_path="papers/Crockett-2025.pdf",
    style="literature_review",     # 文獻回顧風格
    detail_level="detailed",       # 詳細程度
    language="bilingual",          # 中英雙語
    slide_count=20
)

print(f"投影片已保存: {output_path}")
```

### Zettelkasten卡片盒風格

```python
# 生成原子化筆記格式的簡報
result = maker.generate_slides(
    topic="認知科學中的AI應用",
    style="zettelkasten",          # 卡片盒風格
    detail_level="standard",
    language="bilingual",
    slide_count=20,
    custom_requirements="""
    - 每張投影片為獨立概念卡片
    - 標註卡片ID格式：ZK-YYYYMMDD-NNN
    - 明確標示概念間的連結
    - 包含反向連結區塊
    """
)
```

### 命令行使用

```bash
# 使用make-slides命令行工具
python make_slides.py "深度學習應用" --style modern_academic --slides 15

# 基於PDF
python make_slides.py "論文評論" --pdf paper.pdf --style literature_review

# Zettelkasten風格
python make_slides.py "知識管理系統" --style zettelkasten --detail standard

# 完整選項
python make_slides.py "研究方法探討" \
    --pdf paper.pdf \
    --style research_methods \
    --detail detailed \
    --language chinese \
    --slides 20 \
    --output my_presentation.pptx
```

## 8種學術風格

### 1. classic_academic（經典學術）
- 傳統學術語言，強調理論和研究方法
- 適合正式學術場合
- 嚴謹的用語和結構

### 2. modern_academic（現代學術）⭐ 默認
- 現代學術語言，結合視覺化和數據
- 清晰易懂，平衡深度與可讀性
- 適合一般學術報告

### 3. clinical（臨床導向）
- 臨床實務語言，強調應用和病例
- 適合醫學臨床相關簡報
- 連結理論與實踐

### 4. research_methods（研究方法）
- 著重研究設計和統計分析
- 適合方法學討論
- 詳細的方法論說明

### 5. literature_review（文獻回顧）
- 系統性文獻整理，比較不同研究
- 適合綜述類簡報
- 強調趨勢與發展脈絡

### 6. case_analysis（案例分析）
- 以具體案例為主的深入分析
- 適合個案研究報告
- 情境脈絡詳述

### 7. teaching（教學導向）
- 教學語言，循序漸進易懂
- 適合學習者
- 豐富的解釋說明

### 8. zettelkasten（Zettelkasten卡片盒）🆕
- 原子化筆記方法，每張投影片為獨立知識單元
- 強調概念連結與知識網絡
- 適合知識管理與長期累積

**Zettelkasten特色**：
- 每張投影片聚焦單一概念（原子筆記）
- 使用唯一識別碼（ID）標記知識卡片
- 明確標示概念間的連結關係
- 包含反向連結與相關概念
- 強調知識的可組合性與重用性

**Zettelkasten投影片格式**：
```
===ZK-20251027-001: 認知負荷理論===
卡片ID: ZK-20251027-001

核心概念：
認知負荷理論 (Cognitive Load Theory) 描述工作記憶在學習過程中的限制...

定義：
• 內在認知負荷 (Intrinsic Load)
• 外在認知負荷 (Extraneous Load)
• 相關認知負荷 (Germane Load)

連結概念：
→ ZK-20251027-002: 工作記憶模型
→ ZK-20251027-015: 多媒體學習原則

參考文獻：
Sweller, J. (1988). Cognitive load theory...

個人思考：
此理論對於設計教學簡報有重要啟示...
```

## 5種詳細程度

| 程度 | 每張重點 | 每點句數 | 適用場景 |
|------|---------|---------|---------|
| **minimal** | 2-3點 | 1句 | 快速概覽、高階報告 |
| **brief** | 3-4點 | 1-2句 | 標準簡報、團隊分享 |
| **standard** ⭐ | 4-5點 | 2-3句 | Journal Club、學術討論 |
| **detailed** | 5-6點 | 3-4句 | 深入分析、教學用途 |
| **comprehensive** | 6-8點 | 4-5句 | 全面報告、技術文件 |

## 3種語言模式

- **chinese**：繁體中文（請使用繁體中文撰寫所有內容）
- **english**：英文（Please write all content in English）
- **bilingual**：中英雙語（繁體中文為主，關鍵術語附英文）

## LLM平台支援

### 支援的LLM後端

此Skill設計為**平台無關**，可根據使用環境串接不同的LLM平台：

#### 1. Ollama（本地部署）⭐ 默認
```python
maker = SlideMaker(ollama_url="http://localhost:11434")

# 推薦模型
# - gemma2:latest - 通用生成，平衡性能
# - llama3.2:latest - 複雜分析，理解力強
# - qwen2.5:latest - 多語言支援優秀
```

**優勢**：
- ✅ 完全本地運行，隱私保護
- ✅ 無API費用
- ✅ 可離線使用
- ✅ 支援繁體中文優化模型

#### 2. OpenAI（雲端API）
```python
# 未來擴展支援
# 配置方式：
# export OPENAI_API_KEY="your-key"
# maker = SlideMaker(backend="openai", model="gpt-4")
```

**優勢**：
- ✅ 生成品質高
- ✅ 多模型選擇
- ⚠️ 需要API費用
- ⚠️ 需要網路連接

#### 3. Google AI（Gemini）
```python
# 未來擴展支援
# 配置方式：
# export GOOGLE_AI_API_KEY="your-key"
# maker = SlideMaker(backend="google", model="gemini-pro")
```

**優勢**：
- ✅ 整合Google生態
- ✅ 多模態支援
- ⚠️ 需要API金鑰

#### 4. 其他LLM平台
- Claude (Anthropic)
- Azure OpenAI
- 本地部署的其他模型（LM Studio, vLLM等）

### 選擇LLM的建議

| 使用情境 | 推薦平台 | 原因 |
|---------|---------|------|
| 日常使用、隱私要求高 | Ollama | 本地部署，無費用 |
| 最高品質、複雜任務 | OpenAI GPT-4 | 生成品質最佳 |
| 繁體中文優化 | Ollama (qwen2.5) | 中文理解佳 |
| 預算有限、大量使用 | Ollama | 無API費用 |
| 企業環境、合規要求 | Azure OpenAI | 企業級支援 |

### 配置LLM後端

**通過環境變數**：
```bash
# Ollama（默認）
export OLLAMA_URL="http://localhost:11434"

# 未來擴展：OpenAI
# export OPENAI_API_KEY="sk-..."
# export LLM_BACKEND="openai"

# 未來擴展：Google AI
# export GOOGLE_AI_API_KEY="..."
# export LLM_BACKEND="google"
```

**通過配置文件** (`config/settings.yaml`):
```yaml
llm:
  default_backend: "ollama"

  ollama:
    base_url: "http://localhost:11434"
    default_model: "gemma2:latest"
    timeout: 300

  # 未來擴展
  # openai:
  #   api_key: "from_env"
  #   default_model: "gpt-4"
  #   timeout: 120
```

**通過Python API**：
```python
# 使用Ollama
maker = SlideMaker(
    ollama_url="http://localhost:11434"
)

# 未來擴展：切換到其他後端
# maker = SlideMaker(
#     backend="openai",
#     api_key="sk-...",
#     model="gpt-4"
# )
```

## 工作流程

```
1. 輸入 → 主題 + 風格 + 詳細程度 + 語言
   ↓
2. 生成Prompt → 基於Jinja2模板 + 風格配置
   ↓
3. 調用LLM → Ollama/OpenAI/Google等
   ↓
4. 解析輸出 → Regex提取投影片結構
   ↓
5. 生成PPTX → python-pptx創建PowerPoint
   ↓
6. 輸出 → .pptx文件
```

## 投影片格式

### 標準格式
```
===標題頁===
標題：[主標題]
副標題：[副標題]

===投影片1===
標題：[投影片1的標題]
內容：
• [重點1，使用**粗體**標記關鍵詞]
• [重點2]
• [重點3]
```

### Zettelkasten格式
```
===ZK-20251027-001: 概念名稱===
卡片ID: ZK-20251027-001

核心概念：
[單一概念的定義與說明]

定義：
• [子概念1]
• [子概念2]

連結概念：
→ [相關卡片ID]: [概念名稱]

參考文獻：
[相關文獻]

個人思考：
[延伸思考]
```

## 配置選項

### 通過settings.yaml配置

```yaml
slides:
  default_style: "modern_academic"
  default_detail: "standard"
  default_language: "chinese"
  default_slide_count: 15
  min_slides: 5
  max_slides: 30

  output:
    save_directory: "output/slides"
    filename_pattern: "{topic}_{style}_{timestamp}.pptx"
```

## 輸出示例

生成的PPTX包含：
- 標題頁（含主標題和副標題）
- 內容頁（含標題和項目符號列表）
- 16:9比例
- 標準字體大小（標題大、內容適中）
- 清晰的視覺層次

**Zettelkasten特殊輸出**：
- 每張投影片包含卡片ID
- 明確的概念連結標記
- 結構化的筆記區塊
- 適合匯出為Markdown進行知識管理

## 進階功能

### 1. 自訂要求

```python
result = maker.generate_slides(
    topic="深度學習",
    custom_requirements="""
    - 著重於臨床應用
    - 加入統計分析細節
    - 強調研究限制
    """
)
```

### 2. PDF內容整合

```python
from src.extractors import PDFExtractor

# 提取PDF
extractor = PDFExtractor(max_chars=10000)
pdf_data = extractor.extract("paper.pdf")

# 基於PDF生成
result = maker.generate_slides(
    topic=pdf_data['structure']['title'],
    pdf_content=pdf_data['full_text'],
    style="literature_review"
)
```

### 3. Zettelkasten工作流

```python
# 步驟1：生成原子筆記簡報
result = maker.generate_slides(
    topic="認知負荷理論",
    style="zettelkasten",
    slide_count=10
)

# 步驟2：可以匯出為Markdown格式
# （待開發：PPTX → Markdown轉換工具）

# 步驟3：整合到知識管理系統
# （可串接Obsidian、Notion等）
```

### 4. 批量生成

```python
papers = ["paper1.pdf", "paper2.pdf", "paper3.pdf"]

for paper in papers:
    output = make_slides(
        topic=f"評論：{Path(paper).stem}",
        pdf_path=paper,
        style="literature_review"
    )
    print(f"完成: {output}")
```

## 錯誤處理

常見問題與解決方案：

**LLM連接失敗**:
```python
# Ollama - 檢查服務是否運行
curl http://localhost:11434/api/tags

# 修改API地址
maker = SlideMaker(ollama_url="http://custom:port")
```

**投影片解析失敗**:
- 檢查LLM輸出格式
- 確保使用正確的模板
- 查看 `llm_output` 欄位診斷問題

**依賴缺失**:
```bash
pip install jinja2 pyyaml python-pptx
```

## 與其他Skills整合

```python
# 完整工作流：PDF → 分析 → 簡報 → 知識庫
from src.extractors import PDFExtractor
from src.knowledge_base import KnowledgeBaseManager
from src.generators import make_slides

# 1. 提取PDF
extractor = PDFExtractor()
paper_data = extractor.extract("paper.pdf")

# 2. 加入知識庫
kb = KnowledgeBaseManager()
paper_id = kb.add_paper(...)

# 3. 生成投影片
output = make_slides(
    topic=paper_data['structure']['title'],
    pdf_path="paper.pdf",
    style="zettelkasten"  # 原子筆記風格
)

# 4. 連結到知識庫主題
topic_id = kb.add_topic("認知科學")
kb.link_paper_to_topic(paper_id, topic_id)
```

## 最佳實踐

1. **選擇合適風格**：根據聽眾和場合選擇
2. **Zettelkasten用於知識積累**：長期研究項目使用卡片盒風格
3. **調整詳細程度**：時間短用minimal，深入討論用detailed
4. **PDF長度限制**：保持在10,000字元以內
5. **測試LLM輸出**：先用少量投影片測試
6. **選擇合適的LLM平台**：根據需求、預算和環境選擇

## 限制與注意事項

- 需要運行LLM服務（Ollama或其他平台）
- PDF內容限制10,000字元（可配置）
- LLM生成時間取決於模型和長度（通常1-5分鐘）
- 格式依賴LLM輸出品質
- 目前不支援圖表插入（待開發）
- Zettelkasten風格需要後續工具支援（Markdown匯出等）

## 未來擴展

- [ ] OpenAI、Google AI等多平台後端支援
- [ ] Zettelkasten專用Markdown匯出工具
- [ ] 圖表和表格插入
- [ ] 自訂PPTX模板
- [ ] 批量處理介面
- [ ] 投影片品質評估
- [ ] 與Obsidian、Notion等知識管理工具整合

---

**相關文檔**:
- templates/styles/academic_styles.yaml - 風格配置（含Zettelkasten）
- templates/prompts/journal_club_template.jinja2 - Prompt模板
- src/generators/slide_maker.py - 源碼
