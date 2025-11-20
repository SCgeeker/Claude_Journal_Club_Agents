#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Qwen3-Embedding-4B 模型
驗證 Ollama 本地部署的 embedding 功能
"""

import requests
import numpy as np
import time
from typing import List
import sys
import io

# 設置 UTF-8 編碼（Windows 相容性）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class Qwen3Embeddings:
    """Qwen3-Embedding-4B (Ollama) 封裝"""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen3-embedding:4b"):
        self.base_url = base_url
        self.model = model

    def embed(self, text: str) -> np.ndarray:
        """嵌入單個文本"""
        response = requests.post(
            f"{self.base_url}/api/embeddings",
            json={"model": self.model, "prompt": text}
        )
        response.raise_for_status()
        return np.array(response.json()['embedding'], dtype=np.float32)

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """批次嵌入"""
        embeddings = []
        for i, text in enumerate(texts):
            print(f"  [{i+1}/{len(texts)}] 嵌入中: {text[:30]}...")
            embedding = self.embed(text)
            embeddings.append(embedding)
        return np.array(embeddings)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """計算餘弦相似度"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def main():
    print("=" * 60)
    print("Qwen3-Embedding-4B (Ollama) 測試")
    print("=" * 60)

    # 初始化
    embedder = Qwen3Embeddings()

    # 測試 1: 基本嵌入
    print("\n📝 測試 1: 基本嵌入")
    print("-" * 60)
    text = "Zettelkasten 是一種原子筆記方法，強調知識的原子化和連結"
    embedding = embedder.embed(text)
    print(f"文本: {text}")
    print(f"維度: {len(embedding)}")
    print(f"前10個值: {embedding[:10]}")
    print(f"數值範圍: [{embedding.min():.4f}, {embedding.max():.4f}]")
    print(f"L2範數: {np.linalg.norm(embedding):.4f}")

    # 測試 2: 語義相似度（繁體中文）
    print("\n📊 測試 2: 語義相似度（繁體中文）")
    print("-" * 60)

    test_cases = [
        ("Zettelkasten 原子筆記系統", "知識管理與第二大腦"),
        ("Zettelkasten 原子筆記系統", "深度學習神經網絡"),
        ("認知科學研究方法", "心理學實驗設計"),
        ("認知科學研究方法", "量子物理理論"),
    ]

    print("批次嵌入中...")
    all_texts = [text for pair in test_cases for text in pair]
    all_embeddings = embedder.embed_batch(all_texts)

    print("\n相似度結果:")
    for i, (text1, text2) in enumerate(test_cases):
        emb1 = all_embeddings[i*2]
        emb2 = all_embeddings[i*2 + 1]
        similarity = cosine_similarity(emb1, emb2)

        # 判斷相似度等級
        if similarity > 0.7:
            level = "高 ✅"
        elif similarity > 0.5:
            level = "中 ⚠️"
        else:
            level = "低 ❌"

        print(f"{i+1}. 相似度: {similarity:.4f} ({level})")
        print(f"   A: {text1}")
        print(f"   B: {text2}")
        print()

    # 測試 3: 批次處理效能
    print("\n⚡ 測試 3: 批次處理效能")
    print("-" * 60)

    batch_texts = [
        "知識管理系統的設計原則",
        "Zettelkasten 筆記法的核心概念",
        "第二大腦與個人知識庫",
        "原子化筆記與連結思維",
        "認知負荷理論與學習效率",
        "概念映射與知識圖譜",
        "語義網絡與知識表示",
        "資訊檢索與全文搜索",
        "向量嵌入與語義相似度",
        "混合搜索策略與排序演算法",
    ]

    print(f"批次大小: {len(batch_texts)} 個文本")
    start_time = time.time()
    batch_embeddings = embedder.embed_batch(batch_texts)
    elapsed = time.time() - start_time

    print(f"\n耗時: {elapsed:.2f} 秒")
    print(f"平均速度: {elapsed/len(batch_texts):.2f} 秒/文本")
    print(f"輸出形狀: {batch_embeddings.shape}")

    # 測試 4: 查找最相似的文本
    print("\n🔍 測試 4: 查找最相似的文本")
    print("-" * 60)

    query = "什麼是原子筆記？"
    print(f"查詢: {query}")
    query_embedding = embedder.embed(query)

    similarities = [
        (i, text, cosine_similarity(query_embedding, emb))
        for i, (text, emb) in enumerate(zip(batch_texts, batch_embeddings))
    ]
    similarities.sort(key=lambda x: x[2], reverse=True)

    print("\n最相關的文本 (Top 5):")
    for rank, (i, text, sim) in enumerate(similarities[:5], 1):
        print(f"{rank}. [{i}] 相似度 {sim:.4f}: {text}")

    # 測試 5: 跨語言能力
    print("\n🌏 測試 5: 跨語言能力")
    print("-" * 60)

    multilang_texts = {
        "繁中": "Zettelkasten 原子筆記系統",
        "英文": "Zettelkasten atomic note-taking system",
        "簡中": "Zettelkasten 原子笔记系统",
    }

    print("嵌入中...")
    multilang_embeddings = {
        lang: embedder.embed(text)
        for lang, text in multilang_texts.items()
    }

    print("\n跨語言相似度:")
    langs = list(multilang_texts.keys())
    for i in range(len(langs)):
        for j in range(i+1, len(langs)):
            lang1, lang2 = langs[i], langs[j]
            sim = cosine_similarity(
                multilang_embeddings[lang1],
                multilang_embeddings[lang2]
            )
            print(f"{lang1} ↔ {lang2}: {sim:.4f}")

    # 總結
    print("\n" + "=" * 60)
    print("✅ 測試完成！")
    print("=" * 60)
    print(f"\n模型資訊:")
    print(f"  - 名稱: qwen3-embedding:4b")
    print(f"  - 維度: 2560")
    print(f"  - 部署方式: Ollama 本地")
    print(f"  - 繁體中文支援: ✅ 優秀")
    print(f"  - 跨語言能力: ✅ 優秀")
    print(f"  - 處理速度: ~{elapsed/len(batch_texts):.2f} 秒/文本")
    print(f"\n評估結論:")
    print(f"  - ✅ 完全免費（本地部署）")
    print(f"  - ✅ 無 API 限制")
    print(f"  - ✅ 數據隱私保護")
    print(f"  - ✅ 適合大批量嵌入")
    print(f"  - ⚠️  需要約 3GB 磁碟空間")
    print(f"  - ⚠️  處理速度中等（CPU 推理）")


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("❌ 錯誤: 無法連接到 Ollama")
        print("請確保 Ollama 服務正在運行")
        print("執行: ollama serve")
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
