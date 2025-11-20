-- 批次更新關鍵詞 SQL 腳本
-- 用法: sqlite3 knowledge_base/index.db < output/batch_update_keywords.sql

-- ===== 從摘要提取的明確關鍵詞 =====

-- 論文 3: LanguageSciences (摘要已提供)
UPDATE papers SET keywords = '["Chinese", "Classifier", "Coercion", "kinds", "individuals", "events"]' WHERE id = 3;

-- 論文 8: LinguisticsVanguard (摘要已提供)
UPDATE papers SET keywords = '["classifiers", "database", "nominal classification", "numeral classifiers", "sortal classifiers", "WACL"]' WHERE id = 8;

-- ===== 從標題和內容推斷的關鍵詞 =====

-- 論文 1: Taxonomy of Numeral Classifiers
UPDATE papers SET keywords = '["numeral classifiers", "taxonomy", "linguistic typology", "formal semantics"]' WHERE id = 1;

-- 論文 4: Concepts in the Brain
UPDATE papers SET keywords = '["concepts", "brain", "neuroscience", "cognitive science", "semantic typology", "cross-linguistic"]' WHERE id = 4;

-- 論文 5: 華語分類詞（需確認年份後再執行）
-- UPDATE papers SET keywords = '["量詞", "分類詞", "對外華語教學", "教學分級"]' WHERE id = 5;

-- 論文 7: International Journal (需確認標題後再執行)
-- UPDATE papers SET keywords = '["Chinese", "Natural Language Processing", "Computational Linguistics"]' WHERE id = 7;

-- 論文 9: Classifiers
UPDATE papers SET keywords = '["classifiers", "Mandarin Chinese", "semantic", "measure words"]' WHERE id = 9;

-- 論文 10: HuangLinguaSinica
UPDATE papers SET keywords = '["measure words", "classifiers", "Chinese grammar", "ontology", "endurant", "perdurant"]' WHERE id = 10;

-- 論文 14: Journal of Cognitive Psychology
UPDATE papers SET keywords = '["cognitive psychology", "language comprehension", "mental representation"]' WHERE id = 14;

-- 論文 15: PsychonomicBulletin
UPDATE papers SET keywords = '["embodied cognition", "language comprehension", "action", "grounding"]' WHERE id = 15;

-- 論文 17: Multimodal Language Models (需確認年份後再執行)
-- UPDATE papers SET keywords = '["multimodal language models", "embodiment", "grounding", "shape simulation", "psycholinguistics"]' WHERE id = 17;

-- 論文 18: Memory&Cognition
UPDATE papers SET keywords = '["object state", "mental representation", "language comprehension", "tense", "picture verification"]' WHERE id = 18;

-- 論文 19: Cognitive Processing
UPDATE papers SET keywords = '["cognitive processing", "mental simulation", "color", "language comprehension"]' WHERE id = 19;

-- 論文 22: JOURNAL OF VERBAL LEARNING
UPDATE papers SET keywords = '["verbal learning", "verbal behavior", "noun phrases", "understanding"]' WHERE id = 22;

-- 論文 23: Psychological Science
UPDATE papers SET keywords = '["psychological science", "mental representation", "orientation", "shape"]' WHERE id = 23;

-- 論文 25: Memory & Cognition
UPDATE papers SET keywords = '["memory", "cognition", "mental simulation", "color match", "bilingualism", "non-native speaker"]' WHERE id = 25;

-- 論文 26: Educational Psychology
UPDATE papers SET keywords = '["educational psychology", "experimental", "learning"]' WHERE id = 26;

-- 論文 28: Revisiting Mental Simulation
UPDATE papers SET keywords = '["mental simulation", "language comprehension", "replication", "orientation", "shape", "color"]' WHERE id = 28;

-- 論文 29: PsychonBullRev
UPDATE papers SET keywords = '["participant nonnaivete", "open science", "replication"]' WHERE id = 29;

-- 論文 30: HCOMP2022 (需確認年份後再執行)
-- UPDATE papers SET keywords = '["crowdsourcing", "human computation", "AAAI", "exploratory study"]' WHERE id = 30;

-- ===== 檢查更新結果 =====
SELECT
    id,
    title,
    year,
    CASE
        WHEN keywords IS NULL OR keywords = '[]' THEN '❌ 缺失'
        ELSE '✅ 有'
    END as keywords_status
FROM papers
WHERE id IN (1, 3, 4, 8, 9, 10, 14, 15, 18, 19, 22, 23, 25, 26, 28, 29)
ORDER BY id;
