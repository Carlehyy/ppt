# PPT汇报文档生成器 Skill

## 何时使用此Skill

当用户请求涉及以下任何关键词或意图时，**必须**使用此Skill：
- 从文档/资料生成PPT汇报大纲
- 整理资料做汇报文档
- 多个文档整合成汇报材料
- 生成PPT汇报的Markdown文档
- prepare presentation outline, create report from documents

**典型用户指令**：
```
"帮我把这几份文档整理成一个汇报大纲"
"从这些资料中提取关键信息，生成一个PPT汇报文档"
"把这些PDF整合成一个结构化的汇报材料"
```

---

## 核心理念

> 你不是一个"文档搬运工"，而是一个"汇报策略师"。
> 你的任务是：**内容提炼** + **结构重构** + **叙事设计**。

### 三大核心能力

1. **内容提炼**：从冗长文档中提取"汇报逻辑链"，识别关键信息和支撑要点
2. **结构重构**：将"文档逻辑"转换为"演示逻辑"，设计清晰的章节和页面结构
3. **叙事设计**：选择最合适的叙事策略，让听众容易理解和记住

---

## 执行流程（三阶段Pipeline）

### 阶段1：内容解析

**目标**：从多个原始语料中提取结构化信息

```python
import sys, os
sys.path.insert(0, os.path.join("SKILL_DIR", "scripts"))
from parse_content import ContentParser
from llm_client import LLMClient

llm = LLMClient()
parser = ContentParser(llm)
parsed_content = parser.parse(["文件路径1", "文件路径2", ...])
```

**四层递进解析架构**：
- **第一层·物理层**：提取文本、标题层级、表格、图片等原始元素
- **第二层·语义层**：识别文档类型、提取信息要素（成果/问题/数据/计划）、标注重要性
- **第三层·关联层**：分析多文档间的时间关系、主题关系、层级关系
- **第四层·框架映射层**：确定章节结构、识别信息缺口

---

### 阶段2：大纲规划

**目标**：基于内容分析和用户需求，设计汇报大纲

```python
from outline_planner import OutlinePlanner

planner = OutlinePlanner(llm)
outline_plan = planner.plan(
    parsed_content=parsed_content,
    user_config={
        "presentation_title": "汇报标题",
        "scenario": "向上汇报",  # 向上汇报/项目汇报/客户汇报/团队分享
        "core_intent": "最希望听众记住什么",
        "target_pages": 15,  # 目标页数
        "language_style": "专业简洁"  # 专业简洁/轻松活泼/数据驱动
    }
)
```

**叙事策略选择**（融合职场沟通模型）：

| 策略 | 结构（基于职场模型） | 适用场景 | 底层模型 |
|:---|:---|:---|:---|
| **成果导向型** | S（背景）→ T（目标）→ A（行动+挑战）→ R（成果）→ 下一步 | 向上汇报、工作总结、述职报告 | STAR法则 |
| **问题导向型** | S（情境）→ C（冲突）→ Q（问题）→ A（应对策略+进展+待解决） | 争取资源、项目提案、故事讲述 | SCQA模型 |
| **快速汇报型** | P（核心结论）→ R（关键原因）→ E（支撑案例）→ P（总结强调） | 简短汇报、快速决策、会议发言 | PREP模型 |
| **时间线型** | 目标回顾 → 阶段进展 → 当前状态 → 下期规划 | 常规周期汇报 | 时间线 + 金字塔 |
| **对比型** | 原定计划 → 实际执行 → 差异分析 → 调整方案 | 项目复盘、偏差较大时 | 对比 + 金字塔 |
| **知识传递型** | 背景介绍 → 核心概念 → 应用场景 → 案例分析 | 技术分享、知识普及 | 知识传递 + 金字塔 |

**职场沟通模型说明**：

1. **STAR法则**（面试和复盘的王牌）
   - S（Situation）情境：当时的背景是什么？
   - T（Task）任务：面临的具体任务或目标是什么？
   - A（Action）行动：具体采取了哪些行动？（重点，多用“我”作为主语）
   - R（Result）结果：行动带来了什么可量化的结果？

2. **SCQA模型**（讲故事、做汇报的黄金框架）
   - S（Situation）情境：描述大家熟悉的背景
   - C（Complication）冲突：引入挑战或问题，制造悬念
   - Q（Question）问题：基于冲突，提出关键问题
   - A（Answer）答案：给出解决方案或核心观点

3. **PREP模型**（最快表明观点的利器）
   - P（Point）观点：先亮出核心结论
   - R（Reason）理由：简单说明原因
   - E（Example）例子：举具体例子支撑观点
   - P（Point）重申：最后再强调一遍观点

