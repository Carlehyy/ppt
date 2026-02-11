#!/usr/bin/env python3
"""
内容解析模块 — 从多个文档中提取结构化信息
支持PDF、Word、TXT、Markdown格式
"""

import os
from typing import List, Dict, Any
from .llm_client import LLMClient
from .utils import detect_file_type, validate_files, load_prompt


class ContentParser:
    """内容解析器"""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def parse(self, file_paths: List[str]) -> Dict[str, Any]:
        """
        解析多个文档，提取结构化信息

        Args:
            file_paths: 文档文件路径列表

        Returns:
            解析结果字典
        """
        print("📄 开始解析文档...")

        # 验证文件
        valid_files = validate_files(file_paths)
        if not valid_files:
            raise ValueError("没有有效的文件可以解析")

        # 解析每个文档
        all_parsed = []
        for i, file_path in enumerate(valid_files, 1):
            print(f"  [{i}/{len(valid_files)}] 解析: {os.path.basename(file_path)}")
            parsed = self._parse_single_file(file_path)
            all_parsed.append(parsed)

        # 多文档关联分析
        if len(all_parsed) > 1:
            print("  🔗 分析多文档关联关系...")
            combined_result = self._combine_multi_documents(all_parsed)
        else:
            combined_result = all_parsed[0]

        print("✅ 文档解析完成\n")
        return combined_result

    def _parse_single_file(self, file_path: str) -> Dict[str, Any]:
        """解析单个文件"""
        # 读取文件内容
        content = self._read_file_content(file_path)

        # 调用LLM进行四层递进分析
        prompt = load_prompt("content_analysis", document_content=content)
        result = self.llm.call_llm(prompt, response_json=True)

        # 添加文件元信息
        result["file_info"] = {
            "file_path": file_path,
            "file_name": os.path.basename(file_path),
            "file_type": detect_file_type(file_path)
        }

        return result

    def _read_file_content(self, file_path: str) -> str:
        """读取文件内容"""
        file_type = detect_file_type(file_path)

        if file_type == "pdf":
            return self._read_pdf(file_path)
        elif file_type == "docx":
            return self._read_docx(file_path)
        elif file_type in ("txt", "markdown"):
            return self._read_text(file_path)
        else:
            raise ValueError(f"不支持的文件类型: {file_type}")

    def _read_pdf(self, file_path: str) -> str:
        """读取PDF文件"""
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n\n"
            return text.strip()
        except ImportError:
            raise ImportError("请安装PyPDF2: pip install PyPDF2")

    def _read_docx(self, file_path: str) -> str:
        """读取Word文档"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text.strip()
        except ImportError:
            raise ImportError("请安装python-docx: pip install python-docx")

    def _read_text(self, file_path: str) -> str:
        """读取纯文本文件"""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def _combine_multi_documents(self, parsed_docs: List[Dict]) -> Dict[str, Any]:
        """合并多个文档的解析结果"""
        # 构建合并提示词
        docs_summary = []
        for i, doc in enumerate(parsed_docs, 1):
            profile = doc.get("document_profile", {})
            docs_summary.append(f"文档{i}: {profile.get('core_topic', '未知主题')}")

        # 合并所有信息要素
        combined_elements = {
            "background_goals": [],
            "key_achievements": [],
            "methods_process": [],
            "issues_challenges": [],
            "data_metrics": [],
            "key_conclusions": [],
            "next_steps": []
        }

        for doc in parsed_docs:
            elements = doc.get("information_elements", {})
            for key in combined_elements.keys():
                combined_elements[key].extend(elements.get(key, []))

        # 使用第一个文档的框架作为基础
        result = parsed_docs[0].copy()
        result["information_elements"] = combined_elements
        result["source_documents"] = [doc.get("file_info", {}) for doc in parsed_docs]

        # 更新跨文档分析
        if "cross_document_analysis" in result:
            result["cross_document_analysis"]["document_count"] = len(parsed_docs)
            result["cross_document_analysis"]["documents_summary"] = docs_summary

        return result
