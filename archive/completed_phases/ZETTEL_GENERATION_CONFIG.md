# Zettelkasten 生成配置标准

**记录日期**: 2025-11-03
**状态**: Phase 2.3 执行 - 选项 A（所有 64 篇论文重新生成）

## 📋 Zettel 原子笔记生成的预设配置

### 核心参数

| 参数 | 设置值 | 说明 |
|------|--------|------|
| **分析详细程度** | `comprehensive` | 每张卡片 6-8 个重点，4-5 句话/点 |
| **生成风格** | `zettelkasten` | 专用原子笔记模式 |
| **覆盖范围** | 64 篇论文 | 全数据库论文 |
| **输出格式** | Markdown | 独立卡片 + 索引 |

### 详细程度定义（5 种）

```
minimal:        2-3 个重点/张，1 句话/点         (最精简)
brief:          3-4 个重点/张，1-2 句话/点       (简要)
standard:       4-5 个重点/张，2-3 句话/点       (标准，默认)
detailed:       5-6 个重点/张，3-4 句话/点       (详细)
comprehensive:  6-8 个重点/张，4-5 句话/点       (完整) ⭐ 已选
```

### 选定原因：comprehensive

- ✅ 知识库面向**学术研究**，需要**充分深度**
- ✅ 支持**多维度分析**（理论、方法、发现、批判）
- ✅ 适合**后续概念提取**（更丰富的内容素材）
- ✅ 便于**Markdown 内容分析**（更多隐含概念）
- ✅ 满足**论文-Zettel-概念**三层映射的数据需求

## 🛠️ 批处理命令模板

```bash
python make_slides.py "<title>" \
  --from-kb <id> \
  --style zettelkasten \
  --domain <domain> \
  --detail comprehensive
```

### 执行范围

**论文数量分布**:
- CogSci:    1 篇
- Linguistics: 2 篇
- Research:  61 篇
- **总计**: 64 篇

### 预期输出

- **Zettel 卡片**: 64 组（每组平均 10-15 张）
- **总卡片数**: ~800-1000 张
- **输出目录**: `output/zettelkasten_notes/zettel_[identifier]_[date]/`
- **每个 Zettel 集合包含**:
  - `zettel_index.md` - 索引和概念网络
  - `zettel_cards/` 目录 - 52 个 Zettel ID.md 文件

## 📊 数据质量要求

### Zettel 卡片质量标准

每张卡片应包含：
- ✅ 唯一 ID（语义化：Domain-Date-Number）
- ✅ 核心概念（直接引用原文）
- ✅ AI Agent 批判性思考
- ✅ Human TODO 占位符
- ✅ 标签和连结网络
- ✅ paper_id 正确映射

### 概念提取质量

- **核心概念密度**: 每篇论文 10-15 个原子概念
- **标签丰富度**: 每张卡片 3-5 个标签
- **连结完整性**: 平均每个概念 2-3 个关联
- **内容覆盖**: 原文引用 + 深度分析

## 🔗 相关配置文件

- `batch_zettel_generation_plan.json` - 论文清单和执行计划
- `batch_generate_zettel.py` - 批处理执行脚本
- `batch_zettel_generation.log` - 执行日志

## 📌 注意事项

1. **执行时间预估**: 8-12 小时（根据 LLM 速度）
2. **中途保存**: 日志实时记录，可随时检查进度
3. **失败恢复**: 支持跳过失败的论文，继续执行
4. **验证步骤**: 生成完成后验证 paper_id 映射和内容完整性

## ✅ 执行清单

- [ ] 确认配置（本文档）
- [ ] 执行 `batch_generate_zettel.py`
- [ ] 监控进度和错误
- [ ] 验证生成质量
- [ ] 创建 Markdown 内容分析器
- [ ] 重新计算概念网络
- [ ] 生成改进版 zettel_concept_network.md

---

**状态**: ⏳ 等待执行
**预计开始**: 2025-11-03
**预计完成**: 2025-11-04 或 2025-11-05

