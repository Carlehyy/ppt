# PPT汇报文档生成器

从多个原始语料文件中提取信息，生成结构化的Markdown汇报文档。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API Key

```bash
export OPENAI_API_KEY="your-api-key"
```

### 3. 使用示例

```python
import sys, os
sys.path.insert(0, os.path.join("SKILL_DIR", "scripts"))
from orchestrator import ReportOrchestrator

agent = ReportOrchestrator(config_path="SKILL_DIR/config.json")

result = agent.run(
    input_files=["doc1.pdf", "doc2.docx", "doc3.txt"],
    user_config={
        "presentation_title": "项目汇报",
        "scenario": "向上汇报",
        "core_intent": "展示核心成果",
        "target_pages": 15,
        "language_style": "专业简洁"
    },
    output_path="汇报文档.md"
)
```

## 文件结构

```
ppt-report-md/
├── SKILL.md              # Skill使用说明
├── README.md             # 本文件
├── config.json           # 配置文件
├── requirements.txt      # Python依赖
├── scripts/              # 核心代码
│   ├── orchestrator.py   # 主控制器
│   ├── parse_content.py  # 内容解析
│   ├── outline_planner.py # 大纲规划
│   ├── md_generator.py   # Markdown生成
│   ├── llm_client.py     # LLM交互
│   └── utils.py          # 工具函数
└── prompts/              # 提示词
    ├── content_analysis.txt
    └── outline_planning.txt
```

## 支持的文档格式

- PDF (.pdf)
- Word (.docx)
- 文本 (.txt)
- Markdown (.md)

## 职场沟通模型

本 skill 融合了经典的职场沟通模型，确保生成的汇报文档符合职场表达习惯：

- **STAR法则**：适用于向上汇报、工作总结、述职报告
- **SCQA模型**：适用于争取资源、项目提案、故事讲述
- **PREP模型**：适用于简短汇报、快速决策、会议发言
- **金字塔原理**：所有策略的底层逻辑（结论先行、以上统下、归类分组、逻辑递进）
