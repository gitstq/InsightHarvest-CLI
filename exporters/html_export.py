"""HTML导出器 - 将数据导出为HTML格式"""

import os
from datetime import datetime
from exporters.base import BaseExporter


class HTMLExporter(BaseExporter):
    """HTML格式导出器"""

    name = "html"
    extension = "html"

    def export(self, items, analysis=None, output_path=None, title="InsightHarvest Report", **kwargs):
        """
        导出为HTML格式

        Args:
            items: 数据项列表
            analysis: 分析结果字典
            output_path: 输出文件路径
            title: 报告标题
        """
        if output_path is None:
            output_path = self._generate_filename("insight_harvest", "html")

        self._ensure_output_dir(output_path)

        html_parts = []

        # HTML头部
        html_parts.append(self._render_header(title))

        # 统计摘要
        if analysis:
            html_parts.append(self._render_summary(analysis))

        # 关键词
        keywords = kwargs.get("keywords", [])
        if keywords:
            html_parts.append(self._render_keywords(keywords))

        # 数据列表
        html_parts.append(self._render_items(items))

        # LLM摘要
        llm_summary = kwargs.get("llm_summary", "")
        if llm_summary:
            html_parts.append(self._render_llm_summary(llm_summary))

        # HTML尾部
        html_parts.append(self._render_footer())

        content = "\n".join(html_parts)

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            if self.logger:
                self.logger.info("[export] HTML报告已保存: {}".format(output_path))
        except (IOError, OSError) as e:
            if self.logger:
                self.logger.error("[export] 保存失败: {}".format(str(e)))

        return output_path

    def _escape_html(self, text):
        """转义HTML特殊字符"""
        if not text:
            return ""
        text = str(text)
        text = text.replace("&", "&amp;")
        text = text.replace("<", "&lt;")
        text = text.replace(">", "&gt;")
        text = text.replace('"', "&quot;")
        text = text.replace("'", "&#39;")
        return text

    def _render_header(self, title):
        """渲染HTML头部"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px;
                background: #f5f5f5; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                   color: white; padding: 30px; border-radius: 12px; margin-bottom: 24px; }}
        .header h1 {{ font-size: 28px; margin-bottom: 8px; }}
        .header .meta {{ opacity: 0.8; font-size: 14px; }}
        .card {{ background: white; border-radius: 8px; padding: 20px; margin-bottom: 16px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .card h2 {{ font-size: 20px; margin-bottom: 16px; color: #555;
                   border-bottom: 2px solid #eee; padding-bottom: 8px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 16px; }}
        .stat {{ text-align: center; padding: 16px; background: #f8f9fa; border-radius: 8px; }}
        .stat .number {{ font-size: 32px; font-weight: bold; color: #667eea; }}
        .stat .label {{ font-size: 12px; color: #888; text-transform: uppercase; }}
        .item {{ padding: 16px; border-bottom: 1px solid #eee; }}
        .item:last-child {{ border-bottom: none; }}
        .item h3 {{ font-size: 16px; margin-bottom: 8px; }}
        .item h3 a {{ color: #667eea; text-decoration: none; }}
        .item h3 a:hover {{ text-decoration: underline; }}
        .item .meta {{ font-size: 12px; color: #888; margin-bottom: 8px; }}
        .item .desc {{ font-size: 14px; color: #555; }}
        .tags {{ display: flex; gap: 6px; flex-wrap: wrap; margin-top: 8px; }}
        .tag {{ background: #e8eaf6; color: #3f51b5; padding: 2px 8px; border-radius: 12px;
               font-size: 12px; }}
        .keywords {{ display: flex; flex-wrap: wrap; gap: 8px; }}
        .keyword {{ background: #fff3e0; color: #e65100; padding: 4px 12px; border-radius: 16px;
                  font-size: 13px; }}
        .keyword .freq {{ font-size: 11px; color: #888; }}
        .llm-summary {{ background: #f3e5f5; padding: 20px; border-radius: 8px;
                       border-left: 4px solid #9c27b0; white-space: pre-wrap; font-size: 14px; }}
        .source-table {{ width: 100%; border-collapse: collapse; }}
        .source-table th, .source-table td {{ padding: 8px 12px; text-align: left;
                                              border-bottom: 1px solid #eee; }}
        .source-table th {{ background: #f8f9fa; font-weight: 600; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <div class="meta">Generated by InsightHarvest-CLI | {timestamp}</div>
    </div>
""".format(
            title=self._escape_html(title),
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

    def _render_summary(self, analysis):
        """渲染统计摘要"""
        stats = analysis.get("statistics", {})
        source_dist = analysis.get("source_distribution", {})

        parts = ['<div class="card"><h2>Summary</h2>']
        parts.append('<div class="stats">')
        parts.append('<div class="stat"><div class="number">{}</div><div class="label">Total Items</div></div>'.format(
            analysis.get("total_items", 0)))
        parts.append('<div class="stat"><div class="number">{}</div><div class="label">Total Score</div></div>'.format(
            stats.get("total_score", 0)))
        parts.append('<div class="stat"><div class="number">{}</div><div class="label">Avg Score</div></div>'.format(
            stats.get("avg_score", 0)))
        parts.append('<div class="stat"><div class="number">{}</div><div class="label">Sources</div></div>'.format(
            len(source_dist)))
        parts.append('</div>')

        if source_dist:
            parts.append('<table class="source-table" style="margin-top:16px">')
            parts.append('<tr><th>Source</th><th>Count</th></tr>')
            for source, count in sorted(source_dist.items(), key=lambda x: x[1], reverse=True):
                parts.append('<tr><td>{}</td><td>{}</td></tr>'.format(
                    self._escape_html(source), count))
            parts.append('</table>')

        parts.append('</div>')
        return "\n".join(parts)

    def _render_keywords(self, keywords):
        """渲染关键词"""
        parts = ['<div class="card"><h2>Top Keywords</h2><div class="keywords">']
        for kw in keywords[:20]:
            parts.append('<span class="keyword">{} <span class="freq">({})</span></span>'.format(
                self._escape_html(kw.get("keyword", "")),
                kw.get("frequency", 0),
            ))
        parts.append('</div></div>')
        return "\n".join(parts)

    def _render_items(self, items):
        """渲染数据列表"""
        parts = ['<div class="card"><h2>Collected Items ({})</h2>'.format(len(items))]
        for item in items:
            parts.append('<div class="item">')
            title = self._escape_html(item.get("title", "Untitled"))
            url = item.get("url", "")
            if url:
                parts.append('<h3><a href="{}" target="_blank">{}</a></h3>'.format(
                    self._escape_html(url), title))
            else:
                parts.append('<h3>{}</h3>'.format(title))

            meta_parts = []
            if item.get("source"):
                meta_parts.append("Source: {}".format(self._escape_html(item.get("source"))))
            if item.get("author"):
                meta_parts.append("Author: {}".format(self._escape_html(item.get("author"))))
            if item.get("score"):
                meta_parts.append("Score: {}".format(item.get("score")))
            if meta_parts:
                parts.append('<div class="meta">{}</div>'.format(" | ".join(meta_parts)))

            desc = item.get("description", "")
            if desc:
                if len(desc) > 300:
                    desc = desc[:300] + "..."
                parts.append('<div class="desc">{}</div>'.format(self._escape_html(desc)))

            tags = item.get("tags", [])
            if tags:
                parts.append('<div class="tags">')
                for tag in tags:
                    parts.append('<span class="tag">{}</span>'.format(self._escape_html(tag)))
                parts.append('</div>')

            parts.append('</div>')
        parts.append('</div>')
        return "\n".join(parts)

    def _render_llm_summary(self, summary):
        """渲染LLM摘要"""
        return '\n<div class="card"><h2>AI Analysis Summary</h2><div class="llm-summary">{}</div></div>'.format(
            self._escape_html(summary)
        )

    def _render_footer(self):
        """渲染HTML尾部"""
        return """
    <div style="text-align:center; padding:20px; color:#888; font-size:12px;">
        InsightHarvest-CLI | Lightweight Terminal AI Multi-Source Intelligence Engine
    </div>
</body>
</html>"""
