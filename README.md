# 每日诗词 · Poem Daily

> 以墨为韵，以诗为友 —— 一个中国古典诗词赏析网站

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)

## 简介

「每日诗词」收录了 **31,065** 首中国古典诗词，涵盖唐诗、宋词、元曲三大经典体裁，并配有由 AI 生成的专业赏析。网站以中国水墨画风为设计理念，每日自动推荐一首诗词，带您领略千年文脉之美。

## 功能特性

- **每日推荐** — 根据日期自动推荐诗词，每天不同，全年不重复
- **诗词赏析** — 为每首诗词生成 60-80 字精炼赏析，引用权威出处
- **分类筛选** — 唐诗 / 宋词 / 元曲，一键切换
- **全文搜索** — 支持按标题、作者搜索
- **随机赏读** — 点击切换随机诗词
- **收藏功能** — 本地存储个人收藏
- **水墨风格** — 中国古典美学设计，优雅排版

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/Haoqin860/poem-daily.git
cd poem-daily

# 启动本地服务器
python3 -m http.server 8080

# 访问 http://localhost:8080
```

> **提示**：直接双击 `index.html` 可能因浏览器安全策略导致数据无法加载，建议使用本地服务器。

## 项目结构

```
poem-daily/
├── index.html                  # 主页面（纯前端，零依赖）
├── generate_appreciations.py   # 赏析生成脚本
├── .env.example                # API 密钥配置模板
├── data/
│   ├── poems.json              # 诗词数据库（31,065 首）
│   └── appreciations.json      # 赏析数据（18,339 条）
└── README.md
```

## 数据来源

诗词数据来自开源项目 [chinese-poetry](https://github.com/chinese-poetry/chinese-poetry)：

| 朝代 | 数量 | 说明 |
|------|------|------|
| 唐诗 | 10,008 首 | 唐代经典诗作 |
| 宋词 | 10,000 首 | 宋代名家词作 |
| 元曲 | 11,057 首 | 元代散曲杂剧 |

## 重新生成赏析

如需重新生成诗词赏析，需配置 API 密钥：

```bash
# 复制配置模板
cp .env.example .env

# 编辑 .env，填入你的 API Key
# OPENAI_API_KEY=sk-xxxxx

# 运行生成脚本
python3 generate_appreciations.py
```

## 技术细节

- **纯前端**：无需后端服务，单个 HTML 文件即可运行
- **零依赖**：不依赖任何第三方框架或库
- **本地存储**：收藏数据保存在浏览器 localStorage
- **并发生成**：赏析脚本支持多线程并发调用 API

## 致谢

- [chinese-poetry](https://github.com/chinese-poetry/chinese-poetry) — 诗词数据来源
- [DeepSeek](https://www.deepseek.com/) — 赏析文本生成 API

## 许可

本项目仅供学习交流使用。诗词原文版权归原作者所有。
