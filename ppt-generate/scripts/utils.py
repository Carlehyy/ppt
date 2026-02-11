#!/usr/bin/env python3
"""
Utility functions for PPT Report Agent
"""

import os
import json
from typing import Dict, List, Any


def load_json(file_path: str) -> Dict:
    """Load JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(data: Dict, file_path: str):
    """Save data to JSON file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_text(file_path: str) -> str:
    """Load text file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def save_text(text: str, file_path: str):
    """Save text to file"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)


def get_file_extension(file_path: str) -> str:
    """Get file extension"""
    return os.path.splitext(file_path)[1].lower()


def ensure_dir(dir_path: str):
    """Ensure directory exists"""
    os.makedirs(dir_path, exist_ok=True)


def format_source_info(file_path: str, page_num: int = None) -> str:
    """Format source information"""
    filename = os.path.basename(file_path)
    if page_num:
        return f"{filename}:第{page_num}页"
    return filename


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Merge two dictionaries"""
    result = dict1.copy()
    result.update(dict2)
    return result
