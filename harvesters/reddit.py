"""Reddit采集器 - 通过Reddit公开JSON API采集数据"""

import json
from harvesters.base import BaseHarvester


class RedditHarvester(BaseHarvester):
    """Reddit数据采集器，使用公开JSON API"""

    name = "reddit"
    description = "Reddit热门话题采集"

    SUBREDDITS = ["programming", "technology", "artificial", "MachineLearning",
                   "datascience", "python", "javascript", "startups"]

    def __init__(self, config=None, cache=None, logger=None):
        super().__init__(config, cache, logger)
        self.subreddits = self.SUBREDDITS

    def fetch(self, keywords=None, days=7, limit=None, subreddits=None):
        """
        采集Reddit数据

        Args:
            keywords: 关键词过滤列表
            days: 时间范围
            limit: 最大条数
            subreddits: 自定义子版块列表
        """
        subs = subreddits or self.subreddits
        all_items = []

        for sub in subs:
            items = self._fetch_subreddit(sub)
            if items:
                all_items.extend(items)

        # 标准化
        normalized = [self._normalize_item(item) for item in all_items]

        # 过滤
        normalized = self._filter_by_date(normalized, days)
        normalized = self._filter_by_keywords(normalized, keywords)
        normalized = self._apply_limits(normalized, limit)

        return normalized

    def _fetch_subreddit(self, subreddit):
        """获取单个子版块的热门帖子"""
        # 尝试从缓存读取
        if self.cache:
            cached = self.cache.get("reddit", subreddit)
            if cached:
                if self.logger:
                    self.logger.debug("[reddit] 缓存命中: r/{}".format(subreddit))
                return cached

        url = "https://www.reddit.com/r/{}/hot.json?limit=25".format(subreddit)

        if self.logger:
            self.logger.info("[reddit] 正在采集 r/{}...".format(subreddit))

        text = self._fetch_url(url)
        if not text:
            return []

        data = self._parse_json(text)
        if not data:
            return []

        items = []
        children = data.get("data", {}).get("children", [])

        for child in children:
            child_data = child.get("data", {})
            items.append({
                "title": child_data.get("title", ""),
                "description": child_data.get("selftext", "")[:500],
                "url": "https://reddit.com" + child_data.get("permalink", ""),
                "author": child_data.get("author", ""),
                "timestamp": child_data.get("created_utc", 0),
                "score": child_data.get("score", 0),
                "tags": [],
                "extra": {
                    "subreddit": subreddit,
                    "num_comments": child_data.get("num_comments", 0),
                    "upvote_ratio": child_data.get("upvote_ratio", 0),
                },
            })

        # 写入缓存
        if self.cache:
            self.cache.set("reddit", subreddit, items)

        if self.logger:
            self.logger.info("[reddit] r/{} 获取到 {} 条数据".format(
                subreddit, len(items)
            ))

        return items
