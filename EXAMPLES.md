# PPT Report Agent - 使用示例

本文档提供了在Claude Code CLI中使用此Skill的实际示例。

## 示例1：基础PPT生成

**用户指令**：
```
请帮我从Q4总结.docx生成一份工作汇报PPT
```

**AI助手响应流程**：

1. 识别到"生成PPT"意图，加载`ppt-report-agent` Skill
2. 向用户确认需求
3. 执行生成代码
4. 交付结果

**完整代码示例**：

```python
import sys
import os

# 添加Skill路径
skill_path = "/Users/yourname/.config/claude-code/skills/ppt-report-agent"
sys.path.insert(0, skill_path)

from scripts.orchestrator import PPTAgentOrchestrator

# 初始化
agent = PPTAgentOrchestrator()

# 生成PPT
output_path, review = agent.run(
    input_files=["Q4总结.docx"],
    template_path=os.path.join(skill_path, "templates/user_templates/default.pptx")
)

print(f"生成完成: {output_path}")
print(f"质量评分: {review['overall_score']}/100")
```

## 示例2：指定模板风格

**用户指令**：
```
请学习项目报告.docx资料，参考tech_modern.pptx的风格，帮我生成一个《AI项目进展汇报》
```

**代码示例**：

```python
import sys
import os

skill_path = "/Users/yourname/.config/claude-code/skills/ppt-report-agent"
sys.path.insert(0, skill_path)

from scripts.orchestrator import PPTAgentOrchestrator

agent = PPTAgentOrchestrator()

user_config = {
    "scenario": "项目进展汇报",
    "core_intent": "展示成果",
    "page_limit": 20,
    "presentation_title": "AI项目进展汇报"
}

output_path, review = agent.run(
    input_files=["项目报告.docx"],
    template_path="tech_modern.pptx",  # 用户提供的模板
    user_config=user_config
)

print(f"✓ 生成完成: {output_path}")
```

## 示例3：多文档合并

**用户指令**：
```
请把Q4总结.docx、数据报表.pdf和成果展示.pptx这三个文件合并成一份PPT
```

**代码示例**：

```python
import sys
import os

skill_path = "/Users/yourname/.config/claude-code/skills/ppt-report-agent"
sys.path.insert(0, skill_path)

from scripts.orchestrator import PPTAgentOrchestrator

agent = PPTAgentOrchestrator()

output_path, review = agent.run(
    input_files=[
        "Q4总结.docx",
        "数据报表.pdf",
        "成果展示.pptx"
    ],
    template_path=os.path.join(skill_path, "templates/user_templates/business_pro.pptx")
)

print(f"✓ 已合并生成: {output_path}")
```

## 示例4：自定义配置

**用户指令**：
```
生成一份15页的数据分析PPT，风格要简洁专业
```

**代码示例**：

```python
import sys
import os

skill_path = "/Users/yourname/.config/claude-code/skills/ppt-report-agent"
sys.path.insert(0, skill_path)

from scripts.orchestrator import PPTAgentOrchestrator

agent = PPTAgentOrchestrator()

user_config = {
    "scenario": "数据分析汇报",
    "core_intent": "分析问题",
    "page_limit": 15,
    "language_style": "简洁明快",
    "presentation_title": "数据分析报告"
}

output_path, review = agent.run(
    input_files=["数据分析.docx"],
    template_path=os.path.join(skill_path, "templates/user_templates/minimal_elegant.pptx"),
    user_config=user_config
)

print(f"✓ 生成完成: {output_path}")
print(f"✓ 质量评分: {review['overall_score']}/100")

# 显示改进建议
if review.get('suggestions'):
    print("\n💡 改进建议:")
    for i, suggestion in enumerate(review['suggestions'][:3], 1):
        print(f"{i}. {suggestion}")
```

## 典型对话流程

```
用户: 请学习Q4总结.docx资料，然后参考business.pptx的风格，帮我生成一个《星链洞察报告》

AI: 我将使用ppt-report-agent Skill帮您生成《星链洞察报告》PPT。

    请确认以下信息：
    - 原始素材: Q4总结.docx
    - 参考模板: business.pptx
    - 汇报场景: 工作总结汇报
    - 预计页数: 15-20页
    
    是否开始生成？

用户: 是的，开始吧

AI: [执行生成代码]
    
    ✓ 已成功生成《星链洞察报告》PPT
    
    📊 质量评估:
    - 总体评分: 85/100 (良好)
    - 内容准确性: 18/20
    - 逻辑连贯性: 17/20
    
    📄 生成文件: output.pptx (共18页)
    
    💡 改进建议:
    1. 第5页的增长率数据建议补充来源
    2. 第8页建议拆分为两页
    
    您可以在PowerPoint中打开并进一步编辑此文件。
```

## 常见问题处理

### 问题1：找不到模板文件

**错误信息**：
```
FileNotFoundError: templates/user_templates/business.pptx not found
```

**解决方案**：
```python
# 使用绝对路径
template_path = os.path.join(skill_path, "templates/user_templates/business.pptx")

# 或者检查文件是否存在
if not os.path.exists(template_path):
    print(f"模板文件不存在: {template_path}")
    print("请将模板文件放入 templates/user_templates/ 目录")
```

### 问题2：依赖未安装

**错误信息**：
```
ModuleNotFoundError: No module named 'python-pptx'
```

**解决方案**：
```bash
cd /path/to/ppt-report-agent
pip install -r requirements.txt
```

### 问题3：LLM API错误

**错误信息**：
```
openai.error.AuthenticationError: Invalid API key
```

**解决方案**：
```bash
# 设置环境变量
export OPENAI_API_KEY="your-api-key-here"

# 或在代码中设置
import os
os.environ['OPENAI_API_KEY'] = "your-api-key-here"
```

## 性能优化建议

1. **预先准备模板**：将常用模板放入`templates/user_templates/`目录
2. **批量处理**：一次性提供所有文档，避免多次调用
3. **缓存结果**：保存生成的PPT，避免重复生成
4. **调整页数限制**：根据内容量合理设置`page_limit`

## 进阶用法

### 自定义提示词

编辑`prompts/`目录下的文件来调整LLM行为：

```bash
# 编辑大纲规划策略
vim prompts/outline_planning.txt

# 编辑内容生成规则
vim prompts/slide_generation.txt
```

### 调整配置参数

编辑`config.json`：

```json
{
  "llm": {
    "model": "gpt-4.1-mini",
    "temperature": 0.7
  },
  "generation": {
    "default_page_limit": 20,
    "max_bullets_per_slide": 5
  }
}
```
