"""配置管理模块 - 管理应用配置和API密钥"""

import os
import json
import sys


class Config:
    """应用配置管理器，支持配置文件和环境变量"""

    DEFAULT_CONFIG = {
        "llm": {
            "provider": "openai",
            "api_key": "",
            "api_base": "https://api.openai.com/v1",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 2000,
        },
        "harvest": {
            "timeout": 30,
            "user_agent": "InsightHarvest-CLI/1.0",
            "max_items": 50,
        },
        "cache": {
            "enabled": True,
            "dir": "",
            "ttl": 3600,
        },
        "output": {
            "format": "markdown",
            "dir": "",
        },
    }

    _instance = None

    def __new__(cls, config_path=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, config_path=None):
        if self._initialized:
            return
        self._initialized = True

        self._config = dict(self.DEFAULT_CONFIG)

        # 确定配置文件路径
        if config_path is None:
            config_path = os.path.join(
                os.path.expanduser("~"),
                ".insight_harvest",
                "config.json"
            )
        self.config_path = config_path

        # 设置缓存目录
        if not self._config["cache"]["dir"]:
            self._config["cache"]["dir"] = os.path.join(
                os.path.expanduser("~"),
                ".insight_harvest",
                "cache"
            )

        # 设置输出目录
        if not self._config["output"]["dir"]:
            self._config["output"]["dir"] = os.getcwd()

        # 加载配置文件
        self._load_config()

        # 环境变量覆盖
        self._load_env()

    def _load_config(self):
        """从配置文件加载配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    file_config = json.load(f)
                self._deep_merge(self._config, file_config)
            except (json.JSONDecodeError, IOError) as e:
                sys.stderr.write("警告: 无法加载配置文件 {}: {}\n".format(
                    self.config_path, str(e)
                ))

    def _load_env(self):
        """从环境变量加载敏感配置"""
        env_map = {
            "INSIGHTHARVEST_LLM_API_KEY": ("llm", "api_key"),
            "INSIGHTHARVEST_LLM_API_BASE": ("llm", "api_base"),
            "INSIGHTHARVEST_LLM_MODEL": ("llm", "model"),
            "INSIGHTHARVEST_LLM_PROVIDER": ("llm", "provider"),
            "OPENAI_API_KEY": ("llm", "api_key"),
            "CLAUDE_API_KEY": ("llm", "api_key"),
        }

        for env_var, (section, key) in env_map.items():
            value = os.environ.get(env_var)
            if value:
                # 如果API_KEY环境变量已设置，直接覆盖
                self._config[section][key] = value

    def _deep_merge(self, base, override):
        """深度合并字典"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def get(self, section, key=None, default=None):
        """获取配置值"""
        if key is None:
            return self._config.get(section, default)
        return self._config.get(section, {}).get(key, default)

    def set(self, section, key, value):
        """设置配置值"""
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value

    def save(self, path=None):
        """保存配置到文件"""
        save_path = path or self.config_path
        try:
            save_dir = os.path.dirname(save_path)
            if save_dir and not os.path.exists(save_dir):
                os.makedirs(save_dir, exist_ok=True)
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
        except (IOError, OSError) as e:
            sys.stderr.write("错误: 无法保存配置文件: {}\n".format(str(e)))

    @property
    def llm_config(self):
        return self._config["llm"]

    @property
    def harvest_config(self):
        return self._config["harvest"]

    @property
    def cache_config(self):
        return self._config["cache"]

    @property
    def output_config(self):
        return self._config["output"]

    def __repr__(self):
        return "Config(path={!r})".format(self.config_path)
