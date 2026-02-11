#!/usr/bin/env python3
"""
Orchestrator — PPT生成主控制器
串联五阶段Pipeline: 分析 → 咨询 → 规划 → 生成 → 校审
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, Optional, List

# 路径常量
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(SCRIPT_DIR)

# 支持包导入和直接运行两种模式
try:
    from .parse_content import ContentParser
    from .analyze_template import TemplateAnalyzer
    from .llm_client import LLMClient
    from .consultation import ConsultationManager
    from .outline_planner import OutlinePlanner
    from .generate_slides import SlideGenerator
    from .quality_reviewer import QualityReviewer
except ImportError:
    sys.path.insert(0, SCRIPT_DIR)
    from parse_content import ContentParser
    from analyze_template import TemplateAnalyzer
    from llm_client import LLMClient
    from consultation import ConsultationManager
    from outline_planner import OutlinePlanner
    from generate_slides import SlideGenerator
    from quality_reviewer import QualityReviewer


class PPTOrchestrator:
    """PPT生成主控制器"""

    def __init__(self, config_path: str = None):
        """
        初始化控制器

        Args:
            config_path: 配置文件路径，默认使用 skill 目录下的 config.json
        """
        self.config = self._load_config(config_path)
        self.llm_client = LLMClient(self.config.get("llm", {}))

        # 初始化各模块
        self.content_parser = ContentParser(self.llm_client)
        self.template_analyzer = TemplateAnalyzer(self.llm_client)
        self.consultation_mgr = ConsultationManager(self.llm_client)
        self.outline_planner = OutlinePlanner(self.llm_client)
        self.slide_generator = SlideGenerator(self.llm_client)
        self.quality_reviewer = QualityReviewer(self.llm_client)

        # 运行时状态
        self.state = {
            "phase": "init",
            "parsed_content": None,
            "template_analysis": None,
            "consultation_result": None,
            "outline_plan": None,
            "generation_result": None,
            "review_result": None,
        }

    def _load_config(self, config_path: str = None) -> Dict:
        """加载配置"""
        if not config_path:
            config_path = os.path.join(SKILL_DIR, "config.json")
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    # ================================================================== #
    #  主流程（一键执行）
    # ================================================================== #
    def run(self, input_files: List[str], template_path: str,
            output_path: str = "output.pptx",
            user_config: Dict = None) -> Dict[str, Any]:
        """
        执行完整的PPT生成流程

        Args:
            input_files: 输入素材文件路径列表
            template_path: PPT模板文件路径
            output_path: 输出PPT文件路径
            user_config: 用户配置（标题、场景、意图等）

        Returns:
            完整的运行结果
        """
        user_config = user_config or {}
        print("=" * 60)
        print("  PPT Report Agent — 智能PPT生成")
        print("=" * 60)

        # ── 阶段1: 内容解析 ──
        print("\n📖 阶段1/5: 内容解析")
        self.state["phase"] = "parsing"
        parsed_content = self.content_parser.parse(input_files)
        self.state["parsed_content"] = parsed_content

        doc_count = len(parsed_content.get("document_profiles", []))
        unit_count = len(parsed_content.get("semantic_units", []))
        print(f"  ✓ 解析完成: {doc_count}份文档, {unit_count}个语义单元")

        # ── 阶段2: 模板分析 ──
        print("\n🎨 阶段2/5: 模板分析")
        self.state["phase"] = "template_analysis"
        template_analysis = self.template_analyzer.analyze(template_path)
        self.state["template_analysis"] = template_analysis

        layout_count = template_analysis.get("total_layouts", 0)
        temperament = template_analysis.get("design_language", {}).get(
            "design_temperament", "未知"
        )
        print(f"  ✓ 分析完成: {layout_count}个版式, 设计气质: {temperament}")

        # ── 阶段3: 智能咨询 ──
        print("\n💬 阶段3/5: 智能咨询")
        self.state["phase"] = "consultation"
        consultation_result = self.consultation_mgr.run_consultation(
            parsed_content, template_analysis, user_config
        )
        self.state["consultation_result"] = consultation_result

        final_config = consultation_result.get("final_config", user_config)
        questions = consultation_result.get("consultation_questions", [])
        print(f"  ✓ 咨询完成: {len(questions)}个待确认问题")

        # ── 阶段4: 大纲规划 ──
        print("\n📝 阶段4/5: 大纲规划")
        self.state["phase"] = "planning"
        outline_plan = self.outline_planner.plan(
            parsed_content, template_analysis, final_config
        )
        self.state["outline_plan"] = outline_plan

        outline = outline_plan.get("outline", {})
        total_pages = outline.get("total_pages", 0)
        strategy_name = outline_plan.get("narrative_strategy", {}).get("name", "未知")
        print(f"  ✓ 规划完成: {strategy_name}, {total_pages}页")

        # ── 阶段5a: 逐页生成 ──
        print("\n🖼️ 阶段5/5: 逐页生成")
        self.state["phase"] = "generating"
        generation_result = self.slide_generator.generate(
            outline, parsed_content, template_analysis,
            final_config, template_path, output_path
        )
        self.state["generation_result"] = generation_result

        success_count = sum(
            1 for s in generation_result.get("slides_data", [])
            if s.get("status") == "success"
        )
        total = generation_result.get("total_slides", 0)
        print(f"  ✓ 生成完成: {success_count}/{total}页成功")

        # ── 阶段5b: 质量校审 ──
        print("\n🔍 质量校审")
        self.state["phase"] = "reviewing"
        review_result = self.quality_reviewer.review(
            generation_result.get("slides_data", []),
            outline, parsed_content, template_analysis, final_config
        )
        self.state["review_result"] = review_result

        # ── 输出结果 ──
        print("\n" + "=" * 60)
        print(f"  ✅ PPT生成完成!")
        print(f"  📄 输出文件: {output_path}")
        print(f"  📊 质量评分: {review_result.get('overall_score', 0)}/100")
        print(f"  {'✅ 通过' if review_result.get('passed') else '⚠️ 需改进'}")
        print("=" * 60)

        return {
            "output_path": output_path,
            "total_slides": total,
            "quality_score": review_result.get("overall_score", 0),
            "quality_passed": review_result.get("passed", False),
            "consultation_output": self.consultation_mgr.format_consultation_output(
                consultation_result
            ),
            "outline_output": self.outline_planner.format_outline_for_confirmation(
                outline_plan
            ),
            "review_output": self.quality_reviewer.format_review_output(review_result),
            "state": self.state,
        }

    # ================================================================== #
    #  分步执行接口（供AI助手逐步调用）
    # ================================================================== #
    def step_parse(self, input_files: List[str]) -> Dict:
        """步骤1: 解析内容"""
        parsed = self.content_parser.parse(input_files)
        self.state["parsed_content"] = parsed
        self.state["phase"] = "parsed"
        return parsed

    def step_analyze_template(self, template_path: str) -> Dict:
        """步骤2: 分析模板"""
        analysis = self.template_analyzer.analyze(template_path)
        self.state["template_analysis"] = analysis
        self.state["phase"] = "template_analyzed"
        return analysis

    def step_consult(self, user_config: Dict = None) -> Dict:
        """步骤3: 智能咨询"""
        result = self.consultation_mgr.run_consultation(
            self.state["parsed_content"],
            self.state["template_analysis"],
            user_config or {}
        )
        self.state["consultation_result"] = result
        self.state["phase"] = "consulted"
        return result

    def step_plan_outline(self, final_config: Dict = None) -> Dict:
        """步骤4: 规划大纲"""
        config = final_config or self.state["consultation_result"].get(
            "final_config", {}
        )
        plan = self.outline_planner.plan(
            self.state["parsed_content"],
            self.state["template_analysis"],
            config
        )
        self.state["outline_plan"] = plan
        self.state["phase"] = "planned"
        return plan

    def step_generate(self, template_path: str,
                       output_path: str = "output.pptx") -> Dict:
        """步骤5: 生成PPT"""
        config = self.state["consultation_result"].get("final_config", {})
        result = self.slide_generator.generate(
            self.state["outline_plan"]["outline"],
            self.state["parsed_content"],
            self.state["template_analysis"],
            config, template_path, output_path
        )
        self.state["generation_result"] = result
        self.state["phase"] = "generated"
        return result

    def step_review(self) -> Dict:
        """步骤6: 质量校审"""
        config = self.state["consultation_result"].get("final_config", {})
        result = self.quality_reviewer.review(
            self.state["generation_result"]["slides_data"],
            self.state["outline_plan"]["outline"],
            self.state["parsed_content"],
            self.state["template_analysis"],
            config
        )
        self.state["review_result"] = result
        self.state["phase"] = "reviewed"
        return result

    def step_modify(self, modification: Dict, template_path: str,
                     output_path: str = "output.pptx") -> Dict:
        """步骤7: 处理修改请求"""
        config = self.state["consultation_result"].get("final_config", {})
        result = self.slide_generator.handle_modification_request(
            modification,
            self.state["generation_result"]["slides_data"],
            self.state["outline_plan"]["outline"],
            self.state["parsed_content"],
            self.state["template_analysis"],
            config, template_path, output_path
        )
        if result.get("status") == "success":
            self.state["generation_result"] = result
        return result

    # ================================================================== #
    #  格式化输出（供AI助手展示给用户）
    # ================================================================== #
    def get_consultation_text(self) -> str:
        """获取咨询结果的格式化文本"""
        if self.state.get("consultation_result"):
            return self.consultation_mgr.format_consultation_output(
                self.state["consultation_result"]
            )
        return ""

    def get_outline_text(self) -> str:
        """获取大纲的格式化文本"""
        if self.state.get("outline_plan"):
            return self.outline_planner.format_outline_for_confirmation(
                self.state["outline_plan"]
            )
        return ""

    def get_review_text(self) -> str:
        """获取评审结果的格式化文本"""
        if self.state.get("review_result"):
            return self.quality_reviewer.format_review_output(
                self.state["review_result"]
            )
        return ""


# ================================================================== #
#  CLI 入口
# ================================================================== #
def main():
    parser = argparse.ArgumentParser(
        description="PPT Report Agent — 智能PPT生成"
    )
    parser.add_argument(
        "--input", "-i", nargs="+", required=True,
        help="输入素材文件路径（支持多个）"
    )
    parser.add_argument(
        "--template", "-t", required=True,
        help="PPT模板文件路径"
    )
    parser.add_argument(
        "--output", "-o", default="output.pptx",
        help="输出PPT文件路径（默认: output.pptx）"
    )
    parser.add_argument("--title", default=None, help="PPT标题")
    parser.add_argument("--scenario", default=None, help="汇报场景")
    parser.add_argument("--config", default=None, help="配置文件路径")

    args = parser.parse_args()

    user_config = {}
    if args.title:
        user_config["presentation_title"] = args.title
    if args.scenario:
        user_config["scenario"] = args.scenario

    orchestrator = PPTOrchestrator(config_path=args.config)
    result = orchestrator.run(
        input_files=args.input,
        template_path=args.template,
        output_path=args.output,
        user_config=user_config,
    )

    # 输出评审报告
    print("\n" + orchestrator.get_review_text())


if __name__ == "__main__":
    main()
