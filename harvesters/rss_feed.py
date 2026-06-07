"""通用RSS采集器 - 支持任意RSS/Atom Feed"""

from harvesters.base import BaseHarvester
from html.parser import HTMLParser


class RSSFeedHarvester(BaseHarvester):
    """通用RSS/Atom Feed采集器"""

    name = "rss"
    description = "通用RSS/Atom Feed采集"

    def __init__(self, config=None, cache=None, logger=None):
        super().__init__(config, cache, logger)
        self.feeds = []

    def fetch(self, keywords=None, days=7, limit=None, feed_urls=None):
        """
        采集RSS Feed数据

        Args:
            keywords: 关键词过滤列表
            days: 时间范围
            limit: 最大条数
            feed_urls: RSS Feed URL列表
        """
        urls = feed_urls or self.feeds
        if not urls:
            if self.logger:
                self.logger.warning("[rss] 未指定Feed URL")
            return []

        all_items = []

        for url in urls:
            if self.logger:
                self.logger.info("[rss] 正在采集: {}".format(url))

            # 尝试缓存
            if self.cache:
                cached = self.cache.get("rss", url)
                if cached:
                    all_items.extend(cached)
                    continue

            text = self._fetch_url(url)
            if not text:
                continue

            items = self._parse_feed(text, url)
            if items:
                all_items.extend(items)
                if self.cache:
                    self.cache.set("rss", url, items)

        # 标准化
        normalized = [self._normalize_item(item) for item in all_items]

        # 过滤
        normalized = self._filter_by_date(normalized, days)
        normalized = self._filter_by_keywords(normalized, keywords)
        normalized = self._apply_limits(normalized, limit)

        return normalized

    def _parse_feed(self, text, source_url=""):
        """解析RSS或Atom Feed"""
        # 检测是RSS还是Atom
        if "<feed" in text.lower() and "atom" in text.lower():
            return self._parse_atom(text, source_url)
        return self._parse_rss(text, source_url)

    def _parse_rss(self, text, source_url=""):
        """解析RSS 2.0格式"""
        parser = _RSSParser()
        try:
            parser.feed(text)
        except Exception as e:
            if self.logger:
                self.logger.error("[rss] RSS解析错误: {}".format(str(e)))
            return []

        items = []
        for entry in parser.items:
            items.append({
                "title": entry.get("title", "").strip(),
                "description": entry.get("description", "").strip(),
                "url": entry.get("link", "").strip(),
                "author": entry.get("author", "").strip(),
                "timestamp": entry.get("pubdate", ""),
                "score": 0,
                "tags": [],
                "extra": {
                    "feed_url": source_url,
                    "categories": entry.get("categories", []),
                },
            })

        return items

    def _parse_atom(self, text, source_url=""):
        """解析Atom格式"""
        parser = _AtomParser()
        try:
            parser.feed(text)
        except Exception as e:
            if self.logger:
                self.logger.error("[rss] Atom解析错误: {}".format(str(e)))
            return []

        items = []
        for entry in parser.entries:
            items.append({
                "title": entry.get("title", "").strip(),
                "description": entry.get("summary", "").strip(),
                "url": entry.get("link", "").strip(),
                "author": entry.get("author", "").strip(),
                "timestamp": entry.get("updated", entry.get("published", "")),
                "score": 0,
                "tags": [],
                "extra": {
                    "feed_url": source_url,
                    "categories": entry.get("categories", []),
                },
            })

        return items


class _RSSParser(HTMLParser):
    """简单的RSS 2.0解析器"""

    def __init__(self):
        super().__init__()
        self.items = []
        self.current_item = None
        self.current_tag = ""
        self.current_data = ""
        self.in_item = False

    def handle_starttag(self, tag, attrs):
        tag_lower = tag.lower()
        if tag_lower == "item":
            self.in_item = True
            self.current_item = {}
        self.current_tag = tag_lower
        self.current_data = ""

    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if tag_lower == "item":
            if self.current_item:
                self.items.append(self.current_item)
            self.current_item = None
            self.in_item = False
        elif self.in_item and self.current_item is not None:
            key = tag_lower
            if key in self.current_item:
                self.current_item[key] += self.current_data.strip()
            else:
                self.current_item[key] = self.current_data.strip()
        self.current_data = ""

    def handle_data(self, data):
        self.current_data += data


class _AtomParser(HTMLParser):
    """简单的Atom Feed解析器"""

    def __init__(self):
        super().__init__()
        self.entries = []
        self.current_entry = None
        self.current_tag = ""
        self.current_data = ""
        self.in_entry = False
        self.link_href = ""

    def handle_starttag(self, tag, attrs):
        tag_lower = tag.lower()
        if tag_lower == "entry":
            self.in_entry = True
            self.current_entry = {}
        self.current_tag = tag_lower
        self.current_data = ""

        # Atom link标签
        if tag_lower == "link" and self.in_entry:
            for attr_name, attr_value in attrs:
                if attr_name.lower() == "href":
                    self.link_href = attr_value
                elif attr_name.lower() == "rel" and attr_value != "alternate":
                    self.link_href = ""

    def handle_endtag(self, tag):
        tag_lower = tag.lower()
        if tag_lower == "entry":
            if self.current_entry:
                self.entries.append(self.current_entry)
            self.current_entry = None
            self.in_entry = False
        elif self.in_entry and self.current_entry is not None:
            if tag_lower == "link":
                self.current_entry["link"] = self.link_href
                self.link_href = ""
            else:
                key = tag_lower
                if key in self.current_entry:
                    self.current_entry[key] += self.current_data.strip()
                else:
                    self.current_entry[key] = self.current_data.strip()
        self.current_data = ""

    def handle_data(self, data):
        self.current_data += data
