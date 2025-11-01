"""
EmbeddingManager - 統一的嵌入管理器
提供高層次 API 簡化向量搜索操作
"""

import numpy as np
from typing import Dict, List, Optional, Union
from pathlib import Path
import sys

# 添加專案根目錄到路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.embeddings.providers import GeminiEmbedder, OllamaEmbedder
from src.embeddings.vector_db import VectorDatabase
from src.knowledge_base.kb_manager import KnowledgeBaseManager
from src.knowledge_base.auto_link import auto_link_v2, auto_link_all_papers


class EmbeddingManager:
    """統一的嵌入管理器

    提供簡化的 API 用於：
    - 生成嵌入
    - 語義搜索
    - 相似度查找
    - 自動連結
    """

    def __init__(
        self,
        kb_root: str = "knowledge_base",
        provider: str = "gemini",
        chroma_db_path: str = "chroma_db"
    ):
        """
        初始化嵌入管理器

        Args:
            kb_root: 知識庫根目錄
            provider: 嵌入提供者（gemini 或 ollama）
            chroma_db_path: ChromaDB 持久化目錄
        """
        self.kb_root = kb_root
        self.provider = provider
        self.chroma_db_path = chroma_db_path

        # 初始化組件
        self.kb = KnowledgeBaseManager(kb_root=kb_root)
        self.embedder = self._init_embedder(provider)
        self.vector_db = VectorDatabase(persist_directory=chroma_db_path)

    def _init_embedder(self, provider: str):
        """初始化嵌入提供者"""
        if provider.lower() == "gemini":
            return GeminiEmbedder()
        elif provider.lower() == "ollama":
            return OllamaEmbedder()
        else:
            raise ValueError(f"不支援的提供者: {provider}。請使用 'gemini' 或 'ollama'。")

    # ========== 嵌入生成 ==========

    def generate_for_paper(
        self,
        paper_id: int,
        force_regenerate: bool = False
    ) -> Dict:
        """為單篇論文生成嵌入

        Args:
            paper_id: 論文 ID
            force_regenerate: 是否強制重新生成（默認：False）

        Returns:
            {
                'paper_id': int,
                'vector_id': str,
                'generated': bool,
                'message': str
            }
        """
        vector_id = f"paper_{paper_id}"

        # 檢查是否已存在
        if not force_regenerate:
            existing = self.vector_db.get_paper_by_id(vector_id)
            if existing:
                return {
                    'paper_id': paper_id,
                    'vector_id': vector_id,
                    'generated': False,
                    'message': '向量已存在，跳過生成'
                }

        # 從知識庫獲取論文
        paper = self.kb.get_paper_by_id(paper_id)
        if not paper:
            raise ValueError(f"論文 ID {paper_id} 不存在")

        # 組合文本
        text_parts = []
        if paper.get('title'):
            text_parts.append(f"標題: {paper['title']}")
        if paper.get('authors'):
            authors_str = ', '.join(paper['authors']) if isinstance(paper['authors'], list) else paper['authors']
            text_parts.append(f"作者: {authors_str}")
        if paper.get('abstract'):
            text_parts.append(f"摘要: {paper['abstract']}")
        if paper.get('keywords'):
            keywords_str = ', '.join(paper['keywords']) if isinstance(paper['keywords'], list) else paper['keywords']
            text_parts.append(f"關鍵詞: {keywords_str}")

        combined_text = "\n".join(text_parts)

        # 生成嵌入
        embedding = self.embedder.embed(combined_text, task_type="retrieval_document")

        # 準備元數據
        metadata = {
            'paper_id': paper_id,
            'title': paper.get('title', ''),
            'authors': ', '.join(paper['authors']) if isinstance(paper['authors'], list) else paper.get('authors', ''),
            'year': paper.get('year', 0) or 0,
            'type': 'paper'
        }

        # 保存到向量數據庫
        self.vector_db.upsert_papers(
            embeddings=[embedding],
            documents=[combined_text],
            ids=[vector_id],
            metadatas=[metadata]
        )

        return {
            'paper_id': paper_id,
            'vector_id': vector_id,
            'generated': True,
            'message': '成功生成並保存向量'
        }

    def generate_for_zettel(
        self,
        card_id: int,
        force_regenerate: bool = False
    ) -> Dict:
        """為單張 Zettelkasten 卡片生成嵌入

        Args:
            card_id: 卡片 ID
            force_regenerate: 是否強制重新生成

        Returns:
            生成結果字典
        """
        # 從知識庫獲取卡片
        import sqlite3
        conn = sqlite3.connect(self.kb.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT zettel_id, title, content, core_concept, description, card_type, domain
            FROM zettel_cards
            WHERE card_id = ?
        """, (card_id,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            raise ValueError(f"卡片 ID {card_id} 不存在")

        zettel_id, title, content, core_concept, description, card_type, domain = result
        vector_id = f"zettel_{zettel_id}"

        # 檢查是否已存在
        if not force_regenerate:
            existing = self.vector_db.get_zettel_by_id(vector_id)
            if existing:
                return {
                    'card_id': card_id,
                    'vector_id': vector_id,
                    'generated': False,
                    'message': '向量已存在，跳過生成'
                }

        # 組合文本
        text_parts = []
        if title:
            text_parts.append(f"標題: {title}")
        if core_concept:
            text_parts.append(f"核心概念: {core_concept}")
        if description:
            text_parts.append(f"描述: {description}")
        if content:
            text_parts.append(f"內容: {content[:1500]}")  # 限制長度

        combined_text = "\n".join(text_parts)

        # 生成嵌入
        embedding = self.embedder.embed(combined_text, task_type="retrieval_document")

        # 準備元數據
        metadata = {
            'card_id': card_id,
            'zettel_id': zettel_id,
            'title': title or '',
            'core_concept': core_concept or '',
            'card_type': card_type or 'concept',
            'domain': domain,
            'type': 'zettel'
        }

        # 保存到向量數據庫
        self.vector_db.upsert_zettel(
            embeddings=[embedding],
            documents=[combined_text],
            ids=[vector_id],
            metadatas=[metadata]
        )

        return {
            'card_id': card_id,
            'vector_id': vector_id,
            'generated': True,
            'message': '成功生成並保存向量'
        }

    # ========== 搜索功能 ==========

    def search(
        self,
        query: str,
        type: str = "all",
        limit: int = 10,
        return_embeddings: bool = False
    ) -> Dict:
        """統一的語義搜索接口

        Args:
            query: 搜索查詢
            type: 搜索類型（papers / zettel / all）
            limit: 返回數量
            return_embeddings: 是否返回向量（默認：False）

        Returns:
            {
                'query': str,
                'type': str,
                'papers': List[Dict],
                'zettel': List[Dict]
            }
        """
        # 生成查詢向量
        query_embedding = self.embedder.embed(query, task_type="retrieval_query")

        results = {
            'query': query,
            'type': type,
            'papers': [],
            'zettel': []
        }

        # 搜索論文
        if type in ['papers', 'all']:
            paper_results = self.vector_db.semantic_search_papers(
                query_embedding=query_embedding,
                n_results=limit
            )

            if paper_results and paper_results['ids'] and len(paper_results['ids'][0]) > 0:
                for i, (pid, distance, metadata) in enumerate(zip(
                    paper_results['ids'][0],
                    paper_results['distances'][0],
                    paper_results['metadatas'][0]
                )):
                    paper_id = int(pid.replace('paper_', ''))
                    similarity = 1.0 - distance

                    result_item = {
                        'rank': i + 1,
                        'paper_id': paper_id,
                        'similarity': similarity,
                        'title': metadata.get('title', ''),
                        'authors': metadata.get('authors', ''),
                        'year': metadata.get('year', 0)
                    }

                    if return_embeddings:
                        result_item['embedding'] = paper_results['embeddings'][0][i]

                    results['papers'].append(result_item)

        # 搜索 Zettelkasten
        if type in ['zettel', 'all']:
            zettel_results = self.vector_db.semantic_search_zettel(
                query_embedding=query_embedding,
                n_results=limit
            )

            if zettel_results and zettel_results['ids'] and len(zettel_results['ids'][0]) > 0:
                for i, (zid, distance, metadata) in enumerate(zip(
                    zettel_results['ids'][0],
                    zettel_results['distances'][0],
                    zettel_results['metadatas'][0]
                )):
                    similarity = 1.0 - distance

                    result_item = {
                        'rank': i + 1,
                        'zettel_id': zid,
                        'similarity': similarity,
                        'title': metadata.get('title', ''),
                        'core_concept': metadata.get('core_concept', ''),
                        'card_type': metadata.get('card_type', ''),
                        'domain': metadata.get('domain', '')
                    }

                    if return_embeddings:
                        result_item['embedding'] = zettel_results['embeddings'][0][i]

                    results['zettel'].append(result_item)

        return results

    def find_similar(
        self,
        id: Union[int, str],
        limit: int = 10,
        exclude_self: bool = True
    ) -> List[Dict]:
        """統一的相似度查找接口

        Args:
            id: 論文 ID（整數）或 Zettelkasten ID（字串）
            limit: 返回數量
            exclude_self: 是否排除自身

        Returns:
            相似結果列表
        """
        # 判斷類型
        if isinstance(id, int):
            # 論文 ID
            vector_id = f"paper_{id}"
            results = self.vector_db.find_similar_papers(
                paper_id=vector_id,
                n_results=limit,
                exclude_self=exclude_self
            )

            similar_items = []
            if results and results['ids'] and len(results['ids'][0]) > 0:
                for pid, distance, metadata in zip(
                    results['ids'][0],
                    results['distances'][0],
                    results['metadatas'][0]
                ):
                    paper_id = int(pid.replace('paper_', ''))
                    similarity = 1.0 - distance

                    similar_items.append({
                        'type': 'paper',
                        'paper_id': paper_id,
                        'similarity': similarity,
                        'title': metadata.get('title', ''),
                        'authors': metadata.get('authors', ''),
                        'year': metadata.get('year', 0)
                    })

            return similar_items

        else:
            # Zettelkasten ID
            if not id.startswith('zettel_'):
                vector_id = f"zettel_{id}"
            else:
                vector_id = id

            results = self.vector_db.find_similar_zettel(
                zettel_id=vector_id,
                n_results=limit,
                exclude_self=exclude_self
            )

            similar_items = []
            if results and results['ids'] and len(results['ids'][0]) > 0:
                for zid, distance, metadata in zip(
                    results['ids'][0],
                    results['distances'][0],
                    results['metadatas'][0]
                ):
                    similarity = 1.0 - distance

                    similar_items.append({
                        'type': 'zettel',
                        'zettel_id': zid,
                        'similarity': similarity,
                        'title': metadata.get('title', ''),
                        'core_concept': metadata.get('core_concept', ''),
                        'card_type': metadata.get('card_type', ''),
                        'domain': metadata.get('domain', '')
                    })

            return similar_items

    # ========== 自動連結 ==========

    def auto_link_papers_to_zettel(
        self,
        paper_id: Optional[int] = None,
        threshold: float = 0.6,
        max_links: int = 5,
        batch_mode: bool = False,
        verbose: bool = False
    ) -> Dict:
        """自動建立論文-Zettelkasten 連結（基於向量相似度）

        Args:
            paper_id: 論文 ID（None 表示處理所有論文）
            threshold: 相似度閾值（0-1）
            max_links: 每篇論文最多建立幾個連結
            batch_mode: 是否批次模式（處理所有論文）
            verbose: 是否顯示詳細進度

        Returns:
            單篇模式: auto_link_v2() 的返回結果
            批次模式: auto_link_all_papers() 的返回結果
        """
        if batch_mode or paper_id is None:
            return auto_link_all_papers(
                threshold=threshold,
                max_links=max_links,
                kb_root=self.kb_root,
                chroma_db_path=self.chroma_db_path,
                verbose=verbose
            )
        else:
            return auto_link_v2(
                paper_id=paper_id,
                threshold=threshold,
                max_links=max_links,
                kb_root=self.kb_root,
                chroma_db_path=self.chroma_db_path
            )

    def get_paper_links(
        self,
        paper_id: int,
        min_similarity: float = 0.0
    ) -> List[Dict]:
        """獲取論文的 Zettelkasten 連結

        Args:
            paper_id: 論文 ID
            min_similarity: 最小相似度過濾

        Returns:
            連結列表
        """
        return self.kb.get_paper_zettel_links(paper_id, min_similarity)

    def get_zettel_links(
        self,
        card_id: int,
        min_similarity: float = 0.0
    ) -> List[Dict]:
        """獲取 Zettelkasten 卡片的論文連結

        Args:
            card_id: 卡片 ID
            min_similarity: 最小相似度過濾

        Returns:
            連結列表
        """
        return self.kb.get_zettel_paper_links(card_id, min_similarity)

    # ========== 統計與管理 ==========

    def get_stats(self) -> Dict:
        """獲取系統統計信息

        Returns:
            {
                'kb_stats': Dict,
                'vector_stats': Dict
            }
        """
        return {
            'kb_stats': self.kb.get_stats(),
            'vector_stats': self.vector_db.get_stats()
        }

    def switch_provider(self, provider: str):
        """切換嵌入提供者

        Args:
            provider: 新的提供者（gemini 或 ollama）
        """
        self.provider = provider
        self.embedder = self._init_embedder(provider)


# ========== 便利函數 ==========

def create_manager(
    provider: str = "gemini",
    kb_root: str = "knowledge_base",
    chroma_db_path: str = "chroma_db"
) -> EmbeddingManager:
    """創建 EmbeddingManager 實例的便利函數

    Args:
        provider: 嵌入提供者
        kb_root: 知識庫根目錄
        chroma_db_path: ChromaDB 目錄

    Returns:
        EmbeddingManager 實例
    """
    return EmbeddingManager(
        kb_root=kb_root,
        provider=provider,
        chroma_db_path=chroma_db_path
    )


if __name__ == "__main__":
    """測試 EmbeddingManager"""
    import argparse
    import io

    # 設置 UTF-8 編碼（Windows 相容性）
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

    parser = argparse.ArgumentParser(description="EmbeddingManager 測試工具")
    parser.add_argument("--search", type=str, help="測試搜索功能")
    parser.add_argument("--similar", type=str, help="測試相似度查找（論文ID或Zettel ID）")
    parser.add_argument("--stats", action="store_true", help="顯示統計信息")
    parser.add_argument("--provider", choices=['gemini', 'ollama'], default='gemini', help="提供者")

    args = parser.parse_args()

    # 創建管理器
    manager = create_manager(provider=args.provider)

    if args.stats:
        print("\n" + "=" * 60)
        print("📊 系統統計")
        print("=" * 60)
        stats = manager.get_stats()
        print(f"\n知識庫統計:")
        for key, value in stats['kb_stats'].items():
            print(f"  {key}: {value}")
        print(f"\n向量數據庫統計:")
        for key, value in stats['vector_stats'].items():
            print(f"  {key}: {value}")
        print("\n" + "=" * 60)

    elif args.search:
        print("\n" + "=" * 60)
        print(f"🔍 搜索: '{args.search}'")
        print("=" * 60)
        results = manager.search(args.search, type="all", limit=5)

        if results['papers']:
            print(f"\n📄 論文結果 ({len(results['papers'])}篇):")
            for item in results['papers']:
                print(f"  {item['rank']}. [{item['similarity']:.1%}] {item['title']}")

        if results['zettel']:
            print(f"\n🗂️  Zettelkasten 結果 ({len(results['zettel'])}張):")
            for item in results['zettel']:
                print(f"  {item['rank']}. [{item['similarity']:.1%}] {item['title']}")

        print("\n" + "=" * 60)

    elif args.similar:
        # 判斷是論文 ID 還是 Zettel ID
        try:
            id_val = int(args.similar)
            type_str = "論文"
        except:
            id_val = args.similar
            type_str = "Zettelkasten"

        print("\n" + "=" * 60)
        print(f"🔍 尋找與 {type_str} '{id_val}' 相似的內容")
        print("=" * 60)

        similar = manager.find_similar(id_val, limit=5)

        for i, item in enumerate(similar, 1):
            if item['type'] == 'paper':
                print(f"{i}. [{item['similarity']:.1%}] {item['title']}")
                print(f"   類型: 論文 | ID: {item['paper_id']}")
            else:
                print(f"{i}. [{item['similarity']:.1%}] {item['title']}")
                print(f"   類型: Zettelkasten | ID: {item['zettel_id']}")

        print("\n" + "=" * 60)

    else:
        parser.print_help()
