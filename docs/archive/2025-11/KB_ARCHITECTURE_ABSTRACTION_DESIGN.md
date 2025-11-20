# 知識庫架構抽象設計 (KB Architecture Abstraction Layer)

**設計日期**: 2025-11-02
**狀態**: 📋 設計階段 (待 Phase 2.2 實現)
**目標**: 支援多種知識庫結構，為未來第二套知識庫整合做準備

---

## 🎯 設計目標

用戶提到："核心 CLI 工具到達能調適不同知識庫架構的狀態時，提示我可以導入的數量及篩選建議"

這意味著需要：
1. **統一接口** - 支持不同的 KB 結構
2. **自適應分析** - 根據 KB 結構推薦導入數量
3. **智能建議** - 提供針對性的篩選建議

---

## 📐 整體架構設計

```
┌─────────────────────────────────────────────────────┐
│           KB Architecture Abstraction Layer          │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │
│  │  KB Adapter  │  │ KB Analyzer  │  │ Import   │ │
│  │   Interface  │  │    Engine    │  │ Advisor  │ │
│  └──────────────┘  └──────────────┘  └──────────┘ │
│         △                  △                △       │
│         │                  │                │       │
│  ┌──────┴──────────────────┴────────────────┴────┐ │
│  │     Unified KB Access Layer                   │ │
│  └──────────────────────────────────────────────┘ │
│         △                  △                       │
└─────────┼──────────────────┼───────────────────────┘
          │                  │
    ┌─────┴─────┐      ┌─────┴────────────┐
    │ Current KB│      │ Future KB(s)     │
    │ (SQLite)  │      │ (Various types)  │
    └───────────┘      └──────────────────┘
```

---

## 🔧 核心組件設計

### 1. KB Adapter Interface

抽象基類，定義所有 KB 必須實現的接口：

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class PaperMetadata:
    """統一的論文元數據結構"""
    id: str                          # 唯一識別符
    title: str
    authors: List[str]
    year: int
    abstract: Optional[str]
    keywords: List[str]
    source: str                      # 'current_kb' / 'zotero' / 'other_kb'

    # 架構特定欄位
    extra_fields: Dict[str, Any]    # 容納不同 KB 的額外欄位

class KBAdapter(ABC):
    """知識庫適配器基類"""

    @abstractmethod
    def connect(self, connection_params: Dict[str, Any]) -> bool:
        """連接到知識庫"""
        pass

    @abstractmethod
    def get_total_papers(self) -> int:
        """獲取論文總數"""
        pass

    @abstractmethod
    def get_papers(self, limit: int = None) -> List[PaperMetadata]:
        """獲取所有論文"""
        pass

    @abstractmethod
    def get_paper_by_id(self, paper_id: str) -> PaperMetadata:
        """根據 ID 獲取論文"""
        pass

    @abstractmethod
    def search_papers(self, query: str) -> List[PaperMetadata]:
        """搜索論文"""
        pass

    @abstractmethod
    def get_schema_info(self) -> Dict[str, Any]:
        """獲取 KB 的架構信息"""
        pass

    @abstractmethod
    def add_paper(self, paper: PaperMetadata) -> str:
        """添加論文，返回新 ID"""
        pass

    @abstractmethod
    def update_paper(self, paper_id: str, paper: PaperMetadata) -> bool:
        """更新論文"""
        pass

    @abstractmethod
    def delete_paper(self, paper_id: str) -> bool:
        """刪除論文"""
        pass
