<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/Zero_Dependencies-✓-success.svg" alt="Zero Dependencies">
  <img src="https://img.shields.io/badge/Platforms-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg" alt="Cross Platform">
</p>

<p align="center">
  <a href="#-项目介绍-简体中文">简体中文</a> •
  <a href="#-專案介紹-繁體中文">繁體中文</a> •
  <a href="#-project-introduction-english">English</a>
</p>

---

# 🦞 InsightHarvest-CLI

> 轻量级终端AI多源情报采集与综合分析引擎
> Lightweight Terminal AI Multi-Source Intelligence Harvesting & Synthesis Engine

---

## 🎉 项目介绍（简体中文）

### 💡 项目定位

**InsightHarvest-CLI** 是一款零外部依赖的终端AI情报采集工具，能够从 Hacker News、Reddit、GitHub Trending、Product Hunt 以及任意 RSS/Atom 订阅源中自动采集数据，通过智能去重、关键词提取、趋势分析等引擎进行深度处理，并可借助 LLM（大语言模型）生成高质量的综合分析报告。

### 🔥 核心痛点

- **信息碎片化**：技术情报散落在十几个平台，手动逐一浏览效率极低
- **噪音过多**：重复内容、低质量帖子充斥各平台，难以快速定位高价值信息
- **缺乏综合视角**：单一平台的数据无法反映全局趋势，跨平台对比分析成本高
- **工具依赖重**：现有方案普遍依赖 Docker、Node.js 等重型运行时，部署门槛高

### ✨ 自研差异化亮点

- **🚫 零外部依赖**：纯 Python 标准库实现，`pip install` 都不需要，下载即用
- **🌐 5大内置数据源**：HN、Reddit、GitHub Trending、Product Hunt、通用 RSS
- **🧠 LLM 驱动分析**：支持 OpenAI / Claude / GLM（智谱）等多种后端
- **📊 TUI 交互式仪表盘**：curses 实现的终端原生界面，5个视图切换
- **📝 三格式导出**：Markdown / JSON / HTML（含精美 CSS 样式）
- **⚡ 智能去重引擎**：精确匹配 + 模糊相似度双重去重
- **🏷️ TF-IDF 关键词提取**：中英文双语停用词，自动提取核心关键词
- **💾 本地缓存系统**：文件级 MD5 缓存 + TTL 过期机制

---

## ✨ 核心特性（简体中文）

| 特性 | 描述 |
|------|------|
| 🔍 **多源采集** | Hacker News、Reddit、GitHub Trending、Product Hunt、RSS/Atom |
| 🧠 **LLM 分析** | 一键调用 GPT / Claude / GLM 生成综合分析摘要 |
| 📊 **TUI 仪表盘** | 终端原生交互界面，列表/统计/关键词/详情/帮助 5 大视图 |
| 🔄 **智能去重** | 精确标题匹配 + 模糊相似度双重过滤，自动合并重复项 |
| 🏷️ **关键词提取** | TF-IDF 算法，中英文双语停用词支持 |
| 📈 **趋势分析** | 来源分布、时间分布、热度排名等多维统计 |
| 📝 **多格式导出** | Markdown / JSON / HTML（含完整 CSS 样式表） |
| 💾 **本地缓存** | 文件级 MD5 键缓存 + TTL 自动过期 |
| ⚙️ **灵活配置** | YAML/JSON 配置文件 + 环境变量 + 命令行参数三级覆盖 |
| 🚫 **零依赖** | 纯 Python 标准库，Python 3.8+ 即可运行 |

---

## 🚀 快速开始（简体中文）

### 📋 环境要求

- **Python 3.8+**（无需安装任何第三方库）

### 📥 安装

```bash
# 克隆仓库
git clone https://github.com/gitstq/InsightHarvest-CLI.git
cd InsightHarvest-CLI

# 无需 pip install！直接运行
python insight_harvest.py --help
```

### ⚡ 一键运行

```bash
# 采集 Hacker News 最近7天的热门内容
python insight_harvest.py collect --sources hackernews --days 7

# 多源采集 + 关键词过滤 + Markdown导出
python insight_harvest.py collect --sources hackernews,reddit,github_trending --keywords "AI,LLM,GPT" --export markdown

# 启动 TUI 交互式仪表盘
python insight_harvest.py dashboard --sources hackernews,reddit

# LLM 驱动的深度分析
python insight_harvest.py analyze --sources all --days 30 --llm --export json
```

