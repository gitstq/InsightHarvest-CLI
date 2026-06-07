"""Hacker News采集器 - 通过HN公开API采集数据"""

import json
from harvesters.base import BaseHarvester


class HackerNewsHarvester(BaseHarvester):
    """Hacker News数据采集器，使用官方公开API"""

    name = "hackernews"
    description = "Hacker News热门故事采集"

    API_BASE = "https://hacker-news.firebaseio.com/v0"

    def __init__(self, config=None, cache=None, logger=None):
        super().__init__(config, cache, logger)

    def fetch(self, keywords=None, days=7, limit=None, story_type="top"):
        """
        采集HN数据

        Args:
            keywords: 关键词过滤列表
            days: 时间范围
            limit: 最大条数
            story_type: 故事类型 (top/new/best/show/ask/job)
        """
        all_items = []

        # 获取故事ID列表
        story_ids = self._fetch_story_ids(story_type)
        if not story_ids:
            return []

        fetch_limit = min(limit or self.max_items, len(story_ids))

        if self.logger:
            self.logger.info("[hackernews] 正在采集 {} 条 {} 故事...".format(
                fetch_limit, story_type
            ))

        for sid in story_ids[:fetch_limit]:
            item = self._fetch_story_detail(sid)
            if item:
                all_items.append(item)

        # 标准化
        normalized = [self._normalize_item(item) for item in all_items]

        # 过滤
        normalized = self._filter_by_date(normalized, days)
        normalized = self._filter_by_keywords(normalized, keywords)
        normalized = self._apply_limits(normalized, limit)

        return normalized

    def _fetch_story_ids(self, story_type="top"):
        """获取故事ID列表"""
        if self.cache:
            cached = self.cache.get("hackernews", "ids_{}".format(story_type))
            if cached:
                return cached

        url = "{}/{}.json".format(self.API_BASE, story_type + "stories")
        text = self._fetch_url(url)

        if not text:
            return []

        ids = self._parse_json(text)
        if not ids or not isinstance(ids, list):
            return []

        if self.cache:
            self.cache.set("hackernews", "ids_{}".format(story_type), ids)

        return ids

    def _fetch_story_detail(self, story_id):
        """获取单个故事详情"""
        if self.cache:
            cached = self.cache.get("hackernews", "story_{}".format(story_id))
            if cached:
                return cached

        url = "{}/item/{}.json".format(self.API_BASE, story_id)
        text = self._fetch_url(url)

        if not text:
            return None

        data = self._parse_json(text)
        if not data:
            return None

        item = {
            "title": data.get("title", ""),
            "description": data.get("text", "")[:500] if data.get("text") else "",
            "url": data.get("url", "https://news.ycombinator.com/item?id={}".format(story_id)),
            "author": data.get("by", ""),
            "timestamp": data.get("time", 0),
            "score": data.get("score", 0),
            "tags": [],
            "extra": {
                "hn_id": story_id,
                "descendants": data.get("descendants", 0),
                "type": data.get("type", "story"),
            },
        }

        if self.cache:
            self.cache.set("hackernews", "story_{}".format(story_id), item)

        return item
