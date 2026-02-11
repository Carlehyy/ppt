# PPT Report Agent

一个智能的PPT生成Skill，能够从原始素材和模板自动生成专业的、可编辑的PowerPoint演示文稿。

## 功能特性

- ✅ **多格式支持**: 解析Word (.docx)、PDF (.pdf)、PowerPoint (.pptx) 文档
- ✅ **模板应用**: 深度分析并应用用户提供的高质量PPT模板
- ✅ **智能规划**: 基于LLM的大纲规划和内容生成
- ✅ **版式匹配**: 自动为每页内容选择最合适的版式
- ✅ **质量校审**: 五维度质量评估和改进建议
- ✅ **完全可编辑**: 生成的PPTX文件可在PowerPoint中完全编辑

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 准备模板

将您的高质量PPT模板（.pptx文件）放入 `templates/user_templates/` 目录。

推荐模板来源：[优品PPT](https://www.ypppt.com)

### 3. 运行测试

```bash
python test_skill.py
```

### 4. 生成PPT

```bash
python scripts/orchestrator.py \
  --input /path/to/document1.docx /path/to/document2.pdf \
  --template templates/user_templates/your_template.pptx
```

## 工作流程

```
原始素材 + 模板
    ↓
[阶段1+2] 内容解析 & 模板分析
    ↓
[阶段3] 智能咨询
    ↓
[阶段4] 大纲规划
    ↓
[阶段5] 逐页生成
    ↓
[阶段6] 质量校审
    ↓
output.pptx (可编辑)
```

## 目录结构

```
ppt-report-agent/
├── SKILL.md                # Skill核心指导文档
├── README.md               # 本文件
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

## 配置说明

编辑 `config.json` 可以调整：

- **LLM模型**: 默认使用 `gpt-4.1-mini`
- **温度参数**: 控制生成内容的创造性
- **页数限制**: 默认20页
- **质量阈值**: 最低置信度要求

## 使用示例

### Python API

```python
from ppt_report_agent.scripts.orchestrator import PPTAgentOrchestrator

agent = PPTAgentOrchestrator()

output_path, review = agent.run(
    input_files=["Q4总结.docx", "数据报表.pdf"],
    template_path="templates/user_templates/business_pro.pptx"
)

print(f"生成的PPT: {output_path}")
print(f"质量评分: {review['overall_score']}/100")
```

### 命令行

```bash
python scripts/orchestrator.py \
  --input Q4总结.docx 数据报表.pdf \
  --template templates/user_templates/business_pro.pptx \
  --output my_presentation.pptx
```

## 质量保证

生成的PPT会从以下五个维度进行评估：

1. **内容准确性**: 数据来源可追溯
2. **焦点精准性**: 每页一个核心信息
3. **逻辑连贯性**: 叙事流畅
4. **风格一致性**: 符合模板设计语言
5. **质量标准**: 格式规范

## 技术栈

- **python-pptx**: PPT创建和模板分析
- **python-docx**: Word文档解析
- **PyPDF2**: PDF文档解析
- **openai**: LLM交互
- **Pillow**: 图片处理

## 许可证

MIT License

## 支持

如有问题，请查阅 `SKILL.md` 或 `references/` 目录下的文档。
