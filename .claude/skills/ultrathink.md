# ultrathink - 深度思考與優雅設計 Skill

**版本**: 1.0
**類型**: Design & Architecture
**優先級**: High（複雜任務）

---

## 📖 Skill 描述

Use when tackling complex architectural challenges, feature development requiring innovative thinking, or when the user explicitly requests "ultrathink" mode. This skill embodies Steve Jobs' philosophy of "making a dent in the universe" through elegant design and relentless refinement.

**觸發條件**:
- User explicitly invokes `/ultrathink` command
- Task complexity > 5 steps or > 100 lines of code
- Requires architectural design or innovation
- User asks for "best possible solution" or "elegant design"

**不使用時機**:
- Simple file operations (read, write, search)
- Quick bug fixes (< 10 lines)
- Documentation updates
- Format adjustments

---

## 🎯 核心工作流

### 1. Deep Understanding Phase

```python
# Before ANY coding:
1. Read CLAUDE.md thoroughly
2. Understand the codebase philosophy
3. Study existing patterns and conventions
4. Question ALL assumptions
5. Ask: "What would the most elegant solution look like?"
```

**Tools to use**:
- `Read`: Study CLAUDE.md, README.md, relevant code
- `Grep`: Search for existing patterns
- `Glob`: Find related files

**Output**:
```markdown
## 🧠 Deep Dive Analysis

### Current State
[What exists now]

### Assumptions Questioned
1. Assumption: X must work this way
   Challenge: What if we...?

### Elegant Solution Vision
[The ideal approach]
```

---

### 2. Da Vinci Planning Phase

```python
# Create a masterpiece plan:
1. Use TodoWrite for detailed task breakdown
2. Sketch the architecture mentally
3. Document design decisions
4. Identify key abstractions
5. Plan for edge cases upfront
```

**Tools to use**:
- `TodoWrite`: Create detailed task list
- `Write`: Document design decisions in `docs/`

**Output**:
```markdown
## 📐 Architectural Plan

### Design Philosophy
[Why this approach?]

### Key Abstractions
- Abstraction 1: [Purpose]
- Abstraction 2: [Purpose]

### Data Flow
[Diagram or description]

### Edge Cases Considered
1. Case 1: [How handled]
2. Case 2: [How handled]
```

**TodoWrite Template**:
```python
[
  {
    "content": "Phase 1: Setup and foundation",
    "status": "pending",
    "activeForm": "Setting up foundation"
  },
  {
    "content": "Phase 2: Core implementation (TDD)",
    "status": "pending",
    "activeForm": "Implementing core with TDD"
  },
  {
    "content": "Phase 3: Edge cases and refinement",
    "status": "pending",
    "activeForm": "Handling edge cases"
  },
  {
    "content": "Phase 4: Testing and verification",
    "status": "pending",
    "activeForm": "Testing and verifying"
  },
  {
    "content": "Phase 5: Documentation and review",
    "status": "pending",
    "activeForm": "Documenting and reviewing"
  }
]
```

---

### 3. Craftsman Implementation Phase

**Principle**: Code should read like poetry.

```python
# TDD First:
1. Write failing test
2. Implement minimal solution
3. Refactor to elegance
4. Repeat

# Naming Guidelines:
- Functions: Verbs that "sing" (calculate_similarity, not calc_sim)
- Classes: Nouns that feel inevitable (ConnectionNoteGenerator, not CNGen)
- Variables: Self-documenting (user_selected_domain, not dom)
```

**Tools to use**:
- `Write`: Create test files first
- `Edit`: Implement and refactor
- `Bash`: Run tests frequently

**Code Quality Checklist**:
```markdown
For EACH function/class:
- [ ] Name is self-explanatory
- [ ] Single Responsibility Principle
- [ ] Test coverage = 100%
- [ ] Edge cases handled gracefully
- [ ] No magic numbers or strings
- [ ] Docstring explains "why", not "what"
```

---

### 4. Relentless Iteration Phase

```python
# Never settle for "it works":
1. Run ALL tests
2. Check performance
3. Review for simplification opportunities
4. Get feedback (use superpowers:requesting-code-review)
5. Refine until "insanely great"
```

**Tools to use**:
- `Bash`: Run tests, performance benchmarks
- `Read`: Re-read code with fresh eyes
- `Skill`: Invoke `superpowers:requesting-code-review`

**Iteration Criteria**:
```markdown
Keep iterating until:
- [ ] No redundant code
- [ ] No unnecessary complexity
- [ ] All tests pass
- [ ] Performance acceptable
- [ ] Code review approved
- [ ] You feel PROUD of this code
```

---

## 🔧 Integration with Superpowers

### Recommended Skill Combinations

```python
# Workflow 1: Greenfield Feature
1. /ultrathink → Deep understanding
2. superpowers:brainstorming → Explore alternatives
3. superpowers:writing-plans → Detailed implementation plan
4. ultrathink → Craft implementation (TDD)
5. superpowers:requesting-code-review → Validate quality

# Workflow 2: Complex Refactoring
1. /ultrathink → Understand current code
2. superpowers:systematic-debugging → Identify issues
3. ultrathink → Design elegant replacement
4. superpowers:test-driven-development → Ensure correctness
5. superpowers:verification-before-completion → Confirm improvement

# Workflow 3: Architectural Decision
1. /ultrathink → Deep dive analysis
2. superpowers:brainstorming → Multiple approaches
3. ultrathink → Select and plan best approach
4. superpowers:executing-plans → Implement in batches
```

---

## 📋 使用場景矩陣

