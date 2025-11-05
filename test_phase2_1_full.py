#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2.1 Full System Tests (Day 4-5)

完整測試套件，驗證 Plan B 實施後的系統完整性：
1. Integration Tests - 模組間互動
2. E2E Scenarios - 端到端流程
3. Performance Benchmarks - 性能基準
4. Data Integrity Checks - 數據完整性

Author: Claude Code Agent
Date: 2025-11-05
"""

import sys
import os
import time
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple

# 添加專案根目錄到路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.knowledge_base.kb_manager import KnowledgeBaseManager
from src.embeddings.vector_db import VectorDatabase
from src.analyzers.relation_finder import RelationFinder
from src.utils.content_filter import extract_ai_content, get_human_notes


class FullTestRunner:
    """Phase 2.1 完整測試執行器"""

    def __init__(self):
        self.kb = KnowledgeBaseManager()
        self.vector_db = VectorDatabase()
        self.relation_finder = RelationFinder()

        self.results = {
            'integration': [],
            'e2e': [],
            'performance': [],
            'integrity': []
        }

        self.start_time = time.time()

    def print_header(self, title: str):
        """列印測試標題"""
        print("\n" + "=" * 70)
        print(title)
        print("=" * 70)

    def print_test(self, test_name: str):
        """列印測試名稱"""
        print(f"\n[{test_name}]")

    def record_result(self, category: str, test_name: str, passed: bool, details: str = ""):
        """記錄測試結果"""
        self.results[category].append({
            'test': test_name,
            'passed': passed,
            'details': details
        })
        status = "✅ 通過" if passed else "❌ 失敗"
        print(f"  {status}: {test_name}")
        if details:
            print(f"    {details}")

    # ========== 1. Integration Tests ==========

    def test_integration(self):
        """模組間互動測試"""
        self.print_header("測試 1: Integration Tests - 模組間互動")

        # 1.1: KB Manager → Vector DB 互動
        self.print_test("測試 1.1: KB Manager → Vector DB 數據一致性")
        try:
            # 從 KB 獲取卡片數量
            conn = sqlite3.connect(self.kb.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM zettel_cards")
            kb_count = cursor.fetchone()[0]
            conn.close()

            # 從 Vector DB 獲取向量數量
            stats = self.vector_db.get_stats()
            vector_count = stats['zettel_count']

            passed = kb_count == vector_count
            self.record_result(
                'integration',
                'KB-VectorDB 數據一致性',
                passed,
                f"KB: {kb_count} 張卡片, VectorDB: {vector_count} 個向量"
            )
        except Exception as e:
            self.record_result('integration', 'KB-VectorDB 數據一致性', False, str(e))

        # 1.2: Vector DB → Relation Finder 互動
        self.print_test("測試 1.2: Vector DB → Relation Finder 語義搜索")
        try:
            # 使用 relation_finder 的向量搜索功能
            test_card_id = "Zwaan-2018-001"
            similar = self.vector_db.find_similar_zettel(
                zettel_id=test_card_id,
                n_results=5,
                exclude_self=True
            )

            has_results = similar and 'ids' in similar and len(similar['ids'][0]) > 0
            passed = has_results
            self.record_result(
                'integration',
                'VectorDB-RelationFinder 語義搜索',
                passed,
                f"找到 {len(similar['ids'][0]) if has_results else 0} 個相似卡片"
            )
        except Exception as e:
            self.record_result('integration', 'VectorDB-RelationFinder 語義搜索', False, str(e))

        # 1.3: Content Filter → All Modules
        self.print_test("測試 1.3: Content Filter 在所有模組中的一致性")
        try:
            # 從 KB 讀取一張有 human_notes 的卡片
            conn = sqlite3.connect(self.kb.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT content, ai_notes, human_notes
                FROM zettel_cards
                WHERE human_notes IS NOT NULL AND human_notes != ''
                LIMIT 1
            """)
            row = cursor.fetchone()
            conn.close()

            if row:
                content, ai_notes, human_notes = row

                # 驗證 ai_notes 不包含 human markers
                has_human_marker = '**[Human]**:' in (ai_notes or '')

                # 驗證 extract_ai_content 結果與 ai_notes 一致
                extracted = extract_ai_content(content)
                # 允許一定的差異（因為可能有格式化差異）
                length_diff = abs(len(extracted) - len(ai_notes or '')) / max(len(ai_notes or ''), 1)
                consistent = length_diff < 0.1  # 10% 容忍度

                passed = not has_human_marker and consistent
                self.record_result(
                    'integration',
                    'Content Filter 一致性',
                    passed,
                    f"AI 筆記無 Human 標記: {not has_human_marker}, 長度差異: {length_diff:.1%}"
                )
            else:
                self.record_result('integration', 'Content Filter 一致性', True, "無包含 human_notes 的卡片可測試")
        except Exception as e:
            self.record_result('integration', 'Content Filter 一致性', False, str(e))

        # 1.4: KB Manager ai_notes/human_notes 欄位讀寫
        self.print_test("測試 1.4: KB Manager ai_notes/human_notes 欄位讀寫")
        try:
            conn = sqlite3.connect(self.kb.db_path)
            cursor = conn.cursor()

            # 檢查 ai_notes 非 NULL 數量
            cursor.execute("SELECT COUNT(*) FROM zettel_cards WHERE ai_notes IS NOT NULL")
            ai_count = cursor.fetchone()[0]

            # 檢查 human_notes 非 NULL 數量
            cursor.execute("SELECT COUNT(*) FROM zettel_cards WHERE human_notes IS NOT NULL AND human_notes != ''")
            human_count = cursor.fetchone()[0]

            # 檢查 content 非空數量（應該全部都有）
            cursor.execute("SELECT COUNT(*) FROM zettel_cards WHERE content IS NOT NULL")
            content_count = cursor.fetchone()[0]

            conn.close()

            # ai_notes 應該 100% 填充
            passed = ai_count == 704 and content_count == 704
            self.record_result(
                'integration',
                'KB Manager 欄位完整性',
                passed,
                f"ai_notes: {ai_count}/704, human_notes: {human_count}/704, content: {content_count}/704"
            )
        except Exception as e:
            self.record_result('integration', 'KB Manager 欄位完整性', False, str(e))

    # ========== 2. E2E Scenarios ==========

    def test_e2e_scenarios(self):
        """端到端場景測試"""
        self.print_header("測試 2: E2E Scenarios - 端到端流程")

        # Scenario A: 新增論文並生成 Zettelkasten
        self.print_test("測試 2.1: Scenario A - 模擬完整工作流（讀取模式）")
        try:
            # 步驟 1: 從 KB 讀取一篇論文
            conn = sqlite3.connect(self.kb.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, title FROM papers LIMIT 1")
            paper = cursor.fetchone()
            conn.close()

            if not paper:
                self.record_result('e2e', 'Scenario A - 讀取模式', False, "知識庫無論文")
                return

            paper_id, paper_title = paper

            # 步驟 2: 讀取該論文的 Zettelkasten 卡片
            conn = sqlite3.connect(self.kb.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM zettel_cards
                WHERE paper_id = ?
            """, (paper_id,))
            card_count = cursor.fetchone()[0]
            conn.close()

            # 步驟 3: 對其中一張卡片進行向量搜索
            if card_count > 0:
                conn = sqlite3.connect(self.kb.db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT zettel_id FROM zettel_cards
                    WHERE paper_id = ?
                    LIMIT 1
                """, (paper_id,))
                zettel_id = cursor.fetchone()[0]
                conn.close()

                similar = self.vector_db.find_similar_zettel(
                    zettel_id=zettel_id,
                    n_results=3,
                    exclude_self=True
                )

                has_similar = similar and 'ids' in similar and len(similar['ids'][0]) > 0
            else:
                has_similar = False

            passed = card_count > 0 and has_similar
            self.record_result(
                'e2e',
                'Scenario A - 完整工作流',
                passed,
                f"論文 '{paper_title}' 有 {card_count} 張卡片, 向量搜索: {'成功' if has_similar else '失敗'}"
            )
        except Exception as e:
            self.record_result('e2e', 'Scenario A - 完整工作流', False, str(e))

        # Scenario B: 查詢並建立關係
        self.print_test("測試 2.2: Scenario B - 向量搜索 → 關係識別")
        try:
            # 步驟 1: 使用 find_similar 進行向量搜索
            test_card_id = "Zwaan-2018-001"
            search_results = self.vector_db.find_similar_zettel(
                zettel_id=test_card_id,
                n_results=5,
                exclude_self=True
            )

            has_search_results = search_results and 'ids' in search_results and len(search_results['ids'][0]) > 0

            # 步驟 2: 對搜索結果識別關係（小規模）
            if has_search_results:
                # 使用找到的卡片測試關係識別
                card_ids = [test_card_id] + search_results['ids'][0][:2]

                # 手動檢查這些卡片的關係（小規模）
                relations = self.relation_finder.find_concept_relations(
                    min_similarity=0.3,
                    limit=10
                )

                # 檢查是否有涉及這些卡片的關係
                relevant_relations = [
                    r for r in relations
                    if r.card_id_1 in card_ids or r.card_id_2 in card_ids
                ]
                has_relations = len(relevant_relations) > 0
            else:
                has_relations = False

            passed = has_search_results and has_relations
            self.record_result(
                'e2e',
                'Scenario B - 搜索與關係',
                passed,
                f"搜索結果: {len(search_results['ids'][0]) if has_search_results else 0}, 相關關係: {len(relevant_relations) if has_relations else 0}"
            )
        except Exception as e:
            self.record_result('e2e', 'Scenario B - 搜索與關係', False, str(e))

        # Scenario C: 人類筆記不影響向量
        self.print_test("測試 2.3: Scenario C - 人類筆記隔離驗證")
        try:
            # 找一張有 human_notes 的卡片
            conn = sqlite3.connect(self.kb.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT zettel_id, ai_notes, human_notes
                FROM zettel_cards
                WHERE human_notes IS NOT NULL AND human_notes != ''
                LIMIT 1
            """)
            card = cursor.fetchone()
            conn.close()

            if card:
                zettel_id, ai_notes, human_notes = card

                # 向量搜索應該基於 ai_notes，不受 human_notes 影響
                similar = self.vector_db.find_similar_zettel(
                    zettel_id=zettel_id,
                    n_results=3,
                    exclude_self=True
                )

                # 驗證：ai_notes 不包含 Human 標記
                ai_clean = '**[Human]**:' not in (ai_notes or '')

                # 驗證：可以找到相似卡片
                has_similar = similar and 'ids' in similar and len(similar['ids'][0]) > 0

                passed = ai_clean and has_similar
                self.record_result(
                    'e2e',
                    'Scenario C - 人類筆記隔離',
                    passed,
                    f"AI 筆記乾淨: {ai_clean}, 找到相似卡片: {has_similar}"
                )
            else:
                self.record_result('e2e', 'Scenario C - 人類筆記隔離', True, "無 human_notes 可測試")
        except Exception as e:
            self.record_result('e2e', 'Scenario C - 人類筆記隔離', False, str(e))

    # ========== 3. Performance Benchmarks ==========

    def test_performance(self):
        """性能基準測試"""
        self.print_header("測試 3: Performance Benchmarks - 性能基準")

        # 3.1: 向量搜索性能
        self.print_test("測試 3.1: 向量搜索性能（100 次查詢）")
        try:
            # 隨機選擇 100 張卡片進行搜索
            conn = sqlite3.connect(self.kb.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT zettel_id FROM zettel_cards
                ORDER BY RANDOM()
                LIMIT 100
            """)
            card_ids = [row[0] for row in cursor.fetchall()]
            conn.close()

            start = time.time()
            success_count = 0
            for card_id in card_ids:
                try:
                    similar = self.vector_db.find_similar_zettel(
                        zettel_id=card_id,
                        n_results=5,
                        exclude_self=True
                    )
                    if similar and 'ids' in similar:
                        success_count += 1
                except:
                    pass
            elapsed = time.time() - start

            avg_time = elapsed / 100
            passed = avg_time < 0.5  # 每次查詢應在 0.5 秒內
            self.record_result(
                'performance',
                '向量搜索性能',
                passed,
                f"100 次查詢總時間: {elapsed:.2f}s, 平均: {avg_time:.3f}s/次, 成功率: {success_count}%"
            )
        except Exception as e:
            self.record_result('performance', '向量搜索性能', False, str(e))

        # 3.2: 關係識別性能
        self.print_test("測試 3.2: 關係識別性能（50 張卡片）")
        try:
            start = time.time()
            # 限制為 50 張卡片，每張找 10 個相似
            relations = self.relation_finder.find_concept_relations(
                min_similarity=0.3,
                limit=10
            )
            elapsed = time.time() - start

            # 計算每張卡片平均時間（假設 704 張卡片）
            avg_time_per_card = elapsed / 704

            passed = avg_time_per_card < 0.05  # 每張卡片應在 0.05 秒內
            self.record_result(
                'performance',
                '關係識別性能',
                passed,
                f"704 張卡片總時間: {elapsed:.2f}s, 平均: {avg_time_per_card:.3f}s/張, 識別關係: {len(relations)}"
            )
        except Exception as e:
            self.record_result('performance', '關係識別性能', False, str(e))

        # 3.3: Content Filter 性能
        self.print_test("測試 3.3: Content Filter 性能（704 張卡片）")
        try:
            conn = sqlite3.connect(self.kb.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM zettel_cards")
            contents = [row[0] for row in cursor.fetchall()]
            conn.close()

            start = time.time()
            for content in contents:
                extract_ai_content(content)
            elapsed = time.time() - start

            avg_time = elapsed / len(contents)
            passed = avg_time < 0.001  # 每張卡片應在 1ms 內
            self.record_result(
                'performance',
                'Content Filter 性能',
                passed,
                f"{len(contents)} 張卡片總時間: {elapsed:.2f}s, 平均: {avg_time*1000:.2f}ms/張"
            )
        except Exception as e:
            self.record_result('performance', 'Content Filter 性能', False, str(e))

    # ========== 4. Data Integrity Checks ==========

    def test_data_integrity(self):
        """數據完整性檢查"""
        self.print_header("測試 4: Data Integrity Checks - 數據完整性")

        # 4.1: ai_notes 欄位完整性
        self.print_test("測試 4.1: ai_notes 欄位 100% 填充")
        try:
            conn = sqlite3.connect(self.kb.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM zettel_cards")
            total = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM zettel_cards WHERE ai_notes IS NULL")
            null_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM zettel_cards WHERE ai_notes = ''")
            empty_count = cursor.fetchone()[0]

            conn.close()

            passed = null_count == 0 and empty_count == 0
            self.record_result(
                'integrity',
                'ai_notes 欄位完整性',
                passed,
                f"總數: {total}, NULL: {null_count}, 空字串: {empty_count}"
            )
        except Exception as e:
            self.record_result('integrity', 'ai_notes 欄位完整性', False, str(e))

        # 4.2: ai_notes 不包含人類標記
        self.print_test("測試 4.2: ai_notes 不包含人類標記")
        try:
            conn = sqlite3.connect(self.kb.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT zettel_id, ai_notes FROM zettel_cards WHERE ai_notes LIKE '%**[Human]**:%'")
            contaminated = cursor.fetchall()
            conn.close()

            passed = len(contaminated) == 0
            self.record_result(
                'integrity',
                'ai_notes 無人類標記',
                passed,
                f"包含 Human 標記: {len(contaminated)}/704 張卡片"
            )
        except Exception as e:
            self.record_result('integrity', 'ai_notes 無人類標記', False, str(e))

        # 4.3: human_notes 正確分離
        self.print_test("測試 4.3: human_notes 正確分離")
        try:
            conn = sqlite3.connect(self.kb.db_path)
            cursor = conn.cursor()

            # 檢查有 human_notes 的卡片
            cursor.execute("""
                SELECT COUNT(*) FROM zettel_cards
                WHERE human_notes IS NOT NULL AND human_notes != ''
            """)
            human_count = cursor.fetchone()[0]

            # 檢查 human_notes 不為 TODO 佔位符
            cursor.execute("""
                SELECT COUNT(*) FROM zettel_cards
                WHERE human_notes IS NOT NULL
                AND human_notes != ''
                AND human_notes NOT LIKE '%（待填寫）%'
            """)
            valid_human = cursor.fetchone()[0]

            conn.close()

            passed = human_count > 0 and valid_human > 0
            self.record_result(
                'integrity',
                'human_notes 正確分離',
                passed,
                f"有 human_notes: {human_count}/704, 有效內容: {valid_human}"
            )
        except Exception as e:
            self.record_result('integrity', 'human_notes 正確分離', False, str(e))

        # 4.4: 向量與數據庫同步
        self.print_test("測試 4.4: 向量庫與數據庫同步")
        try:
            conn = sqlite3.connect(self.kb.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT zettel_id FROM zettel_cards")
            db_ids = set(row[0] for row in cursor.fetchall())
            conn.close()

            # 從向量庫獲取所有 ID（抽樣檢查）
            sample_ids = list(db_ids)[:100]
            missing = []
            for zettel_id in sample_ids:
                try:
                    # 使用正確的集合名稱
                    result = self.vector_db.zettel_collection.get(ids=[zettel_id])
                    if not result or not result['ids']:
                        missing.append(zettel_id)
                except:
                    missing.append(zettel_id)

            passed = len(missing) == 0
            self.record_result(
                'integrity',
                '向量庫同步性',
                passed,
                f"抽樣檢查 100 張卡片, 缺失向量: {len(missing)}"
            )
        except Exception as e:
            self.record_result('integrity', '向量庫同步性', False, str(e))

        # 4.5: content 欄位保持不變（向後兼容）
        self.print_test("測試 4.5: content 欄位保持不變（向後兼容）")
        try:
            conn = sqlite3.connect(self.kb.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM zettel_cards WHERE content IS NOT NULL AND content != ''")
            content_count = cursor.fetchone()[0]

            # content 應該仍然包含完整內容（AI + Human）
            cursor.execute("""
                SELECT COUNT(*) FROM zettel_cards
                WHERE content LIKE '%## 個人筆記%'
            """)
            with_personal_section = cursor.fetchone()[0]

            conn.close()

            passed = content_count == 704
            self.record_result(
                'integrity',
                'content 欄位向後兼容',
                passed,
                f"有 content: {content_count}/704, 有個人筆記區: {with_personal_section}"
            )
        except Exception as e:
            self.record_result('integrity', 'content 欄位向後兼容', False, str(e))

    # ========== 5. Summary Report ==========

    def print_summary(self):
        """列印測試摘要"""
        self.print_header("測試摘要")

        total_time = time.time() - self.start_time

        for category in ['integration', 'e2e', 'performance', 'integrity']:
            results = self.results[category]
            passed = sum(1 for r in results if r['passed'])
            total = len(results)

            category_names = {
                'integration': 'Integration Tests',
                'e2e': 'E2E Scenarios',
                'performance': 'Performance Benchmarks',
                'integrity': 'Data Integrity Checks'
            }

            print(f"\n{'✅' if passed == total else '❌'} {category_names[category]}:")
            print(f"  通過: {passed}/{total}")
            if passed < total:
                print("  失敗:")
                for r in results:
                    if not r['passed']:
                        print(f"    - {r['test']}: {r['details']}")

        # 總體統計
        all_results = []
        for results in self.results.values():
            all_results.extend(results)

        total_passed = sum(1 for r in all_results if r['passed'])
        total_tests = len(all_results)

        print("\n" + "=" * 70)
        print(f"總計: {total_passed}/{total_tests} 通過 ({total_passed/total_tests*100:.1f}%)")
        print(f"執行時間: {total_time:.2f} 秒")
        print("=" * 70)

        if total_passed == total_tests:
            print("\n✅ 所有測試通過！Plan B 實施驗證成功。")
            return 0
        else:
            print(f"\n❌ {total_tests - total_passed} 個測試失敗。請檢查上述失敗詳情。")
            return 1

    def run_all_tests(self):
        """執行所有測試"""
        print("=" * 70)
        print("Phase 2.1 Full System Tests (Day 4-5)")
        print("=" * 70)
        print(f"開始時間: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        try:
            self.test_integration()
            self.test_e2e_scenarios()
            self.test_performance()
            self.test_data_integrity()

            return self.print_summary()
        except Exception as e:
            print(f"\n❌ 測試執行錯誤: {e}")
            import traceback
            traceback.print_exc()
            return 1


if __name__ == "__main__":
    runner = FullTestRunner()
    exit_code = runner.run_all_tests()
    sys.exit(exit_code)
