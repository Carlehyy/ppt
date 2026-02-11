#!/usr/bin/env python3
"""
Markdown生成模块 — 将大纲转换为结构化的Markdown文档
"""

from typing import Dict, Any, List
from .utils import save_text


class MarkdownGenerator:
    """Markdown文档生成器"""

    def generate(self, outline_plan: Dict[str, Any], parsed_content: Dict[str, Any],
                 output_path: str) -> str:
        """
        生成Markdown汇报文档

        Args:
            outline_plan: 大纲规划结果
            parsed_content: 内容解析结果
            output_path: 输出文件路径

        Returns:
            生成的Markdown内容
        """
        print("📝 开始生成Markdown文档...")

        md_content = []

        # 1. 标题和概览
        md_content.append(self._generate_header(outline_plan))

        # 2. 目录（可选）
        if outline_plan.get("overview", {}).get("total_pages", 0) > 10:
            md_content.append(self._generate_toc(outline_plan))

        # 3. 逐章节生成内容
        md_content.append(self._generate_chapters(outline_plan))

        # 4. 附录：内容来源索引
        md_content.append(self._generate_sources(parsed_content))

        # 合并所有内容
        full_content = "\n\n".join(md_content)

        # 保存到文件
        save_text(full_content, output_path)

        print(f"✅ Markdown文档已生成: {output_path}\n")
        return full_content

    def _generate_header(self, outline_plan: Dict[str, Any]) -> str:
        """生成文档头部"""
        overview = outline_plan.get("overview", {})
        narrative = outline_plan.get("narrative_strategy", {})

        lines = []
        lines.append("# PPT汇报文档")
        lines.append("")
        lines.append("## 概览")
        lines.append("")
        lines.append(f"- **总页数**: {overview.get('total_pages', 'N/A')}页")
        lines.append(f"- **预计时长**: {overview.get('estimated_duration', 'N/A')}")
        lines.append(f"- **章节数**: {overview.get('chapter_count', 'N/A')}章")
        lines.append(f"- **叙事策略**: {narrative.get('type', 'N/A')}")
        lines.append(f"- **核心故事线**: {narrative.get('core_storyline', 'N/A')}")
        lines.append("")
        lines.append("---")

        return "\n".join(lines)

    def _generate_toc(self, outline_plan: Dict[str, Any]) -> str:
        """生成目录"""
        chapters = outline_plan.get("chapters", [])

        lines = []
        lines.append("## 目录")
        lines.append("")

        for chapter in chapters:
            chapter_id = chapter.get("chapter_id", 0)
            title = chapter.get("title", "未命名章节")
            page_count = chapter.get("page_count", 0)
            is_key = "⭐" if chapter.get("is_key_chapter", False) else ""
            lines.append(f"{chapter_id}. **{title}** {is_key} ({page_count}页)")

        lines.append("")
        lines.append("---")

        return "\n".join(lines)

    def _generate_chapters(self, outline_plan: Dict[str, Any]) -> str:
        """生成章节内容"""
        pages = outline_plan.get("pages", [])
        chapters = outline_plan.get("chapters", [])

        # 按章节分组页面
        chapter_pages = {}
        for page in pages:
            chapter_id = page.get("chapter_id", 0)
            if chapter_id not in chapter_pages:
                chapter_pages[chapter_id] = []
            chapter_pages[chapter_id].append(page)

        lines = []

        # 生成每个章节
        for chapter in chapters:
            chapter_id = chapter.get("chapter_id", 0)
            chapter_title = chapter.get("title", "未命名章节")
            chapter_summary = chapter.get("summary", "")

            # 章节标题
            lines.append(f"## 第{chapter_id}章：{chapter_title}")
            lines.append("")
            if chapter_summary:
                lines.append(f"> {chapter_summary}")
                lines.append("")

            # 章节内的页面
            pages_in_chapter = chapter_pages.get(chapter_id, [])
            for page in pages_in_chapter:
                lines.append(self._generate_page(page))

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def _generate_page(self, page: Dict[str, Any]) -> str:
        """生成单个页面内容"""
        page_num = page.get("page_number", 0)
        page_type = page.get("page_type", "content")
        core_message = page.get("core_message", "")
        supporting_points = page.get("supporting_points", [])
        data_elements = page.get("data_elements", [])
        content_source = page.get("content_source", "")
        notes = page.get("notes", "")

        lines = []

        # 页面标题
        lines.append(f"### 页面{page_num}：{core_message}")
        lines.append("")

        # 页面类型标签
        type_labels = {
            "cover": "📌 封面页",
            "toc": "📑 目录页",
            "chapter_title": "📂 章节标题页",
            "content": "📄 内容页",
            "data": "📊 数据页",
            "comparison": "⚖️ 对比页",
            "summary": "📝 总结页"
        }
        type_label = type_labels.get(page_type, "📄 内容页")
        lines.append(f"**类型**: {type_label}")
        lines.append("")

        # 核心信息
        lines.append(f"**核心信息**: {core_message}")
        lines.append("")

        # 支撑要点
        if supporting_points:
            lines.append("**关键要点**:")
            for point in supporting_points:
                lines.append(f"- {point}")
            lines.append("")

        # 数据元素
        if data_elements:
            lines.append("**数据/图表建议**:")
            for element in data_elements:
                lines.append(f"- {element}")
            lines.append("")

        # 内容来源
        if content_source:
            lines.append(f"**内容来源**: {content_source}")
            lines.append("")

        # 备注
        if notes:
            lines.append(f"**备注**: {notes}")
            lines.append("")

        return "\n".join(lines)

    def _generate_sources(self, parsed_content: Dict[str, Any]) -> str:
        """生成内容来源索引"""
        lines = []
        lines.append("## 附录：内容来源索引")
        lines.append("")

        # 单文档
        if "file_info" in parsed_content:
            file_info = parsed_content["file_info"]
            lines.append(f"- **文档**: {file_info.get('file_name', 'N/A')}")
            lines.append(f"  - 类型: {file_info.get('file_type', 'N/A')}")

        # 多文档
        elif "source_documents" in parsed_content:
            source_docs = parsed_content["source_documents"]
            for i, doc in enumerate(source_docs, 1):
                lines.append(f"- **文档{i}**: {doc.get('file_name', 'N/A')}")
                lines.append(f"  - 类型: {doc.get('file_type', 'N/A')}")

        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*本文档由PPT汇报文档生成器自动生成*")

        return "\n".join(lines)
