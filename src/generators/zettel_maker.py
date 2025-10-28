"""
Zettelkasten原子筆記生成器
支援語義化ID、概念連結網絡、Markdown輸出
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict

try:
    from jinja2 import Template
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class ZettelMaker:
    """
    Zettelkasten原子筆記生成器
    基於文獻內容生成原子化知識卡片
    """

    def __init__(self,
                 card_template_path: Optional[str] = None,
                 index_template_path: Optional[str] = None,
                 styles_config: Optional[str] = None):
        """
        初始化Zettelkasten生成器

        Args:
            card_template_path: 卡片模板路徑
            index_template_path: 索引模板路徑
            styles_config: 風格配置路徑
        """
        if not JINJA2_AVAILABLE:
            raise ImportError("Jinja2 not installed. Run: pip install jinja2")

        if not YAML_AVAILABLE:
            raise ImportError("PyYAML not installed. Run: pip install pyyaml")

        # 載入卡片模板
        if card_template_path is None:
            card_template_path = Path(__file__).parent.parent.parent / "templates" / "markdown" / "zettelkasten_card.jinja2"

        with open(card_template_path, 'r', encoding='utf-8') as f:
            self.card_template = Template(f.read())

        # 載入索引模板
        if index_template_path is None:
            index_template_path = Path(__file__).parent.parent.parent / "templates" / "markdown" / "zettelkasten_index.jinja2"

        with open(index_template_path, 'r', encoding='utf-8') as f:
            self.index_template = Template(f.read())

        # 載入風格配置
        if styles_config is None:
            styles_config = Path(__file__).parent.parent.parent / "templates" / "styles" / "academic_styles.yaml"

        with open(styles_config, 'r', encoding='utf-8') as f:
            self.styles_config = yaml.safe_load(f)

        self.zettel_config = self.styles_config['styles']['zettelkasten']

    def generate_card_id(self, domain: str, sequence: int, date: Optional[str] = None) -> str:
        """
        生成語義化卡片ID

        Args:
            domain: 領域代碼（如 NeuroPsy, AI, CompBio）
            sequence: 序號
            date: 日期（YYYYMMDD），默認今天

        Returns:
            格式化ID（如 NeuroPsy-20251028-001）
        """
        if date is None:
            date = datetime.now().strftime("%Y%m%d")

        return f"{domain}-{date}-{sequence:03d}"

    def parse_llm_output(self, llm_output: str) -> List[Dict[str, Any]]:
        """
        解析LLM生成的Zettelkasten卡片內容

        期望格式：
        ===CARD: {card_id}===
        標題: {title}
        類型: {concept|method|finding|question}
        核心: {one_sentence}
        標籤: {tag1}, {tag2}

        說明:
        {detailed_explanation}

        連結:
        基於 -> {card_id1}, {card_id2}
        導向 -> {card_id3}
        相關 <-> {card_id4}
        對比 <-> {card_id5}

        個人筆記:
        {notes}

        待解問題:
        {questions}
        ===

        Args:
            llm_output: LLM生成的文本

        Returns:
            卡片數據列表
        """
        # 使用正則分割卡片
        card_pattern = r'===CARD:\s*([^=]+)==='
        parts = re.split(card_pattern, llm_output)

        cards = []

        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                card_id = parts[i].strip()
                card_content = parts[i + 1].strip()

                card_data = self._parse_single_card(card_id, card_content)
                if card_data:
                    cards.append(card_data)

        return cards

    def _parse_single_card(self, card_id: str, content: str) -> Optional[Dict[str, Any]]:
        """解析單張卡片內容"""
        card = {
            'id': card_id,
            'title': '',
            'card_type': 'concept',
            'core_summary': '',
            'tags': [],
            'detailed_explanation': '',
            'foundation_links': [],
            'derived_links': [],
            'related_links': [],
            'contrast_links': [],
            'personal_notes': '',
            'open_questions': ''
        }

        # 解析欄位
        lines = content.split('\n')
        current_section = None
        section_content = []

        for line in lines:
            line_stripped = line.strip()

            # 識別欄位
            if line_stripped.startswith('標題:') or line_stripped.startswith('Title:'):
                card['title'] = line_stripped.split(':', 1)[1].strip()
            elif line_stripped.startswith('類型:') or line_stripped.startswith('Type:'):
                card['card_type'] = line_stripped.split(':', 1)[1].strip()
            elif line_stripped.startswith('核心:') or line_stripped.startswith('Core:'):
                card['core_summary'] = line_stripped.split(':', 1)[1].strip()
            elif line_stripped.startswith('標籤:') or line_stripped.startswith('Tags:'):
                tags_str = line_stripped.split(':', 1)[1].strip()
                card['tags'] = [t.strip() for t in tags_str.split(',')]

            # 識別章節
            elif line_stripped in ['說明:', 'Explanation:', '說明：']:
                current_section = 'explanation'
                section_content = []
            elif line_stripped in ['連結:', 'Links:', '連結：']:
                current_section = 'links'
                section_content = []
            elif line_stripped in ['個人筆記:', 'Personal Notes:', '個人筆記：']:
                current_section = 'notes'
                section_content = []
            elif line_stripped in ['待解問題:', 'Open Questions:', '待解問題：']:
                current_section = 'questions'
                section_content = []

            # 收集章節內容
            elif current_section:
                if current_section == 'links':
                    self._parse_link_line(line_stripped, card)
                else:
                    section_content.append(line)

            # 保存章節內容
            if current_section and (not line_stripped or line_stripped.startswith('===')):
                if current_section == 'explanation':
                    card['detailed_explanation'] = '\n'.join(section_content).strip()
                elif current_section == 'notes':
                    card['personal_notes'] = '\n'.join(section_content).strip()
                elif current_section == 'questions':
                    card['open_questions'] = '\n'.join(section_content).strip()
                section_content = []

        return card if card['title'] else None

    def _parse_link_line(self, line: str, card: Dict[str, Any]):
        """解析連結行"""
        if '基於' in line or 'foundation' in line.lower():
            links = self._extract_links(line)
            card['foundation_links'].extend(links)
        elif '導向' in line or 'derived' in line.lower():
            links = self._extract_links(line)
            card['derived_links'].extend(links)
        elif '相關' in line or 'related' in line.lower():
            links = self._extract_links(line)
            card['related_links'].extend(links)
        elif '對比' in line or 'contrast' in line.lower():
            links = self._extract_links(line)
            card['contrast_links'].extend(links)

    def _extract_links(self, line: str) -> List[str]:
        """從行中提取連結ID"""
        # 移除箭頭和符號
        line = re.sub(r'[→←↔⚡⬆⬇\-><]', '', line)
        # 分割並清理
        parts = line.split(',')
        links = []
        for part in parts:
            # 移除欄位名稱
            part = re.sub(r'(基於|導向|相關|對比|foundation|derived|related|contrast)', '', part, flags=re.IGNORECASE)
            part = part.strip()
            if part and not part.endswith(':'):
                # 修復格式：將 XXX20251028001 轉換為 XXX-20251028-001
                # 檢測沒有破折號的ID格式（如 CogSci20251028001）
                match = re.match(r'^([A-Za-z]+)(\d{8})(\d{3})$', part)
                if match:
                    domain, date, seq = match.groups()
                    part = f"{domain}-{date}-{seq}"
                links.append(part)
        return links

    def create_card_file(self,
                        card_data: Dict[str, Any],
                        output_dir: Path,
                        paper_info: Dict[str, str]) -> str:
        """
        創建單張卡片Markdown文件

        Args:
            card_data: 卡片數據
            output_dir: 輸出目錄
            paper_info: 論文信息（title, authors, year, citation等）

        Returns:
            輸出文件路徑
        """
        # 合併論文信息
        render_data = {
            **card_data,
            'paper_title': paper_info.get('title', ''),
            'year': paper_info.get('year', ''),
            'paper_id': paper_info.get('paper_id', ''),
            'citation': paper_info.get('citation', ''),
            'created_date': datetime.now().strftime("%Y-%m-%d"),
            'section': paper_info.get('section', ''),
            'page_number': paper_info.get('page', ''),
            'context': paper_info.get('context', ''),
            'confidence': paper_info.get('confidence', '')
        }

        # 渲染模板
        markdown_content = self.card_template.render(**render_data)

        # 保存文件
        output_path = output_dir / f"{card_data['id']}.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return str(output_path)

    def create_index_file(self,
                         cards: List[Dict[str, Any]],
                         output_path: Path,
                         paper_info: Dict[str, str]) -> str:
        """
        創建卡片索引文件

        Args:
            cards: 所有卡片數據
            output_path: 輸出路徑
            paper_info: 論文信息

        Returns:
            輸出文件路徑
        """
        # 按標籤分組
        cards_by_tag = defaultdict(list)
        for card in cards:
            for tag in card['tags']:
                cards_by_tag[tag].append(card)

        # 建議閱讀順序（基於連結關係的拓撲排序簡化版）
        reading_order = self._suggest_reading_order(cards)

        # 渲染模板
        markdown_content = self.index_template.render(
            paper_title=paper_info.get('title', ''),
            authors=paper_info.get('authors', ''),
            year=paper_info.get('year', ''),
            generated_date=datetime.now().strftime("%Y-%m-%d %H:%M"),
            card_count=len(cards),
            cards=cards,
            cards_by_tag=dict(cards_by_tag),
            reading_order=reading_order
        )

        # 保存文件
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

        return str(output_path)

    def _suggest_reading_order(self, cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """建議閱讀順序（簡化的拓撲排序）"""
        # 計算每張卡片的依賴數（被多少卡片依賴）
        dependency_count = {card['id']: 0 for card in cards}
        card_map = {card['id']: card for card in cards}

        for card in cards:
            for linked_id in card.get('foundation_links', []):
                if linked_id in dependency_count:
                    dependency_count[linked_id] += 1

        # 按依賴數排序（依賴少的先讀）
        sorted_cards = sorted(cards, key=lambda c: dependency_count[c['id']])

        return sorted_cards

    def generate_zettelkasten(self,
                             llm_output: str,
                             output_dir: Path,
                             paper_info: Dict[str, str]) -> Dict[str, Any]:
        """
        完整生成Zettelkasten卡片集

        Args:
            llm_output: LLM生成的內容
            output_dir: 輸出目錄
            paper_info: 論文信息

        Returns:
            生成結果
        """
        # 1. 解析卡片
        cards = self.parse_llm_output(llm_output)

        if not cards:
            raise ValueError("無法解析任何卡片，請檢查LLM輸出格式")

        # 2. 創建卡片目錄
        cards_dir = output_dir / "zettel_cards"
        cards_dir.mkdir(parents=True, exist_ok=True)

        # 3. 生成獨立卡片文件
        card_files = []
        for card in cards:
            card_path = self.create_card_file(card, cards_dir, paper_info)
            card_files.append(card_path)

        # 4. 生成索引文件
        index_path = output_dir / "zettel_index.md"
        index_file = self.create_index_file(cards, index_path, paper_info)

        return {
            'success': True,
            'card_count': len(cards),
            'card_files': card_files,
            'index_file': index_file,
            'output_dir': str(output_dir)
        }


if __name__ == "__main__":
    # 測試代碼
    print("Zettelkasten Maker 模組已載入")
    print("用法: from src.generators import ZettelMaker")
