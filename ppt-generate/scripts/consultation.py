#!/usr/bin/env python3
"""
Consultation Module — 智能咨询与信息完备性检查
PRD要求：
1. 关键信息池确认 — 向用户展示提取的关键信息，请求确认
2. 信息完备性检查 — 识别缺失信息，引导用户补充
3. 汇报意图澄清 — 明确场景、受众、核心诉求
"""

import json
from typing import Dict, Any, List, Optional


class ConsultationManager:
    """智能咨询管理器"""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def run_consultation(self, parsed_content: Dict, template_analysis: Dict,
                         user_config: Optional[Dict] = None) -> Dict[str, Any]:
        """
        执行完整的咨询流程

        Args:
            parsed_content: 内容解析结果（四层递进）
            template_analysis: 模板分析结果
            user_config: 用户已提供的配置

        Returns:
            {
                "key_info_pool": {},        # 关键信息池
                "information_gaps": [],     # 信息缺口
                "consultation_questions": [],# 需要向用户确认的问题
                "auto_decisions": [],       # Agent自动做出的决策
                "final_config": {},         # 最终配置（合并用户输入和推断）
            }
        """
        user_config = user_config or {}

        # Step 1: 构建关键信息池
        print("  [咨询] 构建关键信息池...")
        key_info_pool = self._build_key_info_pool(parsed_content)

        # Step 2: 信息完备性检查
        print("  [咨询] 信息完备性检查...")
        completeness = self._check_information_completeness(
            parsed_content, template_analysis, user_config
        )

        # Step 3: 生成咨询问题
        print("  [咨询] 生成咨询问题...")
        questions = self._generate_consultation_questions(
            key_info_pool, completeness, user_config, template_analysis
        )

        # Step 4: 自动决策（对于可推断的信息）
        print("  [咨询] 自动决策...")
        auto_decisions = self._make_auto_decisions(
            parsed_content, template_analysis, user_config
        )

        # Step 5: 合并最终配置
        final_config = self._merge_final_config(user_config, auto_decisions)

        return {
            "key_info_pool": key_info_pool,
            "information_gaps": completeness.get("gaps", []),
            "consultation_questions": questions,
            "auto_decisions": auto_decisions,
            "final_config": final_config,
        }

    def _build_key_info_pool(self, parsed_content: Dict) -> Dict[str, Any]:
        """
        构建关键信息池 — 将语义单元按类型分组，标注来源和置信度
        """
        semantic_units = parsed_content.get("semantic_units", [])
        framework = parsed_content.get("framework_mapping", {})

        # 按类型分组
        pool = {
            "background": [],      # 背景/目标
            "achievement": [],     # 关键成果
            "data": [],            # 关键数据
            "problem": [],         # 问题/风险
            "plan": [],            # 下一步计划
            "method": [],          # 方法/过程
            "conclusion": [],      # 关键结论
        }

        for unit in semantic_units:
            unit_type = unit.get("type", "other")
            if unit_type in pool:
                pool[unit_type].append({
                    "content": unit.get("content", ""),
                    "source": unit.get("source", ""),
                    "confidence": unit.get("confidence", "medium"),
                    "granularity": unit.get("granularity", "should_show"),
                    "key_data": unit.get("key_data", []),
                    "data_validation": unit.get("data_validation", []),
                })

        # 统计信息
        pool["_stats"] = {
            "total_units": len(semantic_units),
            "must_show": sum(1 for u in semantic_units if u.get("granularity") == "must_show"),
            "has_data_warnings": any(
                u.get("validation_warning") for u in semantic_units
            ),
            "estimated_pages": framework.get("estimated_total_pages", 0),
        }

        return pool

    def _check_information_completeness(self, parsed_content: Dict,
                                         template_analysis: Dict,
                                         user_config: Dict) -> Dict:
        """信息完备性检查"""
        gaps = []

        # 检查PRD要求的必要信息
        # 1. 汇报场景
        if not user_config.get("scenario"):
            gaps.append({
                "field": "scenario",
                "description": "汇报场景未指定",
                "importance": "high",
                "can_infer": True,
            })

        # 2. 核心意图
        if not user_config.get("core_intent"):
            gaps.append({
                "field": "core_intent",
                "description": "核心汇报意图未明确",
                "importance": "high",
                "can_infer": True,
            })

        # 3. 目标受众
        if not user_config.get("audience"):
            gaps.append({
                "field": "audience",
                "description": "目标受众未指定",
                "importance": "medium",
                "can_infer": True,
            })

        # 4. 页数限制
        if not user_config.get("page_limit"):
            gaps.append({
                "field": "page_limit",
                "description": "页数限制未指定",
                "importance": "medium",
                "can_infer": True,
            })

        # 5. 检查内容层面的缺口
        content_gaps = parsed_content.get("information_gaps", [])
        for gap in content_gaps:
            gaps.append({
                "field": "content",
                "description": gap.get("expected_info", ""),
                "importance": "medium",
                "status": gap.get("status", "missing"),
                "suggestion": gap.get("suggestion", ""),
            })

        # 6. 检查PPT标题
        if not user_config.get("presentation_title"):
            gaps.append({
                "field": "presentation_title",
                "description": "PPT标题未指定",
                "importance": "high",
                "can_infer": False,
            })

        return {
            "gaps": gaps,
            "completeness_score": max(0, 100 - len(gaps) * 10),
            "critical_gaps": [g for g in gaps if g["importance"] == "high" and not g.get("can_infer")],
        }

    def _generate_consultation_questions(self, key_info_pool: Dict,
                                          completeness: Dict,
                                          user_config: Dict,
                                          template_analysis: Dict) -> List[Dict]:
        """生成需要向用户确认的咨询问题"""
        questions = []

        if not self.llm_client:
            return self._generate_fallback_questions(completeness, user_config)

        # 准备上下文
        stats = key_info_pool.get("_stats", {})
        gaps = completeness.get("gaps", [])
        design_lang = template_analysis.get("design_language", {})

        prompt = (
            "你是专业的PPT咨询顾问。根据以下信息，生成需要向用户确认的问题。\n\n"
            "## 原则\n"
            "1. 只问必要的问题，能推断的就不问\n"
            "2. 提供选项让用户快速选择\n"
            "3. 问题数量控制在3-5个\n"
            "4. 每个问题都要有合理的默认推荐\n\n"
            f"## 已知信息\n"
            f"- 用户已提供配置: {json.dumps(user_config, ensure_ascii=False)}\n"
            f"- 素材统计: {json.dumps(stats, ensure_ascii=False)}\n"
            f"- 信息缺口: {json.dumps(gaps, ensure_ascii=False)}\n"
            f"- 模板气质: {design_lang.get('design_temperament', '未知')}\n\n"
            "## 必须确认的信息（如果用户未提供）\n"
            "1. 汇报场景（工作总结/项目进展/数据分析/方案提案）\n"
            "2. 核心意图（展示成果/分析问题/提出方案/争取资源）\n"
            "3. 目标受众（直属领导/高层管理/客户/团队成员）\n"
            "4. 页数偏好\n"
            "5. 关键信息确认（是否有需要特别强调或删除的内容）\n\n"
            "请输出JSON:\n"
            '{"questions": [\n'
            '  {"id": 1, "field": "scenario", "question": "问题文本", '
            '"type": "single_choice", "options": ["选项1", "选项2"], '
            '"default": "推荐选项", "reason": "推荐理由", '
            '"skip_if": "如果用户已提供则跳过"}\n'
            "]}"
        )
        try:
            result = self.llm_client.call_llm(prompt, response_json=True)
            questions = result.get("questions", [])
        except Exception as e:
            print(f"    ⚠ 生成咨询问题失败: {e}")
            questions = self._generate_fallback_questions(completeness, user_config)

        # 过滤掉用户已经提供的信息
        filtered = []
        for q in questions:
            field = q.get("field", "")
            if field and user_config.get(field):
                continue
            filtered.append(q)

        return filtered

    def _generate_fallback_questions(self, completeness: Dict, user_config: Dict) -> List[Dict]:
        """当LLM不可用时的兜底问题"""
        questions = []
        if not user_config.get("scenario"):
            questions.append({
                "id": 1, "field": "scenario",
                "question": "这是什么类型的汇报？",
                "type": "single_choice",
                "options": ["工作总结汇报", "项目进展汇报", "数据分析汇报", "方案提案汇报"],
                "default": "工作总结汇报",
            })
        if not user_config.get("core_intent"):
            questions.append({
                "id": 2, "field": "core_intent",
                "question": "您希望通过这份PPT传达什么核心信息？",
                "type": "single_choice",
                "options": ["展示成果", "分析问题", "提出方案", "争取资源"],
                "default": "展示成果",
            })
        if not user_config.get("page_limit"):
            questions.append({
                "id": 3, "field": "page_limit",
                "question": "期望的页数范围？",
                "type": "single_choice",
                "options": ["10-15页", "15-20页", "20-30页"],
                "default": "15-20页",
            })
        return questions

    def _make_auto_decisions(self, parsed_content: Dict, template_analysis: Dict,
                              user_config: Dict) -> List[Dict]:
        """对于可推断的信息，自动做出决策"""
        decisions = []
        profiles = parsed_content.get("document_profiles", [])
        framework = parsed_content.get("framework_mapping", {})
        design_lang = template_analysis.get("design_language", {})

        # 1. 推断汇报场景
        if not user_config.get("scenario") and profiles:
            doc_types = [p.get("doc_type", "") for p in profiles]
            if any("总结" in t for t in doc_types):
                inferred = "工作总结汇报"
            elif any("项目" in t for t in doc_types):
                inferred = "项目进展汇报"
            elif any("数据" in t or "分析" in t for t in doc_types):
                inferred = "数据分析汇报"
            else:
                inferred = "工作总结汇报"
            decisions.append({
                "field": "scenario",
                "value": inferred,
                "confidence": "medium",
                "reason": f"根据文档类型({', '.join(doc_types)})推断",
            })

        # 2. 推断核心意图
        if not user_config.get("core_intent") and profiles:
            natures = [p.get("info_nature", "") for p in profiles]
            if any("成果" in n for n in natures):
                inferred = "展示成果"
            elif any("问题" in n for n in natures):
                inferred = "分析问题"
            elif any("规划" in n or "建议" in n for n in natures):
                inferred = "提出方案"
            else:
                inferred = "展示成果"
            decisions.append({
                "field": "core_intent",
                "value": inferred,
                "confidence": "medium",
                "reason": f"根据内容性质({', '.join(natures)})推断",
            })

        # 3. 推断页数
        if not user_config.get("page_limit"):
            estimated = framework.get("estimated_total_pages", 15)
            decisions.append({
                "field": "page_limit",
                "value": max(10, min(30, estimated)),
                "confidence": "medium",
                "reason": f"根据内容量估算约{estimated}页",
            })

        # 4. 推断语言风格
        if not user_config.get("language_style"):
            temperament = design_lang.get("design_temperament", "")
            formality = design_lang.get("formality_level", "正式")
            if "活泼" in temperament or "创意" in temperament:
                style = "生动活泼"
            elif "学术" in temperament or "严谨" in temperament:
                style = "专业严谨"
            else:
                style = "简洁明快"
            decisions.append({
                "field": "language_style",
                "value": style,
                "confidence": "medium",
                "reason": f"根据模板气质({temperament})和正式程度({formality})推断",
            })

        return decisions

    def _merge_final_config(self, user_config: Dict, auto_decisions: List[Dict]) -> Dict:
        """合并用户配置和自动决策，用户配置优先"""
        final = dict(user_config)
        for decision in auto_decisions:
            field = decision["field"]
            if field not in final or not final[field]:
                final[field] = decision["value"]
                final[f"_{field}_source"] = "auto_inferred"
                final[f"_{field}_confidence"] = decision["confidence"]
        return final

    def format_consultation_output(self, consultation_result: Dict) -> str:
        """
        将咨询结果格式化为人类可读的文本
        供AI助手展示给用户
        """
        lines = []
        pool = consultation_result.get("key_info_pool", {})
        stats = pool.get("_stats", {})
        questions = consultation_result.get("consultation_questions", [])
        auto_decisions = consultation_result.get("auto_decisions", [])
        gaps = consultation_result.get("information_gaps", [])

        # 1. 素材分析摘要
        lines.append("## 📋 素材分析摘要\n")
        lines.append(f"- 共提取 **{stats.get('total_units', 0)}** 个信息要素")
        lines.append(f"- 其中 **{stats.get('must_show', 0)}** 个为必须呈现的核心信息")
        if stats.get("has_data_warnings"):
            lines.append("- ⚠ 部分数据需要您确认准确性")
        lines.append("")

        # 2. 关键信息池概览
        for category, label in [
            ("achievement", "🏆 关键成果"),
            ("data", "📊 关键数据"),
            ("problem", "⚠️ 问题/风险"),
            ("plan", "📅 下一步计划"),
        ]:
            items = pool.get(category, [])
            if items:
                lines.append(f"### {label} ({len(items)}项)")
                for item in items[:5]:
                    conf_icon = {"high": "✅", "medium": "⚡", "low": "❓"}.get(
                        item.get("confidence", "medium"), "⚡"
                    )
                    lines.append(f"  {conf_icon} {item['content']}")
                    if item.get("data_validation"):
                        for dv in item["data_validation"]:
                            if not dv.get("verified"):
                                lines.append(f"     ⚠ 数据 '{dv['value']}' 未在原文中精确匹配，请确认")
                if len(items) > 5:
                    lines.append(f"  ... 还有 {len(items) - 5} 项")
                lines.append("")

        # 3. 自动决策
        if auto_decisions:
            lines.append("## 🤖 Agent自动推断\n")
            for d in auto_decisions:
                lines.append(f"- **{d['field']}**: {d['value']} ({d['reason']})")
            lines.append("")

        # 4. 需要确认的问题
        if questions:
            lines.append("## ❓ 需要您确认\n")
            for q in questions:
                lines.append(f"**{q.get('id', '')}. {q['question']}**")
                if q.get("options"):
                    for opt in q["options"]:
                        prefix = "  → " if opt == q.get("default") else "    "
                        lines.append(f"{prefix}{opt}")
                if q.get("default"):
                    lines.append(f"  （推荐: {q['default']}）")
                lines.append("")

        # 5. 信息缺口
        critical_gaps = [g for g in gaps if g.get("importance") == "high" and not g.get("can_infer")]
        if critical_gaps:
            lines.append("## ⚠️ 需要补充的信息\n")
            for g in critical_gaps:
                lines.append(f"- {g['description']}")
            lines.append("")

        return "\n".join(lines)
