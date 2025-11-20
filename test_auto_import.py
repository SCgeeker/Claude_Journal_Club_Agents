#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自動化測試 batch_processor.py 的 Zettelkasten 自動導入功能
"""

import sys
import sqlite3
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def check_zettel_count():
    """檢查數據庫中的卡片總數"""
    conn = sqlite3.connect('knowledge_base/index.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM zettel_cards')
    count = cursor.fetchone()[0]
    conn.close()
    return count

def clear_zettel_cards():
    """清空卡片表（保留論文）"""
    conn = sqlite3.connect('knowledge_base/index.db')
    conn.execute('DELETE FROM zettel_cards')
    conn.execute('DELETE FROM zettel_paper_links')
    conn.commit()
    conn.close()

def run_batch_process():
    """執行批次處理（簡化版，只生成 5 張卡片以加快測試）"""
    cmd = [
        sys.executable,
        'batch_process.py',
        '--files', 'D:/core/research/Program_verse/+/pdf/Crockett-2025.pdf',
        '--domain', 'AI_literacy',
        '--add-to-kb',
        '--generate-zettel',
        '--detail', 'brief',
        '--cards', '5',
        '--llm-provider', 'google',
        '--model', 'gemini-2.0-flash-exp'
    ]

    print(f"執行命令: {' '.join(cmd)}\n")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )

    return result

def main():
    print("\n" + "=" * 70)
    print("自動化測試: Zettelkasten 卡片自動導入功能")
    print("=" * 70)

    # Step 1: 初始狀態
    print("\n[Step 1/5] 檢查初始狀態...")
    initial_count = check_zettel_count()
    print(f"  當前卡片數: {initial_count}")

    # Step 2: 清空
    print("\n[Step 2/5] 清空卡片表...")
    clear_zettel_cards()
    after_clear = check_zettel_count()
    print(f"  清空後卡片數: {after_clear}")
    assert after_clear == 0, "清空失敗！"

    # Step 3: 執行批次處理
    print("\n[Step 3/5] 執行批次處理（5 張卡片）...")
    print("  這可能需要 30-60 秒...\n")

    result = run_batch_process()

    if result.returncode != 0:
        print("\n❌ 批次處理失敗！")
        print("\nSTDOUT:")
        print(result.stdout)
        print("\nSTDERR:")
        print(result.stderr)
        return 1

    # 顯示部分輸出（尋找關鍵信息）
    if "[DB]" in result.stdout:
        for line in result.stdout.split('\n'):
            if "[DB]" in line or "已導入" in line:
                print(f"  {line.strip()}")

    # Step 4: 驗證導入
    print("\n[Step 4/5] 驗證導入結果...")
    final_count = check_zettel_count()
    print(f"  導入後卡片數: {final_count}")

    # Step 5: 評估
    print("\n[Step 5/5] 測試結果評估")
    print("=" * 70)

    expected = 5
    success = final_count == expected

    print(f"\n預期卡片數: {expected}")
    print(f"實際卡片數: {final_count}")

    if success:
        print("\n✅ 測試通過！")
        print("   卡片已成功自動導入到數據庫")
        print("\n修復內容:")
        print("   ✅ ProcessResult 添加 zettel_imported_to_db 和 zettel_failed_import")
        print("   ✅ 添加 _import_zettel_to_kb() 方法")
        print("   ✅ process_single() 自動調用導入方法")
        print("   ✅ 自動關聯卡片到論文")

    elif final_count > 0:
        print(f"\n⚠️ 部分成功！")
        print(f"   已導入 {final_count} 張卡片，但預期為 {expected} 張")
        print("   可能原因:")
        print("   - 部分卡片解析失敗")
        print("   - LLM 未生成足夠數量的卡片")

    else:
        print("\n❌ 測試失敗！")
        print("   卡片未導入到數據庫")
        print("\n可能原因:")
        print("   1. _import_zettel_to_kb() 未被調用")
        print("   2. zettel_dir 路徑解析失敗")
        print("   3. 卡片目錄不存在")
        print("   4. parse_zettel_card() 失敗")

    print("\n" + "=" * 70 + "\n")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