4. **金字塔原理**（构建复杂内容的基石）
   - **结论先行**：每页核心信息必须是一句话（≤ 20字）
   - **以上统下**：章节标题统领章节内容，核心信息统领支撑要点
   - **归类分组**：支撑要点不超过3个，逻辑分组
   - **逻辑递进**：章节之间、页面之间有明确的逻辑关系

**重要**：所有叙事策略都必须遵循金字塔原理的四大原则！

**"每页一个核心信息"的强约束**：
- **core_message**：该页要传达的核心信息（一句话）
- **supporting_points**：不超过3个支撑要点
- **data_elements**：该页需要的图表或数据元素
- **content_source**：内容来源标注

---

### 阶段3：文档生成

**目标**：生成结构化的Markdown汇报文档

```python
from md_generator import MarkdownGenerator

generator = MarkdownGenerator()
md_content = generator.generate(
    outline_plan=outline_plan,
    parsed_content=parsed_content,
    output_path="汇报文档.md"
)
```

**输出Markdown格式**：
- 清晰的章节结构
- 每页的核心信息和支撑要点
- 数据元素和图表建议
- 内容来源索引

---

## 一键执行（完整流程）

```python
import sys, os
sys.path.insert(0, os.path.join("SKILL_DIR", "scripts"))
from orchestrator import ReportOrchestrator

agent = ReportOrchestrator(config_path="SKILL_DIR/config.json")
result = agent.run(
    input_files=["文件1.pdf", "文件2.docx", "文件3.txt"],
    user_config={
        "presentation_title": "汇报标题",
        "scenario": "向上汇报",
        "core_intent": "最希望听众记住什么",
        "target_pages": 15,
        "language_style": "专业简洁"
    },
    output_path="汇报文档.md"
)
```

**参数说明**：
- `input_files`：原始语料文件路径列表（支持PDF、Word、TXT、Markdown）
- `presentation_title`：汇报标题
- `scenario`：汇报场景（向上汇报/项目汇报/客户汇报/团队分享）
- `core_intent`：核心诉求（一句话描述最希望听众记住什么）
- `target_pages`：目标页数（默认15页）
- `language_style`：语言风格（专业简洁/轻松活泼/数据驱动）
- `output_path`：输出Markdown文件路径

---

## 依赖安装

首次使用前，请安装Python依赖：

```bash
pip install -r SKILL_DIR/requirements.txt
```

主要依赖：`python-docx`, `PyPDF2`, `openai`, `markdown`

---

## 配置说明

配置文件位于 `SKILL_DIR/config.json`，支持以下配置：

```json
{
  "llm": {
    "model": "gpt-4.1-mini",
    "temperature": 0.3,
    "max_tokens": 4096
  },
  "generation": {
    "default_page_limit": 20,
    "max_bullets_per_page": 5
  }
}
```

---

## 文件结构

```
ppt-report-md/
├── SKILL.md              ← 你正在阅读的文件
├── config.json           ← 配置文件
├── requirements.txt      ← Python依赖
├── scripts/
│   ├── __init__.py
│   ├── orchestrator.py   ← 主控制器
│   ├── parse_content.py  ← 内容解析（四层递进）
│   ├── outline_planner.py ← 大纲规划
│   ├── md_generator.py   ← Markdown生成器
│   ├── llm_client.py     ← LLM交互
│   └── utils.py          ← 工具函数
└── prompts/
    ├── content_analysis.txt  ← 内容分析提示词
    └── outline_planning.txt  ← 大纲规划提示词
```

---

## 注意事项

1. **SKILL_DIR** 在代码中需替换为此Skill的实际安装路径
2. 所有提取的信息都必须标注来源（哪份文档、哪个章节）
3. 数字、比例、金额等敏感数据需要保持原文准确性
4. 生成的Markdown文档可以直接用于制作PPT或进一步编辑

---

## 输出示例

生成的Markdown文档包含：

```markdown
# [汇报标题]

## 概览
- **汇报场景**：向上汇报
- **核心诉求**：展示项目核心成果和下一步规划
- **预计页数**：15页
- **预计时长**：18分钟

---

## 第一章：项目背景与目标

### 页面1：项目启动背景

**核心信息**：本项目旨在解决XX问题，提升XX能力

**关键要点**：
- 市场痛点：XX
- 业务目标：XX
- 预期收益：XX

**内容来源**：项目方案.docx - 第1章

---

### 页面2：核心目标拆解
...
```
