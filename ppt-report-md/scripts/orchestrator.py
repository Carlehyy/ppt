#!/usr/bin/env python3
"""
主控制器 — 协调整个汇报文档生成流程
"""

import os
from typing import List, Dict, Any
from llm_client import LLMClient
from parse_content import ContentParser
from outline_planner import OutlinePlanner
from md_generator import MarkdownGenerator
from utils import load_config


class ReportOrchestrator:
    """汇报文档生成主控制器"""

    def __init__(self, config_path: str = None):
        """
        初始化控制器

        Args:
            config_path: 配置文件路径（可选）
        """
        # 加载配置
        if config_path and os.path.exists(config_path):
            from utils import load_json
            self.config = load_json(config_path)
        else:
            self.config = load_config()

        # 初始化LLM客户端
        llm_config = self.config.get("llm", {})
        self.llm = LLMClient(llm_config)

        # 初始化各个模块
        self.planner = OutlinePlanner(self.llm)
        self.generator = MarkdownGenerator()

    def run(self, input_files: List[str], user_config: Dict[str, Any],
            output_path: str = "汇报文档.md") -> Dict[str, Any]:
        """
        执行完整的文档生成流程

        Args:
            input_files: 输入文件路径列表
            user_config: 用户配置
            output_path: 输出文件路径

        Returns:
            执行结果
        """
        print("=" * 60)
        print("🚀 PPT汇报文档生成器")
        print("=" * 60)
        print()

        try:
            # 阶段1: 内容解析
            # 初始化parser，传入output_dir
            output_dir = os.path.dirname(os.path.abspath(output_path))
            self.parser = ContentParser(self.llm, extract_images=True, output_dir=output_dir)
            parsed_content = self.parser.parse(input_files)

            # 阶段2: 大纲规划
            outline_plan = self.planner.plan(parsed_content, user_config)

            # 阶段3: Markdown生成
            md_content = self.generator.generate(outline_plan, parsed_content, output_path)

            # 返回结果
            result = {
                "status": "success",
                "output_path": output_path,
                "total_pages": outline_plan.get("overview", {}).get("total_pages", 0),
                "estimated_duration": outline_plan.get("overview", {}).get("estimated_duration", "N/A"),
                "narrative_strategy": outline_plan.get("narrative_strategy", {}).get("type", "N/A")
            }

            print("=" * 60)
            print("✅ 汇报文档生成成功！")
            print(f"📄 输出文件: {output_path}")
            print(f"📊 总页数: {result['total_pages']}页")
            print(f"⏱️  预计时长: {result['estimated_duration']}")
            print(f"📖 叙事策略: {result['narrative_strategy']}")
            print("=" * 60)

            return result

        except Exception as e:
            print(f"\n❌ 生成失败: {e}")
            raise
