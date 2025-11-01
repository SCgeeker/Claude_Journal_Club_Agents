#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qwen3-Embedding 簡化測試
測試論文: Guest-2025b (Paper ID: 36)
"""

import sys
import io
import requests
import numpy as np
import time
from pathlib import Path

# UTF-8 編碼
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

class Qwen3Embeddings:
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.model = "qwen3-embedding:4b"

    def embed(self, text: str) -> np.ndarray:
        response = requests.post(
            f"{self.base_url}/api/embeddings",
            json={"model": self.model, "prompt": text},
            timeout=60
        )
        response.raise_for_status()
        return np.array(response.json()['embedding'], dtype=np.float32)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def main():
    print("=" * 70)
    print("Qwen3-Embedding 論文向量化測試")
    print("=" * 70)

    # 從知識庫讀取論文
    print("\n📖 步驟 1: 讀取論文（Paper ID: 36）")
    print("-" * 70)

    from src.knowledge_base.kb_manager import KnowledgeBaseManager
    kb = KnowledgeBaseManager()

    paper = kb.get_paper_by_id(36)
    if not paper:
        print("❌ 找不到論文 ID 36")
        return

    print(f"✅ 論文資訊:")
    print(f"   標題: {paper['title']}")
    print(f"   作者: {paper['authors']}")
    print(f"   關鍵詞: {paper.get('keywords', [])}")

    # 讀取 Markdown 內容
    md_path = Path(paper['file_path'])
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取摘要（前 1000 字元）
    abstract = content[:1000]
    print(f"\n摘要（前 1000 字元）:")
    print(f"{abstract}...")

    # 初始化 embedder
    print("\n🔢 步驟 2: 生成向量嵌入")
    print("-" * 70)

    embedder = Qwen3Embeddings()

    # 組合文本
    text = f"{paper['title']}. {', '.join(paper.get('keywords', []))}. {abstract}"
    print(f"文本長度: {len(text)} 字元")

    print("生成嵌入中...")
    start = time.time()
    embedding = embedder.embed(text)
    elapsed = time.time() - start

    print(f"✅ 嵌入完成!")
    print(f"   維度: {len(embedding)}")
    print(f"   耗時: {elapsed:.2f} 秒")
    print(f"   範圍: [{embedding.min():.4f}, {embedding.max():.4f}]")
    print(f"   L2範數: {np.linalg.norm(embedding):.4f}")

    # 測試語義搜索
    print("\n🔍 步驟 3: 語義搜索測試")
    print("-" * 70)

    queries = [
        "人工智慧與認知科學",
        "以人為中心的AI設計",
        "機器學習演算法",
        "認知勞動與技術",
        "社會技術關係",
    ]

    print(f"測試 {len(queries)} 個查詢...\n")

    results = []
    for query in queries:
        q_emb = embedder.embed(query)
        sim = cosine_similarity(embedding, q_emb)
        results.append((query, sim))

    # 排序
    results.sort(key=lambda x: x[1], reverse=True)

    print("相似度排名:")
    for i, (query, sim) in enumerate(results, 1):
        if sim > 0.6:
            level = "高 ✅"
        elif sim > 0.4:
            level = "中 ⚠️"
        else:
            level = "低 ❌"

        print(f"{i}. [{sim:.4f}] {level} - {query}")

    # 保存嵌入
    print("\n💾 步驟 4: 保存向量")
    print("-" * 70)

    output_dir = Path("output/embeddings")
    output_dir.mkdir(parents=True, exist_ok=True)

    emb_file = output_dir / f"paper_36_guest2025b_qwen3.npy"
    np.save(emb_file, embedding)

    print(f"✅ 向量已保存: {emb_file}")
    print(f"   大小: {emb_file.stat().st_size / 1024:.1f} KB")

    # 總結
    print("\n" + "=" * 70)
    print("✅ 測試完成！")
    print("=" * 70)

    print(f"\n實測性能:")
    print(f"  - 模型: Qwen3-Embedding-4B (Ollama)")
    print(f"  - 維度: 2560")
    print(f"  - 嵌入速度: {elapsed:.2f} 秒/文本")
    print(f"  - 成本: $0 (本地部署)")

    print(f"\n最相關查詢:")
    for i, (query, sim) in enumerate(results[:3], 1):
        print(f"  {i}. {query} ({sim:.4f})")

    print(f"\n下一步:")
    print(f"  1. 為其餘 30 篇論文生成嵌入")
    print(f"  2. 為 644 張 Zettelkasten 卡片生成嵌入")
    print(f"  3. 整合 ChromaDB 向量存儲")
    print(f"  4. 實作 auto_link_zettel_v3() 向量版本")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
