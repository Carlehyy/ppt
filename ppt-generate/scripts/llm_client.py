#!/usr/bin/env python3
"""
LLM Client Module
Handles all interactions with Large Language Models
"""

import os
import json
from typing import Dict, List, Any
from openai import OpenAI


class LLMClient:
    """Client for interacting with LLM"""
    
    def __init__(self, config: Dict = None):
        self.client = OpenAI()  # Uses OPENAI_API_KEY from environment
        self.config = config or {}
        self.model = self.config.get('llm', {}).get('model', 'gpt-4.1-mini')
        self.temperature = self.config.get('llm', {}).get('temperature', 0.7)
        
        # Get prompts directory
        self.prompts_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'prompts'
        )
    
    def _load_prompt(self, prompt_name: str) -> str:
        """Load prompt template from file"""
        prompt_path = os.path.join(self.prompts_dir, f"{prompt_name}.txt")
        
        if os.path.exists(prompt_path):
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Return a default prompt if file doesn't exist
            return f"You are a helpful assistant for {prompt_name}."
    
    def extract_semantic_units(self, raw_content: str) -> List[Dict[str, Any]]:
        """Extract semantic units from raw content"""
        prompt = self._load_prompt('content_analysis')
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"请分析以下内容并提取语义单元:\n\n{raw_content[:4000]}"}
                ],
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('semantic_units', [])
        
        except Exception as e:
            print(f"  警告: LLM语义分析失败: {e}")
            return []
    
    def generate_consultation_questions(self, parsed_content: Dict, template_profile: Dict) -> Dict[str, Any]:
        """Generate consultation questions for user"""
        prompt = self._load_prompt('consultation')
        
        context = {
            'material_summary': parsed_content.get('summary', ''),
            'total_documents': len(parsed_content.get('documents', [])),
            'available_layouts': len(template_profile.get('layouts', []))
        }
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"材料概况: {json.dumps(context, ensure_ascii=False)}"}
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        
        except Exception as e:
            print(f"  警告: 生成咨询问题失败: {e}")
            return {'questions': []}
    
    def plan_outline(self, user_intent: Dict, parsed_content: Dict, template_profile: Dict) -> Dict[str, Any]:
        """Plan presentation outline"""
        prompt = self._load_prompt('outline_planning')
        
        context = {
            'user_intent': user_intent,
            'content_summary': parsed_content.get('summary', ''),
            'semantic_units': parsed_content.get('semantic_units', [])[:20],  # Limit to avoid token overflow
            'available_layouts': [
                {'index': l['index'], 'name': l['name'], 'best_for': l['best_for']}
                for l in template_profile.get('layouts', [])
            ]
        }
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"请规划PPT大纲:\n\n{json.dumps(context, ensure_ascii=False)}"}
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        
        except Exception as e:
            print(f"  错误: 大纲规划失败: {e}")
            raise
    
    def generate_slide_content(self, slide_spec: Dict, available_info: Dict, layout_info: Dict) -> Dict[str, Any]:
        """Generate content for a single slide"""
        prompt = self._load_prompt('slide_generation')
        
        context = {
            'slide_title': slide_spec.get('title', ''),
            'content_type': slide_spec.get('content_type', ''),
            'layout_name': layout_info.get('name', ''),
            'layout_constraints': {
                'has_title': any(ph['type_name'] == 'TITLE' for ph in layout_info.get('placeholders', [])),
                'has_body': any(ph['type_name'] == 'BODY' for ph in layout_info.get('placeholders', [])),
                'max_bullets': 5
            },
            'available_info': available_info
        }
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"请生成幻灯片内容:\n\n{json.dumps(context, ensure_ascii=False)}"}
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        
        except Exception as e:
            print(f"  警告: 生成幻灯片内容失败: {e}")
            return {
                'title': slide_spec.get('title', ''),
                'body': ['内容生成失败，请手动编辑'],
                'source': 'generated',
                'confidence': 'low'
            }
    
    def review_presentation(self, slides_data: List[Dict]) -> Dict[str, Any]:
        """Review the complete presentation"""
        prompt = self._load_prompt('quality_review')
        
        # Prepare summary for review
        review_context = {
            'total_slides': len(slides_data),
            'slides_summary': [
                {'title': s.get('title', ''), 'content_type': s.get('content_type', '')}
                for s in slides_data[:10]  # Limit to first 10 slides
            ]
        }
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"请评审PPT质量:\n\n{json.dumps(review_context, ensure_ascii=False)}"}
                ],
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
        
        except Exception as e:
            print(f"  警告: 质量评审失败: {e}")
            return {
                'overall_score': 0,
                'dimensions': {},
                'suggestions': []
            }
