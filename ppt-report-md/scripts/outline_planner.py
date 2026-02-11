#!/usr/bin/env python3
"""
大纲规划模块 — 基于内容分析设计汇报大纲
"""

import json
from typing import Dict, Any
from llm_client import LLMClient
from utils import load_prompt


class OutlinePlanner:
    """大纲规划器"""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def plan(self, parsed_content: Dict[str, Any], user_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成汇报大纲

        Args:
            parsed_content: 内容解析结果
            user_config: 用户配置

        Returns:
            大纲规划结果
        """
        print("📋 开始规划汇报大纲...")

        # 准备用户配置
        config_str = self._format_user_config(user_config)

        # 准备内容分析摘要
        content_str = json.dumps(parsed_content, ensure_ascii=False, indent=2)

        # 调用LLM生成大纲
        prompt = load_prompt(
            "outline_planning",
            content_analysis=content_str,
            user_config=config_str
        )

        outline_result = self.llm.call_llm(prompt, response_json=True)

        print("✅ 大纲规划完成\n")
        return outline_result

    def _format_user_config(self, user_config: Dict[str, Any]) -> str:
        """格式化用户配置为可读字符串"""
        config_lines = []
        config_lines.append(f"汇报标题: {user_config.get('presentation_title', '未指定')}")
        config_lines.append(f"汇报场景: {user_config.get('scenario', '向上汇报')}")
        config_lines.append(f"核心诉求: {user_config.get('core_intent', '未指定')}")
        config_lines.append(f"目标页数: {user_config.get('target_pages', 15)}页")
        config_lines.append(f"语言风格: {user_config.get('language_style', '专业简洁')}")
        return "\n".join(config_lines)
