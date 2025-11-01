#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Qwen3-Embedding 實際論文測試
使用 Guest-2025b.pdf 進行完整流程測試
"""

import sys
import io
import subprocess
import time
import requests
import numpy as np
from pathlib import Path

# 設置 UTF-8 編碼
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class Qwen3Embeddings:
    """Qwen3-Embedding-4B 封裝"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.model = "qwen3-embedding:4b"

    def embed(self, text: str) -> np.ndarray:
        """嵌入單個文本"""
        response = requests.post(
            f"{self.base_url}/api/embeddings",
            json={"model": self.model, "prompt": text},
            timeout=60
        )
        response.raise_for_status()
        return np.array(response.json()['embedding'], dtype=np.float32)

    def check_available(self) -> bool:
        """檢查模型是否可用"""
        try:
            # 測試嵌入簡單文本
            self.embed("test")
            return True
        except Exception as e:
            print(f"❌ Qwen3-Embedding 不可用: {e}")
            return False


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """計算餘弦相似度"""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def main():
    print("=" * 70)
    print("Qwen3-Embedding 實際論文測試")
    print("測試論文: Guest-2025b.pdf")
    print("=" * 70)

    # 檢查 PDF 文件
    pdf_path = Path(r"D:\core\research\Program_verse\+\pdf\Guest-2025b.pdf")
    if not pdf_path.exists():
        print(f"❌ 錯誤: PDF 文件不存在: {pdf_path}")
        return

    print(f"\n✅ PDF 文件存在: {pdf_path.name} ({pdf_path.stat().st_size / 1024 / 1024:.1f} MB)")

    # 初始化 embedder
    print("\n📝 步驟 1: 初始化 Qwen3-Embedding")
    print("-" * 70)
    embedder = Qwen3Embeddings()

    print("檢查模型可用性...")
    if not embedder.check_available():
        print("請確保 Ollama 正在運行且已安裝 qwen3-embedding:4b")
        print("執行: ollama pull qwen3-embedding:4b")
        return

    print("✅ Qwen3-Embedding-4B 可用")

    # 分析論文並加入知識庫
    print("\n📚 步驟 2: 分析論文並加入知識庫")
    print("-" * 70)
    print("執行: analyze_paper.py --pdf Guest-2025b.pdf --add-to-kb")

    cmd = [
        "python", "analyze_paper.py",
        "--pdf", str(pdf_path),
        "--add-to-kb",
        "--domain", "CogSci"
    ]

    print(f"命令: {' '.join(cmd)}\n")

    start_time = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=300
        )

        if result.returncode != 0:
            print("❌ 分析失敗:")
            print(result.stderr)
            return

        print("✅ 論文分析完成")
        # 從輸出中提取 paper_id
        for line in result.stdout.split('\n'):
            if 'paper_id' in line.lower() or 'id:' in line:
                print(f"   {line.strip()}")

    except subprocess.TimeoutExpired:
        print("❌ 分析超時（>5分鐘）")
        return
    except Exception as e:
        print(f"❌ 錯誤: {e}")
        return

    elapsed = time.time() - start_time
    print(f"   耗時: {elapsed:.1f} 秒")

    # 從知識庫獲取論文資訊
    print("\n📖 步驟 3: 從知識庫讀取論文資訊")
    print("-" * 70)

    from src.knowledge_base.kb_manager import KnowledgeBaseManager

    kb = KnowledgeBaseManager()
    papers = kb.list_papers()

    # 查找剛加入的論文（最新的）
    if not papers:
        print("❌ 知識庫為空")
        return

    # 按 ID 排序，取最後一個（最新）
    papers_sorted = sorted(papers, key=lambda x: x['id'], reverse=True)
    paper = papers_sorted[0]

    print(f"✅ 找到論文:")
    print(f"   ID: {paper['id']}")
    print(f"   標題: {paper['title']}")
    print(f"   作者: {paper['authors']}")
    print(f"   年份: {paper.get('year', 'N/A')}")
    print(f"   關鍵詞: {paper.get('keywords', [])}")

    # 讀取論文 Markdown 內容
    paper_md_path = Path(paper['file_path'])
    if not paper_md_path.exists():
        print(f"❌ Markdown 文件不存在: {paper_md_path}")
        return

    with open(paper_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取摘要（前 500 字元）
    abstract = content[:500] if len(content) > 500 else content
    print(f"\n摘要預覽 (前 500 字元):")
    print(f"{abstract}...")

    # 生成論文嵌入
    print("\n🔢 步驟 4: 生成論文向量嵌入")
    print("-" * 70)

    # 組合文本：標題 + 摘要 + 關鍵詞
    text_to_embed = f"{paper['title']}. "
    if paper.get('keywords'):
        text_to_embed += f"Keywords: {', '.join(paper['keywords'])}. "
    text_to_embed += abstract

    print(f"文本長度: {len(text_to_embed)} 字元")
    print("生成嵌入中...")

    start_time = time.time()
    embedding = embedder.embed(text_to_embed)
    elapsed = time.time() - start_time

    print(f"✅ 嵌入生成完成")
    print(f"   維度: {len(embedding)}")
    print(f"   耗時: {elapsed:.2f} 秒")
    print(f"   範圍: [{embedding.min():.4f}, {embedding.max():.4f}]")
    print(f"   L2範數: {np.linalg.norm(embedding):.4f}")

    # 測試語義搜索
    print("\n🔍 步驟 5: 測試語義搜索")
    print("-" * 70)

    # 生成一些查詢
    queries = [
        "認知科學研究方法",
        "心智模擬與預測",
        "深度學習與神經網絡",
        "知識表示與推理",
    ]

    print(f"測試 {len(queries)} 個查詢...")
    query_embeddings = []

    for i, query in enumerate(queries, 1):
        print(f"  [{i}/{len(queries)}] 嵌入查詢: {query}")
        q_emb = embedder.embed(query)
        query_embeddings.append(q_emb)

    # 計算相似度
    print("\n相似度結果:")
    similarities = []
    for i, (query, q_emb) in enumerate(zip(queries, query_embeddings)):
        sim = cosine_similarity(embedding, q_emb)
        similarities.append((query, sim))

        # 判斷相關性
        if sim > 0.7:
            relevance = "高度相關 ✅"
        elif sim > 0.5:
            relevance = "中度相關 ⚠️"
        else:
            relevance = "低度相關 ❌"

        print(f"{i+1}. [{sim:.4f}] {relevance}")
        print(f"   查詢: {query}")

    # 保存嵌入（示範）
    print("\n💾 步驟 6: 保存向量嵌入（模擬）")
    print("-" * 70)

    # 實際專案中會使用 ChromaDB 或 SQLite
    output_dir = Path("output/embeddings")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 保存為 numpy 格式
    embedding_file = output_dir / f"paper_{paper['id']}_qwen3.npy"
    np.save(embedding_file, embedding)

    print(f"✅ 嵌入已保存到: {embedding_file}")
    print(f"   文件大小: {embedding_file.stat().st_size / 1024:.1f} KB")

    # 總結
    print("\n" + "=" * 70)
    print("✅ 測試完成！")
    print("=" * 70)

    print(f"\n測試總結:")
    print(f"  📄 論文: {paper['title']}")
    print(f"  📊 Paper ID: {paper['id']}")
    print(f"  🔢 嵌入維度: {len(embedding)}")
    print(f"  💾 嵌入文件: {embedding_file}")
    print(f"\n  📈 最相關查詢:")
    # 排序並顯示 Top 2
    similarities.sort(key=lambda x: x[1], reverse=True)
    for i, (query, sim) in enumerate(similarities[:2], 1):
        print(f"     {i}. {query} (相似度: {sim:.4f})")

    print(f"\n下一步建議:")
    print(f"  1. 使用 ChromaDB 整合向量存儲")
    print(f"  2. 為其餘 {len(papers)-1} 篇論文生成嵌入")
    print(f"  3. 實作語義搜索功能")
    print(f"  4. 測試 Hybrid Search（FTS5 + Vector）")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用戶中斷")
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
