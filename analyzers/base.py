"""分析器基类 - 定义数据分析器的统一接口"""


class BaseAnalyzer:
    """所有分析器的基类"""

    name = "base"
    description = "Base analyzer"

    def __init__(self, config=None, logger=None):
        self.config = config
        self.logger = logger

    def analyze(self, items):
        """
        分析数据

        Args:
            items: 数据项列表

        Returns:
            分析结果
        """
        raise NotImplementedError("子类必须实现 analyze 方法")
