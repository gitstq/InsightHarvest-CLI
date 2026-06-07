"""GitHub Trending采集器 - 通过解析GitHub Trending页面采集数据"""

import re
from harvesters.base import BaseHarvester


class GitHubTrendingHarvester(BaseHarvester):
    """GitHub Trending采集器，通过解析HTML页面获取趋势仓库"""

    name = "github_trending"
    description = "GitHub Trending仓库采集"

    BASE_URL = "https://github.com/trending"

    def __init__(self, config=None, cache=None, logger=None):
        super().__init__(config, cache, logger)

    def fetch(self, keywords=None, days=7, limit=None, language="", since="weekly"):
        """
        采集GitHub Trending数据

        Args:
            keywords: 关键词过滤列表
            days: 时间范围
            limit: 最大条数
            language: 编程语言过滤
            since: 时间范围 (daily/weekly/monthly)
        """
        all_items = []

        # 构建URL
        url = self.BASE_URL
        if language:
            url += "/{}".format(language)
        url += "?since={}".format(since)

        if self.logger:
            self.logger.info("[github] 正在采集 Trending (lang={}, since={})...".format(
                language or "all", since
            ))

        # 尝试缓存
        cache_key = "trending_{}_{}".format(language or "all", since)
        if self.cache:
            cached = self.cache.get("github_trending", cache_key)
            if cached:
                all_items = cached
                if self.logger:
                    self.logger.debug("[github] 缓存命中")
            else:
                html = self._fetch_url(url)
                if html:
                    all_items = self._parse_html(html)
                    if self.cache:
                        self.cache.set("github_trending", cache_key, all_items)
        else:
            html = self._fetch_url(url)
            if html:
                all_items = self._parse_html(html)

        # 标准化
        normalized = [self._normalize_item(item) for item in all_items]

        # 过滤
        normalized = self._filter_by_keywords(normalized, keywords)
        normalized = self._apply_limits(normalized, limit)

        return normalized

    def _parse_html(self, html):
        """解析GitHub Trending页面HTML"""
        items = []

        # 使用正则表达式提取仓库信息
        # 匹配仓库条目: <article class="Box-row">
        article_pattern = re.compile(
            r'<article[^>]*class="Box-row"[^>]*>(.*?)</article>',
            re.DOTALL
        )

        articles = article_pattern.findall(html)

        for article in articles:
            item = self._parse_article(article)
            if item:
                items.append(item)

        return items

    def _parse_article(self, article_html):
        """解析单个仓库条目"""
        item = {}

        # 提取仓库链接和名称
        link_match = re.search(
            r'<h2[^>]*>.*?<a[^>]*href="(/[^"]+)"[^>]*>(.*?)</a>',
            article_html, re.DOTALL
        )
        if link_match:
            repo_path = link_match.group(1).strip()
            item["url"] = "https://github.com{}".format(repo_path)
            item["title"] = repo_path.lstrip("/")
        else:
            return None

        # 提取描述
        desc_match = re.search(
            r'<p[^>]*class="[^"]*col-9[^"]*"[^>]*>(.*?)</p>',
            article_html, re.DOTALL
        )
        if desc_match:
            desc = re.sub(r'<[^>]+>', '', desc_match.group(1)).strip()
            item["description"] = desc
        else:
            item["description"] = ""

        # 提取编程语言
        lang_match = re.search(
            r'<span[^>]*itemprop="programmingLanguage"[^>]*>(.*?)</span>',
            article_html, re.DOTALL
        )
        item["extra"] = {
            "language": lang_match.group(1).strip() if lang_match else "",
        }

        # 提取星标数
        stars_match = re.search(
            r'<a[^>]*href="/{}[^"]*"/stargazers"[^>]*>\s*<svg[^>]*>.*?</svg>\s*([\d,]+)\s*</a>'.format(
                re.escape(item["title"])
            ),
            article_html, re.DOTALL
        )
        if stars_match:
            item["score"] = int(stars_match.group(1).replace(",", ""))
        else:
            # 备用匹配
            stars_alt = re.search(
                r'class="d-inline-block float-sm-right"[^>]*>\s*<svg[^>]*>.*?</svg>\s*([\d,]+)\s*</a>',
                article_html, re.DOTALL
            )
            item["score"] = int(stars_alt.group(1).replace(",", "")) if stars_alt else 0

        # 提取今日星标
        today_match = re.search(
            r'([\d,]+)\s*stars\s*(today|this week|this month)',
            article_html, re.DOTALL
        )
        if today_match:
            item["extra"]["stars_period"] = today_match.group(1).replace(",", "")

        item["author"] = item["title"].split("/")[0] if "/" in item["title"] else ""
        item["timestamp"] = ""
        item["tags"] = [item["extra"]["language"]] if item["extra"]["language"] else []

        return item
