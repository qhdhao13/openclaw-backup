#!/usr/bin/env node
/**
 * 每日新闻抓取系统 - 国内可访问信源版
 * 从可靠信源获取财经、军事、政治新闻，生成单页HTML
 */

const fs = require('fs');
const path = require('path');

// 配置 - 国内可访问的信源
const CONFIG = {
  outputDir: '/Volumes/disk-hfm/每日新闻',
  maxArticlesPerSource: 5,
  sources: {
    // 财经类 - 已验证可用
    cnbc: {
      name: 'CNBC',
      rss: 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
      category: '财经'
    },
    marketwatch: {
      name: 'MarketWatch',
      rss: 'https://feeds.marketwatch.com/marketwatch/topstories/',
      category: '财经'
    },
    
    // 科技/商业 - 已验证可用
    techcrunch: {
      name: 'TechCrunch',
      rss: 'https://techcrunch.com/feed/',
      category: '科技'
    },
    arstechnica: {
      name: 'Ars Technica',
      rss: 'https://feeds.arstechnica.com/arstechnica/index',
      category: '科技'
    },
    wired: {
      name: 'Wired',
      rss: 'https://www.wired.com/feed/rss',
      category: '科技'
    },
    theRegister: {
      name: 'The Register',
      rss: 'https://www.theregister.com/headlines.atom',
      category: '科技'
    },
    
    // 军事防务 - 已验证可用
    defenseNews: {
      name: 'Defense News',
      rss: 'https://www.defensenews.com/arc/outboundfeeds/rss/?outputType=xml',
      category: '军事'
    },
    
    // 综合新闻 - 已验证可用
    npr: {
      name: 'NPR News',
      rss: 'https://feeds.npr.org/1001/rss.xml',
      category: '综合'
    },
    
    // 待测试/需要代理
    scmp: {
      name: '南华早报 SCMP',
      rss: 'https://www.scmp.com/rss/91/feed',
      category: '国际'
    },
    ft: {
      name: 'Financial Times',
      rss: 'https://www.ft.com/rss/home/asia',
      category: '财经'
    },
    bbc: {
      name: 'BBC News',
      rss: 'https://feeds.bbci.co.uk/news/world/rss.xml',
      category: '国际'
    },
    reuters: {
      name: 'Reuters',
      rss: 'https://www.reuters.com/rssFeed/businessNews',
      category: '财经'
    }
  }
};

