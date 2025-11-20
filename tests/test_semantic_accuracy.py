#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
語義搜索準確性測試腳本
評估指標：Recall@K, Precision@K, MRR
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set
import io

# 設置 UTF-8 編碼（Windows 相容性）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加專案根目錄到路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.embeddings import create_manager


def calculate_recall_at_k(predictions: List, ground_truth: List, k: int) -> float:
    """計算 Recall@K

    Args:
        predictions: 預測結果列表（有序）
        ground_truth: 真實相關結果列表
        k: 取前 K 個結果

    Returns:
        Recall 值（0-1）
    """
    if not ground_truth:
        return 0.0

    predictions_at_k = set(predictions[:k])
    ground_truth_set = set(ground_truth)

    relevant_retrieved = len(predictions_at_k & ground_truth_set)
    return relevant_retrieved / len(ground_truth_set)


def calculate_precision_at_k(predictions: List, ground_truth: List, k: int) -> float:
    """計算 Precision@K

    Args:
        predictions: 預測結果列表（有序）
        ground_truth: 真實相關結果列表
        k: 取前 K 個結果

    Returns:
        Precision 值（0-1）
    """
    if k == 0:
        return 0.0

    predictions_at_k = set(predictions[:k])
    ground_truth_set = set(ground_truth)

    relevant_retrieved = len(predictions_at_k & ground_truth_set)
    return relevant_retrieved / k


def calculate_mrr(predictions: List, ground_truth: List) -> float:
    """計算 MRR (Mean Reciprocal Rank)

    找到第一個相關結果的位置，計算其倒數

    Args:
        predictions: 預測結果列表（有序）
        ground_truth: 真實相關結果列表

    Returns:
        RR 值（0-1）
    """
    ground_truth_set = set(ground_truth)

    for rank, pred in enumerate(predictions, 1):
        if pred in ground_truth_set:
            return 1.0 / rank

    return 0.0


def run_semantic_search(
    manager,
    query: str,
    search_type: str,
    limit: int = 20
) -> List:
    """執行語義搜索並返回結果 ID 列表

    Args:
        manager: EmbeddingManager 實例
        query: 搜索查詢
        search_type: 搜索類型（papers 或 zettel）
        limit: 返回數量

    Returns:
        結果 ID 列表
    """
    results = manager.search(query, type=search_type, limit=limit)

    if search_type == 'papers':
        return [item['paper_id'] for item in results['papers']]
    else:  # zettel
        return [item['zettel_id'] for item in results['zettel']]


