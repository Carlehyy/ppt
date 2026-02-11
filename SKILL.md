---
name: ppt-report-agent
description: Intelligent PPT generation from documents and templates for professional work reports. Automatically creates editable PowerPoint presentations by analyzing source materials (Docx/PDF/PPT), applying template styles, and generating structured narratives with AI-powered content planning.
author: Manus AI
version: 1.0.0
license: MIT
tags: [ppt, powerpoint, presentation, document-processing, ai-agent, automation]
---

# PPT Report Agent

一个智能的PPT生成Skill，能够从原始素材文档和PPT模板自动生成专业的、可编辑的PowerPoint演示文稿。

## 功能特性

- ✅ **多格式支持**: 自动解析Word (.docx)、PDF (.pdf)、PowerPoint (.pptx) 文档
- ✅ **智能内容提取**: 使用LLM从非结构化文档中提取结构化语义信息
- ✅ **模板风格应用**: 深度分析并忠实应用用户提供的PPT模板设计
- ✅ **智能版式匹配**: 自动为每页内容选择最合适的模板版式
- ✅ **五阶段Pipeline**: 内容解析 → 智能咨询 → 大纲规划 → 逐页生成 → 质量校审
- ✅ **质量保证**: 五维度质量评估（准确性、精准性、连贯性、一致性、规范性）
- ✅ **完全可编辑**: 生成标准PPTX文件，可在PowerPoint中完全编辑

## 快速开始

### 1. 安装依赖

```bash
cd /path/to/ppt-report-agent
pip install -r requirements.txt
```

### 2. 准备PPT模板

将您的高质量PPT模板（.pptx文件）放入 `templates/user_templates/` 目录。

**模板要求**：
- 包含多种版式（封面、内容、对比、数据等）
- 版式命名清晰（如"Title and Content"、"Comparison"）
- 使用母版统一配色和字体

