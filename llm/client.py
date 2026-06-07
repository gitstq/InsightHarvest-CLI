"""LLM API客户端 - 支持OpenAI兼容格式的多LLM提供商"""

import json
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


class LLMClient:
    """
    LLM API客户端，支持OpenAI兼容格式

    支持的提供商:
    - OpenAI (gpt-3.5-turbo, gpt-4, etc.)
    - Claude (通过OpenAI兼容接口)
    - GLM/智谱AI (通过OpenAI兼容接口)
    - 其他OpenAI兼容API
    """

    PROVIDERS = {
        "openai": {
            "default_base": "https://api.openai.com/v1",
            "default_model": "gpt-3.5-turbo",
        },
        "claude": {
            "default_base": "https://api.anthropic.com/v1",
            "default_model": "claude-3-haiku-20240307",
        },
        "glm": {
            "default_base": "https://open.bigmodel.cn/api/paas/v4",
            "default_model": "glm-4-flash",
        },
    }

    def __init__(self, config=None, logger=None):
        self.config = config
        self.logger = logger

        self.provider = "openai"
        self.api_key = ""
        self.api_base = "https://api.openai.com/v1"
        self.model = "gpt-3.5-turbo"
        self.temperature = 0.7
        self.max_tokens = 2000
        self.timeout = 60

        if config:
            llm_cfg = config.llm_config
            self.provider = llm_cfg.get("provider", "openai")
            self.api_key = llm_cfg.get("api_key", "")
            self.api_base = llm_cfg.get("api_base", "")
            self.model = llm_cfg.get("model", "")
            self.temperature = llm_cfg.get("temperature", 0.7)
            self.max_tokens = llm_cfg.get("max_tokens", 2000)

        # 设置默认值
        if not self.api_base:
            provider_info = self.PROVIDERS.get(self.provider, {})
            self.api_base = provider_info.get("default_base", "https://api.openai.com/v1")
        if not self.model:
            provider_info = self.PROVIDERS.get(self.provider, {})
            self.model = provider_info.get("default_model", "gpt-3.5-turbo")

    @property
    def is_configured(self):
        """检查是否已配置API Key"""
        return bool(self.api_key)

    def chat(self, messages, system_prompt=None, temperature=None, max_tokens=None):
        """
        发送聊天请求

        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            str: LLM回复内容，失败返回None
        """
        if not self.is_configured:
            if self.logger:
                self.logger.warning("[llm] API Key未配置，跳过LLM分析")
            return None

        # 构建消息
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        # 构建请求体
        payload = {
            "model": self.model,
            "messages": full_messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
        }

        # Claude特殊处理
        if self.provider == "claude":
            return self._chat_claude(full_messages, payload)

        # OpenAI兼容格式
        return self._chat_openai_compatible(payload)

    def _chat_openai_compatible(self, payload):
        """使用OpenAI兼容格式调用API"""
        url = "{}/chat/completions".format(self.api_base.rstrip("/"))

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(self.api_key),
        }

        try:
            data = json.dumps(payload).encode("utf-8")
            req = Request(url, data=data, headers=headers, method="POST")

            if self.logger:
                self.logger.info("[llm] 正在调用 {} ({})...".format(
                    self.provider, self.model
                ))

            with urlopen(req, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))

            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

            if self.logger:
                self.logger.info("[llm] 分析完成 (tokens: {})".format(
                    result.get("usage", {}).get("total_tokens", "N/A")
                ))

            return content

        except HTTPError as e:
            error_body = ""
            try:
                error_body = e.read().decode("utf-8")
            except Exception:
                pass
            if self.logger:
                self.logger.error("[llm] HTTP错误 {}: {} - {}".format(
                    e.code, e.reason, error_body[:200]
                ))
            return None
        except URLError as e:
            if self.logger:
                self.logger.error("[llm] 网络错误: {}".format(str(e.reason)))
            return None
        except (json.JSONDecodeError, KeyError) as e:
            if self.logger:
                self.logger.error("[llm] 响应解析错误: {}".format(str(e)))
            return None
        except Exception as e:
            if self.logger:
                self.logger.error("[llm] 未知错误: {}".format(str(e)))
            return None

    def _chat_claude(self, messages, payload):
        """Claude API特殊处理"""
        url = "{}/messages".format(self.api_base.rstrip("/"))

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }

        # Claude格式: 分离system消息
        system_msg = ""
        claude_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                claude_messages.append(msg)

        claude_payload = {
            "model": self.model,
            "messages": claude_messages,
            "max_tokens": payload.get("max_tokens", self.max_tokens),
            "temperature": payload.get("temperature", self.temperature),
        }
        if system_msg:
            claude_payload["system"] = system_msg

        try:
            data = json.dumps(claude_payload).encode("utf-8")
            req = Request(url, data=data, headers=headers, method="POST")

            with urlopen(req, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))

            content_blocks = result.get("content", [])
            text_parts = [b.get("text", "") for b in content_blocks if b.get("type") == "text"]
            content = "\n".join(text_parts)

            if self.logger:
                usage = result.get("usage", {})
                self.logger.info("[llm] Claude分析完成 (input: {}, output: {})".format(
                    usage.get("input_tokens", "N/A"),
                    usage.get("output_tokens", "N/A"),
                ))

            return content

        except Exception as e:
            if self.logger:
                self.logger.error("[llm] Claude调用失败: {}".format(str(e)))
            return None

    def summarize(self, items, keywords=None):
        """
        对采集数据生成综合分析摘要

        Args:
            items: 数据项列表
            keywords: 关键词列表

        Returns:
            str: 分析摘要
        """
        if not items:
            return None

        system_prompt = (
            "你是一个专业的技术情报分析师。请根据提供的数据源信息，"
            "生成一份简洁、有洞察力的综合分析报告。\n"
            "要求：\n"
            "1. 识别主要趋势和热点话题\n"
            "2. 分析各平台关注焦点的异同\n"
            "3. 提炼关键洞察和潜在影响\n"
            "4. 语言简洁专业，使用中文\n"
            "5. 控制在500字以内"
        )

        # 构建数据摘要
        data_summary = "采集到 {} 条数据，来自以下来源：\n\n".format(len(items))

        source_groups = {}
        for item in items:
            source = item.get("source", "unknown")
            if source not in source_groups:
                source_groups[source] = []
            source_groups[source].append(item)

        for source, source_items in source_groups.items():
            data_summary += "【{}】({}条):\n".format(source, len(source_items))
            for item in source_items[:10]:
                title = item.get("title", "")
                score = item.get("score", 0)
                data_summary += "  - {} (score: {})\n".format(title, score)

        if keywords:
            kw_text = ", ".join(
                k.get("keyword", "") for k in keywords[:10]
            )
            data_summary += "\n高频关键词: {}\n".format(kw_text)

        messages = [{"role": "user", "content": data_summary}]

        return self.chat(messages, system_prompt=system_prompt)