```

---

### 2. Specific Implementations

#### A. SQLite KB Adapter (當前實現)

```python
class SQLiteKBAdapter(KBAdapter):
    """當前系統使用的 SQLite 適配器"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None

    def connect(self, connection_params: Dict[str, Any]) -> bool:
        """連接 SQLite 數據庫"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            return True
        except Exception as e:
            return False

    def get_total_papers(self) -> int:
        """從 papers 表獲取總數"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM papers")
        return cursor.fetchone()[0]

    def get_papers(self, limit: int = None) -> List[PaperMetadata]:
        """從 papers 表獲取所有論文"""
        cursor = self.conn.cursor()
        if limit:
            cursor.execute("SELECT * FROM papers LIMIT ?", (limit,))
        else:
            cursor.execute("SELECT * FROM papers")

        papers = []
        for row in cursor.fetchall():
            papers.append(self._row_to_metadata(row))
        return papers

    def get_schema_info(self) -> Dict[str, Any]:
        """分析 SQLite 架構"""
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA table_info(papers)")

        schema = {
            'db_type': 'sqlite',
            'table_name': 'papers',
            'columns': [],
            'primary_key': 'id'
        }

        for col_info in cursor.fetchall():
            schema['columns'].append({
                'name': col_info[1],
                'type': col_info[2],
                'nullable': col_info[3] == 0
            })

        return schema
```

#### B. Future Adapters (等待實現)

```python
class PostgresKBAdapter(KBAdapter):
    """用於 PostgreSQL 數據庫"""
    pass

class MongoDBKBAdapter(KBAdapter):
    """用於 MongoDB NoSQL 數據庫"""
    pass

class GraphDBKBAdapter(KBAdapter):
    """用於圖數據庫 (Neo4j)"""
    pass

class FileSystemKBAdapter(KBAdapter):
    """用於文件系統 (Markdown/JSON)"""
    pass
```

---

### 3. KB Analyzer Engine

```python
@dataclass
class KBProfile:
    """知識庫特性分析結果"""
    total_papers: int
    avg_metadata_completeness: float  # 0-1, 元數據完整度
    author_count: int
    concept_count: int
    year_range: Tuple[int, int]
    language_distribution: Dict[str, int]
    domain_distribution: Dict[str, int]

    # 容量和效能預估
    estimated_search_latency_ms: float
    estimated_vector_embedding_capacity: int

    # 品質評估
    quality_score: float  # 0-100
    completeness_issues: List[str]

class KBAnalyzer:
    """知識庫分析引擎"""

    def __init__(self, adapter: KBAdapter):
        self.adapter = adapter

    def analyze(self) -> KBProfile:
        """深入分析知識庫"""
        papers = self.adapter.get_papers()

        profile = KBProfile(
            total_papers=len(papers),
            avg_metadata_completeness=self._calculate_completeness(papers),
            author_count=self._count_unique_authors(papers),
            concept_count=self._count_unique_concepts(papers),
            year_range=self._get_year_range(papers),
            language_distribution=self._analyze_languages(papers),
            domain_distribution=self._analyze_domains(papers),
            estimated_search_latency_ms=self._estimate_search_latency(len(papers)),
            estimated_vector_embedding_capacity=self._estimate_embedding_capacity(len(papers)),
            quality_score=self._calculate_quality_score(papers),
            completeness_issues=self._identify_completeness_issues(papers)
        )

        return profile

    def _calculate_completeness(self, papers: List[PaperMetadata]) -> float:
        """計算元數據完整度 (0-1)"""
        if not papers:
            return 0.0

        required_fields = ['title', 'authors', 'year']
        completeness_scores = []

        for paper in papers:
            score = 0
            for field in required_fields:
                if getattr(paper, field, None):
                    score += 1
            completeness_scores.append(score / len(required_fields))

        return sum(completeness_scores) / len(papers)
```

---

### 4. Import Advisor

```python
@dataclass
class ImportRecommendation:
    """導入建議"""
    source_kb_profile: KBProfile
    target_kb_profile: KBProfile

    recommended_quantity: int
    recommended_quantity_range: Tuple[int, int]
    risk_level: str  # 'low', 'medium', 'high'

    filtering_criteria: Dict[str, Any]
    expected_impact: Dict[str, Any]

    rationale: str

class ImportAdvisor:
    """導入建議顧問"""

    def __init__(self, target_adapter: KBAdapter):
        """target_adapter: 目標知識庫（當前 KB）"""
        self.target_adapter = target_adapter
        self.target_analyzer = KBAnalyzer(target_adapter)
        self.target_profile = self.target_analyzer.analyze()

    def advise_import(self, source_adapter: KBAdapter) -> ImportRecommendation:
        """為源知識庫提供導入建議"""

        source_analyzer = KBAnalyzer(source_adapter)
        source_profile = source_analyzer.analyze()

        # 計算推薦數量
        recommended_qty = self._calculate_recommended_quantity(
            source_profile,
            self.target_profile
        )

        # 評估風險
        risk_level = self._assess_risk(
            source_profile,
            self.target_profile,
            recommended_qty
        )

        # 提供篩選建議
        filtering_criteria = self._suggest_filtering(
            source_profile,
            recommended_qty
        )

        # 預估影響
        expected_impact = self._estimate_impact(
            self.target_profile,
            recommended_qty
        )

        return ImportRecommendation(
            source_kb_profile=source_profile,
            target_kb_profile=self.target_profile,
            recommended_quantity=recommended_qty,
            recommended_quantity_range=(
                int(recommended_qty * 0.7),
                int(recommended_qty * 1.3)
            ),
            risk_level=risk_level,
            filtering_criteria=filtering_criteria,
            expected_impact=expected_impact,
            rationale=self._generate_rationale(...)
        )

    def _calculate_recommended_quantity(
        self,
        source_profile: KBProfile,
        target_profile: KBProfile
    ) -> int:
        """
        基於多個因素計算推薦導入數量：
        1. 目標 KB 當前大小
        2. 源 KB 的質量
        3. 系統搜索延遲預算
        4. 向量嵌入容量
        """

        # 因素 1: 大小平衡 (保持 10-30 倍增長)
        size_factor = min(
            source_profile.total_papers,
            target_profile.total_papers * 30
        )

        # 因素 2: 質量折扣 (質量低則減少)
        quality_factor = source_profile.quality_score / 100.0

        # 因素 3: 搜索延遲預算 (<200ms)
        latency_budget = self._calculate_latency_budget(
            target_profile.estimated_search_latency_ms
        )

        # 因素 4: 向量容量
        embedding_capacity = source_profile.estimated_vector_embedding_capacity

        # 加權計算
        recommended = int(
            size_factor * quality_factor * latency_budget * 0.8
        )

        return min(recommended, embedding_capacity)

    def _suggest_filtering(
        self,
        source_profile: KBProfile,
        target_quantity: int
    ) -> Dict[str, Any]:
        """提供篩選建議"""

        return {
            'metadata_completeness_threshold': 0.8,
            'exclude_domains': ['unrelated_domain'],
            'exclude_file_sizes': [
                {'min': 0, 'max': 100_000},      # <100KB
                {'min': 5_000_000, 'max': None}  # >5MB
            ],
            'priority_criteria': {
                'language_match': True,
                'domain_relevance': 0.7,
                'metadata_quality': 0.8,
                'recency': True
            }
        }

    def _estimate_impact(
        self,
        target_profile: KBProfile,
        import_quantity: int
    ) -> Dict[str, Any]:
        """預估導入對系統的影響"""

        # 估計導入論文的作者數、概念數等
        estimated_authors = int(import_quantity * 3.5)  # 平均
        estimated_concepts = int(import_quantity * 1.3)

        return {
            'new_papers': import_quantity,
            'new_authors': estimated_authors,
            'new_concepts': estimated_concepts,
            'new_total_papers': target_profile.total_papers + import_quantity,
            'search_latency_increase_percent': 30,  # 預估
            'vector_index_size_increase_mb': import_quantity * 2,
            'database_size_increase_mb': import_quantity * 0.5
        }
```

---

## 📊 應用場景

### 場景 1: 當前系統 (已實現)

```python
from src.knowledge_base import KnowledgeBaseManager

# 當前系統適配器
current_kb = SQLiteKBAdapter(
    db_path="knowledge_base/index.db"
)
current_kb.connect({})

# 分析當前知識庫
analyzer = KBAnalyzer(current_kb)
profile = analyzer.analyze()

print(f"Current KB: {profile.total_papers} papers")
print(f"Quality score: {profile.quality_score}/100")
print(f"Estimated search latency: {profile.estimated_search_latency_ms}ms")
```

### 場景 2: Zotero 導入 (正在進行)

```python
# Zotero 作為源
zotero_kb = ZoteroKBAdapter(
    bibtex_path="D:\\...\\My Library.bib",
    pdf_directory="D:\\...\\+\\pdf"
)
zotero_kb.connect({})

# 獲取導入建議
advisor = ImportAdvisor(current_kb)
recommendation = advisor.advise_import(zotero_kb)

print(f"Recommended import: {recommendation.recommended_quantity} papers")
print(f"Risk level: {recommendation.risk_level}")
print(f"Filtering criteria: {recommendation.filtering_criteria}")
print(f"Expected impact: {recommendation.expected_impact}")
```

### 場景 3: 第二套知識庫整合 (未來)

```python
# 用戶的第二套知識庫（例如 PostgreSQL、Graph DB）
second_kb = PostgresKBAdapter(
    connection_string="postgresql://user:pass@host/dbname"
)
second_kb.connect({'host': 'localhost', 'port': 5432})

# 自動分析並提供建議
recommendation = advisor.advise_import(second_kb)

print(f"Second KB contains: {second_kb.get_total_papers()} papers")
print(f"Recommended to import: {recommendation.recommended_quantity}")
print(f"Estimated new total: {recommendation.expected_impact['new_total_papers']}")
```

---

## 🔄 整合計畫

### Phase 2.2 (下週)
- [ ] 實現 `KBAdapter` 基類和接口
- [ ] 實現 `SQLiteKBAdapter` (當前系統適配)
- [ ] 實現 `ZoteroKBAdapter` (BibTeX + PDF)

### Phase 2.3 (2 週後)
- [ ] 實現 `KBAnalyzer` 分析引擎
- [ ] 實現 `ImportAdvisor` 建議系統
- [ ] 為 CLI 添加 `--analyze-kb` 和 `--advise-import` 命令

### Phase 3.0 (未來)
- [ ] 實現 `PostgresKBAdapter`
- [ ] 實現 `GraphDBKBAdapter`
- [ ] 實現 `FileSystemKBAdapter`
- [ ] 為用戶的第二套知識庫提供整合支持

---

## 💡 設計優勢

1. **可擴展性**
   - 易於添加新的 KB 類型
   - 統一的適配器接口

2. **自適應**
   - 根據 KB 特徵自動調整建議
   - 無需用戶手動設置

3. **智能化**
   - 考慮多個因素：大小、質量、性能
   - 風險評估和預期影響預估

4. **向後兼容**
   - 當前系統無需改動
   - 新功能逐步整合

---

## 📋 實現路線

```
當前狀態 (2025-11-02):
├─ ✅ Zotero 評估完成
├─ ✅ 本地 PDF 分析完成
├─ 📋 KB 架構抽象設計完成 (此文檔)
└─ 🔄 Phase 2.2 準備中

Phase 2.2 (2025-11-08):
├─ ZoteroSync 實現
├─ 第一批導入執行
└─ KBAdapter 框架初步實現

Phase 2.3 (2025-11-15):
├─ KBAnalyzer 完整實現
├─ ImportAdvisor 系統上線
└─ CLI 命令集成

用戶的第二個知識庫整合時:
├─ 選擇/實現合適的適配器
├─ 運行分析和建議
└─ 執行導入
```

---

**設計完成**: 2025-11-02 23:58
**狀態**: 📋 設計階段完成，等待 Phase 2.2 實現
**下一步**: 用戶確認導入計畫後，開始 Phase 2.2 開發

