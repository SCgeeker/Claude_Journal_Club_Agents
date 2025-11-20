#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重新生成失敗的 Zettel 卡片
"""

import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

# 需要重新生成的論文 ID
PAPER_IDS = [1, 3, 8, 10, 13, 14, 15, 16, 18, 19, 20, 22, 25, 26, 27, 28, 29, 37, 38, 39, 40, 41, 42, 43]

def generate_zettel_for_paper(paper_id):
    """為單篇論文生成 Zettel"""
    print(f"\n[{paper_id}] 正在生成 Zettel...")

    cmd = [
        'python', 'make_slides.py',
        f'Paper {paper_id} Zettelkasten',
        '--from-kb', str(paper_id),
        '--style', 'zettelkasten',
        '--domain', 'Research',
        '--detail', 'comprehensive',
        '--llm-provider', 'google',
        '--model', 'gemini-2.0-flash-exp'
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=300,
            errors='replace'
        )

        if result.returncode == 0:
            print(f"[{paper_id}] ✅ 成功")
            return True, None
        else:
            error_msg = result.stderr[:200] if result.stderr else "未知錯誤"
            print(f"[{paper_id}] ❌ 失敗: {error_msg}")
            return False, error_msg

    except subprocess.TimeoutExpired:
        print(f"[{paper_id}] ❌ 超時 (300秒)")
        return False, "超時"
    except Exception as e:
        print(f"[{paper_id}] ❌ 異常: {str(e)}")
        return False, str(e)

def main():
    start_time = datetime.now()

    print("=" * 80)
    print("重新生成失敗的 Zettel 卡片")
    print("=" * 80)
    print(f"開始時間: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"論文數量: {len(PAPER_IDS)} 篇")
    print(f"Paper IDs: {PAPER_IDS}")
    print()

    results = {
        'success': 0,
        'failed': 0,
        'errors': []
    }

    for i, paper_id in enumerate(PAPER_IDS, 1):
        print(f"\n進度: [{i}/{len(PAPER_IDS)}]")

        success, error = generate_zettel_for_paper(paper_id)

        if success:
            results['success'] += 1
        else:
            results['failed'] += 1
            results['errors'].append({
                'paper_id': paper_id,
                'error': error
            })

        # 每 10 篇顯示一次進度
        if i % 10 == 0:
            elapsed = (datetime.now() - start_time).total_seconds()
            avg_time = elapsed / i
            remaining = (len(PAPER_IDS) - i) * avg_time

            print()
            print(f"中間報告 ({i}/{len(PAPER_IDS)}):")
            print(f"  成功: {results['success']}")
            print(f"  失敗: {results['failed']}")
            print(f"  已用時間: {elapsed/60:.1f} 分鐘")
            print(f"  預估剩餘: {remaining/60:.1f} 分鐘")
            print()

    # 最終報告
    end_time = datetime.now()
    elapsed = (end_time - start_time).total_seconds()

    print()
    print("=" * 80)
    print("最終報告")
    print("=" * 80)
    print(f"開始時間: {start_time.strftime('%H:%M:%S')}")
    print(f"結束時間: {end_time.strftime('%H:%M:%S')}")
    print(f"總用時: {elapsed/60:.1f} 分鐘")
    print()
    print(f"成功: {results['success']}/{len(PAPER_IDS)} ({results['success']/len(PAPER_IDS)*100:.1f}%)")
    print(f"失敗: {results['failed']}/{len(PAPER_IDS)} ({results['failed']/len(PAPER_IDS)*100:.1f}%)")

    if results['errors']:
        print()
        print("失敗的論文:")
        for error in results['errors']:
            print(f"  Paper {error['paper_id']}: {error['error'][:50]}")

    # 保存結果
    import json
    result_file = Path(f"regenerate_zettel_result_{start_time.strftime('%Y%m%d_%H%M%S')}.json")
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump({
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'elapsed_seconds': elapsed,
            'total': len(PAPER_IDS),
            'success': results['success'],
            'failed': results['failed'],
            'errors': results['errors']
        }, f, ensure_ascii=False, indent=2)

    print()
    print(f"結果已保存: {result_file}")

if __name__ == '__main__':
    main()