---

## 📖 详细使用指南（简体中文）

### 🔧 配置 LLM API

创建配置文件 `~/.insight_harvest/config.json`：

```json
{
  "llm": {
    "provider": "openai",
    "api_key": "your-api-key-here",
    "model": "gpt-4o-mini",
    "base_url": "https://api.openai.com/v1"
  }
}
```

**支持的 LLM 提供商**：

| 提供商 | provider 值 | base_url 示例 |
|--------|------------|---------------|
| OpenAI | `openai` | `https://api.openai.com/v1` |
| Claude | `claude` | `https://api.anthropic.com` |
| 智谱 GLM | `glm` | `https://open.bigmodel.cn/api/paas/v4` |
| 自定义 | `custom` | 任意 OpenAI 兼容端点 |

### 📊 采集命令详解

```bash
# 基础采集
python insight_harvest.py collect --sources <数据源> [选项]

# 数据源选项：hackernews, reddit, github_trending, producthunt, rss, all
# --days N        采集最近N天的数据（默认7天）
# --keywords K1,K2  关键词过滤
# --language lang  GitHub Trending 语言过滤（如 python, javascript）
# --limit N       每个源最多采集N条（默认50）
# --export fmt    导出格式：markdown, json, html
# --output path   输出文件路径
# --llm           启用LLM分析
# --no-cache      禁用缓存
```

### 🖥️ TUI 仪表盘操作

```bash
python insight_harvest.py dashboard --sources hackernews,reddit,github_trending
```

| 按键 | 功能 |
|------|------|
| `Tab` / `Shift+Tab` | 切换视图 |
| `↑` / `↓` | 上下滚动 |
| `Enter` | 查看详情 |
| `/` | 搜索过滤 |
| `r` | 刷新数据 |
| `e` | 导出当前数据 |
| `q` / `Esc` | 退出 |

### 📡 自定义 RSS 源

```json
{
  "sources": {
    "rss": {
      "feeds": [
        "https://feeds.arstechnica.com/arstechnica/index",
        "https://www.techmeme.com/feed.xml"
      ]
    }
  }
}
```

---

## 💡 设计思路与迭代规划（简体中文）

### 🎯 设计理念

InsightHarvest-CLI 遵循 **"极简主义 + 功能完备"** 的设计哲学：

1. **零依赖原则**：不引入任何第三方库，降低部署门槛，提升可移植性
2. **模块化架构**：采集器、分析器、导出器、UI 各自独立，便于扩展
3. **本地优先**：所有数据处理在本地完成，保护用户隐私
4. **LLM 可选**：核心采集和分析功能不依赖 LLM，LLM 作为增强层

### 🗺️ 后续迭代计划

- [ ] 🔮 支持 Twitter/X、YouTube、知乎、微博等更多平台
- [ ] 📧 邮件/Telegram/Webhook 定时推送
- [ ] 📉 历史趋势对比与可视化图表
- [ ] 🔄 增量采集与变更通知
- [ ] 🌍 多语言界面（i18n）
- [ ] 🧪 插件系统（自定义采集器/分析器）

---

## 📦 打包与部署指南（简体中文）

本项目为纯 Python 脚本工具，无需打包。直接部署：

```bash
# 方式一：直接克隆运行
git clone https://github.com/gitstq/InsightHarvest-CLI.git
cd InsightHarvest-CLI
python insight_harvest.py collect --sources hackernews

# 方式二：添加别名到 shell 配置
echo 'alias insight-harvest="python /path/to/InsightHarvest-CLI/insight_harvest.py"' >> ~/.bashrc
source ~/.bashrc
insight-harvest collect --sources all
```

**兼容环境**：Windows 10+、macOS 10.15+、Ubuntu 18.04+ / CentOS 7+ 等主流操作系统

---

## 🤝 贡献指南（简体中文）

欢迎贡献代码！请遵循以下规范：

1. **Fork** 本仓库
2. 创建特性分支：`git checkout -b feat/your-feature`
3. 提交代码：`git commit -m "feat: 添加某功能"`
4. 推送分支：`git push origin feat/your-feature`
5. 提交 **Pull Request**

