# PPT Skills Collection

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**一个专注于PPT生成和处理的Skills集合**

</div>

---

## 📚 Skills列表

### 1. [ppt-generate](./ppt-generate/) - PPT生成Skill

智能的PPT生成Skill，能够从原始素材文档和PPT模板自动生成专业的、可编辑的PowerPoint演示文稿。

**核心功能**：
- 📄 多格式文档解析（Word、PDF、PPT）
- 🎨 模板风格智能应用
- 🤖 AI驱动的大纲规划和内容生成
- ✅ 五维度质量评估
- 🔧 生成可编辑的PPTX文件

**适用场景**：
- 工作汇报PPT生成
- 项目进展报告制作
- 多文档内容整合
- 模板风格迁移

**快速开始**：
```bash
cd ~/.config/claude-code/skills/
git clone https://github.com/Carlehyy/ppt.git
cp -r ppt/ppt-generate ~/.config/claude-code/skills/
cd ~/.config/claude-code/skills/ppt-generate
pip install -r requirements.txt
```

**使用示例**：
```
请学习Q4总结.docx资料，然后参考business.pptx的风格，帮我生成一个《星链洞察报告》
```

详细文档请查看：[ppt-generate/README.md](./ppt-generate/README.md)

---

## 🚀 快速安装

### 方式1：克隆整个仓库

```bash
cd ~/.config/claude-code/skills/
git clone https://github.com/Carlehyy/ppt.git
```

然后选择需要的Skill：
```bash
# 使用ppt-generate
cp -r ppt/ppt-generate ~/.config/claude-code/skills/
cd ~/.config/claude-code/skills/ppt-generate
pip install -r requirements.txt
```

### 方式2：直接克隆单个Skill

```bash
cd ~/.config/claude-code/skills/
git clone --depth 1 --filter=blob:none --sparse https://github.com/Carlehyy/ppt.git
cd ppt
git sparse-checkout set ppt-generate
cp -r ppt-generate ../
cd ..
rm -rf ppt
cd ppt-generate
pip install -r requirements.txt
```

## 📖 使用说明

### 在Claude Code中使用

1. **安装Skill**（见上方快速安装）
2. **准备PPT模板**：将模板放入对应Skill的`templates/user_templates/`目录
3. **在CLI中使用**：直接输入自然语言指令

```bash
claude
> 请帮我生成一个工作汇报PPT
```

### 在Open Code中使用

Open Code的使用方式与Claude Code相同，只需将Skill安装到Open Code的skills目录即可。

## 🛠️ 环境要求

- Python 3.8+
- Claude Code 或 Open Code
- 已设置 `OPENAI_API_KEY` 环境变量

## 📁 仓库结构

```
ppt/
├── README.md              # 本文件 - 项目总览
│
└── ppt-generate/          # PPT生成Skill
    ├── SKILL.md           # Skill核心指令集
    ├── README.md          # Skill详细说明
    ├── INSTALL.md         # 安装指南
    ├── scripts/           # 核心代码
    ├── prompts/           # LLM提示词
    └── ...
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

如果您有新的PPT相关Skill想要贡献，请：
1. Fork本仓库
2. 在根目录创建新的Skill文件夹（如`ppt-translate`）
3. 确保包含标准的SKILL.md文件
4. 提交Pull Request

## 📄 许可证

[MIT License](LICENSE)

## 🙏 致谢

- 感谢[优品PPT](https://www.ypppt.com)提供高质量模板资源
- 基于[python-pptx](https://python-pptx.readthedocs.io/)构建

## 📞 支持

- GitHub Issues: https://github.com/Carlehyy/ppt/issues
- 文档: 查看各Skill目录下的README.md

---

<div align="center">

**如果这个项目对您有帮助，请给个⭐️Star支持一下！**

Made with ❤️ by Manus AI

</div>
