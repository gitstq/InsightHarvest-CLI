"""数据采集器模块"""

from harvesters.base import BaseHarvester
from harvesters.reddit import RedditHarvester
from harvesters.hackernews import HackerNewsHarvester
from harvesters.github_trending import GitHubTrendingHarvester
from harvesters.producthunt import ProductHuntHarvester
from harvesters.rss_feed import RSSFeedHarvester

HARVESTER_REGISTRY = {
    "reddit": RedditHarvester,
    "hackernews": HackerNewsHarvester,
    "github_trending": GitHubTrendingHarvester,
    "producthunt": ProductHuntHarvester,
    "rss": RSSFeedHarvester,
}

__all__ = [
    "BaseHarvester",
    "RedditHarvester",
    "HackerNewsHarvester",
    "GitHubTrendingHarvester",
    "ProductHuntHarvester",
    "RSSFeedHarvester",
    "HARVESTER_REGISTRY",
]
