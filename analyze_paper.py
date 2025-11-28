#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
論文分析工具
使用方式: python analyze_paper.py <pdf_path> [選項]

支援：
- BibTeX (.bib) 書目檔整合
- RIS (.ris) 書目檔整合
- DOI 自動提取與查詢
- Citekey 自動生成與正規化
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

# 導入 Citekey 相關模組
try:
    from src.utils.citekey_resolver import CitykeyResolver
except ImportError:
    CitykeyResolver = None

try:
    from src.integrations.bibtex_parser import BibTeXParser
except ImportError:
    BibTeXParser = None

try:
    from src.integrations.ris_parser import RISParser
except ImportError:
    RISParser = None

try:
    from src.integrations.doi_resolver import DOIResolver
except ImportError:
    DOIResolver = None


def is_low_quality_metadata(title: str = None, authors: list = None) -> dict:
    """
    檢測 PDF 提取的元數據品質

    Returns:
        dict: {'title': bool, 'authors': bool} - True 表示低品質
    """
    result = {'title': False, 'authors': False}

    # 檢測標題品質
    if title:
        title_lower = title.lower()
        # 標題過長（包含垃圾文字）
        if len(title) > 200:
            result['title'] = True
        # 標題包含 DOI 或文章類型標記
        if any(x in title_lower for x in ['10.1177/', '10.1016/', '10.1037/', 'xxx', 'article', 'ampxxx']):
            result['title'] = True
        # 標題包含明顯的垃圾字元序列（如 TICS2778No.ofPages13）
        if any(c.isdigit() for c in title[:20]) and len(title) > 50:
            result['title'] = True
        # 標題看起來像期刊資訊（包含 vol., no., 括號日期等）
        if any(x in title_lower for x in ['vol.', 'no.', 'pages', 'ofpages']):
            result['title'] = True
        # 標題包含期刊名稱模式
        if 'journal of' in title_lower and ('vol' in title_lower or ':' in title):
            result['title'] = True

    # 檢測作者品質
    if authors:
        suspicious_count = 0
        for author in authors[:5]:  # 只檢查前 5 個
            author_lower = author.lower()
            # 作者名包含常見文本片段（非人名）
            bad_patterns = [
                'simulation', 'understanding', 'effects', 'model', 'method',
                'analysis', 'research', 'study', 'article', 'section',
                'the author', 'linear', 'mixed', 'statistical', 'special',
                # 期刊/出版相關
                'journal', 'science', 'sciences', 'cognitive', 'psychology',
                'linguistics', 'university', 'press', 'publishing',
                # 城市/地點（常見誤判）
                'taipei', 'city', 'new york', 'london', 'beijing',
                'taichung', 'kaohsiung', 'chinese'
            ]
            if any(p in author_lower for p in bad_patterns):
                suspicious_count += 1
            # 作者名過長（可能是句子片段）
            if len(author) > 40:
                suspicious_count += 1
            # 作者名太短（如 "M. De"）且非縮寫格式
            if len(author) < 5 and '.' not in author:
                suspicious_count += 1

        # 有任何可疑作者就標記為低品質（更嚴格）
        if suspicious_count >= 1:
            result['authors'] = True

    return result


