#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批次處理工具
穩定地批次處理大量PDF文件

使用範例:
    # 批次處理資料夾中的所有PDF
    python batch_process.py --folder "D:\\pdfs\\mental_simulation"

    # 批次處理並加入知識庫
    python batch_process.py --folder "D:\\pdfs" --domain CogSci --add-to-kb

    # 批次處理並生成 Zettelkasten
    python batch_process.py --folder "D:\\pdfs" --domain CogSci --generate-zettel

    # 完整處理（知識庫 + Zettelkasten）
    python batch_process.py --folder "D:\\pdfs" --domain CogSci --add-to-kb --generate-zettel

    # 指定特定文件
    python batch_process.py --files paper1.pdf paper2.pdf paper3.pdf
"""

import sys
import argparse
from pathlib import Path

# 添加 src 到路徑
sys.path.insert(0, str(Path(__file__).parent))

from src.processors import BatchProcessor


def main():
    parser = argparse.ArgumentParser(
        description="批次處理工具 - 穩定處理大量PDF文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  # 批次處理資料夾
  python batch_process.py --folder "D:\\pdfs\\mental_simulation" --domain CogSci

  # 加入知識庫
  python batch_process.py --folder "D:\\pdfs" --add-to-kb

  # 生成 Zettelkasten 筆記
  python batch_process.py --folder "D:\\pdfs" --domain CogSci --generate-zettel

  # 完整處理
  python batch_process.py --folder "D:\\pdfs" --domain CogSci --add-to-kb --generate-zettel --workers 4

  # 指定特定文件
  python batch_process.py --files paper1.pdf paper2.pdf --add-to-kb

  # 生成報告
  python batch_process.py --folder "D:\\pdfs" --add-to-kb --report batch_report.json

領域代碼:
  CogSci       - 認知科學
  Linguistics  - 語言學
  AI           - 人工智慧
  Research     - 一般研究（預設）
        """
    )

    # 輸入來源（二選一）
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--folder',
        type=str,
        help='包含PDF文件的資料夾路徑'
    )
    input_group.add_argument(
        '--files',
        type=str,
        nargs='+',
        help='指定的PDF文件列表'
    )

    # 處理選項
    parser.add_argument(
        '--domain',
        type=str,
        default='Research',
        help='領域代碼（預設: Research）'
    )

    parser.add_argument(
        '--add-to-kb',
        action='store_true',
        help='加入知識庫'
    )

    parser.add_argument(
        '--generate-zettel',
        action='store_true',
        help='生成 Zettelkasten 筆記'
    )

    # Zettelkasten 配置
    parser.add_argument(
        '--detail',
        choices=['standard', 'detailed', 'comprehensive'],
        default='detailed',
        help='Zettelkasten 詳細程度（預設: detailed）'
    )

    parser.add_argument(
        '--cards',
        type=int,
        default=20,
        help='Zettelkasten 卡片數量（預設: 20）'
    )

    parser.add_argument(
        '--llm-provider',
        choices=['auto', 'google', 'ollama', 'openai', 'anthropic'],
        default='google',
        help='LLM 提供者（預設: google）'
    )

    # 執行選項
    parser.add_argument(
        '--workers',
        type=int,
        default=3,
        help='平行處理的工作執行緒數（預設: 3）'
    )

    parser.add_argument(
        '--error-handling',
        choices=['skip', 'retry', 'stop'],
        default='skip',
        help='錯誤處理策略（預設: skip）'
    )

    # 輸出選項
    parser.add_argument(
        '--report',
        type=str,
        help='報告輸出路徑（JSON 或文本）'
    )

    args = parser.parse_args()

    # 準備 PDF 路徑
    if args.folder:
        pdf_paths = args.folder
        print(f"\n📁 掃描資料夾: {args.folder}")
    else:
        pdf_paths = args.files
        print(f"\n📄 處理文件: {len(args.files)} 個")

    # 準備 Zettelkasten 配置
    zettel_config = None
    if args.generate_zettel:
        zettel_config = {
            'detail_level': args.detail,
            'card_count': args.cards,
            'llm_provider': args.llm_provider
        }

    # 創建處理器
    try:
        processor = BatchProcessor(
            max_workers=args.workers,
            error_handling=args.error_handling
        )
    except FileNotFoundError as e:
        print(f"\n❌ 錯誤: {e}")
        print("   請確保在專案根目錄執行此腳本")
        sys.exit(1)

    # 執行批次處理
    try:
        result = processor.process_batch(
            pdf_paths=pdf_paths,
            domain=args.domain,
            add_to_kb=args.add_to_kb,
            generate_zettel=args.generate_zettel,
            zettel_config=zettel_config,
            progress_callback=None  # 可選：添加進度條
        )

        # 顯示報告
        print("\n")
        print(result.to_report())

        # 保存報告（如果指定）
        if args.report:
            report_path = Path(args.report)

            # 根據副檔名決定格式
            if report_path.suffix == '.json':
                content = result.to_json()
            else:
                content = result.to_report()

            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"\n📄 報告已保存: {report_path}")

        # 詢問是否整理文件（只在互動式終端）
        if result.success > 0 and sys.stdin.isatty():
            print("\n" + "="*60)
            try:
                cleanup_response = input("📁 是否執行檔案整理？[Y/n] ")
                if cleanup_response.lower() != 'n':
                    print("\n正在整理文件...")
                    from src.utils import SessionOrganizer
                    organizer = SessionOrganizer(dry_run=False, auto_backup=True)
                    cleanup_report = organizer.organize_session(session_type='batch')
                    report_path = organizer.save_report()
                    print(f"✅ 整理完成！報告: {report_path}")
            except KeyboardInterrupt:
                print("\n\n⚠️  已跳過檔案整理")
        elif result.success > 0:
            print("\n💡 提示: 處理完成後可手動執行檔案整理：")
            print("   python cleanup_session.py --session batch --auto")

        # 返回碼
        sys.exit(0 if result.failed == 0 else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  處理已中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 處理失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
