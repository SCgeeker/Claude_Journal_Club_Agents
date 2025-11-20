#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
論文分析工具
使用方式: python analyze_paper.py <pdf_path> [選項]
"""

import sys
import argparse
from pathlib import Path
import json
import os

# 設置UTF-8編碼（Windows相容性）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加src到路徑
sys.path.insert(0, str(Path(__file__).parent))

from src.extractors import PDFExtractor
from src.knowledge_base import KnowledgeBaseManager

# 導入質量檢查和修復工具
try:
    from src.checkers.quality_checker import QualityChecker
except ImportError:
    QualityChecker = None

try:
    from fix_metadata import MetadataFixer
except ImportError:
    MetadataFixer = None


def main():
    parser = argparse.ArgumentParser(
        description="分析學術論文並提取關鍵信息",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本分析
  python analyze_paper.py paper.pdf

  # 分析並加入知識庫
  python analyze_paper.py paper.pdf --add-to-kb

  # 分析並驗證質量
  python analyze_paper.py paper.pdf --validate

  # 分析、驗證並加入知識庫
  python analyze_paper.py paper.pdf --add-to-kb --validate

  # 分析、驗證並嘗試自動修復（需要 LLM）
  python analyze_paper.py paper.pdf --validate --auto-fix

  # 輸出JSON格式
  python analyze_paper.py paper.pdf --format json
  python analyze_paper.py paper.pdf --output-json result.json
        """
    )

    parser.add_argument('pdf_path', help='PDF文件路徑')
    parser.add_argument('--add-to-kb', action='store_true',
                       help='將論文添加到知識庫')
    parser.add_argument('--format', choices=['markdown', 'json', 'both'],
                       default='markdown',
                       help='輸出格式 (默認: markdown)')
    parser.add_argument('--output-json', help='JSON輸出文件路徑')
    parser.add_argument('--max-chars', type=int, default=50000,
                       help='最大字元數 (默認: 50000)')
    parser.add_argument('--validate', action='store_true',
                       help='驗證元數據質量（警告缺失字段）')
    parser.add_argument('--auto-fix', action='store_true',
                       help='自動修復缺失的元數據（使用LLM）')
    parser.add_argument('--min-score', type=int, default=60,
                       help='最低質量分數（配合--validate使用，默認: 60）')

    args = parser.parse_args()

    # 檢查文件是否存在
    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"❌ 錯誤: 找不到文件 {pdf_path}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"📄 分析論文: {pdf_path.name}")
    print(f"{'='*60}\n")

    # 1. 提取PDF內容
    print("🔍 正在提取PDF內容...")
    try:
        extractor = PDFExtractor(max_chars=args.max_chars)
        result = extractor.extract(str(pdf_path))
        print(f"✅ PDF已提取: {result['char_count']:,} 字元")

        if result['truncated']:
            print(f"⚠️  內容已截斷至 {args.max_chars:,} 字元")

    except Exception as e:
        print(f"❌ PDF提取失敗: {e}")
        sys.exit(1)

    # 2. 顯示基本信息
    print(f"\n{'='*60}")
    print("📊 基本信息")
    print(f"{'='*60}")

    structure = result['structure']
    print(f"📖 標題: {structure['title'] or '未識別'}")

    if structure['authors']:
        print(f"👥 作者: {', '.join(structure['authors'][:5])}")
        if len(structure['authors']) > 5:
            print(f"       (+{len(structure['authors'])-5} 位作者)")
    else:
        print(f"👥 作者: 未識別")

    if structure['keywords']:
        print(f"🏷️  關鍵詞: {', '.join(structure['keywords'])}")

    # 3. 顯示論文結構
    if structure['sections']:
        print(f"\n📑 論文結構 ({len(structure['sections'])} 個章節):")
        for i, section in enumerate(structure['sections'][:10], 1):
            print(f"   {i}. {section['title']}")
        if len(structure['sections']) > 10:
            print(f"   ... (+{len(structure['sections'])-10} 個章節)")

    # 4. 顯示摘要
    if structure['abstract']:
        print(f"\n📝 摘要:")
        abstract = structure['abstract']
        if len(abstract) > 500:
            print(f"{abstract[:500]}...")
        else:
            print(abstract)

    # 5. 質量檢查（如果啟用）
    if args.validate or args.auto_fix:
        print(f"\n{'='*60}")
        print("🔍 元數據質量檢查")
        print(f"{'='*60}")

        # 構建簡化的元數據檢查（不依賴 QualityChecker）
        issues = []
        quality_score = 100

        # 檢查標題
        if not structure['title'] or len(structure['title']) < 10:
            issues.append("缺少有效標題")
            quality_score -= 25

        # 檢查作者
        if not structure['authors'] or len(structure['authors']) == 0:
            issues.append("缺少作者信息")
            quality_score -= 20

        # 檢查摘要
        if not structure['abstract'] or len(structure['abstract']) < 50:
            issues.append("缺少摘要或摘要過短")
            quality_score -= 25

        # 檢查關鍵詞
        if not structure['keywords'] or len(structure['keywords']) < 3:
            issues.append("缺少關鍵詞或關鍵詞過少")
            quality_score -= 15

        print(f"📊 質量分數: {quality_score}/100")

        if issues:
            print(f"\n⚠️  發現 {len(issues)} 個問題:")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")

            if quality_score < args.min_score:
                print(f"\n❌ 質量分數 ({quality_score}) 低於最低要求 ({args.min_score})")

                if args.auto_fix:
                    print(f"\n🔧 嘗試自動修復...")
                    print(f"⚠️  自動修復功能需要 LLM API（未實作完整版本）")
                    print(f"建議: 使用 --add-to-kb 導入後，再執行:")
                    print(f"  python kb_manage.py metadata-fix --batch")
                else:
                    print(f"\n提示: 使用 --auto-fix 選項嘗試自動修復")

                    if not args.add_to_kb:
                        print(f"建議: 先不要導入知識庫，修正後再重新分析")
                        response = input(f"\n是否仍要繼續加入知識庫？(y/N): ")
                        if response.lower() != 'y':
                            print(f"\n❌ 已取消加入知識庫")
                            args.add_to_kb = False
        else:
            print(f"✅ 元數據質量良好，沒有發現問題")

    # 6. 輸出JSON（如果指定）
    if args.output_json or args.format in ['json', 'both']:
        json_path = args.output_json or pdf_path.stem + '_analysis.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 JSON已保存: {json_path}")

    # 6. 加入知識庫（如果指定）
    if args.add_to_kb:
        print(f"\n{'='*60}")
        print("📚 加入知識庫")
        print(f"{'='*60}")

        try:
            kb = KnowledgeBaseManager()

            # 創建Markdown筆記
            paper_data = {
                'title': structure['title'] or pdf_path.stem,
                'authors': structure['authors'],
                'abstract': structure['abstract'],
                'keywords': structure['keywords'],
                'content': result['full_text']  # 添加完整PDF內容
            }

            md_path = kb.create_markdown_note(paper_data)
            print(f"📝 筆記已創建: {md_path}")

            # 加入數據庫
            paper_id = kb.add_paper(
                file_path=md_path,
                title=paper_data['title'],
                authors=paper_data['authors'],
                keywords=paper_data['keywords'],
                abstract=paper_data['abstract'],
                content=result['full_text'][:10000]  # 限制索引內容長度
            )

            print(f"✅ 已加入知識庫 (ID: {paper_id})")

            # 顯示統計
            stats = kb.get_stats()
            print(f"\n📊 知識庫統計:")
            print(f"   論文總數: {stats['total_papers']}")
            print(f"   主題總數: {stats['total_topics']}")

        except Exception as e:
            print(f"❌ 加入知識庫失敗: {e}")

    print(f"\n{'='*60}")
    print("✅ 分析完成！")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