**推荐来源**：[优品PPT](https://www.ypppt.com)

### 3. 运行测试

```bash
python test_skill.py
```

确保所有测试项通过。

### 4. 生成PPT

#### 方式1：命令行

```bash
python scripts/orchestrator.py \
  --input /path/to/document1.docx /path/to/document2.pdf \
  --template templates/user_templates/your_template.pptx
```

#### 方式2：Python API

```python
import sys
sys.path.insert(0, '/path/to/ppt-report-agent')

from scripts.orchestrator import PPTAgentOrchestrator

# 初始化Agent
agent = PPTAgentOrchestrator()

# 运行完整Pipeline
output_path, review = agent.run(
    input_files=[
        "/path/to/Q4总结.docx",
        "/path/to/数据报表.pdf"
    ],
    template_path="templates/user_templates/business_pro.pptx"
)

print(f"生成的PPT: {output_path}")
print(f"质量评分: {review['overall_score']}/100")
```

#### 方式3：在AI助手中使用

当您在Claude Code、Open Code或Manus中描述PPT生成需求时，AI助手会自动加载此Skill并调用相应功能。

**示例提示词**：
```
请帮我从Q4总结.docx生成一份工作汇报PPT，使用templates/user_templates/business.pptx作为模板
```

## 工作流程

```
原始素材 (Docx/PDF/PPT) + PPT模板
            ↓
[阶段1+2] 内容解析 & 模板分析 (并行)
            ↓
[阶段3] 智能咨询 (明确需求)
            ↓
[阶段4] 大纲规划 (用户确认)
            ↓
[阶段5] 逐页生成 (LLM + python-pptx)
            ↓
[阶段6] 质量校审 (五维度评估)
            ↓
    output.pptx (可编辑)
```

## 配置说明

### 基础配置 (config.json)

```json
{
  "llm": {
    "model": "gpt-4.1-mini",      // LLM模型
    "temperature": 0.7,            // 创造性参数
    "max_retries": 3,              // 重试次数
    "timeout": 60                  // 超时时间
  },
  "generation": {
    "default_page_limit": 20,      // 默认页数限制
    "max_bullets_per_slide": 5,    // 每页最多要点数
    "font_size_adjustment": true   // 自动调整字号
  }
}
```

### 提示词自定义 (prompts/)

您可以编辑以下提示词文件来调整LLM行为：

- `content_analysis.txt` - 内容解析策略
- `consultation.txt` - 咨询问题生成
- `outline_planning.txt` - 大纲规划逻辑
- `slide_generation.txt` - 页面内容生成
- `quality_review.txt` - 质量评审标准

## 技术架构

### 核心模块

| 模块 | 文件 | 职责 |
|:---|:---|:---|
| **主控制器** | `orchestrator.py` | 编排完整的五阶段Pipeline |
| **内容解析器** | `parse_content.py` | 从Docx/PDF/PPT提取结构化内容 |
| **模板分析器** | `analyze_template.py` | 分析PPT模板版式和设计DNA |
| **LLM客户端** | `llm_client.py` | 封装所有LLM交互逻辑 |
| **PPT生成器** | `generate_slides.py` | 将内容填充到模板版式 |
| **工具函数** | `utils.py` | 通用工具函数 |

### 技术栈

- **python-pptx** (1.0.2): PPT创建和模板分析
- **python-docx** (1.1.0): Word文档解析
- **PyPDF2** (3.0.1): PDF文档解析
- **openai** (>=1.0.0): LLM交互
- **Pillow** (10.2.0): 图片处理

## 使用示例

### 示例1：工作汇报PPT

```python
agent = PPTAgentOrchestrator()

output_path, review = agent.run(
    input_files=["Q4工作总结.docx", "数据报表.pdf"],
    template_path="templates/user_templates/business_pro.pptx",
    user_config={
        "scenario": "工作总结汇报",
        "core_intent": "展示成果",
        "page_limit": 20,
        "language_style": "专业"
    }
)
```

### 示例2：项目进展汇报

```python
output_path, review = agent.run(
    input_files=["项目进展.docx"],
    template_path="templates/user_templates/tech_modern.pptx",
    user_config={
        "scenario": "项目进展汇报",
        "core_intent": "分析问题",
        "page_limit": 15
    }
)
```

## 质量保证

生成的PPT会从以下五个维度进行评估：

1. **内容准确性** (Content Accuracy): 数据来源可追溯，信息与原始素材一致
2. **焦点精准性** (Focus Precision): 每页一个核心信息，标题准确概括
3. **逻辑连贯性** (Logic Coherence): 章节逻辑清晰，叙事流畅
4. **风格一致性** (Style Consistency): 版式选择合理，符合模板设计语言
5. **质量标准** (Quality Standards): 格式规范，要点数量适中

评分标准：
- 90-100分：优秀
- 80-89分：良好
- 70-79分：合格
- <70分：需改进

## 常见问题

### Q: 如何提高生成质量？

1. 提供高质量、结构清晰的原始素材
2. 使用专业的PPT模板（推荐从[优品PPT](https://www.ypppt.com)获取）
3. 调整LLM的temperature参数（降低可提高准确性）
4. 根据质量评审的建议进行手动调整

### Q: 版式选择不合理怎么办？

确保模板的版式有清晰的命名，例如：
- "Title Slide" → 封面页
- "Title and Content" → 内容页
- "Comparison" → 对比页
- "Title and Chart" → 数据页

### Q: 生成的内容不准确？

检查原始素材的质量。Agent会标注每个内容的来源和置信度，低置信度的内容需要人工审核。

### Q: 如何自定义页数？

在`config.json`中调整`default_page_limit`，或在运行时传入`user_config`。

## 目录结构

```
ppt-report-agent/
├── SKILL.md                # 本文件 - Skill核心文档
├── README.md               # 项目总览
├── USAGE_GUIDE.md          # 详细使用指南
├── requirements.txt        # Python依赖
├── config.json             # 配置文件
├── test_skill.py           # 测试脚本
│
├── scripts/                # 核心Python模块
│   ├── orchestrator.py     # 主控制器
│   ├── parse_content.py    # 内容解析
│   ├── analyze_template.py # 模板分析
│   ├── llm_client.py       # LLM交互
│   ├── generate_slides.py  # PPT生成
│   └── utils.py            # 工具函数
│
├── prompts/                # LLM提示词模板
│   ├── content_analysis.txt
│   ├── consultation.txt
│   ├── outline_planning.txt
│   ├── slide_generation.txt
│   └── quality_review.txt
│
├── templates/              # PPT模板库
│   └── user_templates/     # 用户自定义模板
│
└── references/             # 参考文档
    └── layout_mapping_rules.md
```

## 环境要求

- Python 3.8+
- 需要设置环境变量 `OPENAI_API_KEY`
- 支持macOS, Linux, Windows

## 许可证

MIT License

## 支持

- 详细文档：查看 `USAGE_GUIDE.md`
- 参考资料：查看 `references/` 目录
- GitHub仓库：https://github.com/Carlehyy/ppt
