#!/usr/bin/env python3
"""
Test script for PPT Report Agent Skill
"""

import os
import sys

# Add skill directory to path
sys.path.insert(0, os.path.dirname(__file__))

from scripts.parse_content import ContentParser
from scripts.analyze_template import TemplateAnalyzer
from scripts.llm_client import LLMClient
from scripts.generate_slides import SlidesGenerator
from scripts.utils import load_json


def test_imports():
    """Test that all modules can be imported"""
    print("✓ 所有模块导入成功")


def test_config_loading():
    """Test configuration loading"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    if os.path.exists(config_path):
        config = load_json(config_path)
        print(f"✓ 配置文件加载成功: {config.get('llm', {}).get('model', 'unknown')}")
    else:
        print("✗ 配置文件未找到")


def test_module_initialization():
    """Test module initialization"""
    try:
        llm_client = LLMClient()
        print(f"✓ LLM客户端初始化成功: {llm_client.model}")
        
        content_parser = ContentParser(llm_client)
        print("✓ 内容解析器初始化成功")
        
        template_analyzer = TemplateAnalyzer(llm_client)
        print("✓ 模板分析器初始化成功")
        
        slides_generator = SlidesGenerator()
        print("✓ PPT生成器初始化成功")
        
    except Exception as e:
        print(f"✗ 模块初始化失败: {e}")


def test_template_directory():
    """Test template directory structure"""
    template_dir = os.path.join(os.path.dirname(__file__), 'templates/user_templates')
    if os.path.exists(template_dir):
        templates = [f for f in os.listdir(template_dir) if f.endswith('.pptx')]
        if templates:
            print(f"✓ 找到 {len(templates)} 个模板文件")
        else:
            print("⚠ 模板目录为空，请添加.pptx模板文件")
    else:
        print("✗ 模板目录不存在")


def test_prompts_directory():
    """Test prompts directory"""
    prompts_dir = os.path.join(os.path.dirname(__file__), 'prompts')
    expected_prompts = [
        'content_analysis.txt',
        'consultation.txt',
        'outline_planning.txt',
        'slide_generation.txt',
        'quality_review.txt'
    ]
    
    missing = []
    for prompt in expected_prompts:
        if not os.path.exists(os.path.join(prompts_dir, prompt)):
            missing.append(prompt)
    
    if not missing:
        print(f"✓ 所有 {len(expected_prompts)} 个提示词文件就绪")
    else:
        print(f"✗ 缺少提示词文件: {', '.join(missing)}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("PPT Report Agent - Skill 测试")
    print("="*60 + "\n")
    
    print("[1/6] 测试模块导入...")
    test_imports()
    
    print("\n[2/6] 测试配置加载...")
    test_config_loading()
    
    print("\n[3/6] 测试模块初始化...")
    test_module_initialization()
    
    print("\n[4/6] 测试模板目录...")
    test_template_directory()
    
    print("\n[5/6] 测试提示词目录...")
    test_prompts_directory()
    
    print("\n[6/6] 测试环境变量...")
    if os.getenv('OPENAI_API_KEY'):
        print("✓ OPENAI_API_KEY 已设置")
    else:
        print("⚠ OPENAI_API_KEY 未设置（LLM功能将无法使用）")
    
    print("\n" + "="*60)
    print("测试完成!")
    print("="*60 + "\n")
    
    print("下一步:")
    print("1. 将您的高质量PPT模板放入 templates/user_templates/ 目录")
    print("2. 准备原始素材文件（.docx, .pdf, .pptx）")
    print("3. 运行 orchestrator.py 生成PPT")
    print()


if __name__ == "__main__":
    main()