def evaluate_semantic_search(
    test_dataset_path: str,
    provider: str = "gemini",
    verbose: bool = True
) -> Dict:
    """評估語義搜索準確性

    Args:
        test_dataset_path: 測試數據集路徑
        provider: 嵌入提供者
        verbose: 是否顯示詳細過程

    Returns:
        評估結果字典
    """
    # 載入測試數據集
    with open(test_dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    # 初始化 EmbeddingManager
    if verbose:
        print(f"\n初始化 EmbeddingManager (provider: {provider})...")
    manager = create_manager(provider=provider)

    results = []
    total_queries = len(dataset['queries'])

    if verbose:
        print(f"\n開始測試 {total_queries} 個查詢...\n")

    for i, query_data in enumerate(dataset['queries'], 1):
        query_id = query_data['id']
        query_text = query_data['query']
        search_type = query_data['type']
        ground_truth = query_data['relevant_ids']

        if verbose:
            print(f"[{i}/{total_queries}] 測試查詢: '{query_text}'")
            print(f"  類型: {search_type} | 相關項目數: {len(ground_truth)}")

        # 執行搜索
        try:
            predictions = run_semantic_search(
                manager=manager,
                query=query_text,
                search_type=search_type,
                limit=20
            )

            # 計算指標
            recall_at_5 = calculate_recall_at_k(predictions, ground_truth, 5)
            recall_at_10 = calculate_recall_at_k(predictions, ground_truth, 10)
            precision_at_5 = calculate_precision_at_k(predictions, ground_truth, 5)
            precision_at_10 = calculate_precision_at_k(predictions, ground_truth, 10)
            mrr = calculate_mrr(predictions, ground_truth)

            result = {
                'query_id': query_id,
                'query': query_text,
                'type': search_type,
                'domain': query_data.get('domain', ''),
                'ground_truth_count': len(ground_truth),
                'predictions_count': len(predictions),
                'recall@5': recall_at_5,
                'recall@10': recall_at_10,
                'precision@5': precision_at_5,
                'precision@10': precision_at_10,
                'mrr': mrr,
                'predictions': predictions[:10],  # 保存前 10 個預測
                'ground_truth': ground_truth
            }

            results.append(result)

            if verbose:
                print(f"  ✅ Recall@5: {recall_at_5:.1%} | Recall@10: {recall_at_10:.1%} | MRR: {mrr:.3f}")

        except Exception as e:
            if verbose:
                print(f"  ❌ 錯誤: {str(e)}")
            results.append({
                'query_id': query_id,
                'query': query_text,
                'error': str(e)
            })

    # 計算平均指標
    valid_results = [r for r in results if 'error' not in r]

    if not valid_results:
        return {
            'total_queries': total_queries,
            'successful': 0,
            'failed': len(results),
            'results': results
        }

    avg_recall_5 = sum(r['recall@5'] for r in valid_results) / len(valid_results)
    avg_recall_10 = sum(r['recall@10'] for r in valid_results) / len(valid_results)
    avg_precision_5 = sum(r['precision@5'] for r in valid_results) / len(valid_results)
    avg_precision_10 = sum(r['precision@10'] for r in valid_results) / len(valid_results)
    avg_mrr = sum(r['mrr'] for r in valid_results) / len(valid_results)

    # 按類型統計
    papers_results = [r for r in valid_results if r['type'] == 'papers']
    zettel_results = [r for r in valid_results if r['type'] == 'zettel']

    summary = {
        'total_queries': total_queries,
        'successful': len(valid_results),
        'failed': total_queries - len(valid_results),
        'average_metrics': {
            'recall@5': avg_recall_5,
            'recall@10': avg_recall_10,
            'precision@5': avg_precision_5,
            'precision@10': avg_precision_10,
            'mrr': avg_mrr
        },
        'by_type': {
            'papers': {
                'count': len(papers_results),
                'recall@5': sum(r['recall@5'] for r in papers_results) / len(papers_results) if papers_results else 0,
                'recall@10': sum(r['recall@10'] for r in papers_results) / len(papers_results) if papers_results else 0
            },
            'zettel': {
                'count': len(zettel_results),
                'recall@5': sum(r['recall@5'] for r in zettel_results) / len(zettel_results) if zettel_results else 0,
                'recall@10': sum(r['recall@10'] for r in zettel_results) / len(zettel_results) if zettel_results else 0
            }
        },
        'results': results
    }

    return summary


def print_summary_report(summary: Dict):
    """打印摘要報告"""
    print("\n" + "=" * 70)
    print("📊 語義搜索準確性測試報告")
    print("=" * 70)

    print(f"\n總查詢數: {summary['total_queries']}")
    print(f"成功: {summary['successful']} | 失敗: {summary['failed']}")

    avg = summary['average_metrics']
    print("\n平均指標:")
    print(f"  Recall@5:     {avg['recall@5']:.1%}")
    print(f"  Recall@10:    {avg['recall@10']:.1%}")
    print(f"  Precision@5:  {avg['precision@5']:.1%}")
    print(f"  Precision@10: {avg['precision@10']:.1%}")
    print(f"  MRR:          {avg['mrr']:.3f}")

    print("\n按類型統計:")
    for search_type, stats in summary['by_type'].items():
        if stats['count'] > 0:
            print(f"  {search_type.upper()} ({stats['count']} 查詢):")
            print(f"    Recall@5:  {stats['recall@5']:.1%}")
            print(f"    Recall@10: {stats['recall@10']:.1%}")

    # 目標達成情況
    print("\n目標達成情況:")
    target_recall_5 = 0.60
    target_recall_10 = 0.80
    target_mrr = 0.70

    def check_target(value, target, name):
        status = "✅" if value >= target else "❌"
        return f"  {status} {name}: {value:.1%} (目標: {target:.1%})"

    print(check_target(avg['recall@5'], target_recall_5, "Recall@5"))
    print(check_target(avg['recall@10'], target_recall_10, "Recall@10"))
    print(check_target(avg['mrr'], target_mrr, "MRR"))

    print("\n" + "=" * 70)


def save_detailed_report(summary: Dict, output_path: str):
    """保存詳細報告到 JSON 文件"""
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 詳細報告已保存到: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="語義搜索準確性測試",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--dataset',
        type=str,
        default='tests/semantic_search_test_queries.json',
        help='測試數據集路徑（默認：tests/semantic_search_test_queries.json）'
    )
    parser.add_argument(
        '--provider',
        choices=['gemini', 'ollama'],
        default='gemini',
        help='嵌入提供者（默認：gemini）'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='tests/semantic_accuracy_report.json',
        help='輸出報告路徑（默認：tests/semantic_accuracy_report.json）'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='安靜模式（不顯示詳細過程）'
    )

    args = parser.parse_args()

    # 執行評估
    summary = evaluate_semantic_search(
        test_dataset_path=args.dataset,
        provider=args.provider,
        verbose=not args.quiet
    )

    # 打印摘要報告
    print_summary_report(summary)

    # 保存詳細報告
    save_detailed_report(summary, args.output)


if __name__ == "__main__":
    main()
