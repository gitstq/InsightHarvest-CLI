"""采集器基类 - 定义数据采集器的统一接口"""

import json
import sys
from datetime import datetime, timedelta


class BaseHarvester:
    """所有数据采集器的基类"""

    name = "base"
    description = "Base harvester"

    def __init__(self, config=None, cache=None, logger=None):
        self.config = config
        self.cache = cache
        self.logger = logger
        self.timeout = 30
        self.user_agent = "InsightHarvest-CLI/1.0"
        self.max_items = 50

        if config:
            harvest_cfg = config.get("harvest", default={})
            self.timeout = harvest_cfg.get("timeout", 30)
            self.user_agent = harvest_cfg.get("user_agent", self.user_agent)
            self.max_items = harvest_cfg.get("max_items", 50)

    def fetch(self, keywords=None, days=7, limit=None):
        """
        采集数据的主方法

        Args:
            keywords: 关键词过滤列表
            days: 时间范围（天数）
            limit: 最大返回条数

        Returns:
            list[dict]: 采集到的数据项列表
        """
        raise NotImplementedError("子类必须实现 fetch 方法")

    def _fetch_url(self, url):
        """
        使用urllib获取URL内容

        Args:
            url: 目标URL

        Returns:
            str/bytes: 响应内容
        """
        try:
            from urllib.request import urlopen, Request
            from urllib.error import URLError, HTTPError

            req = Request(
                url,
                headers={"User-Agent": self.user_agent}
            )
            with urlopen(req, timeout=self.timeout) as response:
                content_type = response.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    return response.read().decode("utf-8")
                return response.read().decode("utf-8", errors="replace")
        except HTTPError as e:
            if self.logger:
                self.logger.error("[{}] HTTP错误 {}: {}".format(
                    self.name, e.code, e.reason
                ))
            return None
        except URLError as e:
            if self.logger:
                self.logger.error("[{}] 网络错误: {}".format(
                    self.name, str(e.reason)
                ))
            return None
        except Exception as e:
            if self.logger:
                self.logger.error("[{}] 未知错误: {}".format(self.name, str(e)))
            return None

    def _parse_json(self, text):
        """安全解析JSON"""
        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError, ValueError):
            if self.logger:
                self.logger.debug("[{}] JSON解析失败".format(self.name))
            return None

    def _filter_by_date(self, items, days, date_field="timestamp"):
        """按时间范围过滤"""
        if days <= 0:
            return items

        cutoff = datetime.utcnow() - timedelta(days=days)
        cutoff_ts = cutoff.timestamp()

        filtered = []
        for item in items:
            ts = item.get(date_field, 0)
            if isinstance(ts, str):
                try:
                    ts = datetime.strptime(
                        ts, "%Y-%m-%dT%H:%M:%SZ"
                    ).timestamp()
                except (ValueError, TypeError):
                    try:
                        ts = datetime.strptime(
                            ts, "%Y-%m-%d %H:%M:%S"
                        ).timestamp()
                    except (ValueError, TypeError):
                        continue
            if ts >= cutoff_ts:
                filtered.append(item)

        return filtered

    def _filter_by_keywords(self, items, keywords, fields=None):
        """按关键词过滤"""
        if not keywords:
            return items

        if fields is None:
            fields = ["title", "description", "content"]

        keywords_lower = [k.lower() for k in keywords]

        filtered = []
        for item in items:
            text = " ".join(
                str(item.get(f, "")) for f in fields if item.get(f)
            ).lower()

            if any(kw in text for kw in keywords_lower):
                filtered.append(item)

        return filtered

    def _apply_limits(self, items, limit):
        """应用数量限制"""
        if limit is not None:
            return items[:limit]
        return items[:self.max_items]

    def _normalize_item(self, item):
        """标准化数据项格式"""
        return {
            "source": self.name,
            "title": item.get("title", ""),
            "description": item.get("description", item.get("content", "")),
            "url": item.get("url", item.get("link", "")),
            "author": item.get("author", ""),
            "timestamp": item.get("timestamp", item.get("date", "")),
            "score": item.get("score", 0),
            "tags": item.get("tags", []),
            "extra": item.get("extra", {}),
        }