**提交规范**（Angular Convention）：
- `feat:` 新增功能
- `fix:` 修复问题
- `docs:` 文档更新
- `refactor:` 代码重构
- `perf:` 性能优化
- `test:` 测试相关

---

## 📄 开源协议

本项目基于 [MIT License](LICENSE) 开源，可自由使用、修改和分发。

---

---

# 🦞 InsightHarvest-CLI

> 輕量級終端AI多源情報採集與綜合分析引擎
> Lightweight Terminal AI Multi-Source Intelligence Harvesting & Synthesis Engine

---

## 🎉 專案介紹（繁體中文）

### 💡 專案定位

**InsightHarvest-CLI** 是一款零外部依賴的終端AI情報採集工具，能夠從 Hacker News、Reddit、GitHub Trending、Product Hunt 以及任意 RSS/Atom 訂閱源中自動採集數據，透過智慧去重、關鍵詞提取、趨勢分析等引擎進行深度處理，並可借助 LLM（大語言模型）生成高品質的綜合分析報告。

### 🔥 核心痛點

- **資訊碎片化**：技術情報散落在十幾個平台，手動逐一瀏覽效率極低
- **噪音過多**：重複內容、低品質帖子充斥各平台，難以快速定位高價值資訊
- **缺乏綜合視角**：單一平台的數據無法反映全局趨勢，跨平台對比分析成本高
- **工具依賴重**：現有方案普遍依賴 Docker、Node.js 等重型運行時，部署門檻高

### ✨ 自研差異化亮點

- **🚫 零外部依賴**：純 Python 標準庫實現，`pip install` 都不需要，下載即用
- **🌐 5大內建數據源**：HN、Reddit、GitHub Trending、Product Hunt、通用 RSS
- **🧠 LLM 驅動分析**：支援 OpenAI / Claude / GLM（智譜）等多種後端
- **📊 TUI 互動式儀表盤**：curses 實現的終端原生介面，5個視圖切換
- **📝 三格式匯出**：Markdown / JSON / HTML（含精美 CSS 樣式）
- **⚡ 智慧去重引擎**：精確匹配 + 模糊相似度雙重去重
- **🏷️ TF-IDF 關鍵詞提取**：中英文雙語停用詞，自動提取核心關鍵詞
- **💾 本地快取系統**：檔案級 MD5 快取 + TTL 過期機制

---

## ✨ 核心特性（繁體中文）

| 特性 | 描述 |
|------|------|
| 🔍 **多源採集** | Hacker News、Reddit、GitHub Trending、Product Hunt、RSS/Atom |
| 🧠 **LLM 分析** | 一鍵呼叫 GPT / Claude / GLM 生成綜合分析摘要 |
| 📊 **TUI 儀表盤** | 終端原生互動介面，列表/統計/關鍵詞/詳情/幫助 5 大視圖 |
| 🔄 **智慧去重** | 精確標題匹配 + 模糊相似度雙重過濾，自動合併重複項 |
| 🏷️ **關鍵詞提取** | TF-IDF 演算法，中英文雙語停用詞支援 |
| 📈 **趨勢分析** | 來源分佈、時間分佈、熱度排名等多維統計 |
| 📝 **多格式匯出** | Markdown / JSON / HTML（含完整 CSS 樣式表） |
| 💾 **本地快取** | 檔案級 MD5 鍵快取 + TTL 自動過期 |
| ⚙️ **靈活配置** | YAML/JSON 配置檔 + 環境變數 + 命令列參數三級覆蓋 |
| 🚫 **零依賴** | 純 Python 標準庫，Python 3.8+ 即可運行 |

---

## 🚀 快速開始（繁體中文）

### 📋 環境要求

- **Python 3.8+**（無需安裝任何第三方庫）

### 📥 安裝

```bash
# 克隆倉庫
git clone https://github.com/gitstq/InsightHarvest-CLI.git
cd InsightHarvest-CLI

# 無需 pip install！直接運行
python insight_harvest.py --help
```

### ⚡ 一鍵運行

