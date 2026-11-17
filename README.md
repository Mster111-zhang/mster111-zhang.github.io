# 张艺豪的个人网站

网站通过 [GitHub Pages](https://mster111-zhang.github.io/) 发布。导航、栏目和详情页共用 `build.py` 中的页面模板。

## 更新内容

- 页面内容编辑 `build.py`。Agent 专区新增项目时，在 `MORE_AGENT_PROJECTS` 加一项，填项目地址、标题、标签、简介、可选封面和详情段落。项目地址使用 `projects/agent/项目名/`。首页入口会继续指向整个 Agent 专区。
- 图片放入 `assets/`，样式调整编辑 `style.css`。
- 在仓库根目录运行 `python build.py`，将源文件、生成的 HTML 和新增图片一起提交到 `main`。

## 栏目目录

| 栏目 | 目录 |
| --- | --- |
| 首页 | `index.html` |
| Agent 项目 | `projects/agent/` |
| 科研项目 | `research/` |
| 工程项目 | `projects/` |
| 技术博客 | `blog/` |
| 个人简历 | `resume/` |
| 关于我 | `about/` |
