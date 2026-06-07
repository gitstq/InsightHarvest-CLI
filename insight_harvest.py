#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InsightHarvest-CLI
轻量级终端AI多源情报采集与综合分析引擎
Lightweight Terminal AI Multi-Source Intelligence Harvesting & Synthesis Engine

Usage:
    python insight_harvest.py --help
    python insight_harvest.py collect --sources hackernews,reddit --days 7
    python insight_harvest.py collect --sources all --keywords "AI,LLM" --days 30
    python insight_harvest.py collect --sources hackernews --export markdown --output report.md
    python insight_harvest.py dashboard --sources hackernews,reddit
    python insight_harvest.py analyze --sources all --days 7 --llm
"""

import sys
import os
import argparse
import json

# 确保项目根目录在Python路径中
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)


def create_argument_parser():
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog="insight_harvest",
        description=(
            "InsightHarvest-CLI - 轻量级终端AI多源情报采集与综合分析引擎\n"
            "Lightweight Terminal AI Multi-Source Intelligence Harvesting & Synthesis Engine"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "\nExamples:\n"
            "  %(prog)s collect --sources hackernews,reddit --days 7\n"
            "  %(prog)s collect --sources all --keywords 'AI,LLM,GPT' --export markdown\n"
            "  %(prog)s collect --sources github_trending --language python --export html\n"
            "  %(prog)s dashboard --sources hackernews,reddit,github_trending\n"
            "  %(prog)s analyze --sources all --days 7 --llm --export json\n"
            "\nSources: hackernews, reddit, github_trending, producthunt, rss, all"
        ),
    )

    parser.add_argument(
        "--version", "-v",
        action="version",
        version="InsightHarvest-CLI v1.0.0"
    )

    parser.add_argument(
        "--config", "-c",
        type=str, default=None,
        help="配置文件路径 (default: ~/.insight_harvest/config.json)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试日志"
    )

    parser.add_argument(
        "--log-file",
        type=str, default=None,
        help="日志文件路径"
    )

    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="禁用缓存"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        help="可用命令",
        metavar="COMMAND"
    )

    # ===== collect 命令 =====
    collect_parser = subparsers.add_parser(
        "collect",
        help="采集数据并导出报告",
        description="从多个数据源采集数据，进行分析并导出报告"
    )

    collect_parser.add_argument(
        "--sources", "-s",
        type=str, default="all",
        help="数据源 (hackernews,reddit,github_trending,producthunt,rss,all)"
    )

    collect_parser.add_argument(
        "--keywords", "-k",
        type=str, default=None,
        help="关键词过滤，逗号分隔 (e.g., 'AI,LLM,GPT')"
    )

    collect_parser.add_argument(
        "--days", "-d",
        type=int, default=7,
        help="时间范围天数 (default: 7)"
    )

    collect_parser.add_argument(
        "--limit", "-l",
        type=int, default=None,
        help="每个来源最大条数"
    )

    collect_parser.add_argument(
        "--export", "-e",
        type=str, default=None,
        choices=["markdown", "json", "html"],
        help="导出格式"
    )

    collect_parser.add_argument(
        "--output", "-o",
        type=str, default=None,
        help="输出文件路径"
    )

    collect_parser.add_argument(
        "--language",
        type=str, default="",
        help="GitHub Trending语言过滤"
    )

    collect_parser.add_argument(
        "--since",
        type=str, default="weekly",
        choices=["daily", "weekly", "monthly"],
        help="GitHub Trending时间范围 (default: weekly)"
    )

    collect_parser.add_argument(
        "--rss-urls",
        type=str, default=None,
        help="自定义RSS URL，逗号分隔"
    )

    collect_parser.add_argument(
        "--subreddits",
        type=str, default=None,
        help="自定义Reddit子版块，逗号分隔"
    )

    collect_parser.add_argument(
        "--no-dedup",
        action="store_true",
        help="禁用去重"
    )

    collect_parser.add_argument(
        "--no-keywords",
        action="store_true",
        help="禁用关键词提取"
    )

    collect_parser.add_argument(
        "--llm",
        action="store_true",
        help="启用LLM分析摘要"
    )

    collect_parser.add_argument(
        "--title",
        type=str, default="InsightHarvest Report",
        help="报告标题"
    )

    # ===== dashboard 命令 =====
    dash_parser = subparsers.add_parser(
        "dashboard",
        help="启动TUI交互式仪表盘",
        description="在终端中启动交互式数据浏览仪表盘"
    )

    dash_parser.add_argument(
        "--sources", "-s",
        type=str, default="all",
        help="数据源 (hackernews,reddit,github_trending,producthunt,rss,all)"
    )

    dash_parser.add_argument(
        "--keywords", "-k",
        type=str, default=None,
        help="关键词过滤，逗号分隔"
    )

    dash_parser.add_argument(
        "--days", "-d",
        type=int, default=7,
        help="时间范围天数"
    )

    dash_parser.add_argument(
        "--limit", "-l",
        type=int, default=None,
        help="每个来源最大条数"
    )

    # ===== analyze 命令 =====
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="分析数据（不导出）",
        description="采集数据并进行分析，结果输出到终端"
    )

    analyze_parser.add_argument(
        "--sources", "-s",
        type=str, default="all",
        help="数据源"
    )

    analyze_parser.add_argument(
        "--keywords", "-k",
        type=str, default=None,
        help="关键词过滤"
    )

    analyze_parser.add_argument(
        "--days", "-d",
        type=int, default=7,
        help="时间范围天数"
    )

    analyze_parser.add_argument(
        "--limit", "-l",
        type=int, default=None,
        help="每个来源最大条数"
    )

    analyze_parser.add_argument(
        "--export", "-e",
        type=str, default=None,
        choices=["markdown", "json", "html"],
        help="导出格式"
    )

    analyze_parser.add_argument(
        "--output", "-o",
        type=str, default=None,
        help="输出文件路径"
    )

    analyze_parser.add_argument(
        "--llm",
        action="store_true",
        help="启用LLM分析摘要"
    )

    # ===== config 命令 =====
    config_parser = subparsers.add_parser(
        "config",
        help="管理配置",
        description="查看或管理InsightHarvest配置"
    )

    config_parser.add_argument(
        "--show",
        action="store_true",
        help="显示当前配置"
    )

    config_parser.add_argument(
        "--set",
        type=str, nargs=2, metavar=("KEY", "VALUE"),
        help="设置配置项 (e.g., --set llm.provider openai)"
    )

    config_parser.add_argument(
        "--init",
        action="store_true",
        help="初始化默认配置文件"
    )

    # ===== cache 命令 =====
    cache_parser = subparsers.add_parser(
        "cache",
        help="管理缓存",
        description="查看或管理本地数据缓存"
    )

    cache_parser.add_argument(
        "--stats",
        action="store_true",
        help="显示缓存统计"
    )

    cache_parser.add_argument(
        "--clear",
        action="store_true",
        help="清空所有缓存"
    )

    cache_parser.add_argument(
        "--cleanup",
        action="store_true",
        help="清理过期缓存"
    )

    return parser


def parse_sources(source_str):
    """解析数据源参数"""
    sources = [s.strip() for s in source_str.split(",") if s.strip()]
    if "all" in sources:
        return ["hackernews", "reddit", "github_trending", "producthunt"]
    return sources


def parse_keywords(keyword_str):
    """解析关键词参数"""
    if not keyword_str:
        return None
    return [k.strip() for k in keyword_str.split(",") if k.strip()]


def cmd_collect(args, config, logger, cache):
    """执行collect命令"""
    from harvesters import HARVESTER_REGISTRY
    from analyzers.deduplicator import Deduplicator
    from analyzers.keyword_extractor import KeywordExtractor
    from analyzers.trend_analyzer import TrendAnalyzer
    from exporters import EXPORTER_REGISTRY
    from llm.client import LLMClient

    sources = parse_sources(args.sources)
    keywords = parse_keywords(args.keywords)

    # 采集数据
    all_items = []
    for source_name in sources:
        harvester_class = HARVESTER_REGISTRY.get(source_name)
        if not harvester_class:
            logger.warning("未知数据源: {}".format(source_name))
            continue

        harvester = harvester_class(config=config, cache=cache, logger=logger)

        # 来源特定参数
        fetch_kwargs = {
            "keywords": keywords,
            "days": args.days,
            "limit": args.limit,
        }

        if source_name == "github_trending":
            fetch_kwargs["language"] = args.language
            fetch_kwargs["since"] = args.since
        elif source_name == "rss":
            if args.rss_urls:
                fetch_kwargs["feed_urls"] = args.rss_urls.split(",")
        elif source_name == "reddit":
            if args.subreddits:
                fetch_kwargs["subreddits"] = args.subreddits.split(",")

        try:
            items = harvester.fetch(**fetch_kwargs)
            all_items.extend(items)
            logger.info("[collect] {} 采集到 {} 条数据".format(source_name, len(items)))
        except Exception as e:
            logger.error("[collect] {} 采集失败: {}".format(source_name, str(e)))

    if not all_items:
        logger.warning("未采集到任何数据")
        print("No data collected. Check your network connection and try again.")
        return

    # 按分数排序
    all_items.sort(key=lambda x: x.get("score", 0), reverse=True)

    # 去重
    if not args.no_dedup:
        dedup = Deduplicator(config=config, logger=logger)
        all_items, duplicates = dedup.analyze(all_items)

    # 关键词提取
    keywords_result = []
    if not args.no_keywords:
        extractor = KeywordExtractor(config=config, logger=logger)
        keywords_result = extractor.analyze(all_items)

    # 趋势分析
    trend = TrendAnalyzer(config=config, logger=logger)
    analysis = trend.analyze(all_items)

    # LLM分析
    llm_summary = ""
    if args.llm:
        llm_client = LLMClient(config=config, logger=logger)
        llm_summary = llm_client.summarize(all_items, keywords_result) or ""

    # 导出
    if args.export:
        exporter_class = EXPORTER_REGISTRY.get(args.export)
        if exporter_class:
            exporter = exporter_class(config=config, logger=logger)
            output_path = exporter.export(
                all_items,
                analysis=analysis,
                output_path=args.output,
                title=args.title,
                keywords=keywords_result,
                llm_summary=llm_summary,
            )
            print("\nReport exported to: {}".format(output_path))
        else:
            logger.error("未知导出格式: {}".format(args.export))
    else:
        # 终端输出摘要
        print_summary(all_items, analysis, keywords_result, llm_summary)


def cmd_dashboard(args, config, logger, cache):
    """执行dashboard命令"""
    from harvesters import HARVESTER_REGISTRY
    from analyzers.deduplicator import Deduplicator
    from analyzers.keyword_extractor import KeywordExtractor
    from analyzers.trend_analyzer import TrendAnalyzer
    from ui.dashboard import Dashboard

    sources = parse_sources(args.sources)
    keywords = parse_keywords(args.keywords)

    print("Collecting data from {} sources...".format(len(sources)))

    all_items = []
    for source_name in sources:
        harvester_class = HARVESTER_REGISTRY.get(source_name)
        if not harvester_class:
            continue

        harvester = harvester_class(config=config, cache=cache, logger=logger)
        try:
            items = harvester.fetch(
                keywords=keywords,
                days=args.days,
                limit=args.limit,
            )
            all_items.extend(items)
        except Exception as e:
            logger.error("[dashboard] {} 采集失败: {}".format(source_name, str(e)))

    if not all_items:
        print("No data collected. Check your network connection.")
        return

    # 排序和去重
    all_items.sort(key=lambda x: x.get("score", 0), reverse=True)
    dedup = Deduplicator(config=config, logger=logger)
    all_items, _ = dedup.analyze(all_items)

    # 分析
    extractor = KeywordExtractor(config=config, logger=logger)
    keywords_result = extractor.analyze(all_items)

    trend = TrendAnalyzer(config=config, logger=logger)
    analysis = trend.analyze(all_items)

    # 启动TUI
    print("Launching TUI dashboard... (Press 'q' to quit)")
    dashboard = Dashboard(
        items=all_items,
        analysis=analysis,
        keywords=keywords_result,
        logger=logger,
    )
    dashboard.run()


def cmd_analyze(args, config, logger, cache):
    """执行analyze命令"""
    # analyze与collect类似，但默认不导出
    args.no_dedup = False
    args.no_keywords = False
    args.title = "InsightHarvest Analysis"
    args.language = ""
    args.since = "weekly"
    args.rss_urls = None
    args.subreddits = None

    cmd_collect(args, config, logger, cache)


def cmd_config(args, config, logger, cache):
    """执行config命令"""
    if args.init:
        config.save()
        print("Configuration initialized at: {}".format(config.config_path))
        return

    if args.show:
        import json
        # 隐藏API Key
        display_config = dict(config._config)
        if "api_key" in display_config.get("llm", {}):
            key = display_config["llm"]["api_key"]
            if key:
                display_config["llm"]["api_key"] = key[:8] + "..." + key[-4:]
        print(json.dumps(display_config, indent=2, ensure_ascii=False))
        return

    if args.set:
        section, key = args.set[0].split(".", 1)
        value = args.set[1]
        config.set(section, key, value)
        config.save()
        print("Configuration saved: {}.{} = {}".format(section, key, value))
        return

    print("Use --show, --init, or --set KEY VALUE")


def cmd_cache(args, config, logger, cache):
    """执行cache命令"""
    if args.stats:
        stats = cache.stats()
        print("Cache Statistics:")
        print("  Total entries: {}".format(stats["total"]))
        print("  Expired entries: {}".format(stats["expired"]))
        print("  Size: {} bytes".format(stats["size_bytes"]))
        print("  Directory: {}".format(cache.cache_dir))
        return

    if args.clear:
        cache.clear()
        print("Cache cleared.")
        return

    if args.cleanup:
        count = cache.cleanup_expired()
        print("Cleaned up {} expired entries.".format(count or 0))
        return

    print("Use --stats, --clear, or --cleanup")


def print_summary(items, analysis, keywords, llm_summary=""):
    """在终端打印数据摘要"""
    print("\n" + "=" * 60)
    print("  InsightHarvest-CLI Report Summary")
    print("=" * 60)

    # 统计
    stats = analysis.get("statistics", {})
    print("\n  Total Items:    {}".format(len(items)))
    print("  Total Score:    {}".format(stats.get("total_score", 0)))
    print("  Average Score:  {}".format(stats.get("avg_score", 0)))

    # 来源分布
    source_dist = analysis.get("source_distribution", {})
    if source_dist:
        print("\n  Source Distribution:")
        for source, count in sorted(source_dist.items(), key=lambda x: x[1], reverse=True):
            print("    {:>20s}: {}".format(source, count))

    # 关键词
    if keywords:
        print("\n  Top Keywords:")
        for kw in keywords[:10]:
            print("    {:>20s} (freq: {:>3d}, tfidf: {:.4f})".format(
                kw.get("keyword", ""),
                kw.get("frequency", 0),
                kw.get("tfidf_score", 0),
            ))

    # 热门条目
    top_items = analysis.get("top_items", [])
    if top_items:
        print("\n  Top Items:")
        for i, item in enumerate(top_items[:10], 1):
            print("    {:>2d}. [{}] {} (score: {})".format(
                i,
                item.get("source", "?")[:8],
                item.get("title", "")[:60],
                item.get("score", 0),
            ))

    # LLM摘要
    if llm_summary:
        print("\n  AI Analysis Summary:")
        print("  " + "-" * 56)
        for line in llm_summary.split("\n"):
            print("  " + line)
        print("  " + "-" * 56)

    print("\n" + "=" * 60)
    print("  Use --export markdown|json|html to save full report")
    print("=" * 60 + "\n")


def main():
    """主入口函数"""
    parser = create_argument_parser()
    args = parser.parse_args()

    # 初始化配置
    from utils.config import Config
    from utils.logger import get_logger
    from utils.cache import Cache

    config = Config(config_path=args.config)
    log_level = "DEBUG" if args.debug else "INFO"
    logger = get_logger(level=log_level, log_file=args.log_file)

    # 初始化缓存
    if args.no_cache:
        cache = None
    else:
        cache = Cache(
            cache_dir=config.get("cache", "dir"),
            ttl=config.get("cache", "ttl", default=3600),
        )

    # 执行命令
    if args.command == "collect":
        cmd_collect(args, config, logger, cache)
    elif args.command == "dashboard":
        cmd_dashboard(args, config, logger, cache)
    elif args.command == "analyze":
        cmd_analyze(args, config, logger, cache)
    elif args.command == "config":
        cmd_config(args, config, logger, cache)
    elif args.command == "cache":
        cmd_cache(args, config, logger, cache)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == "__main__":
    main()
