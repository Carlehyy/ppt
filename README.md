# PPT汇报文档生成器

从多个原始语料文件中提取信息，生成结构化的Markdown汇报文档。

## 分支说明

- **main**: 原始版本的ppt-generate skill
- **document**: 原始语料和模板PPT
- **report-expert**: 优化版本，融合职场沟通模型（PREP、SCQA、STAR、金字塔原理）

## 使用推荐

推荐使用 **report-expert** 分支，该版本：
- ✅ 融合了经典职场沟通模型
- ✅ 代码精简60%（从2000行减少到800行）
- ✅ 流程简化（从6个阶段简化为3个阶段）
- ✅ 生成的汇报文档更符合职场表达习惯

## 快速开始

```bash
# 克隆仓库并切换到report-expert分支
git clone https://github.com/Carlehyy/ppt.git
cd ppt
git checkout report-expert

# 安装依赖
cd ppt-report-md
pip install -r requirements.txt

# 查看详细使用说明
cat SKILL.md
```

## 支持的文档格式

- PDF (.pdf)
- Word (.docx)
- 文本 (.txt)
- Markdown (.md)

## 职场沟通模型

本 skill 融合了经典的职场沟通模型：

- **STAR法则**：适用于向上汇报、工作总结、述职报告
- **SCQA模型**：适用于争取资源、项目提案、故事讲述
- **PREP模型**：适用于简短汇报、快速决策、会议发言
- **金字塔原理**：所有策略的底层逻辑（结论先行、以上统下、归类分组、逻辑递进）

## 许可证

MIT License
