"""日志工具模块 - 提供统一的日志管理"""

import sys
import os
import datetime


class Logger:
    """轻量级日志工具，支持多级别输出"""

    LEVELS = {
        "DEBUG": 0,
        "INFO": 1,
        "WARNING": 2,
        "ERROR": 3,
        "CRITICAL": 4,
    }

    COLORS = {
        "DEBUG": "\033[36m",      # 青色
        "INFO": "\033[32m",       # 绿色
        "WARNING": "\033[33m",   # 黄色
        "ERROR": "\033[31m",     # 红色
        "CRITICAL": "\033[35m",  # 紫色
    }
    RESET = "\033[0m"

    _instance = None

    def __new__(cls, level="INFO", log_file=None, use_color=True):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, level="INFO", log_file=None, use_color=True):
        if self._initialized:
            return
        self._initialized = True
        self.level_name = level.upper()
        self.level = self.LEVELS.get(self.level_name, 1)
        self.log_file = log_file
        self.use_color = use_color and hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

    def _format_message(self, level, message):
        """格式化日志消息"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = "[{timestamp}] [{level:>8s}] ".format(
            timestamp=timestamp, level=level
        )
        return prefix + message

    def _output(self, level, message):
        """输出日志"""
        if self.LEVELS.get(level, 0) < self.level:
            return

        formatted = self._format_message(level, message)

        # 彩色输出到终端
        if self.use_color:
            color = self.COLORS.get(level, "")
            sys.stderr.write("{color}{msg}{reset}\n".format(
                color=color, msg=formatted, reset=self.RESET
            ))
        else:
            sys.stderr.write(formatted + "\n")

        # 写入日志文件
        if self.log_file:
            try:
                log_dir = os.path.dirname(self.log_file)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir, exist_ok=True)
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(formatted + "\n")
            except (IOError, OSError) as e:
                sys.stderr.write("无法写入日志文件: {}\n".format(str(e)))

    def debug(self, message):
        self._output("DEBUG", message)

    def info(self, message):
        self._output("INFO", message)

    def warning(self, message):
        self._output("WARNING", message)

    def error(self, message):
        self._output("ERROR", message)

    def critical(self, message):
        self._output("CRITICAL", message)

    def set_level(self, level):
        """动态调整日志级别"""
        self.level_name = level.upper()
        self.level = self.LEVELS.get(self.level_name, 1)


def get_logger(level="INFO", log_file=None, use_color=True):
    """获取全局日志实例"""
    return Logger(level=level, log_file=log_file, use_color=use_color)