// RSS解析函数
async function fetchRSS(url) {
  try {
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/rss+xml, application/xml, text/xml, */*'
      }
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.text();
  } catch (err) {
    console.error(`  ✗ 获取失败: ${err.message}`);
    return null;
  }
}

// 简单XML解析
function parseRSS(xml) {
  const items = [];
  const itemRegex = /<item>[\s\S]*?<\/item>/g;
  const items_match = xml.match(itemRegex);
  
  if (!items_match) return items;
  
  for (const item of items_match.slice(0, CONFIG.maxArticlesPerSource)) {
    const title = item.match(/<title>(?:<!\[CDATA\[)?([\s\S]*?)(?:\]\]>)?<\/title>/)?.[1]?.trim() || '';
    const link = item.match(/<link>(?:<!\[CDATA\[)?([\s\S]*?)(?:\]\]>)?<\/link>/)?.[1]?.trim() || 
                 item.match(/<link[^>]*href=["']([^"']+)["']/)?.[1]?.trim() || '';
    const desc = item.match(/<description>(?:<!\[CDATA\[)?([\s\S]*?)(?:\]\]>)?<\/description>/)?.[1]?.trim() || '';
    const pubDate = item.match(/<pubDate>(.*?)<\/pubDate>/)?.[1]?.trim() || 
                    item.match(/<dc:date>(.*?)<\/dc:date>/)?.[1]?.trim() ||
                    item.match(/<published>(.*?)<\/published>/)?.[1]?.trim() || '';
    
    if (title && link) {
      items.push({ title, link, description: desc, pubDate });
    }
  }
  return items;
}

// 生成HTML
function generateHTML(articlesByCategory, date, stats) {
  const categories = {
    '财经': '💰',
    '国际': '🌍',
    '政治': '🏛️',
    '军事': '🎖️',
    '科技': '💻',
    '综合': '📰'
  };

  let html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>每日新闻简报 - ${date}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      line-height: 1.6;
      color: #333;
      background: #f5f5f5;
      padding: 20px;
    }
    .container {
      max-width: 900px;
      margin: 0 auto;
      background: white;
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      overflow: hidden;
    }
    .header {
      background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
      color: white;
      padding: 30px;
      text-align: center;
    }
    .header h1 { font-size: 28px; margin-bottom: 8px; }
    .header .date { opacity: 0.8; font-size: 14px; }
    .header .note {
      margin-top: 15px;
      font-size: 12px;
      opacity: 0.6;
      font-style: italic;
    }
    .category {
      border-bottom: 1px solid #eee;
    }
    .category:last-child { border-bottom: none; }
    .category-header {
      background: #f8f9fa;
      padding: 15px 25px;
      font-size: 18px;
      font-weight: 600;
      color: #1a1a2e;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .article {
      padding: 20px 25px;
      border-bottom: 1px solid #f0f0f0;
      transition: background 0.2s;
    }
    .article:last-child { border-bottom: none; }
    .article:hover { background: #fafafa; }
    .article-title {
      font-size: 16px;
      font-weight: 600;
      margin-bottom: 8px;
    }
    .article-title a {
      color: #1a1a2e;
      text-decoration: none;
    }
    .article-title a:hover { color: #e94560; }
    .article-meta {
      font-size: 12px;
      color: #888;
      margin-bottom: 8px;
    }
    .article-source { color: #e94560; font-weight: 500; }
    .article-desc {
      font-size: 14px;
      color: #666;
      line-height: 1.5;
    }
    .footer {
      background: #f8f9fa;
      padding: 20px;
      text-align: center;
      font-size: 12px;
      color: #888;
    }
    .stats {
      background: #e8f4f8;
      padding: 15px 25px;
      font-size: 13px;
      color: #555;
      border-bottom: 1px solid #eee;
    }
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 10px;
      margin-top: 10px;
    }
    .stat-item {
      background: white;
      padding: 8px 12px;
      border-radius: 6px;
      font-size: 12px;
    }
    .stat-item .label { color: #888; }
    .stat-item .value { color: #1a1a2e; font-weight: 600; }
    .source-tag {
      display: inline-block;
      background: #f0f0f0;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 11px;
      margin-right: 5px;
      margin-bottom: 5px;
    }
    .source-tag.success { background: #d4edda; color: #155724; }
    .source-tag.failed { background: #f8d7da; color: #721c24; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>📰 每日新闻简报</h1>
      <div class="date">${date}</div>
      <div class="note">精选可靠信源 · 去除噪音 · 保留事实</div>
    </div>
    
    <div class="stats">
      <div>📊 本期统计</div>
      <div class="stats-grid">
        <div class="stat-item">
          <span class="label">总文章数</span>
          <span class="value">${stats.totalArticles}</span>
        </div>
        <div class="stat-item">
          <span class="label">成功信源</span>
          <span class="value">${stats.successSources}/${stats.totalSources}</span>
        </div>
      </div>
      <div style="margin-top: 10px;">
        ${stats.sourceStatus.map(s => `<span class="source-tag ${s.success ? 'success' : 'failed'}">${s.name}</span>`).join('')}
      </div>
    </div>
`;

  for (const [category, articles] of Object.entries(articlesByCategory)) {
    if (articles.length === 0) continue;
    
    html += `
    <div class="category">
      <div class="category-header">${categories[category] || '📄'} ${category}</div>
`;
    
    for (const article of articles) {
      const articleDate = article.pubDate ? new Date(article.pubDate).toLocaleString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit' }) : '';
      html += `
      <div class="article">
        <div class="article-title">
          <a href="${article.link}" target="_blank">${escapeHtml(article.title)}</a>
        </div>
        <div class="article-meta">
          <span class="article-source">${article.source}</span>
          ${articleDate ? `· ${articleDate}` : ''}
        </div>
        ${article.description ? `<div class="article-desc">${escapeHtml(stripHtml(article.description).substring(0, 200))}${article.description.length > 200 ? '...' : ''}</div>` : ''}
      </div>
`;
    }
    
    html += `    </div>
`;
  }

  html += `
    <div class="footer">
      自动生成于 ${new Date().toLocaleString('zh-CN')}
    </div>
  </div>
</body>
</html>`;

  return html;
}

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function stripHtml(html) {
  return html.replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim();
}

// 主函数
async function main() {
  console.log('🚀 开始抓取新闻...\n');
  
  const articlesByCategory = {
    '财经': [],
    '国际': [],
    '政治': [],
    '军事': [],
    '科技': [],
    '综合': []
  };

  const stats = {
    totalSources: Object.keys(CONFIG.sources).length,
    successSources: 0,
    totalArticles: 0,
    sourceStatus: []
  };

  for (const [key, source] of Object.entries(CONFIG.sources)) {
    console.log(`📡 ${source.name}`);
    
    const xml = await fetchRSS(source.rss);
    if (xml) {
      const articles = parseRSS(xml);
      articles.forEach(a => {
        a.source = source.name;
        if (articlesByCategory[source.category]) {
          articlesByCategory[source.category].push(a);
        }
      });
      console.log(`  ✓ 获取 ${articles.length} 条`);
      stats.successSources++;
      stats.totalArticles += articles.length;
      stats.sourceStatus.push({ name: source.name, success: true });
    } else {
      console.log(`  ✗ 获取失败`);
      stats.sourceStatus.push({ name: source.name, success: false });
    }
  }

  const today = new Date().toISOString().split('T')[0];
  const html = generateHTML(articlesByCategory, today, stats);
  
  const outputFile = path.join(CONFIG.outputDir, `news-${today}.html`);
  fs.writeFileSync(outputFile, html, 'utf-8');
  
  console.log(`\n✅ 已生成: ${outputFile}`);
  
  // 同时更新最新版本
  const latestFile = path.join(CONFIG.outputDir, 'latest.html');
  fs.writeFileSync(latestFile, html, 'utf-8');
  console.log(`✅ 已更新: ${latestFile}`);
  
  console.log(`\n📊 统计: ${stats.totalArticles} 条新闻，${stats.successSources}/${stats.totalSources} 个信源可用`);
}

main().catch(console.error);
