#!/usr/bin/env python3
"""
Wind API 股票热度分析脚本
"""
import sys
sys.path.insert(0, '/Applications/Wind API.app/Contents/python')

from WindPy import w

def analyze_stock_sentiment(stock_code="000338.SZ"):
    """分析股票的市场热度"""
    print(f"=== 正在分析 {stock_code} 的市场热度 ===\n")
    
    # 启动 Wind
    w.start()
    if not w.isconnected():
        print("❌ Wind 连接失败，请检查终端是否已登录")
        return
    
    print("✅ Wind 连接成功\n")
    
    # 1. 新闻舆情
    print("📰 【新闻舆情】")
    news_fields = "news_count,news_positive,news_negative"
    news = w.wsd(stock_code, news_fields, "ED-30D", "2026-02-25", "")
    if news.Data and len(news.Data) >= 3:
        print(f"   近30天新闻总数: {news.Data[0][-1] if news.Data[0] else 'N/A'}")
        print(f"   正面新闻: {news.Data[1][-1] if news.Data[1] else 'N/A'}")
        print(f"   负面新闻: {news.Data[2][-1] if news.Data[2] else 'N/A'}")
    
    # 2. 机构关注度
    print("\n🏢 【机构关注度】")
    inst_fields = "research_report_num,inst_research_num,inst_rating_avg"
    inst = w.wsd(stock_code, inst_fields, "2026-01-01", "2026-02-25", "")
    if inst.Data and len(inst.Data) >= 3:
        print(f"   研报数量(今年): {inst.Data[0][0] if inst.Data[0] else 'N/A'}")
        print(f"   机构调研次数: {inst.Data[1][0] if inst.Data[1] else 'N/A'}")
        print(f"   平均评级: {inst.Data[2][0] if inst.Data[2] else 'N/A'}")
    
    # 3. 资金流向
    print("\n💰 【资金流向】(近5日)")
    money_fields = "mfd_buyamt_d,mfd_sellamt_d,mfd_netinflow_d"
    money = w.wsd(stock_code, money_fields, "ED-5D", "2026-02-25", "")
    if money.Data and len(money.Data) >= 3:
        buy = sum([x for x in money.Data[0] if x is not None]) / 10000
        sell = sum([x for x in money.Data[1] if x is not None]) / 10000
        net = sum([x for x in money.Data[2] if x is not None]) / 10000
        print(f"   主力买入: {buy:.2f} 万元")
        print(f"   主力卖出: {sell:.2f} 万元")
        print(f"   净流入: {net:.2f} 万元 ({'流入' if net > 0 else '流出'})")
    
    # 4. 盈利预测
    print("\n📊 【盈利预测】")
    eps_fields = "eps_ttm,eps_next,eps_growth"
    eps = w.wsd(stock_code, eps_fields, "2026-02-25", "2026-02-25", "")
    if eps.Data and len(eps.Data) >= 3:
        print(f"   当前EPS(TTM): {eps.Data[0][0] if eps.Data[0] else 'N/A'}")
        print(f"   预测EPS(下期): {eps.Data[1][0] if eps.Data[1] else 'N/A'}")
        print(f"   预期增长率: {eps.Data[2][0] if eps.Data[2] else 'N/A'}")
    
    # 5. 估值水平
    print("\n📈 【估值水平】")
    val_fields = "pe_ttm,pb_mrq,ps_ttm"
    val = w.wsd(stock_code, val_fields, "2026-02-25", "2026-02-25", "")
    if val.Data and len(val.Data) >= 3:
        print(f"   市盈率(TTM): {val.Data[0][0] if val.Data[0] else 'N/A'}")
        print(f"   市净率(MRQ): {val.Data[1][0] if val.Data[1] else 'N/A'}")
        print(f"   市销率(TTM): {val.Data[2][0] if val.Data[2] else 'N/A'}")
    
    print("\n✅ 分析完成")
    w.close()

if __name__ == "__main__":
    stock = sys.argv[1] if len(sys.argv) > 1 else "000338.SZ"
    analyze_stock_sentiment(stock)
