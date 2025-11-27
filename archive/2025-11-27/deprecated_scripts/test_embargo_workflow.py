#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
測試 Embargo 工作流程的完整性
"""

import sys
import io
import sqlite3
from pathlib import Path

# 強制 UTF-8 輸出（Windows 相容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

def test_database_schema():
    """測試 1: 數據庫 schema 是否正確"""
    print("\n[測試 1] 檢查數據庫 schema...")

    db_path = Path('knowledge_base/index.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 檢查 public 欄位
    cursor.execute("PRAGMA table_info(papers)")
    columns = {col[1]: col[2] for col in cursor.fetchall()}

    if 'public' not in columns:
        print("  ❌ 失敗: papers 表缺少 'public' 欄位")
        conn.close()
        return False

    if columns['public'] != 'INTEGER':
        print(f"  ❌ 失敗: public 欄位類型錯誤 ({columns['public']} 應為 INTEGER)")
        conn.close()
        return False

    print("  ✅ 通過: papers 表包含 public 欄位 (INTEGER)")
    conn.close()
    return True


def test_public_marking():
    """測試 2: 公開論文標記是否正確"""
    print("\n[測試 2] 檢查論文公開狀態...")

    db_path = Path('knowledge_base/index.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, title, public
        FROM papers
        ORDER BY id
    ''')
    papers = cursor.fetchall()

    # 檢查前 6 篇是否為公開
    public_count = sum(1 for p in papers if p[2] == 1)
    expected_public = min(6, len(papers))

    if public_count != expected_public:
        print(f"  ❌ 失敗: 公開論文數量錯誤 ({public_count} 應為 {expected_public})")
        conn.close()
        return False

    print(f"  ✅ 通過: {public_count} 篇論文標記為公開")

    for paper_id, title, is_public in papers[:6]:
        status = "🌐" if is_public else "🔒"
        print(f"    {status} Paper {paper_id}: {title[:40]}")

    conn.close()
    return True


def test_public_database_export():
    """測試 3: 公開數據庫是否正確導出"""
    print("\n[測試 3] 檢查公開數據庫...")

    public_db = Path('knowledge_base/index_public.db')

    if not public_db.exists():
        print("  ❌ 失敗: 公開數據庫不存在")
        return False

    conn = sqlite3.connect(public_db)
    cursor = conn.cursor()

    # 檢查是否只包含公開論文
    cursor.execute('SELECT COUNT(*) FROM papers WHERE public = 0 OR public IS NULL')
    embargo_count = cursor.fetchone()[0]

    if embargo_count > 0:
        print(f"  ❌ 失敗: 公開數據庫包含 {embargo_count} 篇 embargo 論文")
        conn.close()
        return False

    # 獲取統計
    cursor.execute('SELECT COUNT(*) FROM papers')
    paper_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM zettel_cards')
    card_count = cursor.fetchone()[0]

    print(f"  ✅ 通過: 公開數據庫只包含公開論文")
    print(f"    - 論文數: {paper_count}")
    print(f"    - Zettelkasten 卡片數: {card_count}")
    print(f"    - 文件大小: {public_db.stat().st_size / 1024:.1f} KB")

    conn.close()
    return True


def test_gitignore_configuration():
    """測試 4: .gitignore 配置是否正確"""
    print("\n[測試 4] 檢查 .gitignore 配置...")

    gitignore_path = Path('.gitignore')

    if not gitignore_path.exists():
        print("  ❌ 失敗: .gitignore 不存在")
        return False

    content = gitignore_path.read_text(encoding='utf-8')

    # 檢查是否排除完整數據庫
    if 'knowledge_base/index.db' not in content:
        print("  ❌ 失敗: .gitignore 未排除 index.db")
        return False

    # 檢查是否包含公開數據庫
    if '!knowledge_base/index_public.db' not in content:
        print("  ❌ 失敗: .gitignore 未包含 index_public.db")
        return False

    print("  ✅ 通過: .gitignore 正確配置")
    print("    - 排除: knowledge_base/index.db")
    print("    - 包含: knowledge_base/index_public.db")

    return True


def test_data_consistency():
    """測試 5: 數據一致性檢查"""
    print("\n[測試 5] 檢查數據一致性...")

    full_db = Path('knowledge_base/index.db')
    public_db = Path('knowledge_base/index_public.db')

    conn_full = sqlite3.connect(full_db)
    conn_public = sqlite3.connect(public_db)

    cursor_full = conn_full.cursor()
    cursor_public = conn_public.cursor()

    # 檢查公開論文數量一致性
    cursor_full.execute('SELECT COUNT(*) FROM papers WHERE public = 1')
    full_public_count = cursor_full.fetchone()[0]

    cursor_public.execute('SELECT COUNT(*) FROM papers')
    public_count = cursor_public.fetchone()[0]

    if full_public_count != public_count:
        print(f"  ❌ 失敗: 公開論文數量不一致")
        print(f"    - 完整數據庫中的公開論文: {full_public_count}")
        print(f"    - 公開數據庫中的論文: {public_count}")
        conn_full.close()
        conn_public.close()
        return False

    # 檢查卡片數量一致性
    cursor_full.execute('''
        SELECT COUNT(*)
        FROM zettel_cards zc
        JOIN papers p ON zc.paper_id = p.id
        WHERE p.public = 1
    ''')
    full_public_cards = cursor_full.fetchone()[0]

    cursor_public.execute('SELECT COUNT(*) FROM zettel_cards')
    public_cards = cursor_public.fetchone()[0]

    if full_public_cards != public_cards:
        print(f"  ❌ 失敗: Zettelkasten 卡片數量不一致")
        print(f"    - 完整數據庫中的公開卡片: {full_public_cards}")
        print(f"    - 公開數據庫中的卡片: {public_cards}")
        conn_full.close()
        conn_public.close()
        return False

    print(f"  ✅ 通過: 數據一致性正確")
    print(f"    - 公開論文數: {public_count}")
    print(f"    - 公開卡片數: {public_cards}")

    conn_full.close()
    conn_public.close()
    return True


def main():
    """執行所有測試"""
    print("=" * 80)
    print("Embargo 工作流程完整性測試")
    print("=" * 80)

    tests = [
        ("數據庫 Schema", test_database_schema),
        ("公開論文標記", test_public_marking),
        ("公開數據庫導出", test_public_database_export),
        (".gitignore 配置", test_gitignore_configuration),
        ("數據一致性", test_data_consistency),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"  ❌ 異常: {e}")
            results.append((name, False))

    # 顯示測試摘要
    print("\n" + "=" * 80)
    print("測試摘要")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"  {status}: {name}")

    print("\n" + "=" * 80)
    print(f"結果: {passed}/{total} 測試通過")

    if passed == total:
        print("🎉 所有測試通過！Embargo 工作流程正常運作。")
        return 0
    else:
        print("⚠️  部分測試失敗，請檢查上述錯誤訊息。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
