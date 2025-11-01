-- 批次更新年份 SQL 腳本
-- 用法: sqlite3 knowledge_base/index.db < output/batch_update_years.sql

-- ⚠️ 注意：以下年份需要查詢確認後再執行（已註解）
-- 請根據 METADATA_REPAIR_PLAN.md 的建議查詢後修改

-- ===== 確定的年份更新 =====

-- 論文 30: HCOMP2022 (從標題確認)
UPDATE papers SET year = 2022 WHERE id = 30;

-- 論文 11: DOI論文 (從 URL 推斷 s41599-021-01003-5)
UPDATE papers SET year = 2021 WHERE id = 11;

-- ===== 需要查詢確認的年份（請先查詢再取消註解） =====

-- 論文 5: 華語分類詞的界定與教學上的分級
-- 查詢方法: Google Scholar 搜尋「華語分類詞的界定與教學上的分級 陳羿如 何萬順」
-- UPDATE papers SET year = 2020 WHERE id = 5;  -- ⚠️ 確認後修改年份

-- 論文 7: International Journal of Computer Processing
-- 查詢方法: 查看 Markdown 文件或搜尋作者名
-- UPDATE papers SET year = 2015 WHERE id = 7;  -- ⚠️ 確認後修改年份

-- 論文 12: Events as Intersecting Object Histories
-- 查詢方法: Google Scholar 搜尋 "Events as Intersecting Object Histories Zachary Ekves"
-- UPDATE papers SET year = 2012 WHERE id = 12;  -- ⚠️ 確認後修改年份

-- 論文 17: Multimodal Language Models Show Evidence
-- 查詢方法: Google Scholar 搜尋 "Multimodal Language Models Show Evidence of Embodied R. Jones Sean Trott"
-- UPDATE papers SET year = 2024 WHERE id = 17;  -- ⚠️ 確認後修改年份

-- 論文 24: Research Article
-- 查詢方法: 從摘要中找線索或搜尋關鍵句
-- UPDATE papers SET year = 2018 WHERE id = 24;  -- ⚠️ 確認後修改年份

-- 論文 36: What Does 'Human-Centred AI' Mean?
-- 查詢方法: Google Scholar 搜尋 "What Does Human-Centred AI Mean? Olivia Guest"
-- UPDATE papers SET year = 2024 WHERE id = 36;  -- ⚠️ 確認後修改年份

-- ===== 檢查更新結果 =====
SELECT
    id,
    title,
    year,
    CASE
        WHEN year IS NULL THEN '❌ 缺失'
        ELSE '✅ ' || year
    END as year_status
FROM papers
WHERE id IN (5, 7, 11, 12, 17, 24, 30, 36)
ORDER BY id;

-- ===== 統計 =====
SELECT
    '總論文數' as metric,
    COUNT(*) as value
FROM papers
UNION ALL
SELECT
    '已有年份',
    COUNT(*)
FROM papers
WHERE year IS NOT NULL
UNION ALL
SELECT
    '缺失年份',
    COUNT(*)
FROM papers
WHERE year IS NULL
UNION ALL
SELECT
    '年份完整率 (%)',
    ROUND(COUNT(CASE WHEN year IS NOT NULL THEN 1 END) * 100.0 / COUNT(*), 1)
FROM papers;