```bash
# 採集 Hacker News 最近7天的熱門內容
python insight_harvest.py collect --sources hackernews --days 7

# 多源採集 + 關鍵詞過濾 + Markdown匯出
python insight_harvest.py collect --sources hackernews,reddit,github_trending --keywords "AI,LLM,GPT" --export markdown

# 啟動 TUI 互動式儀表盤
python insight_harvest.py dashboard --sources hackernews,reddit

# LLM 驅動的深度分析
python insight_harvest.py analyze --sources all --days 30 --llm --export json
```

---

## 📖 詳細使用指南（繁體中文）

### 🔧 配置 LLM API

建立配置檔 `~/.insight_harvest/config.json`：

```json
{
  "llm": {
    "provider": "openai",
    "api_key": "your-api-key-here",
    "model": "gpt-4o-mini",
    "base_url": "https://api.openai.com/v1"
  }
}
```

**支援的 LLM 提供商**：

| 提供商 | provider 值 | base_url 範例 |
|--------|------------|---------------|
| OpenAI | `openai` | `https://api.openai.com/v1` |
| Claude | `claude` | `https://api.anthropic.com` |
| 智譜 GLM | `glm` | `https://open.bigmodel.cn/api/paas/v4` |
| 自訂 | `custom` | 任意 OpenAI 相容端點 |

### 📊 採集命令詳解

```bash
# 基礎採集
python insight_harvest.py collect --sources <數據源> [選項]

# 數據源選項：hackernews, reddit, github_trending, producthunt, rss, all
# --days N        採集最近N天的數據（預設7天）
# --keywords K1,K2  關鍵詞過濾
# --language lang  GitHub Trending 語言過濾（如 python, javascript）
# --limit N       每個源最多採集N條（預設50）
# --export fmt    匯出格式：markdown, json, html
# --output path   輸出檔案路徑
# --llm           啟用LLM分析
# --no-cache      停用快取
```

### 🖥️ TUI 儀表盤操作

```bash
python insight_harvest.py dashboard --sources hackernews,reddit,github_trending
```

| 按鍵 | 功能 |
|------|------|
| `Tab` / `Shift+Tab` | 切換視圖 |
| `↑` / `↓` | 上下捲動 |
| `Enter` | 查看詳情 |
| `/` | 搜尋過濾 |
| `r` | 重新整理數據 |
| `e` | 匯出當前數據 |
| `q` / `Esc` | 退出 |

---

## 💡 設計思路與迭代規劃（繁體中文）

### 🎯 設計理念

InsightHarvest-CLI 遵循 **「極簡主義 + 功能完備」** 的設計哲學：

1. **零依賴原則**：不引入任何第三方庫，降低部署門檻，提升可移植性
2. **模組化架構**：採集器、分析器、匯出器、UI 各自獨立，便於擴展
3. **本地優先**：所有數據處理在本地完成，保護用戶隱私
4. **LLM 可選**：核心採集和分析功能不依賴 LLM，LLM 作為增強層

### 🗺️ 後續迭代計畫

- [ ] 🔮 支援 Twitter/X、YouTube、知乎、微博等更多平台
- [ ] 📧 郵件/Telegram/Webhook 定時推送
- [ ] 📉 歷史趨勢對比與視覺化圖表
- [ ] 🔄 增量採集與變更通知
- [ ] 🌍 多語言介面（i18n）
- [ ] 🧪 外掛系統（自訂採集器/分析器）

---

## 📦 打包與部署指南（繁體中文）

本專案為純 Python 腳本工具，無需打包。直接部署：

```bash
# 方式一：直接克隆運行
git clone https://github.com/gitstq/InsightHarvest-CLI.git
cd InsightHarvest-CLI
python insight_harvest.py collect --sources hackernews

# 方式二：新增別名到 shell 配置
echo 'alias insight-harvest="python /path/to/InsightHarvest-CLI/insight_harvest.py"' >> ~/.bashrc
source ~/.bashrc
insight-harvest collect --sources all
```

**相容環境**：Windows 10+、macOS 10.15+、Ubuntu 18.04+ / CentOS 7+ 等主流作業系統

---

## 🤝 貢獻指南（繁體中文）

歡迎貢獻程式碼！請遵循以下規範：

1. **Fork** 本倉庫
2. 建立特性分支：`git checkout -b feat/your-feature`
3. 提交程式碼：`git commit -m "feat: 新增某功能"`
4. 推送分支：`git push origin feat/your-feature`
5. 提交 **Pull Request**

