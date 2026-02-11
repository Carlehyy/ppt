"""
PPT Report Agent — 工具函数模块
提供文件操作、数据验证、格式转换等通用工具函数。
"""

import os
import re
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


# ─────────────────── 文件操作 ───────────────────

def detect_file_type(file_path: str) -> str:
    """检测文件类型"""
    ext = os.path.splitext(file_path)[1].lower()
    type_map = {
        ".docx": "docx", ".doc": "doc", ".pdf": "pdf",
        ".pptx": "pptx", ".ppt": "ppt", ".txt": "txt",
        ".md": "markdown", ".xlsx": "excel", ".xls": "excel", ".csv": "csv",
    }
    return type_map.get(ext, "unknown")


def validate_file_exists(file_path: str) -> bool:
    """验证文件是否存在"""
    if not os.path.exists(file_path):
        logger.error(f"文件不存在: {file_path}")
        return False
    return True


def validate_files(file_paths: List[str]) -> List[str]:
    """验证文件列表，返回有效的文件路径"""
    supported = ("docx", "pdf", "pptx", "txt", "markdown", "excel", "csv")
    valid = []
    for fp in file_paths:
        if validate_file_exists(fp):
            ft = detect_file_type(fp)
            if ft in supported:
                valid.append(fp)
            else:
                logger.warning(f"不支持的文件类型: {fp} ({ft})")
    return valid


def ensure_dir(dir_path: str) -> str:
    """确保目录存在"""
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def load_json(file_path: str) -> Dict:
    """加载JSON文件"""
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: Any, file_path: str):
    """保存数据到JSON文件"""
    ensure_dir(os.path.dirname(file_path))
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_text(file_path: str) -> str:
    """加载文本文件"""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def save_text(text: str, file_path: str):
    """保存文本到文件"""
    ensure_dir(os.path.dirname(file_path))
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)


# ─────────────────── Skill 路径 ───────────────────

def get_skill_dir() -> str:
    """获取Skill根目录路径"""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_prompt(prompt_name: str, **kwargs) -> str:
    """加载并填充提示词模板"""
    prompt_path = os.path.join(get_skill_dir(), "prompts", f"{prompt_name}.txt")
    if not os.path.exists(prompt_path):
        logger.error(f"提示词模板不存在: {prompt_path}")
        return ""
    template = load_text(prompt_path)
    for key, value in kwargs.items():
        placeholder = "{" + key + "}"
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False, indent=2)
        template = template.replace(placeholder, str(value))
    return template


def load_config() -> Dict:
    """加载配置文件"""
    config_path = os.path.join(get_skill_dir(), "config.json")
    if not os.path.exists(config_path):
        logger.warning("配置文件不存在，使用默认配置")
        return _default_config()
    return load_json(config_path)


def _default_config() -> Dict:
    return {
        "llm": {"model": "gpt-4.1-mini", "temperature": 0.3, "max_tokens": 4096},
        "generation": {
            "default_page_limit": 20,
            "min_font_size": 14,
            "max_bullets_per_page": 5,
        },
        "quality": {"pass_threshold": 70},
    }


# ─────────────────── JSON 安全解析 ───────────────────

def safe_json_parse(text: str) -> Optional[Dict]:
    """安全地解析JSON字符串，处理LLM输出中常见的格式问题"""
    # 直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # 提取 ```json ... ``` 块
    m = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    # 提取第一个 { ... } 块
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    logger.error(f"无法解析JSON: {text[:200]}...")
    return None


# ─────────────────── 数据提取与验证 ───────────────────

def extract_numbers_with_regex(text: str) -> List[Dict[str, Any]]:
    """
    使用正则表达式从文本中提取数字、百分比、金额等数据。
    用于与LLM提取结果进行交叉验证（PRD要求的双重验证机制）。
    """
    results = []
    # 百分比
    for m in re.finditer(r"(\d+\.?\d*)\s*%", text):
        results.append({"type": "percentage", "value": float(m.group(1)),
                        "raw_text": m.group(0), "position": m.start()})
    # 金额
    for m in re.finditer(r"(\d+\.?\d*)\s*(万|亿|千万|百万)", text):
        results.append({"type": "currency", "value": float(m.group(1)),
                        "unit": m.group(2), "raw_text": m.group(0), "position": m.start()})
    # 日期
    for m in re.finditer(r"(\d{4})\s*[年/-]\s*(\d{1,2})\s*[月/-]?\s*(\d{1,2})?\s*日?", text):
        results.append({"type": "date", "year": int(m.group(1)), "month": int(m.group(2)),
                        "day": int(m.group(3)) if m.group(3) else None,
                        "raw_text": m.group(0), "position": m.start()})
    return results


def cross_validate_data(llm_data: List[Dict], regex_data: List[Dict]) -> List[Dict[str, Any]]:
    """
    交叉验证LLM提取的数据和正则提取的数据。
    PRD要求的"数据敏感信息专项处理"。
    """
    validated = []
    for item in llm_data:
        match_found = any(
            str(item.get("value", "")) in rd.get("raw_text", "")
            for rd in regex_data
        )
        validated.append({
            **item,
            "validation": "confirmed" if match_found else "llm_only",
            "validation_source": "regex_cross_check" if match_found else "需要用户确认",
        })
    return validated


# ─────────────────── 文本工具 ───────────────────

def truncate_text(text: str, max_length: int = 30) -> str:
    """截断文本到指定长度"""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_source_info(file_path: str, section: str = None) -> str:
    """格式化来源信息"""
    filename = os.path.basename(file_path)
    if section:
        return f"{filename}·{section}"
    return filename


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
