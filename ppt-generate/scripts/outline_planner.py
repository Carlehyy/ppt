#!/usr/bin/env python3
"""
Outline Planner Module — 大纲规划（叙事策略 + 强约束）
PRD要求：
1. 叙事策略选择 — 根据场景和意图选择最佳叙事框架
2. 章节结构规划 — 一页一核心，逻辑清晰
3. 版式智能匹配 — 内容类型 → 最佳版式
4. 强约束检查 — 页数、版式范围、内容覆盖率
"""

import json
from typing import Dict, Any, List, Optional


# 叙事策略库
NARRATIVE_STRATEGIES = {
    "achievement_driven": {
        "name": "成果导向型",
        "description": "以核心成果为主线，先展示亮点，再展开细节",
        "best_for": ["工作总结汇报", "展示成果"],
        "structure": ["封面", "核心成果总览", "重点项目/成果展开", "数据支撑", "经验总结", "下一步计划", "结束页"],
    },
    "problem_driven": {
        "name": "问题导向型",
        "description": "以问题为切入点，分析原因，提出解决方案",
        "best_for": ["方案提案汇报", "分析问题"],
        "structure": ["封面", "背景与现状", "核心问题分析", "原因剖析", "解决方案", "实施计划", "预期效果", "结束页"],
    },
    "timeline": {
        "name": "时间线型",
        "description": "按时间顺序梳理，展示发展脉络",
        "best_for": ["项目进展汇报"],
        "structure": ["封面", "项目概述", "阶段一回顾", "阶段二回顾", "当前进展", "里程碑", "下一阶段计划", "结束页"],
    },
    "data_insight": {
        "name": "数据洞察型",
        "description": "以数据为核心，从数据中提炼洞察和结论",
        "best_for": ["数据分析汇报"],
        "structure": ["封面", "分析背景", "核心指标总览", "趋势分析", "对比分析", "关键洞察", "建议与行动", "结束页"],
    },
    "proposal": {
        "name": "方案推荐型",
        "description": "提出方案并论证可行性，争取支持",
        "best_for": ["方案提案汇报", "争取资源"],
        "structure": ["封面", "背景与需求", "方案概述", "方案详情", "可行性分析", "资源需求", "预期收益", "实施路线", "结束页"],
    },
}


