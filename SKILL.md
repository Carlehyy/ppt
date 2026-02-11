---
name: ppt-report-agent
description: Generate professional PowerPoint presentations from documents and templates. Use this skill when user asks to create PPT, generate slides, make presentation, or convert documents to PowerPoint format. Automatically analyzes source materials, applies template styles, and creates structured narratives.
author: Manus AI
version: 1.0.0
license: MIT
tags: [ppt, powerpoint, presentation, slides, document-to-ppt, report-generation]
triggers: [生成PPT, 制作PPT, 创建演示文稿, generate ppt, create presentation, make slides, 做PPT, 生成幻灯片]
---

# PPT Report Agent

当用户需要从文档生成PPT时，使用此Skill自动创建专业的、可编辑的PowerPoint演示文稿。

## 🎯 何时使用此Skill

当用户的请求包含以下意图时，应该使用此Skill：

- **生成PPT**: "帮我生成一个PPT"、"制作一份演示文稿"
- **文档转PPT**: "把这个Word文档转成PPT"、"从这些资料生成幻灯片"
- **汇报材料**: "做一份工作汇报PPT"、"生成项目进展报告"
- **参考模板**: "参考这个模板的风格生成PPT"

**典型用户指令示例**：
```
"请学习Q4总结.docx资料，然后参考business.pptx的风格，帮我生成一个《星链洞察报告》"
```

## 📋 使用此Skill的步骤

### 第1步：确认用户需求

当识别到PPT生成需求时，向用户确认以下信息：

1. **原始素材**：用户提供的文档文件（Docx/PDF/PPT）
2. **参考模板**：用户指定的PPT模板文件，或使用默认模板
3. **汇报主题**：PPT的标题和核心主题
4. **特殊要求**：页数限制、风格偏好等

**确认话术示例**：
```
我将帮您生成《星链洞察报告》PPT。请确认：
- 原始素材：Q4总结.docx
- 参考模板：business.pptx
- 预计页数：15-20页
- 汇报场景：工作总结汇报

是否开始生成？
```

### 第2步：准备工作环境

执行以下命令准备环境：

```bash
# 1. 进入Skill目录
cd /path/to/ppt-report-agent

# 2. 确认依赖已安装
pip install -r requirements.txt -q

# 3. 确认模板文件存在
ls -la templates/user_templates/
```

### 第3步：执行PPT生成

使用以下Python代码调用Skill的核心功能：

```python
import sys
import os

# 添加Skill路径
skill_path = "/path/to/ppt-report-agent"
sys.path.insert(0, skill_path)

from scripts.orchestrator import PPTAgentOrchestrator

# 初始化Agent
agent = PPTAgentOrchestrator()

# 配置用户需求
user_config = {
    "scenario": "工作总结汇报",      # 汇报场景
    "core_intent": "展示成果",       # 核心意图
    "page_limit": 20,                # 页数限制
    "language_style": "专业",        # 语言风格
    "presentation_title": "星链洞察报告"  # PPT标题
}

# 执行生成
try:
    output_path, review = agent.run(
        input_files=[
            "/path/to/Q4总结.docx"
        ],
        template_path=os.path.join(skill_path, "templates/user_templates/business.pptx"),
        user_config=user_config
    )
    
    print(f"✓ PPT生成成功: {output_path}")
    print(f"✓ 质量评分: {review['overall_score']}/100")
    
    # 显示质量评审建议
    if review.get('suggestions'):
        print("\n改进建议:")
        for suggestion in review['suggestions'][:3]:
            print(f"  - {suggestion}")
            
except Exception as e:
    print(f"✗ 生成失败: {e}")
    print("请检查文件路径和依赖是否正确")
```

### 第4步：向用户交付结果

生成完成后，向用户报告：

```
✓ 已成功生成《星链洞察报告》PPT

📊 质量评估:
- 总体评分: 85/100 (良好)
- 内容准确性: 18/20
- 逻辑连贯性: 17/20
- 风格一致性: 17/20

📄 生成文件: output.pptx (共18页)

💡 改进建议:
1. 第5页的增长率数据建议补充来源
2. 第8页建议拆分为两页，每页聚焦一个主题

您可以在PowerPoint中打开并进一步编辑此文件。
```

