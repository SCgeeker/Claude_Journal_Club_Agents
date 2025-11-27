#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
測試 batch_processor.py 的 Zettelkasten 自動導入功能
"""

import sys
import sqlite3
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def check_zettel_cards():
    """檢查數據庫中的卡片數量"""
    conn = sqlite3.connect('knowledge_base/index.db')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM zettel_cards')
    total = cursor.fetchone()[0]

    cursor.execute('''
        SELECT p.id, p.cite_key, COUNT(zp.zettel_card_id) as card_count
        FROM papers p
        LEFT JOIN zettel_paper_links zp ON p.id = zp.paper_id
        GROUP BY p.id
        ORDER BY p.id
    ''')
    papers = cursor.fetchall()

    conn.close()

    print("\n" + "=" * 60)
    print("知識庫卡片統計")
    print("=" * 60)
    print(f"\n總卡片數: {total}\n")

    if papers:
        print("各論文卡片數:")
        for paper_id, cite_key, card_count in papers:
            print(f"  Paper {paper_id} ({cite_key or 'N/A'}): {card_count} 張")
    else:
        print("  (無論文記錄)")

    print("\n" + "=" * 60 + "\n")

    return total

def main():
    print("\n📋 測試流程:")
    print("1. 檢查當前卡片數量")
    print("2. 清空 zettel_cards 表（保留論文）")
    print("3. 使用 batch_process.py 處理 1 篇論文")
    print("4. 驗證卡片是否自動導入")
    print("\n" + "=" * 60)

    # Step 1: 當前狀態
    print("\n[Step 1] 當前卡片數量:")
    initial_count = check_zettel_cards()

    # Step 2: 清空卡片表
    print("\n[Step 2] 清空 zettel_cards 表...")
    conn = sqlite3.connect('knowledge_base/index.db')
    conn.execute('DELETE FROM zettel_cards')
    conn.execute('DELETE FROM zettel_paper_links')
    conn.commit()
    conn.close()
    print("  ✅ 已清空")

    after_clear = check_zettel_cards()

    # Step 3: 運行批次處理
    print("\n[Step 3] 執行批次處理（1 篇論文，10 張卡片）...")
    print("\n提示: 請在另一個終端執行以下命令:\n")
    print("python batch_process.py \\")
    print("  --files \"D:/core/research/Program_verse/+/pdf/Crockett-2025.pdf\" \\")
    print("  --domain \"AI_literacy\" \\")
    print("  --add-to-kb \\")
    print("  --generate-zettel \\")
    print("  --detail standard \\")
    print("  --cards 10 \\")
    print("  --llm-provider google \\")
    print("  --model gemini-2.0-flash-exp\n")

    input("執行完成後按 Enter 繼續...")

    # Step 4: 驗證
    print("\n[Step 4] 驗證導入結果:")
    final_count = check_zettel_cards()

    # 評估
    print("\n" + "=" * 60)
    print("測試結果")
    print("=" * 60)
    print(f"\n初始卡片數: {initial_count}")
    print(f"清空後卡片數: {after_clear}")
    print(f"導入後卡片數: {final_count}\n")

    if final_count > 0:
        print("✅ 測試成功！卡片已自動導入到數據庫")
        print(f"   預期: 10 張，實際: {final_count} 張")

        if final_count == 10:
            print("   ⭐ 完美！數量完全符合")
        elif final_count < 10:
            print("   ⚠️ 部分卡片導入失敗")
        else:
            print("   ⚠️ 卡片數量超過預期")
    else:
        print("❌ 測試失敗！卡片未導入到數據庫")
        print("   請檢查:")
        print("   1. batch_process.py 是否成功執行")
        print("   2. 是否有錯誤輸出")
        print("   3. zettel_dir 路徑是否正確")

    print("\n" + "=" * 60 + "\n")

if __name__ == "__main__":
    main()
