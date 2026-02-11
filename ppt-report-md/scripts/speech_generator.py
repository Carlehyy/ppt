#!/usr/bin/env python3
"""
演讲稿生成模块 — 为汇报PPT生成完整的演讲稿
"""

from typing import Dict, Any
from llm_client import LLMClient
from utils import load_prompt, save_text


class SpeechGenerator:
    """演讲稿生成器"""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def generate(self, outline_plan: Dict[str, Any], user_config: Dict[str, Any],
                 output_path: str) -> str:
        """
        生成演讲稿

        Args:
            outline_plan: 大纲规划结果
            user_config: 用户配置
            output_path: 输出文件路径

        Returns:
            生成的演讲稿内容
        """
        print("🎤 开始生成演讲稿...")

        # 调用LLM生成演讲稿（直接生成Markdown）
        prompt = self._build_prompt(outline_plan, user_config)
        speech_content = self.llm.call_llm(prompt, response_json=False)

        # 保存到文件
        save_text(speech_content, output_path)

        print(f"✅ 演讲稿已生成: {output_path}\n")
        return speech_content

    def _build_prompt(self, outline_plan: Dict[str, Any],
                     user_config: Dict[str, Any]) -> str:
        """构建演讲稿生成提示词"""
        import json
        
        prompt = f"""你是一位专业的演讲稿撰写专家，擅长为职场汇报撰写清晰、流畅、有说服力的演讲稿。

## 任务

基于以下信息，为用户生成一份完整的演讲稿。

### 汇报大纲

```json
{json.dumps(outline_plan, ensure_ascii=False, indent=2)}
```

### 用户配置

```json
{json.dumps(user_config, ensure_ascii=False, indent=2)}
```

---

## 要求

请直接生成Markdown格式的演讲稿，包含以下部分：

### 1. 开场白（1-2分钟）
- 问候语（根据场景选择）
- 汇报主题介绍
- 汇报目的
- 结构预告
- 时间说明

### 2. 正文（逐页讲解）
为每一页PPT生成详细的讲解内容：
- **引入语**：如何自然地引出这一页
- **核心讲解**：详细解释页面的核心信息和关键要点
- **数据说明**：如何解读图表和数据
- **强调重点**：这一页最重要的takeaway
- **过渡语**：承上启下，引出下一页

### 3. 结束语（1-2分钟）
- 核心要点总结
- 行动建议
- 致谢
- Q&A引导

---

## 语言风格

- 口语化，符合职场汇报习惯
- 根据场景调整语气（向上汇报/团队分享/客户汇报）
- 重点突出，逻辑清晰
- 每页建议用时：30秒-2分钟

---

## 输出格式

请直接输出Markdown格式的演讲稿，不要包裹在```markdown```代码块中。

格式示例：

```
# 演讲稿：[汇报标题]

## 📋 汇报信息

- **汇报标题**: ...
- **预计时长**: ...
- **总页数**: ...
- **汇报场景**: ...

---

## 🎤 开场白

**[建议用时：90秒]**

各位领导/同事，大家好！

[开场白内容...]

---

## 📖 正文

### 第1页：[页面标题]

**[建议用时：60秒]**

**引入**：[引入语]

**讲解**：[核心讲解]

**重点**：[强调重点]

---

**[过渡]** [过渡语]

---

### 第2页：[页面标题]

...

---

## 🎯 结束语

**[建议用时：90秒]**

[结束语内容...]

感谢大家的倾听！现在我很乐意回答大家的问题。

---

## 📝 备注

- **重点页面**: ...
- **时间分配**: ...
- **注意事项**: ...
```

现在，请开始生成演讲稿。
"""
        return prompt

    def _format_to_markdown_old(self, speech_data: Dict[str, Any], 
                           outline_plan: Dict[str, Any],
                           user_config: Dict[str, Any]) -> str:
        """将演讲稿数据格式化为Markdown"""
        # 确保 speech_data 是 dict
        if not isinstance(speech_data, dict):
            print(f"⚠️  speech_data 类型错误: {type(speech_data)}")
            speech_data = {}
        
        lines = []

        # 标题
        title = user_config.get("presentation_title", "汇报")
        lines.append(f"# 演讲稿：{title}")
        lines.append("")

        # 汇报信息
        lines.append("## 📋 汇报信息")
        lines.append("")
        overview = outline_plan.get("overview", {})
        lines.append(f"- **汇报标题**: {title}")
        lines.append(f"- **预计时长**: {overview.get('estimated_duration', 'N/A')}")
        lines.append(f"- **总页数**: {overview.get('total_pages', 'N/A')}页")
        lines.append(f"- **汇报场景**: {user_config.get('scenario', 'N/A')}")
        lines.append(f"- **语言风格**: {user_config.get('language_style', 'N/A')}")
        lines.append("")
        lines.append("---")
        lines.append("")

        # 开场白
        lines.append(self._format_opening(speech_data.get("opening", {})))

        # 正文（逐页讲解）
        lines.append(self._format_pages_script(speech_data.get("pages_script", [])))

        # 结束语
        lines.append(self._format_closing(speech_data.get("closing", {})))

        # 备注
        lines.append(self._format_metadata(speech_data.get("metadata", {})))

        return "\n".join(lines)

    def _format_opening(self, opening: Dict[str, Any]) -> str:
        """格式化开场白"""
        lines = []
        lines.append("## 🎤 开场白")
        lines.append("")
        lines.append(f"**[建议用时：{opening.get('estimated_duration', 60)}秒]**")
        lines.append("")
        
        # 问候语
        lines.append(opening.get("greeting", ""))
        lines.append("")
        
        # 主题介绍
        lines.append(opening.get("topic_introduction", ""))
        lines.append("")
        
        # 目的
        lines.append(opening.get("purpose", ""))
        lines.append("")
        
        # 结构预告
        lines.append(opening.get("structure_preview", ""))
        lines.append("")
        
        # 时间说明
        lines.append(opening.get("timing_note", ""))
        lines.append("")
        lines.append("---")
        lines.append("")
        
        return "\n".join(lines)

    def _format_pages_script(self, pages_script: list) -> str:
        """格式化正文（逐页讲解）"""
        lines = []
        lines.append("## 📖 正文")
        lines.append("")

        for page in pages_script:
            page_num = page.get("page_number", 0)
            page_title = page.get("page_title", "")
            is_key = "⭐" if page.get("is_key_page", False) else ""
            
            # 页面标题
            lines.append(f"### 第{page_num}页：{page_title} {is_key}")
            lines.append("")
            lines.append(f"**[建议用时：{page.get('estimated_duration', 60)}秒]**")
            lines.append("")
            
            # 引入语
            if page.get("introduction"):
                lines.append(f"**引入**：{page.get('introduction')}")
                lines.append("")
            
            # 核心讲解
            if page.get("main_content"):
                lines.append(f"**讲解**：{page.get('main_content')}")
                lines.append("")
            
            # 数据说明
            if page.get("data_explanation"):
                lines.append(f"**数据说明**：{page.get('data_explanation')}")
                lines.append("")
            
            # 强调重点
            if page.get("key_takeaway"):
                lines.append(f"**重点**：{page.get('key_takeaway')}")
                lines.append("")
            
            # 过渡语
            if page.get("transition"):
                lines.append("---")
                lines.append("")
                lines.append(f"**[过渡]** {page.get('transition')}")
                lines.append("")
                lines.append("---")
                lines.append("")

        return "\n".join(lines)

    def _format_closing(self, closing: Dict[str, Any]) -> str:
        """格式化结束语"""
        lines = []
        lines.append("## 🎯 结束语")
        lines.append("")
        lines.append(f"**[建议用时：{closing.get('estimated_duration', 60)}秒]**")
        lines.append("")
        
        # 总结
        lines.append(closing.get("summary", ""))
        lines.append("")
        
        # 行动建议
        if closing.get("action_items"):
            lines.append(closing.get("action_items"))
            lines.append("")
        
        # 致谢
        lines.append(closing.get("thanks", ""))
        lines.append("")
        
        # Q&A引导
        lines.append(closing.get("qa_invitation", ""))
        lines.append("")
        lines.append("---")
        lines.append("")
        
        return "\n".join(lines)

    def _format_metadata(self, metadata: Dict[str, Any]) -> str:
        """格式化备注信息"""
        lines = []
        lines.append("## 📝 备注")
        lines.append("")
        
        # 总时长
        total_duration = metadata.get("total_estimated_duration", 0)
        minutes = total_duration // 60
        seconds = total_duration % 60
        lines.append(f"- **总预计时长**: {minutes}分{seconds}秒")
        
        # 重点页面
        key_pages = metadata.get("key_pages", [])
        if key_pages:
            key_pages_str = "、".join([f"第{p}页" for p in key_pages])
            lines.append(f"- **重点页面**: {key_pages_str}")
        
        # 注意事项
        if metadata.get("notes"):
            lines.append(f"- **注意事项**: {metadata.get('notes')}")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*本演讲稿由PPT汇报文档生成器自动生成*")
        
        return "\n".join(lines)