class OutlinePlanner:
    """大纲规划器"""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def plan(self, parsed_content: Dict, template_analysis: Dict,
             final_config: Dict) -> Dict[str, Any]:
        """
        执行完整的大纲规划流程

        Returns:
            {
                "narrative_strategy": {},    # 选择的叙事策略
                "outline": {},               # 完整大纲
                "validation": {},            # 强约束检查结果
                "content_mapping": [],       # 内容→页面映射
            }
        """
        # Step 1: 选择叙事策略
        print("  [大纲] 选择叙事策略...")
        strategy = self._select_narrative_strategy(parsed_content, final_config)
        print(f"  [大纲] ✓ 选择策略: {strategy.get('name', '未知')}")

        # Step 2: 生成详细大纲
        print("  [大纲] 生成详细大纲...")
        outline = self._generate_detailed_outline(
            strategy, parsed_content, template_analysis, final_config
        )
        print(f"  [大纲] ✓ 规划 {outline.get('total_pages', 0)} 页")

        # Step 3: 强约束检查
        print("  [大纲] 强约束检查...")
        validation = self._validate_outline(outline, template_analysis, final_config, parsed_content)
        print(f"  [大纲] ✓ 检查完成，{'通过' if validation.get('passed') else '需要调整'}")

        # Step 4: 如果未通过，自动修正
        if not validation.get("passed") and self.llm_client:
            print("  [大纲] 自动修正...")
            outline = self._auto_fix_outline(outline, validation, template_analysis, final_config)
            validation = self._validate_outline(outline, template_analysis, final_config, parsed_content)
            print(f"  [大纲] ✓ 修正后: {'通过' if validation.get('passed') else '仍有问题'}")

        # Step 5: 生成内容映射
        content_mapping = self._generate_content_mapping(outline, parsed_content)

        return {
            "narrative_strategy": strategy,
            "outline": outline,
            "validation": validation,
            "content_mapping": content_mapping,
        }

    def _select_narrative_strategy(self, parsed_content: Dict, config: Dict) -> Dict:
        """选择最佳叙事策略"""
        scenario = config.get("scenario", "")
        intent = config.get("core_intent", "")

        if self.llm_client:
            profiles = parsed_content.get("document_profiles", [])
            relationships = parsed_content.get("document_relationships", {})

            prompt = (
                "你是专业的演示策略顾问。请根据以下信息选择最佳叙事策略。\n\n"
                f"汇报场景: {scenario}\n"
                f"核心意图: {intent}\n"
                f"文档画像: {json.dumps(profiles, ensure_ascii=False)}\n"
                f"叙事主线: {relationships.get('recommended_storyline', '待定')}\n\n"
                f"可选策略:\n{json.dumps(NARRATIVE_STRATEGIES, ensure_ascii=False)}\n\n"
                "请输出JSON:\n"
                "{\n"
                '  "selected_strategy": "策略key（如achievement_driven）",\n'
                '  "name": "策略名称",\n'
                '  "reason": "选择理由",\n'
                '  "customized_structure": ["封面", "章节1", "章节2", ...],\n'
                '  "structure_rationale": "结构设计理由"\n'
                "}"
            )
            try:
                result = self.llm_client.call_llm(prompt, response_json=True)
                key = result.get("selected_strategy", "achievement_driven")
                base = NARRATIVE_STRATEGIES.get(key, NARRATIVE_STRATEGIES["achievement_driven"])
                return {**base, **result}
            except Exception as e:
                print(f"    ⚠ 策略选择失败: {e}")

        # 兜底：基于规则匹配
        return self._rule_based_strategy_selection(scenario, intent)

    def _rule_based_strategy_selection(self, scenario: str, intent: str) -> Dict:
        """基于规则的策略选择"""
        for key, strategy in NARRATIVE_STRATEGIES.items():
            if scenario in strategy["best_for"] or intent in strategy["best_for"]:
                return {**strategy, "selected_strategy": key}
        return {**NARRATIVE_STRATEGIES["achievement_driven"], "selected_strategy": "achievement_driven"}

    def _generate_detailed_outline(self, strategy: Dict, parsed_content: Dict,
                                    template_analysis: Dict, config: Dict) -> Dict:
        """生成详细的逐页大纲"""
        page_limit = config.get("page_limit", 15)
        if isinstance(page_limit, str):
            # 处理 "15-20页" 格式
            import re
            nums = re.findall(r'\d+', str(page_limit))
            page_limit = int(nums[-1]) if nums else 15

        layouts = template_analysis.get("layouts", [])
        recommendations = template_analysis.get("layout_recommendations", {})
        design_lang = template_analysis.get("design_language", {})
        semantic_units = parsed_content.get("semantic_units", [])

        # 准备语义单元摘要（避免token溢出）
        must_show = [u for u in semantic_units if u.get("granularity") == "must_show"]
        should_show = [u for u in semantic_units if u.get("granularity") == "should_show"]

        units_summary = []
        for u in (must_show + should_show)[:30]:
            units_summary.append({
                "type": u.get("type"),
                "content": u.get("content", "")[:100],
                "granularity": u.get("granularity"),
                "key_data": u.get("key_data", []),
            })

        # 准备版式信息
        layout_info = []
        for l in layouts:
            layout_info.append({
                "index": l["index"],
                "name": l["name"],
                "category": l.get("layout_category", ""),
                "best_for": l.get("best_for", ""),
                "capacity": l.get("capacity", {}),
            })

        prompt = (
            "你是专业的PPT结构设计师。请根据以下信息规划详细的PPT大纲。\n\n"
            f"## 叙事策略\n"
            f"策略: {strategy.get('name', '')}\n"
            f"自定义结构: {json.dumps(strategy.get('customized_structure', strategy.get('structure', [])), ensure_ascii=False)}\n\n"
            f"## 约束条件\n"
            f"- 页数限制: {page_limit}页\n"
            f"- PPT标题: {config.get('presentation_title', '未定')}\n"
            f"- 语言风格: {config.get('language_style', '专业')}\n"
            f"- 设计气质: {design_lang.get('design_temperament', '未知')}\n"
            f"- 内容指南: {json.dumps(design_lang.get('content_guidelines', {}), ensure_ascii=False)}\n\n"
            f"## 可用版式\n{json.dumps(layout_info, ensure_ascii=False)}\n\n"
            f"## 版式推荐\n{json.dumps(recommendations, ensure_ascii=False)}\n\n"
            f"## 可用内容（语义单元）\n{json.dumps(units_summary, ensure_ascii=False)}\n\n"
            "## 规划规则\n"
            "1. 第1页必须是封面页\n"
            "2. 最后一页必须是结束页/致谢页\n"
            "3. 每页只传达一个核心信息（一页一核心）\n"
            "4. 章节之间使用分隔页过渡（如果模板有分隔页版式）\n"
            "5. layout_index必须在0到" + str(len(layouts) - 1) + "之间\n"
            "6. 总页数不超过" + str(page_limit) + "页\n"
            "7. 每个must_show的语义单元都必须被覆盖\n\n"
            "请输出JSON:\n"
            "{\n"
            '  "total_pages": 18,\n'
            '  "sections": [\n'
            '    {\n'
            '      "title": "章节名",\n'
            '      "purpose": "该章节的作用",\n'
            '      "pages": [\n'
            '        {\n'
            '          "page_num": 1,\n'
            '          "title": "页面标题",\n'
            '          "subtitle": "副标题（可选）",\n'
            '          "content_type": "cover/section_divider/achievement_list/data_showcase/comparison/problem_analysis/plan_timeline/conclusion/ending",\n'
            '          "layout_index": 0,\n'
            '          "layout_name": "版式名称",\n'
            '          "core_message": "这一页要传达的核心信息",\n'
            '          "key_points": ["要点1", "要点2"],\n'
            '          "data_to_show": ["相关数据"],\n'
            '          "source_units": ["对应的语义单元内容摘要"],\n'
            '          "speaker_notes": "演讲备注"\n'
            '        }\n'
            '      ]\n'
            '    }\n'
            '  ]\n'
            "}"
        )

        try:
            outline = self.llm_client.call_llm(prompt, response_json=True, max_tokens=8192)
            return outline
        except Exception as e:
            print(f"    ⚠ 大纲生成失败: {e}")
            return self._generate_fallback_outline(strategy, config, layouts)

    def _validate_outline(self, outline: Dict, template_analysis: Dict,
                           config: Dict, parsed_content: Dict) -> Dict:
        """强约束检查"""
        issues = []
        total_layouts = template_analysis.get("total_layouts", 0)
        page_limit = config.get("page_limit", 30)
        if isinstance(page_limit, str):
            import re
            nums = re.findall(r'\d+', str(page_limit))
            page_limit = int(nums[-1]) if nums else 30

        total_pages = outline.get("total_pages", 0)
        sections = outline.get("sections", [])

        # 1. 页数检查
        actual_pages = sum(len(s.get("pages", [])) for s in sections)
        if actual_pages > page_limit:
            issues.append({
                "type": "page_overflow",
                "severity": "high",
                "message": f"实际页数({actual_pages})超过限制({page_limit})",
                "suggestion": f"需要删减{actual_pages - page_limit}页",
            })

        # 2. 版式范围检查
        for section in sections:
            for page in section.get("pages", []):
                layout_idx = page.get("layout_index", 0)
                if layout_idx < 0 or layout_idx >= total_layouts:
                    issues.append({
                        "type": "invalid_layout",
                        "severity": "high",
                        "message": f"第{page.get('page_num')}页的layout_index({layout_idx})超出范围(0-{total_layouts-1})",
                        "suggestion": "使用默认版式",
                    })

        # 3. 封面和结束页检查
        all_pages = []
        for s in sections:
            all_pages.extend(s.get("pages", []))
        if all_pages:
            first_type = all_pages[0].get("content_type", "")
            if first_type != "cover":
                issues.append({
                    "type": "missing_cover",
                    "severity": "medium",
                    "message": "第一页不是封面页",
                })
            last_type = all_pages[-1].get("content_type", "")
            if last_type != "ending":
                issues.append({
                    "type": "missing_ending",
                    "severity": "low",
                    "message": "最后一页不是结束页",
                })

        # 4. 内容覆盖率检查
        must_show_units = [u for u in parsed_content.get("semantic_units", [])
                           if u.get("granularity") == "must_show"]
        if must_show_units:
            covered_contents = set()
            for s in sections:
                for page in s.get("pages", []):
                    for su in page.get("source_units", []):
                        covered_contents.add(su[:30])
                    for kp in page.get("key_points", []):
                        covered_contents.add(kp[:30])

            uncovered = []
            for unit in must_show_units:
                content = unit.get("content", "")[:30]
                if not any(content[:15] in c for c in covered_contents):
                    uncovered.append(content)

            if uncovered:
                coverage_rate = 1 - len(uncovered) / len(must_show_units)
                if coverage_rate < 0.7:
                    issues.append({
                        "type": "low_coverage",
                        "severity": "high",
                        "message": f"必须呈现的内容覆盖率仅{coverage_rate:.0%}",
                        "uncovered": uncovered[:5],
                    })

        # 5. 一页一核心检查
        for s in sections:
            for page in s.get("pages", []):
                points = page.get("key_points", [])
                if len(points) > 6:
                    issues.append({
                        "type": "too_many_points",
                        "severity": "medium",
                        "message": f"第{page.get('page_num')}页有{len(points)}个要点，建议不超过5个",
                    })

        passed = not any(i["severity"] == "high" for i in issues)
        return {"passed": passed, "issues": issues}

    def _auto_fix_outline(self, outline: Dict, validation: Dict,
                           template_analysis: Dict, config: Dict) -> Dict:
        """自动修正大纲中的问题"""
        if not self.llm_client:
            return outline

        issues = validation.get("issues", [])
        prompt = (
            "你是PPT结构优化专家。请修正以下大纲中的问题。\n\n"
            f"## 当前大纲\n{json.dumps(outline, ensure_ascii=False)}\n\n"
            f"## 发现的问题\n{json.dumps(issues, ensure_ascii=False)}\n\n"
            f"## 约束条件\n"
            f"- 页数限制: {config.get('page_limit', 30)}\n"
            f"- 可用版式数量: {template_analysis.get('total_layouts', 10)}\n\n"
            "请修正问题并输出完整的修正后大纲JSON（格式与输入相同）。"
        )
        try:
            return self.llm_client.call_llm(prompt, response_json=True, max_tokens=8192)
        except Exception:
            return outline

    def _generate_content_mapping(self, outline: Dict, parsed_content: Dict) -> List[Dict]:
        """生成内容→页面映射关系"""
        mapping = []
        semantic_units = parsed_content.get("semantic_units", [])

        for section in outline.get("sections", []):
            for page in section.get("pages", []):
                page_mapping = {
                    "page_num": page.get("page_num"),
                    "title": page.get("title"),
                    "content_type": page.get("content_type"),
                    "matched_units": [],
                }
                # 尝试匹配语义单元
                for kp in page.get("key_points", []):
                    for unit in semantic_units:
                        content = unit.get("content", "")
                        if kp[:10] in content or content[:10] in kp:
                            page_mapping["matched_units"].append({
                                "content": content,
                                "source": unit.get("source", ""),
                                "confidence": unit.get("confidence", "medium"),
                            })
                            break
                mapping.append(page_mapping)
        return mapping

    def _generate_fallback_outline(self, strategy: Dict, config: Dict,
                                    layouts: List[Dict]) -> Dict:
        """兜底大纲生成"""
        structure = strategy.get("structure", ["封面", "内容", "结束页"])
        title = config.get("presentation_title", "汇报")
        cover_idx = 0
        content_idx = min(1, len(layouts) - 1)

        sections = []
        page_num = 1

        # 封面
        sections.append({
            "title": "封面",
            "pages": [{
                "page_num": page_num,
                "title": title,
                "content_type": "cover",
                "layout_index": cover_idx,
                "layout_name": layouts[cover_idx]["name"] if layouts else "Title Slide",
                "core_message": title,
                "key_points": [],
                "source_units": [],
            }]
        })
        page_num += 1

        # 内容章节
        for section_title in structure[1:-1]:
            sections.append({
                "title": section_title,
                "pages": [{
                    "page_num": page_num,
                    "title": section_title,
                    "content_type": "achievement_list",
                    "layout_index": content_idx,
                    "layout_name": layouts[content_idx]["name"] if layouts else "Content",
                    "core_message": section_title,
                    "key_points": ["待填充"],
                    "source_units": [],
                }]
            })
            page_num += 1

        # 结束页
        sections.append({
            "title": "结束",
            "pages": [{
                "page_num": page_num,
                "title": "谢谢",
                "content_type": "ending",
                "layout_index": cover_idx,
                "layout_name": layouts[cover_idx]["name"] if layouts else "Title Slide",
                "core_message": "感谢聆听",
                "key_points": [],
                "source_units": [],
            }]
        })

        return {"total_pages": page_num, "sections": sections}

    def format_outline_for_confirmation(self, plan_result: Dict) -> str:
        """格式化大纲供用户确认"""
        lines = []
        strategy = plan_result.get("narrative_strategy", {})
        outline = plan_result.get("outline", {})
        validation = plan_result.get("validation", {})

        lines.append(f"## 📝 PPT大纲规划\n")
        lines.append(f"**叙事策略**: {strategy.get('name', '未知')} — {strategy.get('reason', '')}\n")
        lines.append(f"**总页数**: {outline.get('total_pages', 0)}页\n")

        for section in outline.get("sections", []):
            lines.append(f"\n### 📂 {section.get('title', '')}")
            if section.get("purpose"):
                lines.append(f"*{section['purpose']}*\n")
            for page in section.get("pages", []):
                type_icon = {
                    "cover": "🎯", "section_divider": "📌",
                    "achievement_list": "🏆", "data_showcase": "📊",
                    "comparison": "⚖️", "problem_analysis": "⚠️",
                    "plan_timeline": "📅", "conclusion": "💡", "ending": "🎉",
                }.get(page.get("content_type", ""), "📄")
                lines.append(
                    f"  {type_icon} P{page.get('page_num', '?')}: "
                    f"**{page.get('title', '')}** "
                    f"[{page.get('layout_name', '')}]"
                )
                if page.get("core_message"):
                    lines.append(f"     核心信息: {page['core_message']}")

        # 验证结果
        if validation.get("issues"):
            lines.append(f"\n### ⚠️ 注意事项")
            for issue in validation["issues"]:
                lines.append(f"  - [{issue['severity']}] {issue['message']}")

        return "\n".join(lines)
