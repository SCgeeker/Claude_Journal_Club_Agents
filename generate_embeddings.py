#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批次生成 Embeddings 腳本
為知識庫中的論文和 Zettelkasten 卡片生成向量嵌入
"""

import sys
import io
import os
import argparse
import sqlite3
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from tqdm import tqdm

# UTF-8 編碼（Windows 支援）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 導入 embedding providers 和 vector database
from src.embeddings.providers import GeminiEmbedder, OllamaEmbedder
from src.embeddings.vector_db import VectorDatabase
from src.knowledge_base.kb_manager import KnowledgeBaseManager
from src.utils.content_filter import extract_ai_content


class EmbeddingGenerator:
    """嵌入向量生成器"""

    def __init__(
        self,
        kb_root: str = "knowledge_base",
        provider: str = "gemini",
        chroma_path: str = "chroma_db",
        use_cloud_for_batch: bool = True,
        auto_confirm: bool = False
    ):
        """
        初始化生成器

        Args:
            kb_root: 知識庫根目錄
            provider: 嵌入提供者 (gemini/ollama)
            chroma_path: ChromaDB 持久化路徑
            use_cloud_for_batch: 批次處理使用雲端 API
            auto_confirm: 自動確認所有提示
        """
        self.kb = KnowledgeBaseManager(kb_root)
        self.provider_name = provider
        self.use_cloud_for_batch = use_cloud_for_batch
        self.auto_confirm = auto_confirm

        # 初始化 embedding provider
        self._init_provider()

        # 初始化 VectorDatabase
        self.vector_db = VectorDatabase(persist_directory=chroma_path)

    def _init_provider(self):
        """初始化 embedding provider"""
        if self.provider_name == "gemini":
            print("初始化 Google Gemini Embedder...")
            self.embedder = GeminiEmbedder()
            print(f"  模型: {self.embedder.model}")
            print(f"  維度: {self.embedder.dimension}")
            print(f"  成本: ${self.embedder.cost_per_1k_tokens}/1K tokens")

        elif self.provider_name == "ollama":
            print("初始化 Ollama Embedder...")
            self.embedder = OllamaEmbedder()
            print(f"  模型: {self.embedder.model}")
            print(f"  維度: {self.embedder.dimension}")
            print(f"  成本: $0 (本地免費)")

        else:
            raise ValueError(f"不支援的提供者: {self.provider_name}")

    def _read_markdown_content(self, file_path: str) -> str:
        """讀取 Markdown 文件內容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"  ⚠️ 無法讀取 {file_path}: {e}")
            return ""

    def generate_paper_embeddings(self, limit: int = None) -> Tuple[int, int]:
        """
        為所有論文生成嵌入

        Args:
            limit: 處理數量限制（用於測試）

        Returns:
            (成功數, 失敗數)
        """
        print("\n" + "=" * 70)
        print("📄 生成論文嵌入")
        print("=" * 70)

        # 從數據庫獲取論文
        conn = sqlite3.connect(self.kb.db_path)
        cursor = conn.cursor()

        query = "SELECT id, file_path, title, authors, abstract, keywords FROM papers"
        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query)
        papers = cursor.fetchall()
        conn.close()

        if not papers:
            print("⚠️  知識庫中沒有論文")
            return 0, 0

        print(f"找到 {len(papers)} 篇論文")

        # 準備數據
        texts = []
        ids = []
        metadatas = []

        for paper_id, file_path, title, authors, abstract, keywords in papers:
            # 組合文本：標題 + 作者 + 摘要 + 關鍵詞
            components = []

            if title:
                components.append(f"標題: {title}")

            if authors:
                components.append(f"作者: {authors}")

            if abstract:
                components.append(f"摘要: {abstract}")

            if keywords:
                components.append(f"關鍵詞: {keywords}")

            # 如果元數據不足，讀取 Markdown 內容
            if len(components) < 2:
                content = self._read_markdown_content(file_path)
                if content:
                    # 取前 2000 字元
                    components.append(f"內容: {content[:2000]}")

            text = "\n".join(components)

            if not text.strip():
                print(f"  ⚠️ 論文 {paper_id} 無內容，跳過")
                continue

            texts.append(text)
            ids.append(f"paper_{paper_id}")
            metadatas.append({
                "paper_id": paper_id,
                "title": title or "Unknown",
                "authors": authors or "Unknown",
                "file_path": file_path,
                "type": "paper"
            })

        if not texts:
            print("⚠️  沒有可處理的論文")
            return 0, 0

        # 估算成本
        if self.provider_name == "gemini":
            cost = self.embedder.estimate_cost(texts)
            print(f"\n預估成本: ${cost:.4f}")

            if not self.auto_confirm:
                confirm = input("是否繼續？(y/n): ")
                if confirm.lower() != 'y':
                    print("已取消")
                    return 0, 0
            else:
                print("(自動確認)")

        # 生成嵌入
        print(f"\n生成 {len(texts)} 個嵌入...")
        try:
            embeddings = self.embedder.embed_batch(
                texts,
                show_progress=True
            )

            # 保存到 ChromaDB
            print("\n保存到 ChromaDB...")
            self.vector_db.upsert_papers(
                embeddings=embeddings,
                documents=texts,
                ids=ids,
                metadatas=metadatas
            )

            print(f"✅ 成功處理 {len(texts)} 篇論文")
            return len(texts), 0

        except Exception as e:
            print(f"❌ 生成失敗: {e}")
            import traceback
            traceback.print_exc()
            return 0, len(texts)

    def generate_zettel_embeddings(self, limit: int = None) -> Tuple[int, int]:
        """
        為所有 Zettelkasten 卡片生成嵌入

        Args:
            limit: 處理數量限制（用於測試）

        Returns:
            (成功數, 失敗數)
        """
        print("\n" + "=" * 70)
        print("🗂️  生成 Zettelkasten 卡片嵌入")
        print("=" * 70)

        # 從數據庫獲取卡片
        conn = sqlite3.connect(self.kb.db_path)
        cursor = conn.cursor()

        query = """
            SELECT card_id, zettel_id, title, content, core_concept, description, ai_notes, human_notes
            FROM zettel_cards
        """
        if limit:
            query += f" LIMIT {limit}"

        cursor.execute(query)
        cards = cursor.fetchall()
        conn.close()

        if not cards:
            print("⚠️  知識庫中沒有 Zettelkasten 卡片")
            return 0, 0

        print(f"找到 {len(cards)} 張卡片")

        # 準備數據
        texts = []
        ids = []
        metadatas = []

        for card_id, zettel_id, title, content, core_concept, description, ai_notes, human_notes in cards:
            # 組合文本：標題 + 核心概念 + 描述 + 內容
            components = []

            if title:
                components.append(f"標題: {title}")

            if core_concept:
                components.append(f"核心概念: {core_concept}")

            if description:
                components.append(f"描述: {description}")

            # 優先使用 ai_notes（Plan B），如果為 NULL 則 fallback 到從 content 提取
            if ai_notes:
                # ai_notes 已經是純 AI 內容，直接使用
                ai_content = ai_notes
            elif content:
                # Fallback: 從 content 提取 AI 內容（過濾人類筆記）
                ai_content = extract_ai_content(content)
            else:
                ai_content = None

            if ai_content:
                # 內容可能很長，取前 1500 字元
                components.append(f"內容: {ai_content[:1500]}")

            text = "\n".join(components)

            if not text.strip():
                print(f"  ⚠️ 卡片 {zettel_id} 無內容，跳過")
                continue

            texts.append(text)
            # 使用資料庫中的標準 ID 格式（不加前綴）
            ids.append(zettel_id)
            metadatas.append({
                "card_id": card_id,
                "zettel_id": zettel_id,
                "title": title or "Unknown",
                "type": "zettelkasten"
            })

        if not texts:
            print("⚠️  沒有可處理的卡片")
            return 0, 0

        # 估算成本
        if self.provider_name == "gemini":
            cost = self.embedder.estimate_cost(texts)
            print(f"\n預估成本: ${cost:.4f}")

            if not self.auto_confirm:
                confirm = input("是否繼續？(y/n): ")
                if confirm.lower() != 'y':
                    print("已取消")
                    return 0, 0
            else:
                print("(自動確認)")

        # 生成嵌入
        print(f"\n生成 {len(texts)} 個嵌入...")
        try:
            embeddings = self.embedder.embed_batch(
                texts,
                show_progress=True
            )

            # 保存到 ChromaDB
            print("\n保存到 ChromaDB...")
            self.vector_db.upsert_zettel(
                embeddings=embeddings,
                documents=texts,
                ids=ids,
                metadatas=metadatas
            )

            print(f"✅ 成功處理 {len(texts)} 張卡片")
            return len(texts), 0

        except Exception as e:
            print(f"❌ 生成失敗: {e}")
            import traceback
            traceback.print_exc()
            return 0, len(texts)

    def get_stats(self):
        """獲取 ChromaDB 統計信息"""
        print("\n" + "=" * 70)
        print("📊 ChromaDB 統計")
        print("=" * 70)

        stats = self.vector_db.get_stats()

        print(f"論文向量數: {stats['papers_count']}")
        print(f"Zettelkasten 向量數: {stats['zettel_count']}")
        print(f"總計: {stats['total_count']}")


