# PPT Report Agent 使用指南

## 完整使用流程

### 第一步：准备工作

#### 1.1 安装依赖

```bash
cd /home/ubuntu/skills/ppt-report-agent
pip install -r requirements.txt
```

#### 1.2 准备高质量PPT模板

将您的`.pptx`模板文件放入 `templates/user_templates/` 目录。

**模板要求**：
- 格式：`.pptx` (PowerPoint 2007+)
- 包含多种版式（标题页、内容页、对比页等）
- 使用母版定义统一的配色和字体
- 版式中包含清晰的占位符

**推荐来源**：
- [优品PPT](https://www.ypppt.com) - 高质量商务模板
- 企业内部模板
- 专业设计师模板

#### 1.3 准备原始素材

支持的格式：
- Word文档 (`.docx`)
- PDF文档 (`.pdf`)
- PowerPoint文件 (`.pptx`)

### 第二步：运行测试

```bash
python test_skill.py
```

确保所有测试项都通过。

### 第三步：生成PPT

#### 方式1：命令行

```bash
python scripts/orchestrator.py \
  --input /path/to/document1.docx /path/to/document2.pdf \
  --template templates/user_templates/your_template.pptx
```

#### 方式2：Python脚本

```python
from ppt_report_agent.scripts.orchestrator import PPTAgentOrchestrator

# 初始化
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

#### 方式3：在Manus中使用

当Manus检测到PPT生成需求时，会自动加载此Skill并调用 `orchestrator.py`。

### 第四步：查看结果

生成的PPT文件默认保存为 `output.pptx`，可以在PowerPoint中打开并编辑。

## 工作流程详解

### 阶段1+2：内容解析 & 模板分析（并行）

**内容解析**做什么：
- 从Word/PDF/PPT中提取文本
- 使用LLM识别语义单元（成果、数据、问题、计划等）
- 标注来源和置信度

**模板分析**做什么：
- 遍历模板的所有版式
- 分析每个版式的占位符结构
- 推断版式的最佳使用场景

### 阶段3：智能咨询

Agent会生成一组问题来明确需求：
- 汇报场景（工作总结、项目进展等）
- 核心意图（展示成果、分析问题等）
- 页数限制
- 语言风格

**注意**：在自动化流程中，会使用默认值。

### 阶段4：大纲规划

LLM作为"PPT设计师"，会：
- 选择叙事策略（成果导向、问题导向等）
- 规划章节结构
- 为每一页选择合适的版式
- 确保"一页一核心"

**用户确认点**：Agent会展示建议大纲，等待确认。

### 阶段5：逐页生成

LLM为每一页生成具体内容：
- 标题（简洁明了）
- 正文（3-5个要点）
- 保留溯源信息
- 适配版式约束

### 阶段6：质量校审

LLM从五个维度评审：
1. 内容准确性
2. 焦点精准性
3. 逻辑连贯性
4. 风格一致性
5. 质量标准

给出评分和改进建议。

## 高级配置

### 调整LLM参数

编辑 `config.json`：

```json
{
  "llm": {
    "model": "gpt-4.1-mini",      // 可选: gpt-4.1-nano, gemini-2.5-flash
    "temperature": 0.7,            // 0.0-1.0, 越高越有创造性
    "max_retries": 3,              // 失败重试次数
    "timeout": 60                  // 超时时间（秒）
  }
}
```

### 调整生成参数

```json
{
  "generation": {
    "default_page_limit": 20,          // 默认页数限制
    "enable_image_extraction": true,   // 是否提取图片
    "enable_table_generation": true,   // 是否生成表格
    "max_bullets_per_slide": 5,        // 每页最多要点数
    "font_size_adjustment": true       // 是否自动调整字号
  }
}
```

### 自定义提示词

编辑 `prompts/` 目录下的文件来调整LLM行为：

- `content_analysis.txt` - 控制内容解析逻辑
- `consultation.txt` - 控制咨询问题生成
- `outline_planning.txt` - 控制大纲规划策略
- `slide_generation.txt` - 控制页面内容生成
- `quality_review.txt` - 控制质量评审标准

## 常见问题

### Q: 生成的PPT页数太多/太少？

A: 在 `config.json` 中调整 `default_page_limit`，或在运行时传入 `user_config`：

```python
agent.run(
    input_files=[...],
    template_path="...",
    user_config={"page_limit": 15}
)
```

### Q: 版式选择不合理？

A: 确保模板的版式有清晰的命名。例如：
- "Title Slide" 用于封面
- "Title and Content" 用于内容页
- "Comparison" 用于对比页

### Q: 内容不准确？

A: 检查原始素材的质量。Agent会标注每个内容的来源和置信度，低置信度的内容需要人工审核。

### Q: 如何提高生成质量？

A: 
1. 提供高质量、结构清晰的原始素材
2. 使用专业的PPT模板
3. 调整LLM的temperature参数（降低可提高准确性）
4. 根据质量评审的建议进行手动调整

## 最佳实践

1. **模板准备**：
   - 使用企业标准模板
   - 确保版式命名规范
   - 包含多种常用版式

2. **素材准备**：
   - 内容结构清晰
   - 数据准确完整
   - 避免过度冗余

3. **后期调整**：
   - 生成后在PowerPoint中微调
   - 检查数据来源
   - 优化视觉效果

4. **迭代优化**：
   - 根据质量评审建议改进
   - 调整提示词模板
   - 积累最佳实践

## 技术支持

如遇问题，请查阅：
- `SKILL.md` - Skill核心文档
- `references/layout_mapping_rules.md` - 版式映射规则
- `README.md` - 项目总览

或联系技术支持。