def resolve_citekey(args, pdf_path: Path, structure: dict, result: dict) -> dict:
    """
    解析 citekey 和 DOI

    依優先順序：手動指定 > BibTeX > RIS > DOI > 檔名 > 自動生成

    Returns:
        dict: {
            'cite_key': str,
            'original_citekey': str or None,
            'doi': str or None,
            'source': str
        }
    """
    citekey_info = {
        'cite_key': None,
        'original_citekey': None,
        'doi': args.doi if hasattr(args, 'doi') else None,
        'source': 'auto'
    }

    # 初始化解析器
    resolver = CitykeyResolver() if CitykeyResolver else None
    bib_entry = None
    ris_entry = None

    # 1. 解析 BibTeX（如有指定）
    if hasattr(args, 'bib') and args.bib:
        bib_path = Path(args.bib)
        if bib_path.exists() and BibTeXParser:
            print(f"📚 解析 BibTeX: {bib_path.name}")
            try:
                parser = BibTeXParser()
                entries = parser.parse_file(str(bib_path))
                # 嘗試匹配
                matched = parser.find_entry_by_title(
                    entries,
                    structure['title'] or pdf_path.stem,
                    threshold=0.7
                )
                if matched:
                    bib_entry = matched.to_dict()
                    print(f"   ✓ 匹配成功: {matched.cite_key}")
                    citekey_info['original_citekey'] = matched.cite_key
                    citekey_info['doi'] = matched.doi or citekey_info['doi']
                else:
                    print(f"   ⚠ 未找到匹配條目")
            except Exception as e:
                print(f"   ❌ BibTeX 解析失敗: {e}")
        elif not bib_path.exists():
            print(f"⚠️  BibTeX 文件不存在: {bib_path}")

    # 2. 解析 RIS（如有指定）
    if hasattr(args, 'ris') and args.ris:
        ris_path = Path(args.ris)
        if ris_path.exists() and RISParser:
            print(f"📚 解析 RIS: {ris_path.name}")
            try:
                parser = RISParser()
                entries = parser.parse_file(str(ris_path))
                # 嘗試匹配
                matched = parser.find_entry_by_title(
                    entries,
                    structure['title'] or pdf_path.stem,
                    threshold=0.7
                )
                if matched:
                    ris_entry = matched.to_dict()
                    print(f"   ✓ 匹配成功: {matched.id or matched.title[:30]}")
                    if not citekey_info['original_citekey']:
                        citekey_info['original_citekey'] = matched.id
                    citekey_info['doi'] = matched.doi or citekey_info['doi']
                else:
                    print(f"   ⚠ 未找到匹配條目")
            except Exception as e:
                print(f"   ❌ RIS 解析失敗: {e}")
        elif not ris_path.exists():
            print(f"⚠️  RIS 文件不存在: {ris_path}")

    # 3. 從 PDF 提取 DOI（如未指定）
    if not citekey_info['doi'] and DOIResolver:
        print("🔍 從 PDF 提取 DOI...")
        try:
            doi_resolver = DOIResolver()
            extracted_doi = doi_resolver.extract_doi_from_pdf(pdf_path)
            if extracted_doi:
                print(f"   ✓ 提取成功: {extracted_doi}")
                citekey_info['doi'] = extracted_doi
            else:
                # 嘗試從文本提取
                dois = doi_resolver.extract_doi_from_text(result.get('full_text', '')[:5000])
                if dois:
                    print(f"   ✓ 從文本提取: {dois[0]}")
                    citekey_info['doi'] = dois[0]
                else:
                    print("   ⚠ 未找到 DOI")
        except Exception as e:
            print(f"   ⚠ DOI 提取失敗: {e}")

    # 4. 優先從 DOI 查詢權威元數據（如有 DOI 且可連網）
    doi_metadata = None
    if citekey_info['doi'] and DOIResolver:
        print(f"🌐 從 CrossRef 查詢 DOI 元數據（權威來源）...")
        try:
            doi_resolver = DOIResolver()
            doi_metadata = doi_resolver.resolve(citekey_info['doi'])
            if doi_metadata:
                print(f"   ✓ 查詢成功: {doi_metadata.title[:50]}...")

                # DOI 資料作為主要來源
                if doi_metadata.title:
                    structure['title'] = doi_metadata.title
                    print(f"   → 標題: {doi_metadata.title[:60]}...")
                if doi_metadata.authors:
                    structure['authors'] = doi_metadata.authors
                    print(f"   → 作者: {', '.join(doi_metadata.authors[:3])}")
                if doi_metadata.year:
                    structure['year'] = doi_metadata.year
                    print(f"   → 年份: {doi_metadata.year}")
                if doi_metadata.abstract and not structure.get('abstract'):
                    structure['abstract'] = doi_metadata.abstract
                    print(f"   → 摘要: 已取得")
            else:
                print("   ⚠ CrossRef 查詢失敗，使用本地資料")
        except Exception as e:
            print(f"   ⚠ DOI 查詢失敗: {e}，使用本地資料")

    # 5. 使用 BibTeX/RIS 元數據補充缺失欄位（作為 fallback）
    local_source = bib_entry or ris_entry
    if local_source and not doi_metadata:
        source_name = "BibTeX" if bib_entry else "RIS"
        print(f"📖 使用 {source_name} 元數據（本地來源）...")
        if local_source.get('title') and not structure.get('title'):
            structure['title'] = local_source['title']
        if local_source.get('authors') and not structure.get('authors'):
            structure['authors'] = local_source['authors']
        if local_source.get('year') and not structure.get('year'):
            structure['year'] = local_source['year']
        if local_source.get('abstract') and not structure.get('abstract'):
            structure['abstract'] = local_source['abstract']
    elif local_source and doi_metadata:
        # DOI 查詢成功，但補充 DOI 沒有的欄位
        source_name = "BibTeX" if bib_entry else "RIS"
        if local_source.get('abstract') and not structure.get('abstract'):
            structure['abstract'] = local_source['abstract']
            print(f"   → 從 {source_name} 補充摘要")

    # 6. 最後品質檢查（僅當沒有 DOI 資料時）
    if not doi_metadata:
        quality = is_low_quality_metadata(
            title=structure.get('title'),
            authors=structure.get('authors')
        )
        if quality['title'] or quality['authors']:
            print(f"⚠️  偵測到低品質元數據，建議提供 DOI 以取得正確資訊")

    # 7. 使用 CitykeyResolver 解析
    if resolver:
        ck_result = resolver.resolve(
            pdf_path=pdf_path,
            bib_entry=bib_entry,
            ris_entry=ris_entry,
            manual_citekey=args.citekey if hasattr(args, 'citekey') else None,
            doi=citekey_info['doi'],
            title=structure.get('title'),
            authors=structure.get('authors'),
            year=structure.get('year')
        )
        citekey_info['cite_key'] = ck_result.cite_key
        citekey_info['original_citekey'] = ck_result.original_citekey or citekey_info['original_citekey']
        citekey_info['doi'] = ck_result.doi or citekey_info['doi']
        citekey_info['source'] = ck_result.source
    else:
        # Fallback: 使用檔名
        citekey_info['cite_key'] = pdf_path.stem
        citekey_info['source'] = 'filename'

    return citekey_info


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

  # 指定 BibTeX 書目檔（自動取得 citekey）
  python analyze_paper.py paper.pdf --bib library.bib --add-to-kb

  # 指定 RIS 書目檔
  python analyze_paper.py paper.pdf --ris references.ris --add-to-kb

  # 手動指定 citekey（覆蓋書目檔）
  python analyze_paper.py paper.pdf --citekey "Barsalou-1999" --add-to-kb

  # 指定 DOI（用於查詢元數據）
  python analyze_paper.py paper.pdf --doi "10.1017/S0140525X99002149" --add-to-kb

  # 分析並驗證質量
  python analyze_paper.py paper.pdf --validate

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

    # 書目檔與 Citekey 相關參數
    parser.add_argument('--bib', metavar='FILE',
                       help='BibTeX 書目檔路徑')
    parser.add_argument('--ris', metavar='FILE',
                       help='RIS 書目檔路徑')
    parser.add_argument('--citekey', metavar='KEY',
                       help='手動指定 citekey（覆蓋書目檔）')
    parser.add_argument('--doi', metavar='DOI',
                       help='手動指定 DOI')

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

    # 3. 解析 Citekey 和 DOI
    print(f"\n{'='*60}")
    print("🔑 Citekey 解析")
    print(f"{'='*60}")

    citekey_info = resolve_citekey(args, pdf_path, structure, result)
    print(f"\n📌 最終 Citekey: {citekey_info['cite_key']}")
    if citekey_info['original_citekey']:
        print(f"   原始 Citekey: {citekey_info['original_citekey']}")
    if citekey_info['doi']:
        print(f"   DOI: {citekey_info['doi']}")
    print(f"   來源: {citekey_info['source']}")

    # 4. 顯示論文結構
    if structure['sections']:
        print(f"\n📑 論文結構 ({len(structure['sections'])} 個章節):")
        for i, section in enumerate(structure['sections'][:10], 1):
            print(f"   {i}. {section['title']}")
        if len(structure['sections']) > 10:
            print(f"   ... (+{len(structure['sections'])-10} 個章節)")

    # 5. 顯示摘要
    if structure['abstract']:
        print(f"\n📝 摘要:")
        abstract = structure['abstract']
        if len(abstract) > 500:
            print(f"{abstract[:500]}...")
        else:
            print(abstract)

    # 6. 質量檢查（如果啟用）
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

    # 7. 輸出JSON（如果指定）
    if args.output_json or args.format in ['json', 'both']:
        json_path = args.output_json or pdf_path.stem + '_analysis.json'
        # 加入 citekey 資訊
        result['citekey_info'] = citekey_info
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 JSON已保存: {json_path}")

    # 8. 加入知識庫（如果指定）
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
                'year': structure.get('year'),
                'abstract': structure['abstract'],
                'keywords': structure['keywords'],
                'content': result['full_text'],  # 添加完整PDF內容
                'cite_key': citekey_info['cite_key'],
                'doi': citekey_info['doi'],
            }

            md_path = kb.create_markdown_note(paper_data)
            print(f"📝 筆記已創建: {md_path}")

            # 加入數據庫
            paper_id = kb.add_paper(
                file_path=md_path,
                title=paper_data['title'],
                authors=paper_data['authors'],
                year=paper_data.get('year'),
                keywords=paper_data['keywords'],
                abstract=paper_data['abstract'],
                content=result['full_text'][:10000],  # 限制索引內容長度
                cite_key=citekey_info['cite_key'],
                doi=citekey_info['doi']
            )

            print(f"✅ 已加入知識庫 (ID: {paper_id})")
            print(f"   Citekey: {citekey_info['cite_key']}")
            if citekey_info['doi']:
                print(f"   DOI: {citekey_info['doi']}")

            # 顯示統計
            stats = kb.get_stats()
            print(f"\n📊 知識庫統計:")
            print(f"   論文總數: {stats['total_papers']}")
            print(f"   主題總數: {stats['total_topics']}")

        except Exception as e:
            print(f"❌ 加入知識庫失敗: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*60}")
    print("✅ 分析完成！")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