**提交規範**（Angular Convention）：
- `feat:` 新增功能
- `fix:` 修復問題
- `docs:` 文件更新
- `refactor:` 程式碼重構
- `perf:` 效能優化
- `test:` 測試相關

---

## 📄 開源協議

本專案基於 [MIT License](LICENSE) 開源，可自由使用、修改和分發。

---

---

# 🦞 InsightHarvest-CLI

> Lightweight Terminal AI Multi-Source Intelligence Harvesting & Synthesis Engine

---

## 🎉 Project Introduction

### 💡 What is InsightHarvest-CLI?

**InsightHarvest-CLI** is a zero-dependency terminal AI intelligence harvesting tool that automatically collects data from **Hacker News, Reddit, GitHub Trending, Product Hunt**, and any **RSS/Atom** feed. It processes data through smart deduplication, keyword extraction, and trend analysis engines, and can leverage LLMs (Large Language Models) to generate high-quality synthesis reports.

### 🔥 Core Problems Solved

- **Information Fragmentation**: Tech intelligence is scattered across dozens of platforms — manually browsing each one is incredibly inefficient
- **Signal-to-Noise Ratio**: Duplicate content and low-quality posts flood every platform, making it hard to find high-value insights
- **Lack of Holistic View**: Single-platform data fails to reflect global trends; cross-platform comparative analysis is costly
- **Heavy Tool Dependencies**: Existing solutions rely on Docker, Node.js, or other heavy runtimes, raising deployment barriers

### ✨ Differentiation Highlights

- **🚫 Zero External Dependencies**: Pure Python standard library — no `pip install` needed, download and run
- **🌐 5 Built-in Data Sources**: HN, Reddit, GitHub Trending, Product Hunt, Generic RSS
- **🧠 LLM-Powered Analysis**: Supports OpenAI / Claude / GLM (Zhipu) and more
- **📊 TUI Interactive Dashboard**: Native terminal UI with curses, 5 switchable views
- **📝 Triple Format Export**: Markdown / JSON / HTML (with polished CSS)
- **⚡ Smart Deduplication Engine**: Exact match + fuzzy similarity dual-pass filtering
- **🏷️ TF-IDF Keyword Extraction**: Bilingual (English/Chinese) stopword support
- **💾 Local Cache System**: File-level MD5-keyed cache with TTL expiration

---

## ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🔍 **Multi-Source Harvesting** | Hacker News, Reddit, GitHub Trending, Product Hunt, RSS/Atom |
| 🧠 **LLM Analysis** | One-click GPT / Claude / GLM synthesis report generation |
| 📊 **TUI Dashboard** | Native terminal UI — List / Stats / Keywords / Detail / Help views |
| 🔄 **Smart Deduplication** | Exact title match + fuzzy similarity dual-pass filtering |
| 🏷️ **Keyword Extraction** | TF-IDF algorithm with bilingual stopword support |
| 📈 **Trend Analysis** | Source distribution, time distribution, popularity rankings |
| 📝 **Multi-Format Export** | Markdown / JSON / HTML (with full CSS stylesheet) |
| 💾 **Local Cache** | File-level MD5-keyed cache with TTL auto-expiration |
| ⚙️ **Flexible Configuration** | YAML/JSON config + environment variables + CLI args (3-level override) |
| 🚫 **Zero Dependencies** | Pure Python standard library, Python 3.8+ ready |

---

## 🚀 Quick Start

### 📋 Prerequisites

- **Python 3.8+** (no third-party libraries required)

### 📥 Installation

```bash
# Clone the repository
git clone https://github.com/gitstq/InsightHarvest-CLI.git
cd InsightHarvest-CLI

# No pip install needed! Just run
python insight_harvest.py --help
```

### ⚡ One-Line Commands

```bash
# Harvest Hacker News trending from the last 7 days
python insight_harvest.py collect --sources hackernews --days 7

# Multi-source harvest + keyword filter + Markdown export
python insight_harvest.py collect --sources hackernews,reddit,github_trending --keywords "AI,LLM,GPT" --export markdown

# Launch the TUI interactive dashboard
python insight_harvest.py dashboard --sources hackernews,reddit

# LLM-powered deep analysis
python insight_harvest.py analyze --sources all --days 30 --llm --export json
```

