#!/usr/bin/env python3
"""
LLM Client Module — 大模型交互层
支持 OpenAI 兼容 API，内置重试、JSON修复、Token管理
"""

import os
import re
import json
import time
from typing import Dict, Any, Optional, List


class LLMClient:
    """LLM交互客户端"""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.api_key = self.config.get("api_key") or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = self.config.get("base_url") or os.environ.get("OPENAI_BASE_URL", "")
        self.model = self.config.get("model", "gpt-4.1-mini")
        self.max_retries = self.config.get("max_retries", 3)
        self.temperature = self.config.get("temperature", 0.3)
        self.max_tokens = self.config.get("max_tokens", 4096)
        self.client = None
        self._init_client()

    def _init_client(self):
        """初始化 OpenAI 客户端"""
        try:
            from openai import OpenAI
            kwargs = {}
            if self.api_key:
                kwargs["api_key"] = self.api_key
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self.client = OpenAI(**kwargs)
        except ImportError:
            print("⚠ openai 库未安装，请运行: pip install openai")
        except Exception as e:
            print(f"⚠ OpenAI 客户端初始化失败: {e}")

    def call_llm(self, prompt: str, system_prompt: str = "",
                 response_json: bool = False, temperature: float = None,
                 max_tokens: int = None) -> Any:
        """
        调用LLM并返回结果

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            response_json: 是否期望JSON响应
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            如果 response_json=True，返回解析后的dict/list
            否则返回原始字符串
        """
        if not self.client:
            raise RuntimeError("LLM客户端未初始化，请检查API配置")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        temp = temperature if temperature is not None else self.temperature
        tokens = max_tokens if max_tokens is not None else self.max_tokens

        last_error = None
        for attempt in range(self.max_retries):
            try:
                kwargs = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": temp,
                    "max_tokens": tokens,
                }
                if response_json:
                    kwargs["response_format"] = {"type": "json_object"}

                response = self.client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content.strip()

                if response_json:
                    return self._parse_json_response(content)
                return content

            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"    ⚠ LLM调用失败(第{attempt+1}次)，{wait_time}秒后重试: {e}")
                    time.sleep(wait_time)

        raise RuntimeError(f"LLM调用失败（已重试{self.max_retries}次）: {last_error}")

    def call_llm_with_history(self, messages: List[Dict], response_json: bool = False,
                               temperature: float = None) -> Any:
        """
        带对话历史的LLM调用（用于多轮交互）

        Args:
            messages: 完整的消息列表 [{"role": "...", "content": "..."}]
            response_json: 是否期望JSON响应

        Returns:
            LLM响应内容
        """
        if not self.client:
            raise RuntimeError("LLM客户端未初始化")

        temp = temperature if temperature is not None else self.temperature

        last_error = None
        for attempt in range(self.max_retries):
            try:
                kwargs = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": temp,
                    "max_tokens": self.max_tokens,
                }
                if response_json:
                    kwargs["response_format"] = {"type": "json_object"}

                response = self.client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content.strip()

                if response_json:
                    return self._parse_json_response(content)
                return content

            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    time.sleep(wait_time)

        raise RuntimeError(f"LLM调用失败: {last_error}")

    def _parse_json_response(self, content: str) -> Any:
        """解析LLM返回的JSON，带容错修复"""
        # 第一次尝试：直接解析
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # 第二次尝试：提取JSON代码块
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # 第三次尝试：提取花括号/方括号包裹的内容
        for pattern in [r'\{[\s\S]*\}', r'\[[\s\S]*\]']:
            match = re.search(pattern, content)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    pass

        # 第四次尝试：修复常见JSON错误
        fixed = self._fix_common_json_errors(content)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass

        # 最后手段：返回原始内容包装
        print(f"    ⚠ JSON解析失败，返回原始内容")
        return {"raw_content": content, "parse_error": True}

    def _fix_common_json_errors(self, text: str) -> str:
        """修复常见的JSON格式错误"""
        text = re.sub(r'//.*?$', '', text, flags=re.MULTILINE)
        text = re.sub(r',\s*([}\]])', r'\1', text)
        text = text.replace("'", '"')
        match = re.search(r'[{\[][\s\S]*[}\]]', text)
        return match.group() if match else text

    def load_prompt_template(self, template_path: str, **kwargs) -> str:
        """加载并填充提示词模板"""
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
        for key, value in kwargs.items():
            placeholder = "{{" + key + "}}"
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False, indent=2)
            template = template.replace(placeholder, str(value))
        return template
