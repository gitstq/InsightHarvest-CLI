"""Product Hunt采集器 - 通过GraphQL API采集数据"""

import json
from harvesters.base import BaseHarvester


class ProductHuntHarvester(BaseHarvester):
    """Product Hunt数据采集器，使用公开API"""

    name = "producthunt"
    description = "Product Hunt热门产品采集"

    API_BASE = "https://www.producthunt.com"

    def __init__(self, config=None, cache=None, logger=None):
        super().__init__(config, cache, logger)

    def fetch(self, keywords=None, days=7, limit=None):
        """
        采集Product Hunt数据

        通过解析Product Hunt的RSS feed获取数据
        """
        all_items = []

        # Product Hunt提供RSS feed
        rss_url = "https://www.producthunt.com/feed"

        if self.logger:
            self.logger.info("[producthunt] 正在采集热门产品...")

        # 尝试缓存
        if self.cache:
            cached = self.cache.get("producthunt", "feed")
            if cached:
                all_items = cached
            else:
                all_items = self._fetch_and_parse(rss_url)
                if self.cache:
                    self.cache.set("producthunt", "feed", all_items)
        else:
            all_items = self._fetch_and_parse(rss_url)

        # 标准化
        normalized = [self._normalize_item(item) for item in all_items]

        # 过滤
        normalized = self._filter_by_date(normalized, days)
        normalized = self._filter_by_keywords(normalized, keywords)
        normalized = self._apply_limits(normalized, limit)

        return normalized

    def _fetch_and_parse(self, url):
        """获取并解析RSS"""
        text = self._fetch_url(url)
        if not text:
            return []

        return self._parse_rss(text)

    def _parse_rss(self, text):
        """简单RSS解析"""
        items = []

        # 提取所有item
        item_pattern = re.compile(
            r'<item>(.*?)</item>',
            re.DOTALL
        ) if 'import re' in dir() else None

        # 使用html.parser来解析
        try:
            from html.parser import HTMLParser

            class PHFeedParser(HTMLParser):
                def __init__(self_inner):
                    super().__init__()
                    self_inner.items = []
                    self_inner.current_item = None
                    self_inner.current_tag = None
                    self_inner.current_data = ""

                def handle_starttag(self_inner, tag, attrs):
                    tag_lower = tag.lower()
                    if tag_lower == "item":
                        self_inner.current_item = {}
                    self_inner.current_tag = tag_lower

                def handle_endtag(self_inner, tag):
                    tag_lower = tag.lower()
                    if tag_lower == "item" and self_inner.current_item:
                        self_inner.items.append(self_inner.current_item)
                        self_inner.current_item = None
                    elif self_inner.current_item is not None:
                        if tag_lower in self_inner.current_item:
                            self_inner.current_item[tag_lower] += self_inner.current_data
                        else:
                            self_inner.current_item[tag_lower] = self_inner.current_data
                    self_inner.current_data = ""

                def handle_data(self_inner, data):
                    self_inner.current_data += data

            parser = PHFeedParser()
            parser.feed(text)

            for raw_item in parser.items:
                item = {
                    "title": raw_item.get("title", "").strip(),
                    "description": raw_item.get("description", "").strip(),
                    "url": raw_item.get("link", "").strip(),
                    "author": "",
                    "timestamp": raw_item.get("pubdate", ""),
                    "score": 0,
                    "tags": [],
                    "extra": {},
                }
                items.append(item)

        except Exception as e:
            if self.logger:
                self.logger.error("[producthunt] 解析失败: {}".format(str(e)))

        return items


# 需要import re
import re
