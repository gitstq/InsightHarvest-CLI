"""导出器基类 - 定义数据导出的统一接口"""

import os
import sys
from datetime import datetime


class BaseExporter:
    """所有导出器的基类"""

    name = "base"
    extension = ""

    def __init__(self, config=None, logger=None):
        self.config = config
        self.logger = logger
        self.output_dir = os.getcwd()
        if config:
            self.output_dir = config.get("output", "dir", default=os.getcwd())

    def export(self, items, analysis=None, output_path=None, **kwargs):
        """
        导出数据

        Args:
            items: 数据项列表
            analysis: 分析结果
            output_path: 输出文件路径
            **kwargs: 额外参数

        Returns:
            str: 输出文件路径
        """
        raise NotImplementedError("子类必须实现 export 方法")

    def _ensure_output_dir(self, path):
        """确保输出目录存在"""
        dir_path = os.path.dirname(path)
        if dir_path and not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
            except OSError as e:
                sys.stderr.write("错误: 无法创建输出目录: {}\n".format(str(e)))

    def _generate_filename(self, prefix="report", extension=None):
        """生成默认文件名"""
        ext = extension or self.extension
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = "{}_{}.{}".format(prefix, timestamp, ext)
        return os.path.join(self.output_dir, filename)
