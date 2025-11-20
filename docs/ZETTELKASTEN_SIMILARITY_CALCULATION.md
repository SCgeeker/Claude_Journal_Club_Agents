# Zettelkasten 原子卡片概念相似性計算指南

**文件版本**: 1.0
**生成日期**: 2025-11-05
**適用模組**: relation_finder.py (Phase 2.1) 和 concept_mapper.py (Phase 2.2)

---

## 📋 目錄

1. [概述](#概述)
2. [relation_finder 的相似性計算](#relation_finder-的相似性計算)
3. [concept_mapper 的相似性應用](#concept_mapper-的相似性應用)
4. [原子卡片元素詳解](#原子卡片元素詳解)
5. [計算流程圖](#計算流程圖)
6. [使用示例](#使用示例)
7. [性能和優化](#性能和優化)

---

## 概述

Zettelkasten（卡片盒筆記法）系統中，原子卡片之間的概念相似性計算是構建知識網絡的核心。本系統採用**向量相似度 + 多維度信度評分**的混合方法。

### 核心特徵

| 特徵 | 說明 |
|------|------|
| **相似度計算方式** | 基於向量嵌入（Gemini/Ollama）的余弦相似度 |
| **評分維度** | 4個維度加權（語義 40% + 連結 30% + 共同概念 20% + 領域 10%） |
| **關係類型識別** | 6種有向關係類型 |
| **主要依賴** | ChromaDB 向量數據庫 + SQLite 元數據 |
| **最小閾值** | 語義相似度 0.4，信度評分 0.3 |

---

## relation_finder 的相似性計算

### 1. 向量相似度計算（核心算法）

#### 代碼位置
`src/analyzers/relation_finder.py:470-504` (`find_concept_relations` 方法)

#### 計算流程

```python
# 步驟 1：使用向量搜索找相似卡片
similar_results = self.vector_db.find_similar_zettel(
    zettel_id=card_id,
    n_results=min(limit, len(cards) - 1),
    exclude_self=True
)

# 步驟 2：從距離計算相似度
# ChromaDB 返回距離（distance），相似度 = 1 - distance
similarity = 1.0 - similar_results['distances'][0][j]
```

#### 相似度來源

| 來源 | 說明 | 維度 | 模型 |
|------|------|------|------|
| **Gemini 嵌入** | Google Gemini Embedding-001 | 768 | embedding-001 |
| **Ollama 嵌入** | 本地 Qwen3-Embedding-4B | 2560 | qwen3-embedding:4b |

#### 相似度範圍解釋

| 範圍 | 解釋 | 關係類型 |
|------|------|----------|
| 0.9-1.0 | 非常相似，幾乎相同 | 可能是重複卡片 |
| 0.7-0.9 | 高度相似，核心概念相同 | related_to / superclass_of |
| 0.5-0.7 | 中等相似，有相關概念 | related_to / leads_to |
| 0.4-0.5 | 低相似，有間接關聯 | related_to（邊界） |
| <0.4 | 不相似，自動過濾 | （被排除） |

### 2. 多維度信度評分系統

#### 代碼位置
`src/analyzers/relation_finder.py:625-672` (`_calculate_confidence` 方法)

#### 評分公式

```
總信度分數 = Σ(各維度分數 × 權重)

信度 = semantic_similarity×0.4 + link_explicit×0.3 + co_occurrence×0.2 + domain_consistency×0.1
```

#### 維度詳解

##### 維度 1：語義相似度 (40%)

**計算方式**:
```python
semantic_score = similarity * 0.4  # similarity 來自向量相似度
```

**特點**:
- 直接使用向量模型的相似度結果
- 權重最高（40%），因為向量表示涵蓋了完整的語義信息
- 範圍：0.0-0.4（最多貢獻 40% 到總信度）

**例子**:
- 向量相似度 0.8 → 語義分數 = 0.8 × 0.4 = 0.32

##### 維度 2：明確連結 (30%)

**計算方式**:
```python
has_explicit_link = self._check_explicit_link(card1, card2_id)
link_score = 0.3 if has_explicit_link else 0.0
```

**連結檢查邏輯** (`_check_explicit_link` 方法, 674-695 行):
```python
# 優先使用 ai_notes（已淨化的 AI 內容）
ai_notes = card.get('ai_notes')
if ai_notes:
    ai_content = ai_notes
else:
    # Fallback：從 content 提取 AI 內容（過濾人類筆記）
    content = card.get('content', '')
    ai_content = extract_ai_content(content)

# 檢查 Obsidian 格式的連結: [[target_id]]
return f'[[{target_id}]]' in ai_content
```

**連結格式**:
- Obsidian Wiki Links: `[[CogSci-20251028-001]]`
- 不支援其他連結格式（如 `->` 或 `--leads_to-->`）

**特點**:
- 只有在卡片中存在**明確連結**時才獲得滿分
- 權重次高（30%），反映人類標註的重要性
- 範圍：0.0 或 0.3（二值選擇）

**例子**:
- Card A 的 AI 筆記中包含 `[[Card-B-ID]]` → 連結分數 = 0.3
- 無連結 → 連結分數 = 0.0

##### 維度 3：共同概念 (20%)

**計算方式**:
```python
shared_concepts = self._extract_shared_concepts_from_cards(card1, card2)
# 正規化：5 個以上共同概念得滿分
shared_score = min(len(shared) / 5.0, 1.0) * 0.2
```

**共同概念提取** (`_extract_shared_concepts_from_cards` 方法, 697-753 行):

提取來源：
1. **標籤 (tags)**
   - 來自資料庫的 `tags` 欄位
   - 格式：JSON 陣列 `["tag1", "tag2", ...]`

2. **核心概念 (core_concept)**
   - 來自資料庫的 `core_concept` 欄位
   - 提取過程：
     - 正則表達式分詞：`re.findall(r'\w+', core.lower())`
     - 過濾停用詞：只保留長度 ≥ 3 的詞
   - 例子：「認知科學中的視覺處理」→ `['認知', '科學', '中的', '視覺', '處理']` → `['認知', '科學', '視覺', '處理']`

3. **標題 (title)**
   - 來自資料庫的 `title` 欄位
   - 提取方式同核心概念
   - 例子：「視覺字符識別的神經機制」→ `['視覺', '字符', '識別', '神經', '機制']`

**共同概念計算**:
```python
concepts1 = extract_concepts(card1)  # Set of keywords
concepts2 = extract_concepts(card2)  # Set of keywords
shared = concepts1 & concepts2       # 交集
```

**正規化規則**:
```
shared_score = min(len(shared) / 5.0, 1.0) * 0.2

範例：
- 0 個共同概念 → shared_score = 0.0
- 1-2 個共同概念 → shared_score = 0.04-0.08
- 3-4 個共同概念 → shared_score = 0.12-0.16
- 5 個或以上 → shared_score = 0.2（滿分）
```

**特點**:
- 權重適中（20%），反映概念重疊程度
- 範圍：0.0-0.2（漸進式評分，非二值）
- 更多共同概念 = 更高信度

**例子**:
```
Card A: 標籤=[深度學習, 神經網絡], 核心概念="卷積神經網絡"
Card B: 標籤=[神經網絡, 圖像處理], 核心概念="圖像分類"

提取的共同概念：["神經網絡"]  → 1 個
shared_score = (1 / 5.0) * 0.2 = 0.04
```

##### 維度 4：領域一致性 (10%)

**計算方式**:
```python
domain1 = card1.get('domain', '')
domain2 = card2.get('domain', '')
domain_consistent = (domain1 == domain2) if domain1 and domain2 else False
domain_score = 0.1 if domain_consistent else 0.05
```

**領域值來源**:
- 資料庫的 `domain` 欄位
- 例子：`CogSci`、`Linguistics`、`AI`、`Research`

**計算規則**:
```
IF domain1 == domain2 AND 都非空:
    score = 0.1  (同領域，滿分)
ELSE:
    score = 0.05 (不同領域或缺失，半分)
```

**特點**:
- 權重最低（10%），作為補充指標
- 範圍：0.05 或 0.1（二值）
- 促進同領域卡片關聯

**例子**:
```
Card A: domain = "CogSci"
Card B: domain = "CogSci"
→ domain_score = 0.1

Card A: domain = "CogSci"
Card B: domain = "AI"
→ domain_score = 0.05
```

#### 信度評分綜合示例

**案例 1：高信度（優質相關）**
```
Card A: "視覺處理的神經機制"
Card B: "視覺皮層的激活模式"

計算:
- 語義相似度: 0.75 → semantic_score = 0.75 × 0.4 = 0.30
- 明確連結: 有 → link_score = 0.30
- 共同概念: ["視覺", "神經"] (2個) → shared_score = (2/5) × 0.2 = 0.08
- 領域一致性: CogSci = CogSci → domain_score = 0.10

總信度 = 0.30 + 0.30 + 0.08 + 0.10 = 0.78 ✅ 高信度
```

**案例 2：中等信度（需驗證）**
```
Card A: "機器學習基礎"
Card B: "深度學習應用"

計算:
- 語義相似度: 0.55 → semantic_score = 0.55 × 0.4 = 0.22
- 明確連結: 無 → link_score = 0.0
- 共同概念: ["學習", "深度"] (2個) → shared_score = (2/5) × 0.2 = 0.08
- 領域一致性: AI = AI → domain_score = 0.10

總信度 = 0.22 + 0.0 + 0.08 + 0.10 = 0.40 ⚠️ 邊界信度
```

**案例 3：低信度（弱關聯）**
```
Card A: "語言語法結構"
Card B: "音樂節奏模式"

計算:
- 語義相似度: 0.42 → semantic_score = 0.42 × 0.4 = 0.168
- 明確連結: 無 → link_score = 0.0
- 共同概念: [] (0個) → shared_score = 0.0
- 領域一致性: Linguistics ≠ Music → domain_score = 0.05

總信度 = 0.168 + 0.0 + 0.0 + 0.05 = 0.218 ❌ 低信度（可能被過濾）
```

### 3. 關係類型分類

#### 代碼位置
`src/analyzers/relation_finder.py:562-623` (`_classify_relation_type` 方法)

#### 六種關係類型

| 關係類型 | 符號 | 說明 | 判定條件 |
|---------|------|------|---------|
| **leads_to** | A → B | 導向/推導 | 卡片 A 導向卡片 B 的概念發展 |
| **based_on** | A ← B | 基於/依賴 | 卡片 A 基於卡片 B 的概念 |
| **related_to** | A ↔ B | 相關/相似 | 兩張卡片概念相關但無明確方向 |
| **contrasts_with** | A ⊗ B | 對比/對立 | 兩張卡片概念對比或相反 |
| **superclass_of** | A ⊃ B | 上位概念 | A 是 B 的更一般/抽象概念 |
| **subclass_of** | A ⊂ B | 下位概念 | A 是 B 的更具體/特例概念 |

#### 判定邏輯

**優先順序** (從高到低):

1. **檢查明確連結** (最可靠)
   ```python
   if f'[[{card2_id}]]' in card1.get('content', ''):
       # 檢查連結周圍的上下文關鍵詞
       if '-->' in content or '導向' in content or 'leads to' in content:
           return 'leads_to'
       elif '<--' in content or '基於' in content or 'based on' in content:
           return 'based_on'
   ```
   - 格式：`[[Card-ID-123]]`
   - 需要檢查周圍的方向關鍵詞

2. **檢查對比關鍵詞**
   ```python
   contrast_keywords = ['但', '然而', '相反', '對比', 'however', 'but', 'contrast', 'differ']
   if any(kw in content1 or kw in content2 for kw in contrast_keywords):
       return 'contrasts_with'
   ```

3. **檢查上下位關係關鍵詞**
   ```python
   superclass_keywords = ['包含', '抽象', '泛指', 'include', 'general', 'abstract', 'superclass']
   subclass_keywords = ['具體', '特例', '實例', 'specific', 'instance', 'example', 'subclass']

   if any(kw in content1 for kw in superclass_keywords):
       return 'superclass_of'
   if any(kw in content1 for kw in subclass_keywords):
       return 'subclass_of'
   ```

4. **基於相似度判定** (備選)
   ```python
   if similarity >= 0.7:
       return 'related_to'
   elif similarity >= 0.5:
       # 檢查方向性關鍵詞
       directional_keywords = ['因此', '所以', '導致', 'therefore', 'thus', 'result']
       if any(kw in content1 for kw in directional_keywords):
           return 'leads_to'
       return 'related_to'
   else:
       return 'related_to'  # 預設
   ```

#### 關係判定示例

**示例 1：明確導向關係**
```
Card A (AI-20251028-001): 深度學習基礎
內容: "[[AI-20251028-002]] 導向更複雜的...", 相似度=0.72

判定: leads_to
理由: (1) 找到明確連結 [[...]], (2) 內容包含「導向」關鍵詞
```

**示例 2：對比關係**
```
Card A: 古典機器學習
Card B: 深度學習
共同內容: "...但深度學習相比傳統機器學習...", 相似度=0.68

判定: contrasts_with
理由: (1) 內容包含「但」關鍵詞, (2) 邏輯上對比
```

**示例 3：上位概念**
```
Card A: 機器學習（包含各種算法）
Card B: 神經網絡
內容: "機器學習包含監督學習、無監督學習...", 相似度=0.65

判定: superclass_of
理由: (1) A 內容包含「包含」關鍵詞, (2) 概念層級明確
```

**示例 4：純相似度判定**
```
Card A: CNN 架構
Card B: RNN 架構
無明確連結、無特殊關鍵詞, 相似度=0.58

判定: related_to
理由: (1) 無明確連結, (2) 無對比/上下位關鍵詞, (3) 相似度 0.5-0.7 範圍
```

---

## concept_mapper 的相似性應用

concept_mapper 模組基於 relation_finder 計算的相似性和信度，進行高級網絡分析。

### 1. 中心性分析（識別關鍵概念）

#### 代碼位置
`src/analyzers/concept_mapper.py:413-593` (`CentralityAnalyzer` 類)

#### PageRank 計算

**原理**：基於有向圖的迭代算法，識別整體影響力最大的節點。

**計算公式**:
```
PR(A) = (1-d)/N + d × Σ(PR(B)/|B的出邊數|)
        其中：d = damping factor (0.85)
             N = 總節點數
             B = 指向 A 的節點
```

**實現細節**（第 488-527 行）:
```python
def _calculate_pagerank(
    self,
    damping: float = 0.85,      # 阻尼係數
    max_iterations: int = 100,   # 最大迭代次數
    tolerance: float = 1e-6      # 收斂閾值
) -> Dict[str, float]:
    nodes = list(self.network.node_dict.keys())
    n = len(nodes)

    # 初始化：所有節點 PageRank = 1/N
    ranks = {node: 1.0 / n for node in nodes}

    # 迭代直到收斂
    for iteration in range(max_iterations):
        new_ranks = {}
        max_diff = 0.0

        for node in nodes:
            rank_sum = 0.0

            # 計算來自鄰居的貢獻
            for neighbor in self.network.get_neighbors(node):
                neighbor_degree = self.network.node_dict[neighbor]['degree']
                if neighbor_degree > 0:
                    rank_sum += ranks[neighbor] / neighbor_degree

            new_rank = (1 - damping) / n + damping * rank_sum
            new_ranks[node] = new_rank

            # 檢查收斂
            diff = abs(new_rank - ranks[node])
            max_diff = max(max_diff, diff)

        ranks = new_ranks

        if max_diff < tolerance:  # 收斂條件
            break

    return ranks
```

**例子**:
```
網絡: A → B → C → A (迴環)
     D → A (孤立入邊)

初始: PR(A)=PR(B)=PR(C)=PR(D)=0.25

迭代1:
PR(A) = 0.15/4 + 0.85 × (PR(C)/1 + PR(D)/1) = 0.0375 + 0.85×0.5 = 0.4625
PR(B) = 0.15/4 + 0.85 × (PR(A)/2) = 0.0375 + 0.85×0.125 = 0.1438
...

迭代100（收斂後）:
PR(A) ≈ 0.35  ← 最高（有來自C和D的貢獻）
PR(B) ≈ 0.25
PR(C) ≈ 0.25
PR(D) ≈ 0.15  ← 最低（無入邊）
```

#### 度中心性（Degree Centrality）

**公式**:
```
C_d(v) = degree(v) / (n-1)
```

**特點**:
- 簡單直接：直接計算節點的連接數
- 歸一化到 0-1 之間
- 範圍：越高 = 越多連接 = 越中心

**例子**:
```
5 個節點的網絡
Node A: degree=4 → C_d(A) = 4/4 = 1.0（最中心）
Node B: degree=2 → C_d(B) = 2/4 = 0.5
Node C: degree=1 → C_d(C) = 1/4 = 0.25（最邊緣）
```

#### 介數中心性（Betweenness Centrality）

**原理**：經過該節點的最短路徑佔比。

**計算方式** (第 449-475 行，簡化版):
```python
def _betweenness_centrality(self, node_id: str) -> float:
    total_paths = 0
    paths_through_node = 0

    # 隨機採樣節點對（避免計算所有對 O(n³)）
    nodes = list(self.network.node_dict.keys())
    sample_size = min(50, len(nodes))  # 最多採樣 50 對

    import random
    sampled_pairs = []
    for _ in range(sample_size):
        s = random.choice(nodes)
        t = random.choice(nodes)
        if s != t and s != node_id and t != node_id:
            sampled_pairs.append((s, t))

    for s, t in sampled_pairs:
        path = self._bfs_shortest_path(s, t)
        if path:
            total_paths += 1
            if node_id in path:
                paths_through_node += 1

    return paths_through_node / total_paths if total_paths > 0 else 0.0
```

**特點**:
- 高成本算法（原始 O(n³)），此實現採樣 50 對來優化
- 識別「橋接節點」（連接不同社群的節點）
- 範圍：0-1，越高 = 越多路徑經過

#### 接近中心性（Closeness Centrality）

**公式**:
```
C_c(v) = 1 / avg_distance_to_others
```

**計算方式** (第 477-486 行):
```python
def _closeness_centrality(self, node_id: str) -> float:
    distances = self._bfs_distances(node_id)  # BFS 計算距離

    if not distances:
        return 0.0

    avg_distance = sum(distances.values()) / len(distances)
    return 1.0 / avg_distance if avg_distance > 0 else 0.0
```

**特點**:
- 衡量節點到其他所有節點的平均距離
- 越接近 = 越中心
- 對全局網絡結構敏感

### 2. 社群檢測（識別概念群集）

#### 代碼位置
`src/analyzers/concept_mapper.py:120-284` (`CommunityDetector` 類)

#### Louvain 算法（實現）

**目標**：最大化模組度（modularity），找到最優社群分割。

**演算法步驟** (第 182-234 行):

```python
def _detect_by_louvain(self) -> List[Community]:
    # 1. 初始化：每個節點一個社群
    node_to_community = {node: i for i, node in enumerate(self.network.node_dict.keys())}

    improved = True
    iteration = 0
    max_iterations = 10

    # 2. 迭代優化
    while improved and iteration < max_iterations:
        improved = False
        iteration += 1

        for node in self.network.node_dict.keys():
            current_community = node_to_community[node]
            best_community = current_community
            best_gain = 0.0

            # 3. 嘗試移動到鄰居社群
            neighbor_communities = set()
            for neighbor in self.network.get_neighbors(node):
                neighbor_communities.add(node_to_community[neighbor])

            # 4. 計算每個鄰居社群的增益
            for community in neighbor_communities:
                gain = self._calculate_modularity_gain(
                    node, current_community, community, node_to_community
                )
                if gain > best_gain:
                    best_gain = gain
                    best_community = community

            # 5. 移動到最佳社群
            if best_community != current_community:
                node_to_community[node] = best_community
                improved = True

    # 6. 構建社群對象
    community_nodes = defaultdict(list)
    for node, comm_id in node_to_community.items():
        community_nodes[comm_id].append(node)

    communities = []
    for comm_id, nodes in community_nodes.items():
        if len(nodes) > 1:
            community = self._create_community(comm_id, nodes)
            communities.append(community)

    return communities
```

#### 社群密度計算

**公式**:
```
Density = 內部邊數 / 最大可能邊數
        = E_internal / (|V| × (|V|-1) / 2)
```

**實現** (第 257-284 行):
```python
def _create_community(self, community_id: int, nodes: List[str]) -> Community:
    # 計算社群密度
    internal_edges = 0
    for node in nodes:
        for neighbor in self.network.get_neighbors(node):
            if neighbor in nodes:
                internal_edges += 1
    internal_edges //= 2  # 無向圖，每條邊計算兩次

    max_edges = len(nodes) * (len(nodes) - 1) / 2
    density = internal_edges / max_edges if max_edges > 0 else 0.0

    # 找出 hub 節點（度最大）
    hub_node = max(nodes, key=lambda n: self.network.node_dict[n]['degree'])

    # 提取 top 概念
    titles = [self.network.node_dict[n]['title'] for n in nodes]
    top_concepts = titles[:5]

    return Community(
        community_id=community_id,
        nodes=nodes,
        size=len(nodes),
        density=density,
        top_concepts=top_concepts,
        hub_node=hub_node
    )
```

**密度範圍解釋**:
| 密度範圍 | 特徵 | 含義 |
|---------|------|------|
| 0.8-1.0 | 非常密集 | 高度相關的概念群，緊密內聚 |
| 0.5-0.8 | 密集 | 概念相關度高，有清晰邊界 |
| 0.2-0.5 | 中等 | 概念有關聯，但不全連接 |
| <0.2 | 稀疏 | 概念關聯鬆散，可能跨領域 |

**例子**:
```
社群：[Card-A, Card-B, Card-C]（3個節點）

如果內部邊：A-B, B-C, C-A（3條）
max_edges = 3 × 2 / 2 = 3
density = 3 / 3 = 1.0（完全連接）

如果內部邊：A-B, B-C（2條）
density = 2 / 3 ≈ 0.67（66% 密集）
```

### 3. 路徑分析（概念推導）

#### 代碼位置
`src/analyzers/concept_mapper.py:287-410` (`PathAnalyzer` 類)

#### 最短路徑尋找

**方法**：BFS（廣度優先搜索）

**實現** (第 296-324 行):
```python
def find_shortest_path(self, start: str, end: str) -> Optional[ConceptPath]:
    if start not in self.network.node_dict or end not in self.network.node_dict:
        return None

    # BFS
    queue = deque([(start, [start])])
    visited = {start}

    while queue:
        node, path = queue.popleft()

        if node == end:
            confidence = self._calculate_path_confidence(path)
            return ConceptPath(
                start_node=start,
                end_node=end,
                path=path,
                length=len(path) - 1,
                confidence=confidence
            )

        for neighbor in self.network.get_neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return None  # 無路徑
```

**特點**:
- 複雜度：O(V+E)，高效
- 返回最短路徑（最少跳轉數）
- 可用於概念推導鏈

#### 路徑信度計算

**公式**:
```
Path_Confidence = Avg(邊的信度)
```

**實現** (第 377-388 行):
```python
def _calculate_path_confidence(self, path: List[str]) -> float:
    if len(path) < 2:
        return 1.0

    confidences = []
    for i in range(len(path) - 1):
        edge = self.network.get_edge(path[i], path[i+1])
        if edge:
            confidences.append(edge.get('confidence', 0.5))

    return sum(confidences) / len(confidences) if confidences else 0.0
```

**例子**:
```
路徑：Card-A → Card-B → Card-C

邊信度：
- (A→B): 0.75
- (B→C): 0.68

路徑信度 = (0.75 + 0.68) / 2 = 0.715
→ 較高的路徑可靠性
```

---

## 原子卡片元素詳解

### 納入計算的元素總表

| 元素名稱 | 資料庫欄位 | 計算維度 | 權重 | 說明 |
|---------|----------|--------|------|------|
| **嵌入向量** | (ChromaDB) | 語義相似度 | 40% | Gemini/Ollama 向量模型的輸出 |
| **核心概念** | core_concept | 共同概念 | 20% | 卡片的基本理念，用於提取關鍵詞 |
| **標籤** | tags | 共同概念 | 20% | 結構化標籤列表，直接納入概念計算 |
| **標題** | title | 共同概念 | 20% | 卡片標題，用於提取關鍵詞 |
| **內容** | content/ai_notes | 連結識別 | 30% | 用於檢測明確的 Wiki Links |
| **領域** | domain | 領域一致性 | 10% | 知識領域代碼 |
| **AI 筆記** | ai_notes | 連結識別 | 30% | 優先搜索位置（相對於 content） |

### 各元素的具體用途

#### 1. 核心概念（core_concept）

**位置**: `zettel_cards` 表的 `core_concept` 欄位

**內容示例**:
```
"視覺系統的結構與功能，包括視網膜、視叢、視皮層的訊息處理機制"
```

**提取方式**:
```python
# 分詞 (tokenization)
words = re.findall(r'\w+', core.lower())
# 過濾停用詞（保留 ≥3 字的詞）
keywords = [w for w in words if len(w) >= 3]
# 結果：['視覺', '系統', '結構', '功能', '視網膜', '視叢', '視皮層', '訊息', '處理', '機制']
```

**作用**:
- 捕捉卡片的**核心意涵**
- 相比標題更詳細，相比內容更精凝
- 提取的詞用於**共同概念計算**

#### 2. 標籤（tags）

**位置**: `zettel_cards` 表的 `tags` 欄位

**格式**:
```json
["視覺處理", "神經科學", "感知", "認知模型"]
```

**提取邏輯**:
```python
if isinstance(tags, str):
    if tags.startswith('['):
        tag_list = json.loads(tags)  # JSON 格式
    else:
        tag_list = [t.strip() for t in tags.split(',')]  # CSV 格式
elif isinstance(tags, list):
    tag_list = tags  # 已是列表

# 直接納入共同概念集合
concepts.update(tag_list)
```

**作用**:
- 提供**人工標註的概念**
- 比從文本提取更準確（人工選擇）
- 直接計入共同概念集合

**特點**:
- 如果有標籤，優先使用（無需分詞）
- 一個標籤 = 一個完整概念單位

#### 3. 標題（title）

**位置**: `zettel_cards` 表的 `title` 欄位

**內容示例**:
```
"視覺皮層 V1 區的空間頻率選擇性"
```

**提取方式**:
```python
words = re.findall(r'\w+', title.lower())
keywords = [w for w in words if len(w) >= 3]
# 結果：['視覺', '皮層', '空間', '頻率', '選擇']
```

**作用**:
- 提供**卡片的簡潔表述**
- 較之內容，信息密度高
- 用於提取**高質量關鍵詞**

#### 4. 內容（content 和 ai_notes）

**位置**: `zettel_cards` 表的 `content` 和 `ai_notes` 欄位

**用途分工**:

| 欄位 | 用途 | 來源 |
|------|------|------|
| `ai_notes` | 連結檢測優先搜索 | AI 生成的批判性筆記 |
| `content` | Fallback 來源 | 完整卡片內容（包含人類筆記） |

**連結檢測過程**:
```python
def _check_explicit_link(self, card: Dict, target_id: str) -> bool:
    # 優先使用 ai_notes
    ai_notes = card.get('ai_notes')
    if ai_notes:
        ai_content = ai_notes
    else:
        # Fallback：從 content 提取 AI 內容
        content = card.get('content', '')
        ai_content = extract_ai_content(content)  # 過濾人類筆記

    # 檢查 Obsidian Wiki Links
    return f'[[{target_id}]]' in ai_content
```

**連結格式**:
```markdown
# 例子 1：Wiki Link 在 ai_notes 中
**[AI Agent]**: 這個概念與 [[CogSci-20251028-002]] 密切相關...

# 例子 2：Wiki Link 在 content 中
## 相關概念
[[Linguistics-20251028-005]] 討論了類似的語法現象...
```

**作用**:
- 僅用於**明確連結識別**
- 不用於相似度或共同概念計算
- 提供 30% 的信度加權

#### 5. 領域（domain）

**位置**: `zettel_cards` 表的 `domain` 欄位

**常見值**:
```
"CogSci"      # 認知科學
"Linguistics"  # 語言學
"AI"           # 人工智慧
"Research"     # 通用研究
```

**作用**:
- 作為**領域一致性檢查**
- 促進同領域卡片相關（+0.1 vs +0.05）
- 權重最低（10%），作為補充指標

---

## 計算流程圖

### 整體流程（高層）

```
Zettelkasten 原子卡片庫
        ↓
    [1] 向量化
    使用 Gemini/Ollama 生成 768/2560 維向量
        ↓
    [2] 向量搜索
    ChromaDB find_similar_zettel()
    → 返回相似卡片列表 + 距離
        ↓
    [3] 轉換相似度
    similarity = 1.0 - distance
        ↓
    [4] 計算共同概念
    提取：tags + core_concept + title
    計算交集 → shared_concepts[]
        ↓
    [5] 檢查明確連結
    掃描 ai_notes/content 中的 [[card_id]]
        ↓
    [6] 多維度信度評分
    semantic(40%) + link(30%) + shared(20%) + domain(10%)
        ↓
    [7] 分類關係類型
    基於相似度、關鍵詞、連結方向
        ↓
    ConceptRelation 對象
    (card_id_1, card_id_2, relation_type, confidence, similarity)
        ↓
    [8] 高級分析（concept_mapper）
    社群檢測 | 路徑分析 | 中心性分析
        ↓
    最終輸出：概念網絡 + 視覺化 + 報告
```

### 信度評分詳細流程

```
ConceptRelation 創建流程
        ↓
┌─────────────────────────────┐
│   逐對卡片處理              │
│  (card_i, card_j for j>i)  │
└────────┬────────────────────┘
         ↓
    向量相似度計算
    similarity = 1.0 - distance
         ↓
    ↙        ↖
 (< 0.4)?    (≥ 0.4) ✓
   ❌          ↓
   排除    ┌──────────────────┐
          │  分類關係類型    │
          └────────┬─────────┘
                   ↓
            ┌──────────────────────┐
            │  計算信度評分        │
            └────────┬─────────────┘
                     ↓
    ┌────────────────┼────────────────┐
    ↓                ↓                ↓
semantic_score   link_score      co_occurrence
= sim × 0.4     [0.3 or 0]      = min(len/5, 1.0)×0.2
    ↓                ↓                ↓
  檢查            檢查           提取共同
  向量            Wiki           概念
  相似            Links          詞彙
  度              ([[...]])       計數
    ↓                ↓                ↓
  [0-0.4]      [是否存在]      [0-5個]
    │                │                │
    └────────────────┼────────────────┘
                     ↓
                domain_score
                  [0.1 or 0.05]
                     ↓
                     │
    ┌────────────────┴────────────────┐
    ↓                                  ↓
domain1 == domain2            domain1 ≠ domain2
    ↓                                  ↓
  0.1 分                            0.05 分
 (同領域)                          (不同/缺失)
    ↓                                  ↓
    └────────────────┬────────────────┘
                     ↓
        總信度 = sum(所有維度)
                     ↓
    ┌───────────────────────────────────┐
    │  confidence_score ∈ [0.0, 1.0]   │
    └─────────────┬─────────────────────┘
                  ↓
    ┌─────────────────────────────┐
    │  過濾低信度 (<0.3)         │
    └──────────┬──────────────────┘
               ↓
    ConceptRelation 對象
    ✓ 保留用於後續分析
```

---

## 使用示例

### 示例 1：完整的相似性分析工作流

```python
from src.analyzers.relation_finder import RelationFinder
from src.analyzers.concept_mapper import ConceptMapper

# 初始化
finder = RelationFinder(kb_path="knowledge_base")

# 步驟 1：識別概念關係（原子卡片）
print("識別 Zettelkasten 卡片間的語義關係...")
relations = finder.find_concept_relations(
    min_similarity=0.4,      # 最小向量相似度
    relation_types=None,     # 所有關係類型
    limit=100               # 每張卡片最多檢查 100 個相似卡片
)

# 輸出樣本
for rel in relations[:5]:
    print(f"{rel.card_id_1} --{rel.relation_type}--> {rel.card_id_2}")
    print(f"  信度: {rel.confidence_score:.3f}")
    print(f"  相似度: {rel.semantic_similarity:.3f}")
    print(f"  共同概念: {', '.join(rel.shared_concepts)}")
    print(f"  明確連結: {rel.link_explicit}")
    print()

# 步驟 2：建構概念網絡
print("建構概念網絡...")
network_data = finder.build_concept_network(
    min_similarity=0.4,
    min_confidence=0.3
)

# 步驟 3：高級分析
mapper = ConceptMapper(kb_path="knowledge_base")
results = mapper.analyze_all(
    output_dir="output/concept_analysis",
    visualize=True,
    obsidian_mode=True
)

print(f"找到 {len(results['communities'])} 個概念社群")
print(f"識別出 {len(results['paths'])} 條推導路徑")
```

### 示例 2：查詢特定卡片的相似卡片

```python
# 找到與某個卡片最相似的其他卡片
finder = RelationFinder()

# 獲取特定卡片的關係
target_card_id = "CogSci-20251028-001"

relations = finder.find_concept_relations(min_similarity=0.5)

# 篩選與目標卡片相關的關係
target_relations = [
    r for r in relations
    if r.card_id_1 == target_card_id or r.card_id_2 == target_card_id
]

# 按信度排序
target_relations.sort(key=lambda r: r.confidence_score, reverse=True)

# 顯示結果
for rel in target_relations[:10]:
    other_id = rel.card_id_2 if rel.card_id_1 == target_card_id else rel.card_id_1
    print(f"相似卡片: {other_id}")
    print(f"  關係: {rel.relation_type}")
    print(f"  信度: {rel.confidence_score:.3f}")
    print(f"  相似度: {rel.semantic_similarity:.3f}")
```

### 示例 3：信度評分拆解

```python
# 檢查特定關係的信度計算詳情
from src.analyzers.relation_finder import RelationFinder

finder = RelationFinder()

# 取得兩張卡片的數據
card1_id = "AI-20251028-001"
card2_id = "AI-20251028-002"

# 手動計算信度（用於理解）
# 在實際代碼中，這已由 _calculate_confidence 自動完成

# 假設：
similarity = 0.72       # 從向量搜索
has_link = True         # 檢查到 [[AI-20251028-002]]
shared_concepts = ["機器學習", "神經網絡"]  # 2 個共同概念
same_domain = True      # 都是 "AI" 領域

# 計算各維度
semantic_score = similarity * 0.4  # 0.72 * 0.4 = 0.288
link_score = 0.3 if has_link else 0.0  # 0.3
co_occurrence = min(len(shared_concepts) / 5.0, 1.0) * 0.2  # 2/5 * 0.2 = 0.08
domain_score = 0.1 if same_domain else 0.05  # 0.1

total_confidence = semantic_score + link_score + co_occurrence + domain_score
# = 0.288 + 0.3 + 0.08 + 0.1 = 0.768

print(f"總信度: {total_confidence:.3f} ✓ 高信度")
print(f"  語義相似度: {semantic_score:.3f} (40%)")
print(f"  明確連結: {link_score:.3f} (30%)")
print(f"  共同概念: {co_occurrence:.3f} (20%)")
print(f"  領域一致: {domain_score:.3f} (10%)")
```

---

## 性能和優化

### 時間複雜度分析

| 操作 | 時間複雜度 | 備註 |
|------|----------|------|
| **向量相似度搜索** | O(n) | n = 卡片數，ChromaDB 優化 |
| **共同概念計算** | O(m × k) | m = 卡片對數，k = 平均標籤/詞彙數 |
| **信度評分計算** | O(m) | m = 卡片對數 |
| **社群檢測（Louvain）** | O(n × max_iter) | max_iter = 10，通常快速收斂 |
| **PageRank** | O(n × iter) | iter = 100（通常 <50 次收斂） |
| **路徑分析** | O(n + m) | BFS 搜索，單次查詢 |
| **完整分析** | ~O(n² + n log n) | n = 704 卡片，≈ 2-3 分鐘 |

### 記憶體使用

| 結構 | 大小 | 說明 |
|------|------|------|
| **向量索引（ChromaDB）** | ~100-200 MB | 704 張卡片 × 768/2560 維向量 |
| **圖結構** | ~5-10 MB | 節點和邊的鄰接表 |
| **JSON 報告** | ~5 MB | 完整分析數據 |
| **總計** | ~150-250 MB | 單次分析 |

### 優化建議

#### 1. 向量相似度搜索

```python
# ❌ 低效：逐個查詢
for card_id in all_cards:
    results = vector_db.find_similar_zettel(card_id)

# ✅ 高效：批量查詢（未來改進）
results = vector_db.batch_find_similar(card_ids, batch_size=50)
```

#### 2. 介數中心性計算

```python
# 當前實現已採樣（原始 O(n³)）
# 隨機採樣 50 對節點對，而不是所有 C(n,2) 對

sample_size = min(50, len(nodes))  # 限制採樣大小
```

#### 3. 社群檢測迭代次數

```python
# 可根據網絡規模調整
max_iterations = 10  # 704 節點足夠
# 大網絡可減少到 5，小網絡可增加到 20
```

### 生成次數比較

**首次完整分析（704 張卡片）**:
- 向量化：已預計算（不計入）
- 關係識別：~120 秒
- 高級分析：~30 秒
- 視覺化：~10 秒
- **總計：~160 秒（2-3 分鐘）**

**增量更新（新增 10 張卡片）**:
- 新卡片向量化：~10 秒
- 新卡片的關係識別：~15 秒
- 網絡重新計算：~20 秒
- **總計：~45 秒（未來可優化到 20 秒）**

---

## 附錄：資料庫結構參考

### zettel_cards 表結構

```sql
CREATE TABLE zettel_cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zettel_id TEXT UNIQUE NOT NULL,          -- 卡片 ID，如 "CogSci-20251028-001"
    paper_id INTEGER,                        -- 關聯論文 ID
    title TEXT NOT NULL,                     -- 卡片標題
    core_concept TEXT,                       -- 核心概念（用於相似度計算）
    tags TEXT,                               -- JSON 格式標籤列表（用於相似度計算）
    domain TEXT,                             -- 領域代碼（用於領域一致性計算）
    content TEXT,                            -- 完整卡片內容（用於連結檢測 fallback）
    ai_notes TEXT,                           -- AI 筆記（優先用於連結檢測）
    human_notes TEXT,                        -- 人類筆記
    file_path TEXT,                          -- 檔案路徑
    zettel_folder TEXT,                      -- 資料夾名稱
    card_type TEXT,                          -- 卡片類型
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 相似度相關的重要欄位

| 欄位 | 優先度 | 用途 |
|------|--------|------|
| **core_concept** | ⭐⭐⭐ | 共同概念提取（精凝內容） |
| **tags** | ⭐⭐⭐ | 共同概念提取（人工標註） |
| **title** | ⭐⭐ | 共同概念提取（備選） |
| **ai_notes** | ⭐⭐⭐ | 明確連結檢測（優先源） |
| **content** | ⭐⭐ | 明確連結檢測（fallback） |
| **domain** | ⭐ | 領域一致性檢查 |

---

## 常見問題 (FAQ)

### Q1: 為什麼向量相似度的最小閾值是 0.4？

**A**: 0.4 是經驗值，基於實測數據：
- 0.3-0.4：可能無關但巧合相似（假正例）
- 0.4-0.7：中等相關，值得檢查
- 0.7+：高度相關，可信度高

實測 704 張卡片中，0.4 以下的相似度幾乎都是無關的。

### Q2: 為什麼明確連結權重這麼高（30%）？

**A**: 人為標註的連結比自動計算更可靠：
- 人類 review 過，假正例少
- 反映編者的主觀判斷（重要參考）
- 在信度計算中起決定作用

但仍低於向量相似度（40%），避免過度依賴人工。

### Q3: 共同概念只計算 5 個的上限，如果有 10 個呢？

**A**:
```python
shared_score = min(len(shared) / 5.0, 1.0) * 0.2
```

`min(..., 1.0)` 確保超過 5 個時不會無限增長。
邏輯：共同概念太多反而可能是**複製內容**（反面信號）。

### Q4: 領域一致性為何只有 0.1 和 0.05 兩種值？

**A**: 這是設計選擇：
- 簡潔明快，避免梯度計算
- 領域本應是離散值，不是連續光譜
- 實測表明二值足夠區分

若需微調，可改為 0.05-0.15 之間的梯度值。

### Q5: 如何使用相似度進行推薦？

**A**: 按信度排序並呈現：
```python
# 為 Card A 推薦相關卡片
relations = finder.find_concept_relations()
a_relations = [r for r in relations
               if r.card_id_1 == target_id]
a_relations.sort(key=lambda r: r.confidence_score, reverse=True)

# 推薦 Top 5，並說明理由
for i, rel in enumerate(a_relations[:5], 1):
    reason = f"leads_to" if rel.relation_type == 'leads_to' else rel.relation_type
    print(f"{i}. {rel.card_id_2} ({reason}, 信度 {rel.confidence_score:.2%})")
```

---

## 結論

Zettelkasten 原子卡片的概念相似性計算是一個**多維度、多層次**的系統：

1. **底層**：向量嵌入提供語義理解（40%）
2. **中層**：人工標註和連結提供結構信息（30% + 20%）
3. **上層**：領域和上下文提供分類信息（10%）

這種**混合方法**結合了自動化的優勢（向量）和人工智慧的優勢（標註、連結），是構建高質量知識網絡的關鍵。

---

**文件更新記錄**

| 版本 | 日期 | 變更 |
|------|------|------|
| 1.0 | 2025-11-05 | 初始版本，完整說明向量相似度和多維度信度評分系統 |

