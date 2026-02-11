# 安装指南

## 快速安装

### 步骤1：拷贝Skill到Claude Code

```bash
# 拷贝整个文件夹到Claude Code的skills目录
cp -r ppt-report-agent ~/.config/claude-code/skills/
```

或者对于Open Code：

```bash
# 拷贝到Open Code的skills目录
cp -r ppt-report-agent /path/to/opencode/skills/
```

### 步骤2：安装依赖

```bash
cd ~/.config/claude-code/skills/ppt-report-agent
pip install -r requirements.txt
```

### 步骤3：配置环境变量

确保已设置OpenAI API密钥：

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 步骤4：准备PPT模板

将您的PPT模板文件放入 `templates/user_templates/` 目录：

```bash
cp /path/to/your/template.pptx templates/user_templates/
```

**推荐模板来源**: [优品PPT](https://www.ypppt.com)

### 步骤5：测试Skill

```bash
python test_skill.py
```

如果看到所有测试通过，说明安装成功！

## 使用方法

在Claude Code CLI中输入：

```
请学习Q4总结.docx资料，然后参考business.pptx的风格，帮我生成一个《星链洞察报告》
```

AI助手会自动识别并调用此Skill。

## 目录结构

```
ppt-report-agent/
├── SKILL.md           # AI助手核心指令（必需）
├── README.md          # 项目说明
├── INSTALL.md         # 本文件
├── requirements.txt   # Python依赖
├── config.json        # 配置文件
├── scripts/           # 核心代码
├── prompts/           # LLM提示词
├── templates/         # PPT模板目录
└── test_skill.py      # 测试脚本
```

## 常见问题

### Q: 如何验证Skill是否安装成功？

运行测试脚本：
```bash
python test_skill.py
```

### Q: 如何更新Skill？

从GitHub拉取最新版本：
```bash
cd ~/.config/claude-code/skills/ppt-report-agent
git pull
pip install -r requirements.txt --upgrade
```

### Q: 如何卸载Skill？

删除Skill目录：
```bash
rm -rf ~/.config/claude-code/skills/ppt-report-agent
```

## 支持

- GitHub: https://github.com/Carlehyy/ppt
- 文档: 查看SKILL.md和README.md
