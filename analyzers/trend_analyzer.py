"""趋势分析器 - 分析数据趋势和统计信息"""

import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from analyzers.base import BaseAnalyzer


class TrendAnalyzer(BaseAnalyzer):
    """趋势分析器，提供数据统计和趋势检测"""

    name = "trend_analyzer"
    description = "趋势分析与统计"

    def __init__(self, config=None, logger=None):
        super().__init__(config, logger)

    def analyze(self, items):
        """
        综合趋势分析

        Args:
            items: 数据项列表

        Returns:
            dict: 趋势分析结果
        """
        if not items:
            return self._empty_result()

        result = {
            "total_items": len(items),
            "source_distribution": self._analyze_sources(items),
            "time_distribution": self._analyze_time_distribution(items),
            "top_items": self._get_top_items(items, n=10),
            "tag_cloud": self._analyze_tags(items),
            "statistics": self._compute_statistics(items),
        }

        if self.logger:
            self.logger.info("[trend] 分析完成: {} 条数据, {} 个来源".format(
                len(items), len(result["source_distribution"])
            ))

        return result

    def _analyze_sources(self, items):
        """分析来源分布"""
        counter = Counter()
        for item in items:
            source = item.get("source", "unknown")
            counter[source] += 1

        return dict(counter.most_common())

    def _analyze_time_distribution(self, items):
        """分析时间分布"""
        daily = defaultdict(int)
        for item in items:
            ts = item.get("timestamp", 0)
            if isinstance(ts, (int, float)) and ts > 0:
                try:
                    dt = datetime.utcfromtimestamp(ts)
                    day_key = dt.strftime("%Y-%m-%d")
                    daily[day_key] += 1
                except (ValueError, OSError):
                    continue
            elif isinstance(ts, str) and ts:
                try:
                    dt = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
                    day_key = dt.strftime("%Y-%m-%d")
                    daily[day_key] += 1
                except ValueError:
                    try:
                        day_key = ts[:10]
                        daily[day_key] += 1
                    except (IndexError, TypeError):
                        continue

        # 按日期排序
        sorted_days = sorted(daily.items())
        return {
            "daily": dict(sorted_days),
            "peak_day": max(daily.items(), key=lambda x: x[1])[0] if daily else "",
            "peak_count": max(daily.values()) if daily else 0,
        }

    def _get_top_items(self, items, n=10):
        """获取热门条目"""
        sorted_items = sorted(
            items, key=lambda x: x.get("score", 0), reverse=True
        )
        top = []
        for item in sorted_items[:n]:
            top.append({
                "title": item.get("title", ""),
                "source": item.get("source", ""),
                "score": item.get("score", 0),
                "url": item.get("url", ""),
            })
        return top

    def _analyze_tags(self, items):
        """分析标签/关键词云"""
        tag_counter = Counter()
        for item in items:
            tags = item.get("tags", [])
            if isinstance(tags, list):
                tag_counter.update(tags)

            # 从标题提取额外关键词
            title = item.get("title", "")
            if title:
                words = re.findall(r'\b[a-zA-Z]{3,}\b', title.lower())
                tag_counter.update(words)

        return dict(tag_counter.most_common(30))

    def _compute_statistics(self, items):
        """计算基本统计信息"""
        scores = [item.get("score", 0) for item in items if item.get("score")]

        stats = {
            "total_score": sum(scores),
            "avg_score": round(sum(scores) / len(scores), 2) if scores else 0,
            "max_score": max(scores) if scores else 0,
            "min_score": min(scores) if scores else 0,
            "items_with_score": len(scores),
        }

        # 计算分数中位数
        if scores:
            sorted_scores = sorted(scores)
            mid = len(sorted_scores) // 2
            if len(sorted_scores) % 2 == 0:
                stats["median_score"] = round(
                    (sorted_scores[mid - 1] + sorted_scores[mid]) / 2, 2
                )
            else:
                stats["median_score"] = sorted_scores[mid]

        return stats

    def _empty_result(self):
        """返回空结果"""
        return {
            "total_items": 0,
            "source_distribution": {},
            "time_distribution": {"daily": {}, "peak_day": "", "peak_count": 0},
            "top_items": [],
            "tag_cloud": {},
            "statistics": {
                "total_score": 0,
                "avg_score": 0,
                "max_score": 0,
                "min_score": 0,
                "items_with_score": 0,
            },
        }