| 任務類型 | 使用 Ultrathink? | 結合 Skill | 理由 |
|---------|----------------|-----------|------|
| **新功能開發** | ✅ YES | brainstorming, writing-plans | 需要創新和規劃 |
| **架構重構** | ✅ YES | systematic-debugging, TDD | 需要深度理解和測試 |
| **演算法優化** | ✅ YES | - | 需要優雅解決方案 |
| **Bug 修復** | ⚠️ MAYBE | systematic-debugging | 視複雜度決定 |
| **文檔更新** | ❌ NO | - | 不需要深度思考 |
| **格式調整** | ❌ NO | - | 簡單任務 |
| **代碼審查** | ✅ YES | requesting-code-review | 需要細節執著 |
| **API 設計** | ✅ YES | brainstorming | 需要用戶體驗思考 |

---

## 🎯 實際案例

### Case 1: RelationFinder 改進（成功案例）

**任務**: 改進 Zettelkasten 關係識別演算法

**Ultrathink 流程**:

```markdown
[Phase 1: Deep Understanding]
- 閱讀 RELATION_FINDER_TECHNICAL_DETAILS.md
- 分析當前信度評分系統
- 質疑：為什麼是 4 個維度？能否更多？
- 發現：明確連結覆蓋率僅 11.6%（關鍵洞察）

[Phase 2: Da Vinci Planning]
- 設計 5 個改進方案
- 創建 TodoWrite 三階段計畫
- 文檔化在 RELATION_FINDER_IMPROVEMENTS.md
- 預估效果提升 60%

[Phase 3: Craftsman Implementation]
- Phase 1 優先：擴展共同概念 + 領域矩陣
- TDD: 先寫測試 _extract_shared_concepts_enhanced()
- 優雅命名：domain_similarity_matrix
- 處理邊界：多領域解析、中文分詞

[Phase 4: Relentless Iteration]
- 測試 704 張卡片
- 驗證信度提升
- 代碼審查
- 文檔完善

結果: 🌟 信度從 0.35 → 0.56 (+60%)
```

---

### Case 2: 簡單 Bug 修復（不當使用）

**任務**: 修復 print 語句中的拼寫錯誤

```markdown
❌ 錯誤做法:
/ultrathink
[開始深度分析整個日誌系統...]

✅ 正確做法:
這是簡單的文字修正，我將快速完成：
[直接使用 Edit 工具修復]

完成時間: 30秒 vs 5分鐘（過度設計）
```

---

## ⚠️ 陷阱與規避

### 陷阱 1: 過度設計（Over-engineering）

**症狀**:
```python
# 用戶要求：添加一個配置選項
# Ultrathink 過度：設計完整的插件系統

❌ 設計了 5 個類、3 個介面、配置管理器
✅ 只需在 settings.yaml 添加一行
```

**規避方法**:
```python
if task_complexity < 3_steps:
    use_standard_mode()
    notify_user("Task is straightforward, using quick mode")
```

---

### 陷阱 2: 分析癱瘓（Analysis Paralysis）

**症狀**:
```python
# 花 2 小時分析完美方案
# 卻沒有寫任何代碼

❌ 15 頁設計文檔，0 行代碼
✅ 先寫 MVP，再迭代優化
```

**規避方法**:
```python
# Time-box each phase:
Understanding: Max 20% of total time
Planning: Max 30%
Implementation: Min 40%
Iteration: 10%
```

---

### 陷阱 3: 忽略實用性

**症狀**:
```python
# 追求完美的抽象
# 卻犧牲了可讀性和可維護性

❌ 5 層繼承，10 個設計模式
✅ 簡單直接，99% 情況適用
```

**規避方法**:
```python
"Simplicity is the ultimate sophistication"
If abstraction doesn't make code CLEARER, remove it
```

---

## 📊 成功指標

完成 Ultrathink 任務時，應達到：

| 指標 | 目標 | 驗證方法 |
|------|------|---------|
| **代碼優雅度** | 8/10+ | 代碼審查評分 |
| **測試覆蓋率** | 100% | pytest --cov |
| **性能** | 無退化 | Benchmark 比較 |
| **文檔完整性** | 所有決策記錄 | docs/ 目錄檢查 |
| **一致性** | 符合代碼庫風格 | Lint 檢查 |
| **簡潔性** | 無冗餘代碼 | 人工審查 |

---

## 🔄 退出機制

### 自動降級條件

```python
# Ultrathink skill 自動切換回標準模式如果：

1. Task clearly simple (file read, basic query)
2. User explicitly requests "quick solution"
3. Time constraint mentioned ("ASAP", "urgent")
4. Previous iteration already optimal
```

**通知模板**:
```markdown
💡 注意: 此任務相對簡單，我將使用標準高效模式完成。
如需深度分析和架構設計，請明確要求。

預計完成時間: 2分鐘（標準模式）vs 15分鐘（Ultrathink）
```

---

## 📚 參考哲學

### Steve Jobs Quotes

> "It's really hard to design products by focus groups. A lot of times, people don't know what they want until you show it to them."

→ 應用：不只解決stated problem，解決real problem

> "That's been one of my mantras — focus and simplicity. Simple can be harder than complex."

→ 應用：Simplify Ruthlessly

> "The people who are crazy enough to think they can change the world are the ones who do."

→ 應用：Reality Distortion Field - 挑戰不可能

---

### Leonardo da Vinci

> "Simplicity is the ultimate sophistication."

→ 應用：移除複雜性直到無可移除

---

## 🎓 學習資源

- **內部**: CLAUDE.md, RELATION_FINDER_IMPROVEMENTS.md（優秀範例）
- **外部**: "Clean Code" by Robert Martin
- **哲學**: "Zen and the Art of Motorcycle Maintenance"

---

**Remember**: Ultrathink is not about writing MORE code, it's about writing LESS but BETTER code.

**The Ultimate Goal**: Code so elegant, it feels inevitable. 🎨
