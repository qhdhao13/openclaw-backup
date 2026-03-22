# 每日新闻抓取技能

## 功能
从可靠信源自动抓取财经、军事、科技、综合新闻，生成单页HTML简报

## 当前可用信源 (8个)

### 💰 财经
- **CNBC** - 美国主流财经媒体 ✅
- **MarketWatch** - 道琼斯旗下财经新闻 ✅

### 💻 科技
- **TechCrunch** - 科技创业新闻 ✅
- **Ars Technica** - 深度科技报道 ✅
- **Wired** - 科技与文化 ✅

### 🎖️ 军事
- **Defense News** - 防务行业权威 ✅

### 📰 综合
- **NPR News** - 美国公共广播 ✅

### 🔒 需要代理
- Reuters, BBC, Financial Times, SCMP 等

## 使用方法

### 手动运行
```bash
node ~/.openclaw/workspace/skills/news-daily/fetch-news.js
```

### 定时运行（推荐）
添加到 crontab，每天早上7点自动抓取：
```bash
# 编辑 crontab
crontab -e

# 添加这行：
0 7 * * * /usr/local/bin/node /Users/qhdh/.openclaw/workspace/skills/news-daily/fetch-news.js >> /tmp/news-daily.log 2>&1
```

## 输出
- 文件位置: `/Volumes/disk-hfm/每日新闻/`
- 命名格式: `news-YYYY-MM-DD.html`
- 同时生成 `latest.html` 始终指向最新一期

## 文件结构
```
/Volumes/disk-hfm/每日新闻/
├── news-2026-03-22.html    # 每日文件
├── news-2026-03-21.html
├── latest.html             # 始终是最新
└── ...
```

## 使用代理
如需访问更多国际信源，可安装代理客户端：
- Clash Verge (推荐)
- ClashX
- Surge Mac

脚本会自动检测并使用系统代理。

## 检测代理
```bash
node ~/.openclaw/workspace/skills/news-daily/check-proxy.js
```
