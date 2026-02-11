#!/usr/bin/env python3
"""
PPT Report Agent - Main Orchestrator
Coordinates the multi-stage pipeline for intelligent PPT generation
"""

import os
import sys
import json
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from scripts.parse_content import ContentParser
from scripts.analyze_template import TemplateAnalyzer
from scripts.llm_client import LLMClient
from scripts.generate_slides import SlidesGenerator
from scripts.utils import load_json, save_json


class PPTAgentOrchestrator:
    """Main orchestrator for PPT generation pipeline"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the orchestrator with optional config"""
        # Load configuration
        if config_path and os.path.exists(config_path):
            self.config = load_json(config_path)
        else:
            # Use default config from skill directory
            default_config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'config.json'
            )
            if os.path.exists(default_config_path):
                self.config = load_json(default_config_path)
            else:
                self.config = {}
        
        # Initialize modules
        self.llm_client = LLMClient(self.config)
        self.content_parser = ContentParser(self.llm_client)
        self.template_analyzer = TemplateAnalyzer(self.llm_client)
        self.slides_generator = SlidesGenerator(self.config)
    
    def run(self, input_files: List[str], template_path: str, 
            user_config: Optional[Dict] = None) -> tuple:
        """
        Run the complete PPT generation pipeline
        
        Args:
            input_files: List of input document paths
            template_path: Path to PPT template
            user_config: Optional user configuration
            
        Returns:
            (output_path, review_result)
        """
        print("\n" + "="*60)
        print("PPT Report Agent - 智能PPT生成系统")
        print("="*60 + "\n")
        
        # Stage 1+2: Parallel execution
        print("[阶段 1/6] 解析原始素材...")
        parsed_content = self.content_parser.parse(input_files)
        print(f"  ✓ {parsed_content['summary']}")
        
        print("\n[阶段 2/6] 分析模板能力...")
        template_profile = self.template_analyzer.analyze(template_path)
        print(f"  ✓ 发现 {template_profile['total_layouts']} 个版式")
        
        # Stage 0: Intelligent consultation
        print("\n[阶段 3/6] 智能咨询...")
        questions = self.llm_client.generate_consultation_questions(
            parsed_content, template_profile
        )
        user_intent = self._interact_with_user(questions, user_config)
        print(f"  ✓ 确认汇报场景: {user_intent.get('scenario', '工作汇报')}")
        
        # Stage 3: Outline planning
        print("\n[阶段 4/6] 规划演示大纲...")
        outline = self.llm_client.plan_outline(
            user_intent, parsed_content, template_profile
        )
        confirmed_outline = self._confirm_outline(outline)
        print(f"  ✓ 规划 {len(confirmed_outline.get('sections', []))} 个章节")
        
        # Stage 4: Slide generation
        print("\n[阶段 5/6] 生成幻灯片内容...")
        slides_content = self._generate_all_slides(
            confirmed_outline, parsed_content, template_profile
        )
        print(f"  ✓ 生成 {len(slides_content)} 页内容")
        
        # Stage 5: Global review
        print("\n[阶段 6/6] 执行质量校审...")
        review_result = self.llm_client.review_presentation(slides_content)
        score = review_result.get('overall_score', 0)
        print(f"  ✓ 质量评分: {score}/100")
        
        # Generate final PPT
        print("\n[最终生成] 创建PowerPoint文件...")
        output_path = self.slides_generator.generate(
            confirmed_outline, template_path, slides_content
        )
        
        print("\n" + "="*60)
        print(f"✓ 成功! 生成文件: {output_path}")
        print(f"  质量评分: {score}/100")
        print("="*60 + "\n")
        
        return output_path, review_result
    
    def _interact_with_user(self, questions: Dict, user_config: Optional[Dict]) -> Dict:
        """Handle user interaction for consultation stage"""
        # If user_config provided, use it directly
        if user_config:
            return user_config
        
        # Otherwise, use default values
        # In a real implementation with Manus, this would use the message tool
        return {
            "scenario": "工作汇报",
            "core_intent": "展示成果",
            "page_limit": self.config.get('generation', {}).get('default_page_limit', 20),
            "language_style": "专业"
        }
    
    def _confirm_outline(self, outline: Dict) -> Dict:
        """Request user confirmation of outline"""
        print("\n  --- 建议大纲 ---")
        for i, section in enumerate(outline.get('sections', [])):
            print(f"  {i+1}. {section.get('title', '')} ({len(section.get('pages', []))} 页)")
            for page in section.get('pages', []):
                print(f"     - {page.get('title', '')}")
        print()
        
        # In a real implementation, this would wait for user confirmation
        # For now, return as-is
        return outline
    
    def _generate_all_slides(self, outline: Dict, parsed_content: Dict, 
                            template_profile: Dict) -> List[Dict]:
        """Generate content for all slides"""
        slides_content = []
        
        # Create a lookup for layouts
        layouts_by_index = {
            layout['index']: layout 
            for layout in template_profile.get('layouts', [])
        }
        
        for section in outline.get('sections', []):
            for page_spec in section.get('pages', []):
                layout_index = page_spec.get('layout_index', 1)
                layout_info = layouts_by_index.get(layout_index, {})
                
                # Generate slide content
                slide_content = self.llm_client.generate_slide_content(
                    page_spec, 
                    parsed_content.get('semantic_units', []),
                    layout_info
                )
                
                # Add metadata
                slide_content['layout_index'] = layout_index
                slide_content['section'] = section.get('title', '')
                
                slides_content.append(slide_content)
        
        return slides_content


def main():
    """Command-line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='PPT Report Agent')
    parser.add_argument('--input', nargs='+', required=True, help='Input files')
    parser.add_argument('--template', required=True, help='Template file')
    parser.add_argument('--config', help='Config file path')
    parser.add_argument('--output', default='output.pptx', help='Output file path')
    
    args = parser.parse_args()
    
    # Run orchestrator
    agent = PPTAgentOrchestrator(config_path=args.config)
    output_path, review = agent.run(args.input, args.template)
    
    print(f"\n生成的PPT: {output_path}")
    print(f"质量评分: {review.get('overall_score', 0)}/100")


if __name__ == "__main__":
    main()
