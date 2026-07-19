# PPT Auto Studio

一个为 PPT 小白设计的 Codex Skill：把 Word、PDF、Excel、图片、实验结果、会议笔记或旧 PPT 直接交给它，由系统完成内容梳理、故事线、版式匹配、视觉补充、逐页渲染和质量检查，交付可编辑的 `.pptx`。

用户不需要会选模板、配色、字体、排版或图表。

## 它解决什么问题

- **不会组织**：先识别受众、目标和证据，再生成结论驱动的故事线。
- **不会设计**：自动从内置版式与场景配方中选择，不把模板库丢给用户筛选。
- **不会动手**：替换文字、图片和图表，生成可编辑成品。
- **怕翻车**：渲染每一页，检查溢出、遮挡、字体、裁切和整体节奏后再交付。

## 内置资源

- 20 页原创 16:9 黄绿高级感版式；
- 3 个可替换的原创封面视觉；
- 工作汇报、答辩、项目提案、教学/科研分享、管理层简报等场景配方；
- 模板库批量目录工具，可检索页数、比例、图片、图表、动画、字体和主题色；
- 可复现资源包的 `@oai/artifact-tool` 构建脚本；
- 逐页设计与 QA 规则。

内置 PPT 位于 [`assets/premium-green-layout-kit.pptx`](assets/premium-green-layout-kit.pptx)，文字、原生图表和简单图形均可编辑。

## 安装

将仓库克隆或复制到 Codex skills 目录：

```bash
git clone https://github.com/zhoy0409-debug/build-premium-pptx.git
cp -R build-premium-pptx ~/.codex/skills/build-premium-pptx
```

Windows PowerShell：

```powershell
git clone https://github.com/zhoy0409-debug/build-premium-pptx.git
Copy-Item -Recurse .\build-premium-pptx "$env:USERPROFILE\.codex\skills\build-premium-pptx"
```

重启 Codex 后调用 `$build-premium-pptx`。

## 最简单的用法

```text
用 $build-premium-pptx 把这个 Word 和 Excel 做成 10 页工作汇报。我不会做 PPT，你直接决定结构、版式和配图。
```

```text
用 $build-premium-pptx 把这些实验结果做成 8 分钟答辩，听众是老师，结论和证据要一眼看懂。
```

```text
Use $build-premium-pptx to turn these notes into a polished editable deck. Choose the story, layouts, and visuals for me.
```

## 对私有模板库的处理

Skill 可以在本地扫描和调用用户有权使用的模板库，但不会把购买的原始模板、内嵌素材或字体重新上传到公共仓库。公共资源包是根据版式原则重新设计的原创资源；私有模板仅作为本地输入使用。

## 目录

```text
SKILL.md                          核心工作流
agents/openai.yaml                Codex 展示与默认提示词
assets/                           原创 PPTX 与封面视觉
references/layout-recipes.json    版式与场景自动选择规则
references/design-and-qa.md       设计、数据与逐页质检规则
scripts/catalog_pptx.py           本地模板库目录工具
scripts/build_premium_resource_kit.mjs  原创资源包构建脚本
```

## 设计原则

一页一个结论；证据优先于装饰；少问用户专业问题；提供一个推荐方向；保留可编辑性；不虚构数据；没有逐页渲染检查就不算完成。