def main():
    parser = argparse.ArgumentParser(
        description="批次生成知識庫嵌入向量",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用方式：
  # 使用 uv（推薦）
  uv run embeddings [選項]

  # 或直接用 Python
  python generate_embeddings.py [選項]

範例：
  # 為所有論文和卡片生成嵌入
  uv run embeddings

  # 僅處理論文
  uv run embeddings --papers-only

  # 僅處理 Zettelkasten 卡片
  uv run embeddings --zettel-only

  # 使用 Ollama 本地模型
  uv run embeddings --provider ollama

  # 測試模式（限制處理數量）
  uv run embeddings --limit 5

  # 自動確認（用於自動化腳本）
  uv run embeddings -y

  # 僅顯示統計信息
  uv run embeddings --stats
        """
    )

    parser.add_argument(
        "--provider",
        choices=["gemini", "ollama"],
        default="gemini",
        help="嵌入提供者 (默認: gemini)"
    )

    parser.add_argument(
        "--kb-root",
        default="knowledge_base",
        help="知識庫根目錄 (默認: knowledge_base)"
    )

    parser.add_argument(
        "--chroma-path",
        default="chroma_db",
        help="ChromaDB 持久化路徑 (默認: chroma_db)"
    )

    parser.add_argument(
        "--papers-only",
        action="store_true",
        help="僅處理論文"
    )

    parser.add_argument(
        "--zettel-only",
        action="store_true",
        help="僅處理 Zettelkasten 卡片"
    )

    parser.add_argument(
        "--limit",
        type=int,
        help="處理數量限制（用於測試）"
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="僅顯示統計信息"
    )

    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="自動確認所有提示（用於自動化）"
    )

    args = parser.parse_args()

    # 初始化生成器
    print("=" * 70)
    print("知識庫嵌入向量生成器")
    print("=" * 70)

    generator = EmbeddingGenerator(
        kb_root=args.kb_root,
        provider=args.provider,
        chroma_path=args.chroma_path,
        auto_confirm=args.yes
    )

    # 僅顯示統計
    if args.stats:
        generator.get_stats()
        return

    # 處理論文
    papers_success, papers_fail = 0, 0
    if not args.zettel_only:
        papers_success, papers_fail = generator.generate_paper_embeddings(args.limit)

    # 處理 Zettelkasten
    zettel_success, zettel_fail = 0, 0
    if not args.papers_only:
        zettel_success, zettel_fail = generator.generate_zettel_embeddings(args.limit)

    # 總結
    print("\n" + "=" * 70)
    print("✅ 處理完成")
    print("=" * 70)

    total_success = papers_success + zettel_success
    total_fail = papers_fail + zettel_fail

    print(f"論文: {papers_success} 成功, {papers_fail} 失敗")
    print(f"Zettelkasten: {zettel_success} 成功, {zettel_fail} 失敗")
    print(f"總計: {total_success} 成功, {total_fail} 失敗")

    # 顯示統計
    generator.get_stats()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  用戶中斷")
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
        import traceback
        traceback.print_exc()
