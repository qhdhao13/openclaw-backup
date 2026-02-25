#!/usr/bin/env python3
"""
股票新闻自动爬取系统
从东方财富、新浪财经爬取实时新闻
"""
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import re
import time

class StockNewsCrawler:
    """股票新闻爬虫"""
    
    def __init__(self, stock_code, stock_name=None):
        self.stock_code = stock_code
        self.stock_name = stock_name or stock_code
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def crawl_eastmoney(self, days=3):
        """爬取东方财富新闻"""
        news_list = []
        try:
            # 东方财富个股新闻页面
            url = f"https://quote.eastmoney.com/concept/sh{self.stock_code}.html"
            # 备用URL
            url2 = f"https://emweb.securities.eastmoney.com/PC_HSF10/NewStockAnalysis/Index?type=web&code=SZ{self.stock_code}"
            
            # 尝试获取新闻
            try:
                response = requests.get(url2, headers=self.headers, timeout=10)
                response.encoding = 'utf-8'
            except:
                return news_list
            
            # 解析新闻（东方财富页面结构复杂，这里简化处理）
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 尝试提取新闻标题
            news_items = soup.find_all('a', href=re.compile(r'news'))
            for item in news_items[:10]:  # 取前10条
                title = item.get_text().strip()
                if title and len(title) > 10:
                    news_list.append({
                        "title": title,
                        "source": "东方财富",
                        "time": datetime.now().strftime("%Y-%m-%d"),
                        "url": item.get('href', '')
                    })
            
            return news_list
        except Exception as e:
            print(f"东方财富爬取失败: {e}")
            return []
    
    def crawl_sina_finance(self):
        """爬取新浪财经新闻"""
        news_list = []
        try:
            # 新浪财经个股页面
            url = f"https://finance.sina.com.cn/realstock/company/sz{self.stock_code}/nc.shtml"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'gb2312'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 新浪新闻列表通常在特定class中
            news_items = soup.find_all('a', target='_blank')
            
            for item in news_items[:15]:
                title = item.get_text().strip()
                href = item.get('href', '')
                
                # 过滤有效新闻
                if (title and len(title) > 10 and 
                    'finance.sina.com.cn' in href and
                    any(keyword in title for keyword in ['业绩', '营收', '利润', '公告', '订单', '项目', '投资', '合作'])):
                    
                    news_list.append({
                        "title": title,
                        "source": "新浪财经",
                        "time": datetime.now().strftime("%Y-%m-%d"),
                        "url": href
                    })
            
            return news_list
        except Exception as e:
            print(f"新浪财经爬取失败: {e}")
            return []
    
    def crawl_10jqka(self):
        """爬取同花顺新闻"""
        news_list = []
        try:
            url = f"https://basic.10jqka.com.cn/{self.stock_code}/news.html"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找新闻列表
            news_items = soup.find_all('a', class_=re.compile(r'news|title'))
            
            for item in news_items[:10]:
                title = item.get_text().strip()
                if title and len(title) > 10:
                    news_list.append({
                        "title": title,
                        "source": "同花顺",
                        "time": datetime.now().strftime("%Y-%m-%d"),
                        "url": item.get('href', '')
                    })
            
            return news_list
        except Exception as e:
            print(f"同花顺爬取失败: {e}")
            return []
    
    def crawl_all(self):
        """爬取所有来源的新闻"""
        print(f"正在爬取 {self.stock_name}({self.stock_code}) 的新闻...\n")
        
        all_news = []
        
        # 爬取各平台
        sources = [
            ("东方财富", self.crawl_eastmoney),
            ("新浪财经", self.crawl_sina_finance),
            ("同花顺", self.crawl_10jqka)
        ]
        
        for source_name, crawler_func in sources:
            try:
                print(f"正在爬取 {source_name}...")
                news = crawler_func()
                all_news.extend(news)
                print(f"✅ {source_name}: 获取 {len(news)} 条")
                time.sleep(1)  # 礼貌爬取
            except Exception as e:
                print(f"❌ {source_name}: {e}")
        
        # 去重（基于标题相似度）
        unique_news = self._deduplicate_news(all_news)
        
        return unique_news
    
    def _deduplicate_news(self, news_list):
        """去除重复新闻"""
        seen_titles = set()
        unique = []
        
        for news in news_list:
            # 简化标题用于去重
            simplified = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', news['title'])
            if simplified not in seen_titles and len(simplified) > 5:
                seen_titles.add(simplified)
                unique.append(news)
        
        return unique

def analyze_news_sentiment_local(news_list):
    """本地简单情感分析"""
    positive_words = ['增长', '上涨', '突破', '利好', '盈利', '增持', '买入', '看好', '订单', '合作', '签约']
    negative_words = ['下跌', '亏损', '减持', '卖出', '风险', '警告', '处罚', '下滑', '下降']
    
    results = []
    for news in news_list:
        title = news['title']
        pos_count = sum(1 for word in positive_words if word in title)
        neg_count = sum(1 for word in negative_words if word in title)
        
        if pos_count > neg_count:
            sentiment = "正面"
        elif neg_count > pos_count:
            sentiment = "负面"
        else:
            sentiment = "中性"
        
        news['sentiment'] = sentiment
        results.append(news)
    
    return results

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("""
股票新闻爬取系统

用法:
  python3 stock_news.py 000338 潍柴动力
        """)
        return
    
    stock_code = sys.argv[1]
    stock_name = sys.argv[2] if len(sys.argv) > 2 else stock_code
    
    # 爬取新闻
    crawler = StockNewsCrawler(stock_code, stock_name)
    news_list = crawler.crawl_all()
    
    if not news_list:
        print("\n⚠️ 未获取到新闻数据")
        return
    
    # 情感分析
    analyzed_news = analyze_news_sentiment_local(news_list)
    
    # 统计
    positive = sum(1 for n in analyzed_news if n['sentiment'] == '正面')
    negative = sum(1 for n in analyzed_news if n['sentiment'] == '负面')
    neutral = sum(1 for n in analyzed_news if n['sentiment'] == '中性')
    
    # 输出结果
    print(f"\n=== {stock_name}({stock_code}) 新闻分析结果 ===\n")
    print(f"总计获取: {len(analyzed_news)} 条新闻")
    print(f"情感分布: 正面 {positive} | 负面 {negative} | 中性 {neutral}\n")
    
    print("📰 最新新闻（Top 10）：")
    print("-" * 80)
    
    for i, news in enumerate(analyzed_news[:10], 1):
        emoji = "🟢" if news['sentiment'] == '正面' else "🔴" if news['sentiment'] == '负面' else "⚪"
        print(f"{i}. {emoji} [{news['source']}] {news['title']}")
    
    # 保存结果
    output_file = f"news_{stock_code}_{datetime.now().strftime('%Y%m%d')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analyzed_news, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 已保存到: {output_file}")

if __name__ == "__main__":
    main()