---

## 📖 Detailed Usage Guide

### 🔧 LLM API Configuration

Create a config file at `~/.insight_harvest/config.json`:

```json
{
  "llm": {
    "provider": "openai",
    "api_key": "your-api-key-here",
    "model": "gpt-4o-mini",
    "base_url": "https://api.openai.com/v1"
  }
}
```

**Supported LLM Providers**:

| Provider | `provider` value | `base_url` example |
|----------|-------------------|---------------------|
| OpenAI | `openai` | `https://api.openai.com/v1` |
| Claude | `claude` | `https://api.anthropic.com` |
| Zhipu GLM | `glm` | `https://open.bigmodel.cn/api/paas/v4` |
| Custom | `custom` | Any OpenAI-compatible endpoint |

### 📊 Collect Command Reference

```bash
# Basic collection
python insight_harvest.py collect --sources <source> [options]

# Source options: hackernews, reddit, github_trending, producthunt, rss, all
# --days N          Collect data from the last N days (default: 7)
# --keywords K1,K2  Keyword filtering
# --language lang   GitHub Trending language filter (e.g., python, javascript)
# --limit N         Max items per source (default: 50)
# --export fmt      Export format: markdown, json, html
# --output path     Output file path
# --llm             Enable LLM analysis
# --no-cache        Disable caching
```

### 🖥️ TUI Dashboard Controls

```bash
python insight_harvest.py dashboard --sources hackernews,reddit,github_trending
```

| Key | Action |
|-----|--------|
| `Tab` / `Shift+Tab` | Switch views |
| `↑` / `↓` | Scroll up/down |
| `Enter` | View details |
| `/` | Search/filter |
| `r` | Refresh data |
| `e` | Export current data |
| `q` / `Esc` | Quit |

### 📡 Custom RSS Feeds

```json
{
  "sources": {
    "rss": {
      "feeds": [
        "https://feeds.arstechnica.com/arstechnica/index",
        "https://www.techmeme.com/feed.xml"
      ]
    }
  }
}
```

---

## 💡 Design Philosophy & Roadmap

### 🎯 Design Principles

InsightHarvest-CLI follows the philosophy of **"Minimalism + Completeness"**:

1. **Zero Dependency Principle**: No third-party libraries — lower deployment barrier, higher portability
2. **Modular Architecture**: Harvesters, analyzers, exporters, and UI are fully decoupled for easy extension
3. **Local-First**: All data processing happens locally, protecting user privacy
4. **LLM Optional**: Core harvesting and analysis work without LLM; LLM serves as an enhancement layer

### 🗺️ Roadmap

- [ ] 🔮 Support for Twitter/X, YouTube, Zhihu, Weibo, and more platforms
- [ ] 📧 Email / Telegram / Webhook scheduled push notifications
- [ ] 📉 Historical trend comparison and visualization charts
- [ ] 🔄 Incremental harvesting with change notifications
- [ ] 🌍 Multi-language UI (i18n)
- [ ] 🧪 Plugin system (custom harvesters/analyzers)

---

## 📦 Deployment Guide

This is a pure Python script tool — no packaging required. Deploy directly:

```bash
# Option 1: Clone and run
git clone https://github.com/gitstq/InsightHarvest-CLI.git
cd InsightHarvest-CLI
python insight_harvest.py collect --sources hackernews

# Option 2: Add shell alias
echo 'alias insight-harvest="python /path/to/InsightHarvest-CLI/insight_harvest.py"' >> ~/.bashrc
source ~/.bashrc
insight-harvest collect --sources all
```

**Compatible Environments**: Windows 10+, macOS 10.15+, Ubuntu 18.04+ / CentOS 7+ and other major operating systems

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork** this repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Commit your changes: `git commit -m "feat: add some feature"`
4. Push to the branch: `git push origin feat/your-feature`
5. Submit a **Pull Request**

**Commit Convention** (Angular):
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation update
- `refactor:` Code refactoring
- `perf:` Performance optimization
- `test:` Test-related changes

---

## 📄 License

This project is licensed under the [MIT License](LICENSE). Free to use, modify, and distribute.

---

<p align="center">
  Made with 🦞 by <a href="https://github.com/gitstq">LobsterDev</a>
</p>
