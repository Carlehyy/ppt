"""
PPT汇报文档生成器 — 工具函数模块
提供文件操作、数据验证、格式转换等通用工具函数。
"""

import os
import json
from typing import List, Dict, Any


# ─────────────────── 文件操作 ───────────────────

def detect_file_type(file_path: str) -> str:
    """检测文件类型"""
    ext = os.path.splitext(file_path)[1].lower()
    type_map = {
        ".docx": "docx", ".doc": "doc", ".pdf": "pdf",
        ".txt": "txt", ".md": "markdown",
    }
    return type_map.get(ext, "unknown")


def validate_file_exists(file_path: str) -> bool:
    """验证文件是否存在"""
    if not os.path.exists(file_path):
        print(f"⚠ 文件不存在: {file_path}")
        return False
    return True


def validate_files(file_paths: List[str]) -> List[str]:
    """验证文件列表，返回有效的文件路径"""
    supported = ("docx", "pdf", "txt", "markdown")
    valid = []
    for fp in file_paths:
        if validate_file_exists(fp):
            ft = detect_file_type(fp)
            if ft in supported:
                valid.append(fp)
            else:
                print(f"⚠ 不支持的文件类型: {fp} ({ft})")
    return valid


def ensure_dir(dir_path: str) -> str:
    """确保目录存在"""
    if dir_path:
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
        print(f"⚠ 提示词模板不存在: {prompt_path}")
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
        print("⚠ 配置文件不存在，使用默认配置")
        return _default_config()
    return load_json(config_path)


def _default_config() -> Dict:
    return {
        "llm": {"model": "gpt-4.1-mini", "temperature": 0.3, "max_tokens": 4096},
        "generation": {
            "default_page_limit": 20,
            "max_bullets_per_page": 5,
        },
    }


# ─────────────────── 文本工具 ───────────────────

def format_source_info(file_path: str, section: str = None) -> str:
    """格式化来源信息"""
    filename = os.path.basename(file_path)
    if section:
        return f"{filename} - {section}"
    return filename
