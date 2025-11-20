#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zettelkasten 格式修復工具

基於用戶手動調整模式，自動修復 LLM 生成的 Zettelkasten 卡片格式問題。

核心修復規則（基於 Barsalou-2009 卡片分析）：
1. fix_summary_field(): 清理 summary（<100 字元，移除 Markdown）
2. fix_link_format(): 修復連結（AuthorYearNumber → Author-Year-Number）
3. remove_redundant_sections(): 移除冗餘 H1 和「核心」區塊
4. normalize_spacing(): 標準化空行（frontmatter 後 1 行，區段間 2 行）

作者: Claude Code
日期: 2025-11-05
版本: 1.0.0
"""

import re
import sys
import io
from pathlib import Path
from typing import List, Dict, Tuple
import argparse

# Windows 編碼修復
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class ZettelFormatFixer:
    """Zettelkasten 卡片格式修復器"""

    def __init__(self, dry_run: bool = False):
        """
        初始化修復器

        Args:
            dry_run: 是否為 dry-run 模式（僅預覽變更，不實際修改）
        """
        self.dry_run = dry_run
        self.stats = {
            'total': 0,
            'fixed': 0,
            'skipped': 0,
            'errors': 0,
            'fixes': {
                'summary': 0,
                'links': 0,
                'redundant_h1': 0,
                'redundant_core': 0,
                'spacing': 0
            }
        }

    def fix_card(self, card_path: Path, index_data: Dict[str, str] = None) -> Tuple[bool, List[str]]:
        """
        修復單張卡片

        Args:
            card_path: 卡片文件路徑
            index_data: zettel_index.md 中的卡片核心資料（預先解析以提高效率）

        Returns:
            (是否成功, 修復變更列表)
        """
        try:
            # 讀取卡片內容
            content = card_path.read_text(encoding='utf-8')
            original_content = content
            changes = []

            # 分離 frontmatter 和正文
            frontmatter, body = self._split_frontmatter(content)
            if not frontmatter:
                return False, ["無法解析 frontmatter"]

            # 如果沒有提供 index_data，從 zettel_index.md 讀取
            if index_data is None:
                index_data = self._parse_zettel_index(card_path)

            # 規則 1: 修復 summary（從 zettel_index.md 的「核心」提取）
            frontmatter_fixed, summary_changes = self.fix_summary_field(card_path, frontmatter, index_data)
            if summary_changes:
                changes.extend(summary_changes)
                frontmatter = frontmatter_fixed

            # 規則 2: 修復連結格式
            body_fixed, link_changes = self.fix_link_format(body)
            if link_changes:
                changes.extend(link_changes)
                body = body_fixed

            # 規則 3: 移除冗餘區塊
            body_fixed, redundant_changes = self.remove_redundant_sections(body)
            if redundant_changes:
                changes.extend(redundant_changes)
                body = body_fixed

            # 規則 4: 標準化空行
            content_fixed, spacing_changes = self.normalize_spacing(frontmatter, body)
            if spacing_changes:
                changes.extend(spacing_changes)

            # 如果有變更
            if changes:
                self.stats['fixed'] += 1

                # 如果不是 dry-run，寫入文件
                if not self.dry_run:
                    card_path.write_text(content_fixed, encoding='utf-8')

                return True, changes
            else:
                self.stats['skipped'] += 1
                return True, []

        except Exception as e:
            self.stats['errors'] += 1
            return False, [f"錯誤: {str(e)}"]

    def _parse_zettel_index(self, card_path: Path) -> Dict[str, str]:
        """
        解析 zettel_index.md 以提取所有卡片的「核心」內容

        Args:
            card_path: 卡片文件路徑（用於找到對應的 zettel_index.md）

        Returns:
            {card_id: core_content} 字典
        """
        # 找到上層資料夾的 zettel_index.md
        zettel_folder = card_path.parent.parent
        index_path = zettel_folder / "zettel_index.md"

        if not index_path.exists():
            return {}

        try:
            content = index_path.read_text(encoding='utf-8')
            index_data = {}

            # 正則表達式：匹配每張卡片的資訊
            # 格式：### N. [標題](zettel_cards/Card-ID.md)
            #       - **ID**: `Card-ID`
            #       - **核心**: [核心內容] 或 "核心內容" 或 核心內容
            # 支援三種格式：方括號 [...] | 引號 "..." | 無標記（到行尾）
            # 注意：第三種格式使用 [^\n]+ 避免在 re.DOTALL 模式下捕獲過多內容
            pattern = r'###\s+\d+\.\s+\[.*?\]\(zettel_cards/([\w-]+)\.md\)\n.*?\n.*?-\s+\*\*核心\*\*:\s+(?:\[(.*?)\]|"(.*?)"|([^\n]+))\n'

            matches = re.findall(pattern, content, re.DOTALL)

            for match in matches:
                card_id = match[0]
                # match[1] 是方括號內容，match[2] 是引號內容，match[3] 是純文字
                core_content = match[1] if match[1] else (match[2] if match[2] else match[3])

                # 清理核心內容（移除多餘空白）
                core_content = ' '.join(core_content.split())
                index_data[card_id] = core_content

            return index_data

        except Exception as e:
            print(f"⚠️ 警告: 無法解析 zettel_index.md: {e}")
            return {}

    def _split_frontmatter(self, content: str) -> Tuple[str, str]:
        """
        分離 frontmatter 和正文

        Returns:
            (frontmatter, body)
        """
        # 匹配 YAML frontmatter
        pattern = r'^---\n(.*?)\n---\n(.*)$'
        match = re.match(pattern, content, re.DOTALL)

        if not match:
            return "", ""

        frontmatter = match.group(1)
        body = match.group(2)

        return frontmatter, body

    def fix_summary_field(self, card_path: Path, frontmatter: str, index_data: Dict[str, str]) -> Tuple[str, List[str]]:
        """
        規則 1: 修復 summary 欄位（從 zettel_index.md 的「核心」提取）

        用戶反饋：summary 必須與 zettel_index.md 中對應卡片的「核心」一致
        這是 Zettelkasten 系統的設計：index 是單一真相來源

        Args:
            card_path: 卡片路徑（用於提取 card_id）
            frontmatter: frontmatter 內容
            index_data: zettel_index.md 中的 {card_id: core_content} 字典

        Returns:
            (修復後的 frontmatter, 變更列表)
        """
        changes = []

        # 從文件名提取 card_id（例如 "Barsalou-2009-005"）
        card_id = card_path.stem

        # 從 index_data 中查找對應的核心內容
        if card_id not in index_data:
            # 如果找不到，返回原始 frontmatter（可能是 index_data 解析失敗）
            return frontmatter, []

        correct_summary = index_data[card_id]

        # 提取並替換 summary 行
        summary_pattern = r'^(summary:\s*"?)(.+?)("?)$'
        lines = frontmatter.split('\n')

        for i, line in enumerate(lines):
            match = re.match(summary_pattern, line, re.MULTILINE)
            if match:
                prefix = match.group(1)
                current_summary = match.group(2)
                suffix = match.group(3)

                # 檢查是否需要修復
                if current_summary != correct_summary:
                    # 替換為 zettel_index.md 中的核心內容
                    lines[i] = f'{prefix}{correct_summary}{suffix}'
                    changes.append(f"修復 summary: 同步 zettel_index.md 核心內容")
                    changes.append(f"  原: {current_summary[:50]}...")
                    changes.append(f"  新: {correct_summary[:50]}...")
                    self.stats['fixes']['summary'] += 1

                break

        return '\n'.join(lines), changes

    def fix_link_format(self, body: str) -> Tuple[str, List[str]]:
        """
        規則 2: 修復連結格式

        修復: [[AuthorYearNumber]] → [[Author-Year-Number]]
        例如: [[Barsalou2009002]] → [[Barsalou-2009-002]]
              [[Wu202010]] → [[Wu-2020-010]]

        Returns:
            (修復後的正文, 變更列表)
        """
        changes = []

        # 正則表達式: 匹配 [[AuthorYearNumber]] 格式
        # 捕獲群組: 1=Author, 2=Year(4位), 3=Number(2-3位)
        pattern = r'\[\[([A-Za-z]+)(\d{4})(\d{2,3})\]\]'

        # 查找所有匹配
        matches = list(re.finditer(pattern, body))

        if matches:
            # 替換函數：自動補零到 3 位數
            def fix_link(match):
                author = match.group(1)
                year = match.group(2)
                number = match.group(3).zfill(3)  # 補零到 3 位數
                return f"[[{author}-{year}-{number}]]"

            fixed_body = re.sub(pattern, fix_link, body)

            # 記錄變更
            unique_fixes = set()
            for match in matches:
                old_format = match.group(0)
                number_fixed = match.group(3).zfill(3)
                new_format = f"[[{match.group(1)}-{match.group(2)}-{number_fixed}]]"
                unique_fixes.add((old_format, new_format))

            for old, new in unique_fixes:
                changes.append(f"修復連結格式: {old} → {new}")

            self.stats['fixes']['links'] += len(unique_fixes)

            return fixed_body, changes

        return body, changes

    def remove_redundant_sections(self, body: str) -> Tuple[str, List[str]]:
        """
        規則 3: 移除冗餘區塊

        - 移除冗餘 H1 標題（如「# 心理模擬...」）
        - 移除「> **核心**: ...」引用區塊

        Returns:
            (修復後的正文, 變更列表)
        """
        changes = []
        original_body = body

        # 移除 H1 標題（在第一個 ## 之前）
        h1_pattern = r'^#+\s+.+?\n'
        match = re.match(h1_pattern, body.lstrip(), re.MULTILINE)
        if match:
            h1_line = match.group(0).strip()
            body = re.sub(r'^#+\s+.+?\n+', '', body.lstrip(), count=1)
            changes.append(f"移除冗餘 H1: {h1_line[:50]}...")
            self.stats['fixes']['redundant_h1'] += 1

        # 移除「核心」引用區塊
        core_pattern = r'>\s*\*\*核心\*\*:\s*\[.+?\]\s*\n+'
        match = re.search(core_pattern, body)
        if match:
            core_text = match.group(0).strip()[:50]
            body = re.sub(core_pattern, '', body)
            changes.append(f"移除冗餘「核心」區塊: {core_text}...")
            self.stats['fixes']['redundant_core'] += 1

        return body, changes

    def normalize_spacing(self, frontmatter: str, body: str) -> Tuple[str, List[str]]:
        """
        規則 4: 標準化空行

        - frontmatter 後固定 1 個空行
        - 說明段落後: 1 個空行
        - ## 連結網絡後: 2 個空行
        - 連結項之間: 2 個空行
        - 最後連結項後: 3 個空行（在 ## 來源脈絡前）
        - 其他區段間: 2 個空行
        - 文件結尾保留 1 個空行

        Returns:
            (修復後的完整內容, 變更列表)
        """
        changes = []

        # 重組內容
        content = f"---\n{frontmatter}\n---\n"

        # frontmatter 後 1 個空行
        content += "\n"

        # 清理正文多餘空行
        body = body.strip()

        # 標準化區段間空行
        body_lines = body.split('\n')
        normalized_lines = []

        i = 0
        while i < len(body_lines):
            line = body_lines[i]

            # 檢查是否為區段標題
            if line.startswith('## '):
                # 如果不是第一個區段，前面加適當空行
                if normalized_lines:
                    # 移除前面的所有空行
                    while normalized_lines and normalized_lines[-1] == '':
                        normalized_lines.pop()

                    # 檢查前一個區段是否為「連結網絡」
                    is_after_link_section = False
                    for prev_line in reversed(normalized_lines):
                        if prev_line.startswith('## '):
                            if '連結網絡' in prev_line:
                                is_after_link_section = True
                            break

                    # 「## 來源脈絡」在「連結網絡」後需要 3 個空行，其他情況 2 個
                    if is_after_link_section and '來源' in line:
                        normalized_lines.extend(['', '', ''])
                    else:
                        normalized_lines.extend(['', ''])

                normalized_lines.append(line)
            else:
                normalized_lines.append(line)

            i += 1

        body = '\n'.join(normalized_lines)

        # 文件結尾保留 1 個空行
        content += body
        content = content.rstrip() + '\n'

        changes.append("標準化空行格式")
        self.stats['fixes']['spacing'] += 1

        return content, changes

    def process_batch(self, folder_path: Path, pattern: str = "*.md") -> Dict:
        """
        批次處理資料夾中的所有卡片

        Args:
            folder_path: 資料夾路徑
            pattern: 文件匹配模式

        Returns:
            處理統計信息
        """
        # 遞迴查找所有卡片
        card_files = list(folder_path.rglob(pattern))

        # 過濾掉索引文件
        card_files = [f for f in card_files if 'zettel_index' not in f.name]

        self.stats['total'] = len(card_files)

        print(f"\n🔍 找到 {len(card_files)} 張 Zettelkasten 卡片")
        print(f"{'[DRY-RUN] ' if self.dry_run else ''}開始處理...\n")

        # 按資料夾分組卡片（提高效率：每個資料夾只解析一次 zettel_index.md）
        cards_by_folder = {}
        for card_file in card_files:
            zettel_folder = card_file.parent.parent  # zettel_xxx_20251104
            if zettel_folder not in cards_by_folder:
                cards_by_folder[zettel_folder] = []
            cards_by_folder[zettel_folder].append(card_file)

        # 為每個資料夾處理卡片
        processed = 0
        for zettel_folder, cards in cards_by_folder.items():
            # 預先解析該資料夾的 zettel_index.md
            sample_card = cards[0]
            index_data = self._parse_zettel_index(sample_card)

            if not index_data:
                print(f"⚠️ 警告: 無法解析 {zettel_folder.name}/zettel_index.md，跳過 {len(cards)} 張卡片")
                self.stats['errors'] += len(cards)
                continue

            # 處理該資料夾的所有卡片
            for card_file in cards:
                processed += 1
                print(f"[{processed}/{len(card_files)}] 處理: {card_file.name}", end=' ')

                success, changes = self.fix_card(card_file, index_data)

                if success:
                    if changes:
                        print("✅ 已修復")
                        for change in changes:
                            print(f"    - {change}")
                    else:
                        print("⏭️  無需修復")
                else:
                    print("❌ 失敗")
                    for error in changes:
                        print(f"    ! {error}")

        return self.get_stats()

    def get_stats(self) -> Dict:
        """獲取統計信息"""
        return self.stats

    def print_summary(self):
        """打印處理摘要"""
        print("\n" + "=" * 60)
        print("📊 處理摘要")
        print("=" * 60)
        print(f"總卡片數: {self.stats['total']}")
        print(f"已修復: {self.stats['fixed']} ✅")
        print(f"無需修復: {self.stats['skipped']} ⏭️")
        print(f"失敗: {self.stats['errors']} ❌")
        print(f"\n修復詳情:")
        print(f"  - Summary 清理: {self.stats['fixes']['summary']}")
        print(f"  - 連結格式修復: {self.stats['fixes']['links']}")
        print(f"  - 移除冗餘 H1: {self.stats['fixes']['redundant_h1']}")
        print(f"  - 移除冗餘「核心」: {self.stats['fixes']['redundant_core']}")
        print(f"  - 空行標準化: {self.stats['fixes']['spacing']}")

        if self.dry_run:
            print("\n⚠️  DRY-RUN 模式: 未實際修改任何文件")
        else:
            print(f"\n✅ 已寫入 {self.stats['fixed']} 張卡片的修復")

    def fix_index_mermaid(self, index_path: Path) -> Tuple[bool, List[str]]:
        """
        修復 zettel_index.md 中 mermaid 圖表的連結格式錯誤

        問題範例（Wu-2020）:
        - Wu-2020-001 --> Wu2020002  # ❌ 目標節點缺少連字號
        - Wu2020001 --> Wu-2020-002  # ❌ 來源節點缺少連字號
        - Wu-2020-009 --> Wu202010   # ❌ 拼寫錯誤

        修復:
        - 統一為 Author-Year-Number 格式
        - 移除過多空行（3+ 個 → 1-2 個）
        - 移除重複連結

        Returns:
            (是否成功, 變更列表)
        """
        changes = []

        try:
            # 讀取 zettel_index.md
            content = index_path.read_text(encoding='utf-8')
            original_content = content

            # 找到 mermaid 圖表區域
            mermaid_pattern = r'```mermaid\n(.*?)\n```'
            mermaid_match = re.search(mermaid_pattern, content, re.DOTALL)

            if not mermaid_match:
                return False, ["⏭️ 無 mermaid 圖表"]

            mermaid_content = mermaid_match.group(1)
            original_mermaid = mermaid_content

            # 修復 1a: 修復節點 ID 格式（AuthorYearNumber → Author-Year-Number）
            # 匹配模式: Wu2020002 或 Wu202010 (缺少連字號)
            pattern1 = r'\b([A-Za-z]+)(\d{4})(\d{2,3})\b'

            def fix_node_id(match):
                author = match.group(1)
                year = match.group(2)
                number = match.group(3)

                # 補齊為三位數（Wu202010 → Wu-2020-010, Wu20209 → Wu-2020-009）
                number = number.zfill(3)

                return f"{author}-{year}-{number}"

            fixed_mermaid = re.sub(pattern1, fix_node_id, mermaid_content)

            # 修復 1b: 修正已有連字號但數字錯誤的節點 ID
            # 例如: Wu-2020-100 → Wu-2020-010 (之前錯誤修復的結果)
            pattern2 = r'\b([A-Za-z]+-\d{4}-)(1\d{2})\b'  # 匹配 100-199

            def fix_wrong_number(match):
                prefix = match.group(1)  # "Wu-2020-"
                wrong_number = match.group(2)  # "100"

                # 修復邏輯：之前錯誤地在右側補零，現在改為左側補零
                # "10" + "0" = "100" (錯誤) → "0" + "10" = "010" (正確)
                # 方法：移除最後的 '0'，加到前面
                if wrong_number[0] == '1' and wrong_number[2] == '0':
                    correct_number = '0' + wrong_number[:-1]  # "100" → "010"
                    return f"{prefix}{correct_number}"
                return match.group(0)  # 保持不變

            fixed_mermaid = re.sub(pattern2, fix_wrong_number, fixed_mermaid)

            # 修復 1c: 移除指向 "000" 的錯誤連結（因為沒有 000 卡片）
            # 這通常是數據錯誤產生的幻影連結
            pattern3 = r'^\s*.+ --> .+-000\s*$'
            lines_before_000_removal = fixed_mermaid.split('\n')
            lines_after_000_removal = [
                line for line in lines_before_000_removal
                if not re.match(pattern3, line)
            ]

            if len(lines_after_000_removal) < len(lines_before_000_removal):
                removed_000_count = len(lines_before_000_removal) - len(lines_after_000_removal)
                changes.append(f"移除 {removed_000_count} 個指向 '000' 的錯誤連結")
                fixed_mermaid = '\n'.join(lines_after_000_removal)

            if fixed_mermaid != mermaid_content:
                changes.append("修復 mermaid 節點 ID 格式")

            # 修復 2: 移除過多空行（3+ 個空行 → 2 個空行）
            fixed_mermaid = re.sub(r'\n{4,}', '\n\n', fixed_mermaid)

            if fixed_mermaid != mermaid_content and "修復 mermaid 節點 ID 格式" in changes:
                changes.append("標準化 mermaid 圖表空行")
            elif fixed_mermaid != mermaid_content:
                changes.append("標準化 mermaid 圖表空行")

            # 修復 3: 移除重複連結
            lines = fixed_mermaid.split('\n')
            seen_links = set()
            deduplicated_lines = []

            for line in lines:
                stripped = line.strip()
                # 檢查是否為連結行（mermaid 的 --> 或 -.-> 連結）
                is_link_line = ' --> ' in line or ' -.-> ' in line

                if is_link_line:
                    if stripped not in seen_links:
                        seen_links.add(stripped)
                        deduplicated_lines.append(line)
                    # 如果重複，跳過此行
                else:
                    # 非連結行，直接保留
                    deduplicated_lines.append(line)

            if len(deduplicated_lines) < len(lines):
                removed_count = len(lines) - len(deduplicated_lines)
                changes.append(f"移除 {removed_count} 個重複連結")

            fixed_mermaid = '\n'.join(deduplicated_lines)

            # 替換原始內容中的 mermaid 區域
            if fixed_mermaid != original_mermaid:
                content = content.replace(
                    f"```mermaid\n{original_mermaid}\n```",
                    f"```mermaid\n{fixed_mermaid}\n```"
                )

            # 寫入修復結果
            if content != original_content:
                if not self.dry_run:
                    index_path.write_text(content, encoding='utf-8')
                return True, changes
            else:
                return False, ["⏭️ 無需修復"]

        except Exception as e:
            return False, [f"❌ 錯誤: {str(e)}"]

    def batch_fix_indices(self, root_folder: Path) -> Dict:
        """
        批次修復所有 zettel_index.md 文件

        Args:
            root_folder: Zettelkasten 根目錄

        Returns:
            統計信息字典
        """
        stats = {
            'total': 0,
            'fixed': 0,
            'skipped': 0,
            'errors': 0
        }

        # 查找所有 zettel_index.md 文件
        index_files = list(root_folder.glob("*/zettel_index.md"))
        stats['total'] = len(index_files)

        print(f"🔍 找到 {stats['total']} 個 zettel_index.md 文件")
        print("開始修復 mermaid 圖表...\n")

        for i, index_file in enumerate(index_files, 1):
            folder_name = index_file.parent.name
            print(f"[{i}/{stats['total']}] 處理: {folder_name}", end=' ')

            success, changes = self.fix_index_mermaid(index_file)

            if success:
                stats['fixed'] += 1
                print("✅ 已修復")
                for change in changes:
                    print(f"    - {change}")
            elif changes and changes[0].startswith("⏭️"):
                stats['skipped'] += 1
                print(changes[0])
            else:
                stats['errors'] += 1
                print("❌ 失敗")
                for error in changes:
                    print(f"    ! {error}")

        # 打印摘要
        print("\n" + "=" * 60)
        print("📊 Mermaid 圖表修復摘要")
        print("=" * 60)
        print(f"總 index 文件數: {stats['total']}")
        print(f"已修復: {stats['fixed']} ✅")
        print(f"無需修復: {stats['skipped']} ⏭️")
        print(f"失敗: {stats['errors']} ❌")

        if self.dry_run:
            print("\n⚠️  DRY-RUN 模式: 未實際修改任何文件")
        else:
            print(f"\n✅ 已修復 {stats['fixed']} 個 zettel_index.md 文件")

        return stats


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description='Zettelkasten 格式修復工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  # Dry-run 模式預覽變更
  python zettel_format_fixer.py --file card.md --dry-run

  # 修復單張卡片
  python zettel_format_fixer.py --file output/zettel_Barsalou-2009_20251104/zettel_cards/Barsalou-2009-005.md

  # 批次修復資料夾
  python zettel_format_fixer.py --batch output/zettelkasten_notes/

  # 批次修復卡片並修復 mermaid 圖表
  python zettel_format_fixer.py --batch output/zettelkasten_notes/ --fix-index

  # 批次修復並生成報告
  python zettel_format_fixer.py --batch output/zettelkasten_notes/ --fix-index --report fix_report.md
        """
    )

    parser.add_argument('--file', type=str, help='單張卡片文件路徑')
    parser.add_argument('--batch', type=str, help='批次處理資料夾路徑')
    parser.add_argument('--fix-index', action='store_true', help='修復 zettel_index.md 中的 mermaid 圖表')
    parser.add_argument('--dry-run', action='store_true', help='Dry-run 模式（僅預覽，不修改）')
    parser.add_argument('--report', type=str, help='生成修復報告文件路徑')

    args = parser.parse_args()

    # 檢查參數
    if not args.file and not args.batch:
        parser.print_help()
        sys.exit(1)

    # 創建修復器
    fixer = ZettelFormatFixer(dry_run=args.dry_run)

    # 單文件模式
    if args.file:
        card_path = Path(args.file)
        if not card_path.exists():
            print(f"❌ 文件不存在: {card_path}")
            sys.exit(1)

        print(f"\n🔧 修復卡片: {card_path.name}\n")
        success, changes = fixer.fix_card(card_path)

        if success:
            if changes:
                print("✅ 修復成功")
                for change in changes:
                    print(f"  - {change}")
            else:
                print("⏭️  無需修復")
        else:
            print("❌ 修復失敗")
            for error in changes:
                print(f"  ! {error}")

    # 批次模式
    elif args.batch:
        batch_path = Path(args.batch)
        if not batch_path.exists():
            print(f"❌ 資料夾不存在: {batch_path}")
            sys.exit(1)

        stats = fixer.process_batch(batch_path)
        fixer.print_summary()

        # 如果指定 --fix-index，修復 zettel_index.md 的 mermaid 圖表
        if args.fix_index:
            print("\n" + "=" * 60)
            print("🔧 開始修復 zettel_index.md 的 mermaid 圖表")
            print("=" * 60 + "\n")
            index_stats = fixer.batch_fix_indices(batch_path)

        # 生成報告
        if args.report:
            report_path = Path(args.report)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(f"# Zettelkasten 格式修復報告\n\n")
                f.write(f"**生成時間**: {Path().resolve()}\n")
                f.write(f"**模式**: {'DRY-RUN' if args.dry_run else 'LIVE'}\n\n")
                f.write(f"## 統計摘要\n\n")
                f.write(f"- 總卡片數: {stats['total']}\n")
                f.write(f"- 已修復: {stats['fixed']}\n")
                f.write(f"- 無需修復: {stats['skipped']}\n")
                f.write(f"- 失敗: {stats['errors']}\n\n")
                f.write(f"## 修復詳情\n\n")
                f.write(f"- Summary 清理: {stats['fixes']['summary']}\n")
                f.write(f"- 連結格式修復: {stats['fixes']['links']}\n")
                f.write(f"- 移除冗餘 H1: {stats['fixes']['redundant_h1']}\n")
                f.write(f"- 移除冗餘「核心」: {stats['fixes']['redundant_core']}\n")
                f.write(f"- 空行標準化: {stats['fixes']['spacing']}\n")

            print(f"\n📝 報告已生成: {report_path}")


if __name__ == '__main__':
    main()