## 🔧 核心功能说明

### 功能1：内容解析

从用户提供的文档中提取结构化信息：

- 支持格式：`.docx`, `.pdf`, `.pptx`
- 提取内容：文本、表格、图片
- 语义分析：使用LLM识别成果、数据、问题、计划等信息单元

### 功能2：模板分析

深度分析用户提供的PPT模板：

- 提取所有版式（layouts）
- 分析占位符结构
- 推断每个版式的最佳使用场景

### 功能3：智能规划

使用LLM规划PPT大纲：

- 选择叙事策略（成果导向、问题导向等）
- 规划章节结构
- 为每一页匹配合适的版式

### 功能4：内容生成

逐页生成PPT内容：

- 标题：简洁明了（不超过15字）
- 正文：3-5个要点，每个不超过30字
- 数据：优先使用具体数字和百分比
- 溯源：标注内容来源和置信度

### 功能5：质量校审

五维度质量评估：

1. **内容准确性**: 数据来源可追溯
2. **焦点精准性**: 每页一个核心信息
3. **逻辑连贯性**: 叙事流畅
4. **风格一致性**: 符合模板设计
5. **质量标准**: 格式规范

## 📁 文件路径说明

在调用Skill时，需要正确设置以下路径：

```python
# Skill根目录（根据实际安装位置调整）
SKILL_ROOT = "/path/to/ppt-report-agent"

# 核心脚本路径
ORCHESTRATOR = f"{SKILL_ROOT}/scripts/orchestrator.py"

# 模板目录
TEMPLATE_DIR = f"{SKILL_ROOT}/templates/user_templates/"

# 配置文件
CONFIG_FILE = f"{SKILL_ROOT}/config.json"
```

## ⚙️ 配置选项

可以通过`user_config`参数自定义生成行为：

```python
user_config = {
    # 汇报场景
    "scenario": "工作总结汇报" | "项目进展汇报" | "数据分析汇报" | "产品发布汇报",
    
    # 核心意图
    "core_intent": "展示成果" | "分析问题" | "提出方案" | "争取资源",
    
    # 页数限制
    "page_limit": 15,  # 建议10-30页
    
    # 语言风格
    "language_style": "专业严谨" | "简洁明快" | "生动活泼",
    
    # PPT标题
    "presentation_title": "您的PPT标题"
}
```

## 🎨 模板要求

用户提供的PPT模板应满足以下要求：

1. **格式**: `.pptx` (PowerPoint 2007+)
2. **版式**: 包含多种版式（封面、内容、对比、数据等）
3. **命名**: 版式名称清晰（如"Title and Content"、"Comparison"）
4. **母版**: 使用母版统一配色和字体

**推荐模板来源**: [优品PPT](https://www.ypppt.com)

## 🚨 错误处理

如果生成失败，检查以下常见问题：

1. **文件路径错误**: 确认所有文件路径正确且文件存在
2. **依赖未安装**: 运行`pip install -r requirements.txt`
3. **LLM配置错误**: 确认`OPENAI_API_KEY`环境变量已设置
4. **模板格式错误**: 确认模板是有效的`.pptx`文件

## 📊 输出说明

生成的PPT文件：

- **文件名**: `output.pptx`（默认）
- **格式**: 标准PPTX格式
- **可编辑**: 可在Microsoft PowerPoint或WPS中完全编辑
- **包含**: 封面页、内容页、结束页

## 💡 最佳实践

1. **素材准备**: 提供结构清晰、内容完整的原始文档
2. **模板选择**: 使用专业的、版式丰富的PPT模板
3. **需求明确**: 清晰告知汇报场景和核心意图
4. **后期调整**: 生成后在PowerPoint中进行微调和优化

## 🔍 调试模式

如需查看详细的生成过程，可以设置调试模式：

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 然后执行生成
agent.run(...)
```

## 📚 相关文档

- **详细使用指南**: `USAGE_GUIDE.md`
- **版式映射规则**: `references/layout_mapping_rules.md`
- **项目总览**: `README.md`

---

**重要提示**: 此Skill需要访问LLM API（通过`OPENAI_API_KEY`），请确保环境变量已正确配置。
