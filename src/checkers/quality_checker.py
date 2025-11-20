#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
論文質量檢查器
檢查知識庫中論文的元數據質量並提供修復建議
"""

import re
import json
import yaml
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from difflib import SequenceMatcher
import sys

# 添加 src 到路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from knowledge_base import KnowledgeBaseManager


@dataclass
class QualityIssue:
    """質量問題"""
    field: str  # title, authors, year, abstract, keywords
    severity: str  # critical, warning, info
    issue_type: str  # invalid_pattern, missing, suspicious, format_error
    description: str
    current_value: Any
    suggested_fix: Optional[Any] = None
    auto_fixable: bool = False


@dataclass
class QualityReport:
    """質量檢查報告"""
    paper_id: int
    title: str
    overall_score: float = 0.0
    quality_level: str = "unknown"  # excellent, good, acceptable, poor, critical
    issues: List[QualityIssue] = field(default_factory=list)
    metadata_scores: Dict[str, float] = field(default_factory=dict)
    checked_at: str = field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def get_critical_issues(self) -> List[QualityIssue]:
        """獲取嚴重問題"""
        return [issue for issue in self.issues if issue.severity == "critical"]

    def get_warnings(self) -> List[QualityIssue]:
        """獲取警告"""
        return [issue for issue in self.issues if issue.severity == "warning"]

    def get_info(self) -> List[QualityIssue]:
        """獲取信息"""
        return [issue for issue in self.issues if issue.severity == "info"]

    def has_critical_issues(self) -> bool:
        """是否有嚴重問題"""
        return len(self.get_critical_issues()) > 0

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "paper_id": self.paper_id,
            "title": self.title,
            "overall_score": self.overall_score,
            "quality_level": self.quality_level,
            "checked_at": self.checked_at,
            "metadata_scores": self.metadata_scores,
            "issues": {
                "critical": [
                    {
                        "field": i.field,
                        "type": i.issue_type,
                        "description": i.description,
                        "current_value": i.current_value,
                        "suggested_fix": i.suggested_fix,
                        "auto_fixable": i.auto_fixable
                    }
                    for i in self.get_critical_issues()
                ],
                "warnings": [
                    {
                        "field": i.field,
                        "type": i.issue_type,
                        "description": i.description,
                        "current_value": i.current_value
                    }
                    for i in self.get_warnings()
                ],
                "info": [
                    {
                        "field": i.field,
                        "description": i.description
                    }
                    for i in self.get_info()
                ]
            }
        }

    def to_text(self, detail_level: str = "standard") -> str:
        """轉換為文本報告"""
        lines = []
        lines.append("=" * 70)
        lines.append(f"論文質量檢查報告")
        lines.append("=" * 70)
        lines.append(f"論文ID: {self.paper_id}")
        lines.append(f"標題: {self.title}")
        lines.append(f"檢查時間: {self.checked_at}")
        lines.append("")
        lines.append(f"整體評分: {self.overall_score:.1f}/100")
        lines.append(f"質量等級: {self._get_quality_level_label(self.quality_level)}")
        lines.append("")

        if detail_level in ["standard", "comprehensive"]:
            lines.append("元數據評分:")
            for field, score in self.metadata_scores.items():
                lines.append(f"  - {field}: {score:.1f}")
            lines.append("")

        critical = self.get_critical_issues()
        if critical:
            lines.append(f"🚨 嚴重問題 ({len(critical)} 個):")
            for i, issue in enumerate(critical, 1):
                lines.append(f"  {i}. [{issue.field}] {issue.description}")
                lines.append(f"     當前值: {issue.current_value}")
                if issue.suggested_fix and detail_level == "comprehensive":
                    lines.append(f"     建議修復: {issue.suggested_fix}")
                if issue.auto_fixable:
                    lines.append(f"     ✅ 可自動修復")
            lines.append("")

        warnings = self.get_warnings()
        if warnings and detail_level in ["standard", "comprehensive"]:
            lines.append(f"⚠️  警告 ({len(warnings)} 個):")
            for i, issue in enumerate(warnings, 1):
                lines.append(f"  {i}. [{issue.field}] {issue.description}")
            lines.append("")

        info = self.get_info()
        if info and detail_level == "comprehensive":
            lines.append(f"ℹ️  提示 ({len(info)} 個):")
            for i, issue in enumerate(info, 1):
                lines.append(f"  {i}. [{issue.field}] {issue.description}")
            lines.append("")

        lines.append("=" * 70)
        return "\n".join(lines)

    def _get_quality_level_label(self, level: str) -> str:
        """獲取質量等級標籤"""
        labels = {
            "excellent": "優秀 ⭐⭐⭐⭐⭐",
            "good": "良好 ⭐⭐⭐⭐",
            "acceptable": "可接受 ⭐⭐⭐",
            "poor": "較差 ⭐⭐",
            "critical": "嚴重問題 ⭐",
            "unknown": "未知"
        }
        return labels.get(level, level)


class QualityChecker:
    """論文質量檢查器"""

    def __init__(self,
                 kb_manager: Optional[KnowledgeBaseManager] = None,
                 rules_file: Optional[str] = None,
                 enable_api: bool = True):
        """
        初始化質量檢查器

        Args:
            kb_manager: 知識庫管理器實例
            rules_file: 規則配置文件路徑
            enable_api: 是否啟用外部API
        """
        self.kb = kb_manager or KnowledgeBaseManager()

        # 載入規則配置
        if rules_file is None:
            rules_file = Path(__file__).parent / "quality_rules.yaml"

        with open(rules_file, 'r', encoding='utf-8') as f:
            self.rules = yaml.safe_load(f)

        self.enable_api = enable_api
        self.current_year = datetime.now().year

    def check_paper(self, paper_id: int, auto_fix: bool = False) -> QualityReport:
        """
        檢查單篇論文的質量

        Args:
            paper_id: 論文ID
            auto_fix: 是否自動修復問題

        Returns:
            質量檢查報告
        """
        # 獲取論文數據
        paper = self.kb.get_paper_by_id(paper_id)
        if not paper:
            raise ValueError(f"論文 ID {paper_id} 不存在")

        # 創建報告
        report = QualityReport(
            paper_id=paper_id,
            title=paper.get('title', 'Unknown')
        )

        # 檢查各項元數據
        title_issues, title_score = self._check_title(paper)
        authors_issues, authors_score = self._check_authors(paper)
        year_issues, year_score = self._check_year(paper)
        abstract_issues, abstract_score = self._check_abstract(paper)
        keywords_issues, keywords_score = self._check_keywords(paper)

        # 合併所有問題
        report.issues.extend(title_issues)
        report.issues.extend(authors_issues)
        report.issues.extend(year_issues)
        report.issues.extend(abstract_issues)
        report.issues.extend(keywords_issues)

        # 計算元數據評分
        report.metadata_scores = {
            "title": title_score,
            "authors": authors_score,
            "year": year_score,
            "abstract": abstract_score,
            "keywords": keywords_score
        }

        # 計算整體評分
        weights = self.rules['quality_scoring']['weights']
        report.overall_score = (
            title_score * weights['title'] +
            authors_score * weights['authors'] +
            year_score * weights['year'] +
            abstract_score * weights['abstract'] +
            keywords_score * weights['keywords']
        )

        # 確定質量等級
        report.quality_level = self._determine_quality_level(report.overall_score)

        # 自動修復（如果啟用）
        if auto_fix and self.rules['auto_fix']['enabled']:
            self._auto_fix_issues(paper_id, report)

        return report

    def check_all_papers(self, auto_fix: bool = False) -> List[QualityReport]:
        """
        檢查所有論文的質量

        Args:
            auto_fix: 是否自動修復問題

        Returns:
            質量檢查報告列表
        """
        papers = self.kb.list_papers(limit=1000)
        reports = []

        for paper in papers:
            try:
                report = self.check_paper(paper['id'], auto_fix=auto_fix)
                reports.append(report)
            except Exception as e:
                print(f"檢查論文 {paper['id']} 時出錯: {e}")

        return reports

    def _check_title(self, paper: Dict[str, Any]) -> Tuple[List[QualityIssue], float]:
        """檢查標題質量"""
        issues = []
        score = 100.0

        title = paper.get('title', '')
        if not title:
            title = ''

        rules = self.rules['title_checks']

        # 檢查無效模式
        for pattern_rule in rules['invalid_patterns']:
            if re.search(pattern_rule['pattern'], title, re.IGNORECASE):
                issues.append(QualityIssue(
                    field="title",
                    severity=pattern_rule['severity'],
                    issue_type="invalid_pattern",
                    description=pattern_rule['description'],
                    current_value=title,
                    auto_fixable=(pattern_rule.get('auto_fix') == 'extract_from_content')
                ))
                score -= 25  # 嚴重扣分

        # 檢查可疑模式
        for pattern_rule in rules['suspicious_patterns']:
            if re.search(pattern_rule['pattern'], title, re.IGNORECASE):
                issues.append(QualityIssue(
                    field="title",
                    severity=pattern_rule['severity'],
                    issue_type="suspicious",
                    description=pattern_rule['description'],
                    current_value=title,
                    auto_fixable=False
                ))
                if pattern_rule['severity'] == 'warning':
                    score -= 5
                else:
                    score -= 2

        # 檢查長度
        metrics = rules['quality_metrics']
        if len(title) < metrics['min_length']:
            issues.append(QualityIssue(
                field="title",
                severity="critical",
                issue_type="too_short",
                description=f"標題過短（{len(title)} 字元，最少 {metrics['min_length']}）",
                current_value=title,
                auto_fixable=True
            ))
            score -= 10
        elif len(title) < metrics['preferred_min_length']:
            issues.append(QualityIssue(
                field="title",
                severity="info",
                issue_type="suboptimal_length",
                description=f"標題偏短（建議至少 {metrics['preferred_min_length']} 字元）",
                current_value=title,
                auto_fixable=False
            ))
            score -= 3

        if len(title) > metrics['max_length']:
            issues.append(QualityIssue(
                field="title",
                severity="warning",
                issue_type="too_long",
                description=f"標題過長（{len(title)} 字元，最多 {metrics['max_length']}）",
                current_value=title,
                auto_fixable=False
            ))
            score -= 5

        return issues, max(0, score)

    def _check_authors(self, paper: Dict[str, Any]) -> Tuple[List[QualityIssue], float]:
        """檢查作者質量"""
        issues = []
        score = 100.0

        authors = paper.get('authors', [])
        if not authors:
            authors = []

        rules = self.rules['authors_checks']

        # 檢查是否有作者
        if not authors or len(authors) == 0:
            issues.append(QualityIssue(
                field="authors",
                severity="critical",
                issue_type="missing",
                description="缺少作者信息",
                current_value=authors,
                auto_fixable=True
            ))
            return issues, 0.0

        # 檢查每個作者
        for i, author in enumerate(authors):
            # 檢查無效模式
            for pattern_rule in rules['invalid_patterns']:
                if re.search(pattern_rule['pattern'], author, re.IGNORECASE):
                    issues.append(QualityIssue(
                        field="authors",
                        severity=pattern_rule['severity'],
                        issue_type="invalid_pattern",
                        description=f"作者 {i+1} {pattern_rule['description']}: {author}",
                        current_value=author,
                        auto_fixable=True
                    ))
                    score -= 15

        # 檢查作者數量
        metrics = rules['quality_metrics']
        if len(authors) > metrics['max_authors']:
            issues.append(QualityIssue(
                field="authors",
                severity="warning",
                issue_type="suspicious_count",
                description=f"作者數量過多（{len(authors)} 位，通常不超過 {metrics['max_authors']} 位）",
                current_value=len(authors),
                auto_fixable=False
            ))
            score -= 5

        return issues, max(0, score)

    def _check_year(self, paper: Dict[str, Any]) -> Tuple[List[QualityIssue], float]:
        """檢查年份質量"""
        issues = []
        score = 100.0

        year = paper.get('year')
        rules = self.rules['year_checks']

        # 檢查是否有年份
        if year is None:
            issues.append(QualityIssue(
                field="year",
                severity="critical",
                issue_type="missing",
                description="缺少發表年份",
                current_value=None,
                auto_fixable=True
            ))
            return issues, 0.0

        # 檢查年份範圍
        valid_range = rules['valid_range']
        if year < valid_range['min_year'] or year > valid_range['max_year']:
            issues.append(QualityIssue(
                field="year",
                severity="critical",
                issue_type="out_of_range",
                description=f"年份超出有效範圍（{valid_range['min_year']}-{valid_range['max_year']}）",
                current_value=year,
                auto_fixable=True
            ))
            score -= 20

        # 檢查可疑年份
        for condition in rules['suspicious_conditions']:
            if condition['condition'] == 'too_old' and year < condition['threshold']:
                issues.append(QualityIssue(
                    field="year",
                    severity=condition['severity'],
                    issue_type="suspicious",
                    description=condition['description'],
                    current_value=year,
                    auto_fixable=False
                ))
                score -= 2
            elif condition['condition'] == 'future' and year > self.current_year + 2:
                issues.append(QualityIssue(
                    field="year",
                    severity=condition['severity'],
                    issue_type="suspicious",
                    description=condition['description'],
                    current_value=year,
                    auto_fixable=True
                ))
                score -= 5

        return issues, max(0, score)

    def _check_abstract(self, paper: Dict[str, Any]) -> Tuple[List[QualityIssue], float]:
        """檢查摘要質量"""
        issues = []
        score = 100.0

        abstract = paper.get('abstract', '')
        if not abstract:
            abstract = ''

        rules = self.rules['abstract_checks']

        # 檢查是否為空
        if not abstract or len(abstract.strip()) == 0:
            issues.append(QualityIssue(
                field="abstract",
                severity="critical",
                issue_type="missing",
                description="缺少摘要",
                current_value=abstract,
                auto_fixable=True
            ))
            return issues, 0.0

        # 檢查是否為佔位符
        for pattern in rules['content_checks'][1]['patterns']:
            if re.search(pattern, abstract, re.IGNORECASE):
                issues.append(QualityIssue(
                    field="abstract",
                    severity="critical",
                    issue_type="placeholder",
                    description="摘要為佔位符",
                    current_value=abstract,
                    auto_fixable=True
                ))
                return issues, 0.0

        # 檢查長度
        length = rules['length_checks']
        if len(abstract) < length['min_length']:
            issues.append(QualityIssue(
                field="abstract",
                severity="critical",
                issue_type="too_short",
                description=f"摘要過短（{len(abstract)} 字元，最少 {length['min_length']}）",
                current_value=f"{abstract[:50]}...",
                auto_fixable=True
            ))
            score -= 25
        elif len(abstract) < length['preferred_min_length']:
            issues.append(QualityIssue(
                field="abstract",
                severity="info",
                issue_type="suboptimal_length",
                description=f"摘要偏短（建議至少 {length['preferred_min_length']} 字元）",
                current_value=f"{abstract[:50]}...",
                auto_fixable=False
            ))
            score -= 5

        if len(abstract) > length['max_length']:
            issues.append(QualityIssue(
                field="abstract",
                severity="warning",
                issue_type="too_long",
                description=f"摘要過長（{len(abstract)} 字元，最多 {length['max_length']}）",
                current_value=f"{abstract[:50]}...",
                auto_fixable=False
            ))
            score -= 5

        # 檢查詞數
        word_count = len(abstract.split())
        min_words = rules['content_checks'][2]['min_words']
        if word_count < min_words:
            issues.append(QualityIssue(
                field="abstract",
                severity="warning",
                issue_type="insufficient_content",
                description=f"摘要內容過少（{word_count} 字，建議至少 {min_words} 字）",
                current_value=f"{abstract[:50]}...",
                auto_fixable=False
            ))
            score -= 10

        return issues, max(0, score)

    def _check_keywords(self, paper: Dict[str, Any]) -> Tuple[List[QualityIssue], float]:
        """檢查關鍵詞質量"""
        issues = []
        score = 100.0

        keywords = paper.get('keywords', [])
        if not keywords:
            keywords = []

        rules = self.rules['keywords_checks']

        # 檢查數量
        count = rules['count_checks']
        if len(keywords) < count['min_keywords']:
            issues.append(QualityIssue(
                field="keywords",
                severity="warning",
                issue_type="insufficient_count",
                description=f"關鍵詞過少（{len(keywords)} 個，建議至少 {count['preferred_min']} 個）",
                current_value=keywords,
                auto_fixable=True
            ))
            score -= 15
        elif len(keywords) < count['preferred_min']:
            issues.append(QualityIssue(
                field="keywords",
                severity="info",
                issue_type="suboptimal_count",
                description=f"關鍵詞偏少（建議 {count['preferred_min']}-{count['preferred_max']} 個）",
                current_value=keywords,
                auto_fixable=False
            ))
            score -= 5

        if len(keywords) > count['max_keywords']:
            issues.append(QualityIssue(
                field="keywords",
                severity="warning",
                issue_type="excessive_count",
                description=f"關鍵詞過多（{len(keywords)} 個，建議不超過 {count['max_keywords']} 個）",
                current_value=keywords,
                auto_fixable=False
            ))
            score -= 10

        # 檢查重複
        if len(keywords) != len(set(keywords)):
            issues.append(QualityIssue(
                field="keywords",
                severity="warning",
                issue_type="duplicates",
                description="關鍵詞包含重複項",
                current_value=keywords,
                auto_fixable=True
            ))
            score -= 10

        # 檢查空字串
        if any(not kw.strip() for kw in keywords):
            issues.append(QualityIssue(
                field="keywords",
                severity="warning",
                issue_type="empty_keyword",
                description="包含空白關鍵詞",
                current_value=keywords,
                auto_fixable=True
            ))
            score -= 5

        return issues, max(0, score)

    def _determine_quality_level(self, score: float) -> str:
        """根據評分確定質量等級"""
        levels = self.rules['quality_scoring']['score_levels']

        if score >= levels['excellent']:
            return "excellent"
        elif score >= levels['good']:
            return "good"
        elif score >= levels['acceptable']:
            return "acceptable"
        elif score >= levels['poor']:
            return "poor"
        else:
            return "critical"

    def _auto_fix_issues(self, paper_id: int, report: QualityReport):
        """自動修復問題"""
        # TODO: 實作自動修復邏輯
        # 這需要整合 PDF 提取器和外部 API
        pass

    def detect_duplicates(self, threshold: float = 0.85) -> List[Tuple[int, int, float]]:
        """
        檢測重複論文

        Args:
            threshold: 相似度閾值（0-1）

        Returns:
            (paper_id_1, paper_id_2, similarity) 列表
        """
        duplicates = []
        papers = self.kb.list_papers(limit=1000)

        # 兩兩比較
        for i in range(len(papers)):
            for j in range(i+1, len(papers)):
                similarity = self._calculate_similarity(papers[i], papers[j])
                if similarity >= threshold:
                    duplicates.append((papers[i]['id'], papers[j]['id'], similarity))

        return duplicates

    def _calculate_similarity(self, paper1: Dict[str, Any], paper2: Dict[str, Any]) -> float:
        """計算兩篇論文的相似度"""
        # 標題相似度
        title1 = paper1.get('title', '').lower()
        title2 = paper2.get('title', '').lower()
        title_sim = SequenceMatcher(None, title1, title2).ratio()

        # 作者重疊度
        authors1 = set(paper1.get('authors', []))
        authors2 = set(paper2.get('authors', []))
        if authors1 and authors2:
            author_overlap = len(authors1 & authors2) / len(authors1 | authors2)
        else:
            author_overlap = 0

        # 年份相似度
        year1 = paper1.get('year', 0)
        year2 = paper2.get('year', 0)
        year_diff = abs(year1 - year2) if year1 and year2 else 10
        year_sim = max(0, 1 - year_diff / 10)

        # 綜合相似度
        similarity = (
            title_sim * 0.6 +
            author_overlap * 0.3 +
            year_sim * 0.1
        )

        return similarity

    def generate_summary_report(self, reports: List[QualityReport], detail_level: str = "standard") -> str:
        """
        生成總結報告

        Args:
            reports: 質量報告列表
            detail_level: 詳細程度（minimal/standard/comprehensive）

        Returns:
            總結報告文本
        """
        lines = []
        lines.append("=" * 80)
        lines.append("知識庫質量檢查總結報告")
        lines.append("=" * 80)
        lines.append(f"檢查時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"檢查論文數: {len(reports)}")
        lines.append("")

        # 統計
        total_issues = sum(len(r.issues) for r in reports)
        critical_issues = sum(len(r.get_critical_issues()) for r in reports)
        warnings = sum(len(r.get_warnings()) for r in reports)

        avg_score = sum(r.overall_score for r in reports) / len(reports) if reports else 0

        lines.append("📊 總體統計:")
        lines.append(f"  平均評分: {avg_score:.1f}/100")
        lines.append(f"  總問題數: {total_issues}")
        lines.append(f"    - 嚴重問題: {critical_issues}")
        lines.append(f"    - 警告: {warnings}")
        lines.append("")

        # 質量等級分布
        level_counts = {}
        for report in reports:
            level = report.quality_level
            level_counts[level] = level_counts.get(level, 0) + 1

        lines.append("📈 質量等級分布:")
        for level in ["excellent", "good", "acceptable", "poor", "critical"]:
            count = level_counts.get(level, 0)
            percentage = (count / len(reports) * 100) if reports else 0
            label = QualityReport(0, "")._get_quality_level_label(level)
            lines.append(f"  {label}: {count} 篇 ({percentage:.1f}%)")
        lines.append("")

        # 問題論文列表
        if detail_level in ["standard", "comprehensive"]:
            problematic = [r for r in reports if r.has_critical_issues()]
            if problematic:
                lines.append(f"🚨 有嚴重問題的論文 ({len(problematic)} 篇):")
                for r in problematic[:20]:  # 最多顯示20篇
                    lines.append(f"  - [{r.paper_id}] {r.title[:60]}... ({len(r.get_critical_issues())} 個嚴重問題)")
                if len(problematic) > 20:
                    lines.append(f"  ... 還有 {len(problematic) - 20} 篇")
                lines.append("")

        # 詳細建議
        if detail_level == "comprehensive":
            lines.append("💡 改進建議:")

            # 統計各類問題
            issue_types = {}
            for report in reports:
                for issue in report.issues:
                    key = f"{issue.field}_{issue.issue_type}"
                    issue_types[key] = issue_types.get(key, 0) + 1

            # 顯示最常見的問題
            sorted_issues = sorted(issue_types.items(), key=lambda x: x[1], reverse=True)
            for issue_key, count in sorted_issues[:10]:
                field, issue_type = issue_key.split('_', 1)
                lines.append(f"  - {field} {issue_type}: {count} 次")
            lines.append("")

        lines.append("=" * 80)
        return "\n".join(lines)


if __name__ == "__main__":
    # Windows 編碼修復
    import sys
    import io
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    # 測試代碼
    checker = QualityChecker()

    # 檢查所有論文
    print("檢查知識庫中的所有論文...")
    reports = checker.check_all_papers(auto_fix=False)

    # 生成總結報告
    summary = checker.generate_summary_report(reports, detail_level="comprehensive")
    print(summary)

    # 顯示前5篇有嚴重問題的論文詳情
    problematic = [r for r in reports if r.has_critical_issues()]
    if problematic:
        print("\n\n詳細報告（前5篇有嚴重問題的論文）:")
        for report in problematic[:5]:
            print("\n" + report.to_text(detail_level="comprehensive"))
