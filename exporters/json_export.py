"""JSON导出器 - 将数据导出为JSON格式"""

import json
import os
from datetime import datetime
from exporters.base import BaseExporter


class JSONExporter(BaseExporter):
    """JSON格式导出器"""

    name = "json"
    extension = "json"

    def export(self, items, analysis=None, output_path=None, title="InsightHarvest Report", **kwargs):
        """
        导出为JSON格式

        Args:
            items: 数据项列表
            analysis: 分析结果字典
            output_path: 输出文件路径
            title: 报告标题
        """
        if output_path is None:
            output_path = self._generate_filename("insight_harvest", "json")

        self._ensure_output_dir(output_path)

        report = {
            "title": title,
            "generated_at": datetime.now().isoformat(),
            "generator": "InsightHarvest-CLI",
            "version": "1.0.0",
            "total_items": len(items),
            "items": items,
        }

        if analysis:
            report["analysis"] = analysis

        keywords = kwargs.get("keywords", [])
        if keywords:
            report["keywords"] = keywords

        llm_summary = kwargs.get("llm_summary", "")
        if llm_summary:
            report["llm_summary"] = llm_summary

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            if self.logger:
                self.logger.info("[export] JSON报告已保存: {}".format(output_path))
        except (IOError, OSError) as e:
            if self.logger:
                self.logger.error("[export] 保存失败: {}".format(str(e)))

        return output_path
