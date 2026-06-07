"""去重引擎 - 智能识别和去除重复数据"""

import re
from difflib import SequenceMatcher
from analyzers.base import BaseAnalyzer


class Deduplicator(BaseAnalyzer):
    """数据去重引擎，支持精确匹配和模糊匹配"""

    name = "deduplicator"
    description = "数据去重与相似度检测"

    def __init__(self, config=None, logger=None, similarity_threshold=0.7):
        super().__init__(config, logger)
        self.similarity_threshold = similarity_threshold

    def analyze(self, items):
        """
        去除重复数据项

        Args:
            items: 数据项列表

        Returns:
            tuple: (去重后的列表, 被移除的重复项列表)
        """
        if not items:
            return [], []

        unique_items = []
        duplicates = []
        seen_urls = set()
        seen_titles = set()

        for item in items:
            url = item.get("url", "").strip()
            title = item.get("title", "").strip()

            # 精确URL匹配
            if url and url in seen_urls:
                duplicates.append(item)
                continue

            # 精确标题匹配
            if title and title.lower() in seen_titles:
                duplicates.append(item)
                continue

            # 模糊标题匹配
            is_similar = False
            for existing in unique_items:
                existing_title = existing.get("title", "")
                sim = self._title_similarity(title, existing_title)
                if sim >= self.similarity_threshold:
                    # 保留分数更高的
                    if item.get("score", 0) > existing.get("score", 0):
                        duplicates.append(existing)
                        unique_items.remove(existing)
                        unique_items.append(item)
                    else:
                        duplicates.append(item)
                    is_similar = True
                    break

            if not is_similar:
                unique_items.append(item)
                if url:
                    seen_urls.add(url)
                if title:
                    seen_titles.add(title.lower())

        if self.logger:
            self.logger.info(
                "[dedup] 原始: {} 条, 去重后: {} 条, 移除: {} 条".format(
                    len(items), len(unique_items), len(duplicates)
                )
            )

        return unique_items, duplicates

    def _title_similarity(self, title1, title2):
        """计算两个标题的相似度"""
        if not title1 or not title2:
            return 0.0

        # 标准化标题
        t1 = self._normalize_title(title1)
        t2 = self._normalize_title(title2)

        if t1 == t2:
            return 1.0

        # SequenceMatcher相似度
        return SequenceMatcher(None, t1, t2).ratio()

    def _normalize_title(self, title):
        """标准化标题用于比较"""
        # 转小写
        title = title.lower()
        # 移除特殊字符
        title = re.sub(r'[^\w\s]', ' ', title)
        # 移除多余空格
        title = re.sub(r'\s+', ' ', title).strip()
        return title

    def find_duplicates(self, items):
        """仅查找重复项，不修改列表"""
        _, duplicates = self.analyze(items)
        return duplicates

    def get_similarity_groups(self, items):
        """
        将相似项分组

        Returns:
            list[list]: 相似项组列表
        """
        if not items:
            return []

        groups = []
        assigned = set()

        for i, item_a in enumerate(items):
            if i in assigned:
                continue

            group = [item_a]
            assigned.add(i)

            for j in range(i + 1, len(items)):
                if j in assigned:
                    continue

                item_b = items[j]
                sim = self._title_similarity(
                    item_a.get("title", ""),
                    item_b.get("title", "")
                )

                if sim >= self.similarity_threshold:
                    group.append(item_b)
                    assigned.add(j)

            if len(group) > 1:
                groups.append(group)

        return groups
