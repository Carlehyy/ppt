#!/usr/bin/env python3
"""
Quality Reviewer Module — 全局校审与质量保障体系
PRD要求（五维度评估）：
1. 内容准确性 — 数据溯源验证，杜绝幻觉
2. 逻辑连贯性 — 章节间过渡自然，叙事线完整
3. 视觉规范性 — 版式使用正确，风格一致
4. 信息密度 — 每页信息量适中，不过载不空洞
5. 受众适配性 — 语言、深度、侧重点匹配目标受众
"""

import json
from typing import Dict, Any, List, Optional


class QualityReviewer:
    """质量校审器"""

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def review(self, slides_data: List[Dict], outline: Dict,
               parsed_content: Dict, template_analysis: Dict,
               final_config: Dict) -> Dict[str, Any]:
        """
        执行完整的质量校审

        Returns:
            {
                "overall_score": int,           # 总分 0-100
                "dimension_scores": {},         # 五维度评分
                "issues": [],                   # 发现的问题
                "suggestions": [],              # 改进建议
                "passed": bool,                 # 是否通过
                "summary": str,                 # 总结文本
            }
        """
        print("  [校审] 开始五维度质量评估...")

        # 维度1: 内容准确性
        print("  [校审] 维度1: 内容准确性...")
        accuracy = self._check_content_accuracy(slides_data, parsed_content)

        # 维度2: 逻辑连贯性
        print("  [校审] 维度2: 逻辑连贯性...")
        coherence = self._check_logical_coherence(slides_data, outline)

        # 维度3: 视觉规范性
        print("  [校审] 维度3: 视觉规范性...")
        visual = self._check_visual_compliance(slides_data, template_analysis)

        # 维度4: 信息密度
        print("  [校审] 维度4: 信息密度...")
        density = self._check_information_density(slides_data)

        # 维度5: 受众适配性
        print("  [校审] 维度5: 受众适配性...")
        audience = self._check_audience_fit(slides_data, final_config)

        # 汇总
        dimension_scores = {
            "content_accuracy": accuracy,
            "logical_coherence": coherence,
            "visual_compliance": visual,
            "information_density": density,
            "audience_fit": audience,
        }

        # 加权计算总分
        weights = {
            "content_accuracy": 0.30,
            "logical_coherence": 0.25,
            "visual_compliance": 0.15,
            "information_density": 0.15,
            "audience_fit": 0.15,
        }
        overall_score = sum(
            d.get("score", 0) * weights.get(k, 0.2)
            for k, d in dimension_scores.items()
        )
        overall_score = round(overall_score)

        # 收集所有问题和建议
        all_issues = []
        all_suggestions = []
        for d in dimension_scores.values():
            all_issues.extend(d.get("issues", []))
            all_suggestions.extend(d.get("suggestions", []))

        # 如果LLM可用，生成综合评审意见
        summary = self._generate_review_summary(
            overall_score, dimension_scores, all_issues, all_suggestions, final_config
        )

        passed = overall_score >= 70 and not any(
            i.get("severity") == "critical" for i in all_issues
        )

        print(f"  [校审] ✓ 总分: {overall_score}/100 {'(通过)' if passed else '(未通过)'}")

        return {
            "overall_score": overall_score,
            "dimension_scores": dimension_scores,
            "issues": all_issues,
            "suggestions": all_suggestions,
            "passed": passed,
            "summary": summary,
        }

    def _check_content_accuracy(self, slides_data: List[Dict],
                                 parsed_content: Dict) -> Dict:
        """维度1: 内容准确性检查"""
        issues = []
        suggestions = []
        score = 100

        semantic_units = parsed_content.get("semantic_units", [])
        original_data = {}
        for unit in semantic_units:
            for kd in unit.get("key_data", []):
                original_data[kd.get("label", "")] = kd.get("value", "")

        for sd in slides_data:
            if sd.get("status") == "failed":
                issues.append({
                    "dimension": "content_accuracy",
                    "severity": "critical",
                    "page": sd.get("page_num"),
                    "message": f"第{sd.get('page_num')}页生成失败",
                })
                score -= 15
                continue

            content = sd.get("content", {})
            source_info = content.get("source_info", [])

            # 检查是否有低置信度内容
            low_conf = [s for s in source_info if s.get("confidence") == "low"]
            if low_conf:
                issues.append({
                    "dimension": "content_accuracy",
                    "severity": "warning",
                    "page": sd.get("page_num"),
                    "message": f"第{sd.get('page_num')}页有{len(low_conf)}条低置信度内容",
                    "details": [lc.get("content", "")[:30] for lc in low_conf],
                })
                score -= 3 * len(low_conf)

            # 检查是否有无来源的内容
            body = content.get("body", [])
            if body and not source_info:
                if sd.get("content_type") not in ("cover", "ending", "section_divider"):
                    issues.append({
                        "dimension": "content_accuracy",
                        "severity": "info",
                        "page": sd.get("page_num"),
                        "message": f"第{sd.get('page_num')}页内容缺少来源标注",
                    })
                    score -= 2

        # 检查must_show内容覆盖
        must_show = [u for u in semantic_units if u.get("granularity") == "must_show"]
        all_body_text = " ".join(
            " ".join(sd.get("content", {}).get("body", []))
            for sd in slides_data
        )
        uncovered = 0
        for unit in must_show:
            content_text = unit.get("content", "")
            if content_text[:15] not in all_body_text and content_text[-15:] not in all_body_text:
                uncovered += 1

        if must_show and uncovered > 0:
            coverage = 1 - uncovered / len(must_show)
            if coverage < 0.8:
                issues.append({
                    "dimension": "content_accuracy",
                    "severity": "warning",
                    "message": f"必须呈现内容覆盖率: {coverage:.0%} ({uncovered}项未覆盖)",
                })
                score -= int((1 - coverage) * 30)

        score = max(0, min(100, score))
        if score < 80:
            suggestions.append("建议检查低置信度内容的准确性，并补充信息来源标注")

        return {"score": score, "issues": issues, "suggestions": suggestions}

    def _check_logical_coherence(self, slides_data: List[Dict], outline: Dict) -> Dict:
        """维度2: 逻辑连贯性检查"""
        issues = []
        suggestions = []
        score = 100

        # 检查章节结构完整性
        sections = outline.get("sections", [])
        if not sections:
            issues.append({
                "dimension": "logical_coherence",
                "severity": "critical",
                "message": "缺少章节结构",
            })
            return {"score": 30, "issues": issues, "suggestions": ["需要重新规划大纲"]}

        # 检查封面和结束页
        if slides_data:
            first_type = slides_data[0].get("content_type", "")
            if first_type != "cover":
                issues.append({
                    "dimension": "logical_coherence",
                    "severity": "warning",
                    "message": "第一页不是封面页",
                })
                score -= 5

            last_type = slides_data[-1].get("content_type", "")
            if last_type != "ending":
                issues.append({
                    "dimension": "logical_coherence",
                    "severity": "info",
                    "message": "最后一页不是结束页",
                })
                score -= 3

        # 使用LLM检查逻辑连贯性
        if self.llm_client and slides_data:
            titles = [f"P{sd.get('page_num')}: {sd.get('title', '')}" for sd in slides_data]
            prompt = (
                "请评估以下PPT页面标题序列的逻辑连贯性（0-100分）。\n\n"
                f"页面序列:\n" + "\n".join(titles) + "\n\n"
                "评估标准:\n"
                "1. 是否有清晰的叙事主线\n"
                "2. 章节间过渡是否自然\n"
                "3. 是否存在逻辑跳跃\n"
                "4. 结构是否完整（开头-展开-收尾）\n\n"
                "请输出JSON:\n"
                '{"score": 85, "issues": ["问题1"], "suggestions": ["建议1"]}'
            )
            try:
                result = self.llm_client.call_llm(prompt, response_json=True)
                llm_score = result.get("score", 80)
                score = int((score + llm_score) / 2)
                for issue in result.get("issues", []):
                    issues.append({
                        "dimension": "logical_coherence",
                        "severity": "info",
                        "message": issue,
                    })
                suggestions.extend(result.get("suggestions", []))
            except Exception:
                pass

        score = max(0, min(100, score))
        return {"score": score, "issues": issues, "suggestions": suggestions}

    def _check_visual_compliance(self, slides_data: List[Dict],
                                  template_analysis: Dict) -> Dict:
        """维度3: 视觉规范性检查"""
        issues = []
        suggestions = []
        score = 100

        total_layouts = template_analysis.get("total_layouts", 1)

        for sd in slides_data:
            layout_idx = sd.get("layout_index", 0)
            if layout_idx < 0 or layout_idx >= total_layouts:
                issues.append({
                    "dimension": "visual_compliance",
                    "severity": "warning",
                    "page": sd.get("page_num"),
                    "message": f"第{sd.get('page_num')}页使用了无效的版式索引({layout_idx})",
                })
                score -= 5

        # 检查版式多样性
        used_layouts = set(sd.get("layout_index", 0) for sd in slides_data)
        content_pages = [sd for sd in slides_data
                         if sd.get("content_type") not in ("cover", "ending", "section_divider")]
        if len(content_pages) > 5 and len(used_layouts) < 3:
            issues.append({
                "dimension": "visual_compliance",
                "severity": "info",
                "message": f"版式多样性不足，{len(content_pages)}页内容仅使用了{len(used_layouts)}种版式",
            })
            suggestions.append("建议增加版式多样性，避免视觉疲劳")
            score -= 5

        # 检查连续重复版式
        prev_layout = None
        consecutive = 0
        for sd in slides_data:
            if sd.get("content_type") in ("cover", "ending", "section_divider"):
                prev_layout = None
                consecutive = 0
                continue
            curr_layout = sd.get("layout_index")
            if curr_layout == prev_layout:
                consecutive += 1
                if consecutive >= 3:
                    issues.append({
                        "dimension": "visual_compliance",
                        "severity": "info",
                        "page": sd.get("page_num"),
                        "message": f"第{sd.get('page_num')}页附近连续{consecutive+1}页使用相同版式",
                    })
                    score -= 3
            else:
                consecutive = 0
            prev_layout = curr_layout

        score = max(0, min(100, score))
        return {"score": score, "issues": issues, "suggestions": suggestions}

    def _check_information_density(self, slides_data: List[Dict]) -> Dict:
        """维度4: 信息密度检查"""
        issues = []
        suggestions = []
        score = 100

        for sd in slides_data:
            if sd.get("content_type") in ("cover", "ending", "section_divider"):
                continue

            content = sd.get("content", {})
            body = content.get("body", [])
            page_num = sd.get("page_num")

            # 检查过载
            if len(body) > 7:
                issues.append({
                    "dimension": "information_density",
                    "severity": "warning",
                    "page": page_num,
                    "message": f"第{page_num}页有{len(body)}个要点，信息过载",
                })
                score -= 5
                suggestions.append(f"建议将第{page_num}页拆分为多页")

            # 检查空洞
            if len(body) == 0:
                issues.append({
                    "dimension": "information_density",
                    "severity": "warning",
                    "page": page_num,
                    "message": f"第{page_num}页没有正文内容",
                })
                score -= 5

            # 检查单个要点过长
            for i, item in enumerate(body):
                if len(str(item)) > 60:
                    issues.append({
                        "dimension": "information_density",
                        "severity": "info",
                        "page": page_num,
                        "message": f"第{page_num}页第{i+1}个要点过长({len(str(item))}字)",
                    })
                    score -= 2

            # 检查标题过长
            title = content.get("title", "")
            if len(title) > 20:
                issues.append({
                    "dimension": "information_density",
                    "severity": "info",
                    "page": page_num,
                    "message": f"第{page_num}页标题过长({len(title)}字)",
                })
                score -= 2

        score = max(0, min(100, score))
        return {"score": score, "issues": issues, "suggestions": suggestions}

    def _check_audience_fit(self, slides_data: List[Dict], config: Dict) -> Dict:
        """维度5: 受众适配性检查"""
        issues = []
        suggestions = []
        score = 85  # 默认基础分

        audience = config.get("audience", "")
        scenario = config.get("scenario", "")
        language_style = config.get("language_style", "")

        if not self.llm_client:
            return {"score": score, "issues": issues, "suggestions": suggestions}

        # 收集所有内容文本
        all_content = []
        for sd in slides_data:
            content = sd.get("content", {})
            all_content.append({
                "page": sd.get("page_num"),
                "title": content.get("title", ""),
                "body": content.get("body", [])[:3],
            })

        prompt = (
            "请评估以下PPT内容与目标受众的适配度（0-100分）。\n\n"
            f"目标受众: {audience or '未指定'}\n"
            f"汇报场景: {scenario or '未指定'}\n"
            f"期望语言风格: {language_style or '未指定'}\n\n"
            f"PPT内容摘要:\n{json.dumps(all_content[:10], ensure_ascii=False)}\n\n"
            "评估标准:\n"
            "1. 语言专业度是否匹配受众\n"
            "2. 内容深度是否合适\n"
            "3. 重点是否对准受众关注点\n"
            "4. 术语使用是否恰当\n\n"
            "请输出JSON:\n"
            '{"score": 85, "issues": ["问题1"], "suggestions": ["建议1"]}'
        )

        try:
            result = self.llm_client.call_llm(prompt, response_json=True)
            score = result.get("score", 85)
            for issue in result.get("issues", []):
                issues.append({
                    "dimension": "audience_fit",
                    "severity": "info",
                    "message": issue,
                })
            suggestions.extend(result.get("suggestions", []))
        except Exception:
            pass

        score = max(0, min(100, score))
        return {"score": score, "issues": issues, "suggestions": suggestions}

    def _generate_review_summary(self, overall_score: int, dimension_scores: Dict,
                                  issues: List[Dict], suggestions: List[Dict],
                                  config: Dict) -> str:
        """生成综合评审意见"""
        if self.llm_client:
            prompt = (
                "请根据以下评审结果，生成一段简洁的综合评审意见（3-5句话）。\n\n"
                f"总分: {overall_score}/100\n"
                f"各维度得分:\n"
            )
            for k, v in dimension_scores.items():
                prompt += f"  - {k}: {v.get('score', 0)}/100\n"
            prompt += f"\n主要问题: {json.dumps([i['message'] for i in issues[:5]], ensure_ascii=False)}\n"
            prompt += f"改进建议: {json.dumps(suggestions[:5], ensure_ascii=False)}\n"
            prompt += "\n请直接输出评审意见文本，不要JSON格式。"

            try:
                return self.llm_client.call_llm(prompt, temperature=0.3)
            except Exception:
                pass

        # 兜底
        level = "优秀" if overall_score >= 90 else "良好" if overall_score >= 80 else "合格" if overall_score >= 70 else "需改进"
        return f"综合评分: {overall_score}/100 ({level})。共发现{len(issues)}个问题，{len(suggestions)}条改进建议。"

    def format_review_output(self, review_result: Dict) -> str:
        """格式化评审结果供用户查看"""
        lines = []
        overall = review_result.get("overall_score", 0)
        passed = review_result.get("passed", False)

        # 总分
        level_icon = "🟢" if overall >= 80 else "🟡" if overall >= 70 else "🔴"
        lines.append(f"## {level_icon} 质量评审报告\n")
        lines.append(f"**总分: {overall}/100** {'✅ 通过' if passed else '❌ 需改进'}\n")

        # 五维度雷达
        lines.append("### 📊 五维度评分\n")
        dims = review_result.get("dimension_scores", {})
        dim_labels = {
            "content_accuracy": "内容准确性",
            "logical_coherence": "逻辑连贯性",
            "visual_compliance": "视觉规范性",
            "information_density": "信息密度",
            "audience_fit": "受众适配性",
        }
        for key, label in dim_labels.items():
            dim = dims.get(key, {})
            s = dim.get("score", 0)
            bar = "█" * (s // 10) + "░" * (10 - s // 10)
            lines.append(f"  {label}: {bar} {s}/100")
        lines.append("")

        # 综合评审意见
        summary = review_result.get("summary", "")
        if summary:
            lines.append(f"### 💬 综合评审意见\n")
            lines.append(f"> {summary}\n")

        # 问题列表
        issues = review_result.get("issues", [])
        if issues:
            critical = [i for i in issues if i.get("severity") == "critical"]
            warnings = [i for i in issues if i.get("severity") == "warning"]
            infos = [i for i in issues if i.get("severity") == "info"]

            if critical:
                lines.append("### 🔴 严重问题\n")
                for i in critical:
                    page_info = f"(P{i['page']})" if i.get("page") else ""
                    lines.append(f"  - {i['message']} {page_info}")
                lines.append("")

            if warnings:
                lines.append("### 🟡 警告\n")
                for i in warnings:
                    page_info = f"(P{i['page']})" if i.get("page") else ""
                    lines.append(f"  - {i['message']} {page_info}")
                lines.append("")

            if infos:
                lines.append("### 🔵 建议\n")
                for i in infos[:5]:
                    page_info = f"(P{i['page']})" if i.get("page") else ""
                    lines.append(f"  - {i['message']} {page_info}")
                if len(infos) > 5:
                    lines.append(f"  ... 还有 {len(infos) - 5} 条建议")
                lines.append("")

        # 改进建议
        suggestions = review_result.get("suggestions", [])
        if suggestions:
            lines.append("### 💡 改进建议\n")
            for s in suggestions[:5]:
                lines.append(f"  - {s}")
            lines.append("")

        return "\n".join(lines)
