# AI Agent 项目追踪器

一个追踪 GitHub 上 AI Agent 领域最新和最热门开源项目的页面。

## 功能特点

- 🔥 **热门项目**: 按 Stars 数量排序，展示最受欢迎的 AI Agent 项目
- 📈 **活跃上升**: 自动计算并展示项目活跃度趋势，识别增长中的项目
- ✨ **最新创建**: 展示最近创建的 AI Agent 相关项目
- 🔄 **每日自动更新**: 通过 GitHub Actions 每天自动抓取最新数据

## 技术架构

- **前端**: 纯 HTML/CSS/JS，无需构建
- **数据**: JSON 文件存储项目数据
- **自动化**: Python 脚本 + GitHub Actions 每日定时抓取
- **部署**: GitHub Pages

## 本地运行

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/ai-agent-tracker.git
cd ai-agent-tracker

# 直接打开 index.html 或使用本地服务器
python -m http.server 8000
# 然后访问 http://localhost:8000
```

## 数据抓取

```bash
# 安装依赖
pip install requests

# 运行抓取脚本
python src/fetch_projects.py
```

需要设置 `GITHUB_TOKEN` 环境变量以提高 API 请求限制：

```bash
export GITHUB_TOKEN="your_github_token_here"
```

## GitHub Actions

工作流每天早上 8:00 UTC 自动运行，流程如下：

1. 克隆仓库
2. 运行 Python 脚本抓取最新数据
3. 提交并推送更改
4. 自动部署到 GitHub Pages

手动触发：在 GitHub 仓库的 Actions 页面点击 "Run workflow"

## 自定义

### 修改关键词

编辑 `src/fetch_projects.py` 中的 `AI_AGENT_KEYWORDS` 列表：

```python
AI_AGENT_KEYWORDS = [
    "agent",
    "autonomous-agent",
    # 添加更多关键词...
]
```

### 修改样式

直接编辑 `index.html` 中的 CSS 样式。

## 项目结构

```
ai-agent-tracker/
├── index.html              # 主页面
├── data/
│   └── projects.json       # 项目数据
├── src/
│   └── fetch_projects.py   # 数据抓取脚本
└── .github/
    └── workflows/
        └── daily-update.yml # 每日更新工作流
```

## 部署

1. Fork 此仓库
2. 在 Settings → Pages 中选择 Source: GitHub Actions
3. 工作流会自动部署

## License

MIT
