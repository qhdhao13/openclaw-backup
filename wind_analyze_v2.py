#!/usr/bin/env python3
"""
Wind API 股票热度分析脚本 - 优化版
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
        print("❌ Wind 连接失败")
        return
    
    print("✅ Wind 连接成功\n")
    
    # 获取当前日期
    today = "2026-02-25"
    
    # 1. 基本信息
    print("📋 【基本信息】")
    basic = w.wss(stock_code, "sec_name,trade_code,close,change,pct_change")
    if basic.ErrorCode == 0 and basic.Data:
        name = basic.Data[0][0] if basic.Data[0] else stock_code
        close = basic.Data[2][0] if basic.Data[2] else 'N/A'
        change_pct = basic.Data[4][0] if basic.Data[4] else 'N/A'
        print(f"   股票名称: {name}")
        print(f"   最新价格: {close}")
        print(f"   涨跌幅: {change_pct}%")
    
    # 2. 新闻舆情 - 使用历史数据接口
    print("\n📰 【新闻舆情】(近30日)")
    try:
        # 使用 wsd 获取历史新闻数量
        news_count = w.wsd(stock_code, "news_count", "ED-30D", today, "")
        if news_count.ErrorCode == 0 and news_count.Data and news_count.Data[0]:
            total_news = sum([x for x in news_count.Data[0] if x is not None])
            print(f"   新闻提及次数: {total_news}")
        else:
            print(f"   新闻数据: 暂无")
    except Exception as e:
        print(f"   新闻数据获取失败: {e}")
    
    # 3. 机构关注度
    print("\n🏢 【机构关注度】")
    try:
        # 使用 wss 获取静态数据
        inst_fields = "research_report_num,inst_research_num,rating_avg"
        inst = w.wss(stock_code, inst_fields)
        if inst.ErrorCode == 0 and inst.Data:
            report_num = inst.Data[0][0] if inst.Data[0] else 'N/A'
            research_num = inst.Data[1][0] if inst.Data[1] else 'N/A'
            rating = inst.Data[2][0] if inst.Data[2] else 'N/A'
            print(f"   研报数量: {report_num}")
            print(f"   机构调研次数: {research_num}")
            print(f"   平均评级: {rating}")
    except Exception as e:
        print(f"   机构数据获取失败: {e}")
    
    # 4. 资金流向
    print("\n💰 【资金流向】")
    try:
        # 获取近5日资金数据
        money_fields = "mfd_buyamt,mfd_sellamt,mfd_netinflow"
        money = w.wsd(stock_code, money_fields, "ED-5D", today, "")
        if money.ErrorCode == 0 and money.Data and len(money.Data) >= 3:
            buy_amt = sum([x for x in money.Data[0] if x is not None]) / 10000
            sell_amt = sum([x for x in money.Data[1] if x is not None]) / 10000
            net_amt = sum([x for x in money.Data[2] if x is not None]) / 10000
            print(f"   主力买入: {buy_amt:.2f} 万元")
            print(f"   主力卖出: {sell_amt:.2f} 万元")
            print(f"   净流入: {net_amt:.2f} 万元")
            print(f"   流向判断: {'净流入 ✅' if net_amt > 0 else '净流出 ⚠️'}")
    except Exception as e:
        print(f"   资金流向获取失败: {e}")
    
    # 5. 盈利预测
    print("\n📊 【盈利预测】(一致预期)")
    try:
        eps_fields = "eps_ttm,eps_next,eps_growth"
        eps = w.wss(stock_code, eps_fields)
        if eps.ErrorCode == 0 and eps.Data:
            eps_ttm = eps.Data[0][0] if eps.Data[0] else 'N/A'
            eps_next = eps.Data[1][0] if eps.Data[1] else 'N/A'
            growth = eps.Data[2][0] if eps.Data[2] else 'N/A'
            print(f"   当前EPS(TTM): {eps_ttm}")
            print(f"   预测EPS(下期): {eps_next}")
            print(f"   预期增长率: {growth}%")
    except Exception as e:
        print(f"   盈利预测获取失败: {e}")
    
    # 6. 估值水平
    print("\n📈 【估值水平】")
    try:
        val_fields = "pe_ttm,pb_mrq,ps_ttm"
        val = w.wss(stock_code, val_fields)
        if val.ErrorCode == 0 and val.Data:
            pe = val.Data[0][0] if val.Data[0] else 'N/A'
            pb = val.Data[1][0] if val.Data[1] else 'N/A'
            ps = val.Data[2][0] if val.Data[2] else 'N/A'
            print(f"   市盈率(TTM): {pe}")
            print(f"   市净率(MRQ): {pb}")
            print(f"   市销率(TTM): {ps}")
    except Exception as e:
        print(f"   估值数据获取失败: {e}")
    
    # 7. 技术面热度
    print("\n🔥 【技术面热度】")
    try:
        tech_fields = "rsi_14d,macd,macd_signal"
        tech = w.wss(stock_code, tech_fields)
        if tech.ErrorCode == 0 and tech.Data:
            rsi = tech.Data[0][0] if tech.Data[0] else 'N/A'
            macd = tech.Data[1][0] if tech.Data[1] else 'N/A'
            macd_signal = tech.Data[2][0] if tech.Data[2] else 'N/A'
            print(f"   RSI(14日): {rsi}")
            print(f"   MACD: {macd}")
            if rsi != 'N/A':
                if rsi > 70:
                    print(f"   RSI状态: 超买 ⚠️")
                elif rsi < 30:
                    print(f"   RSI状态: 超卖 ✅")
                else:
                    print(f"   RSI状态: 中性")
    except Exception as e:
        print(f"   技术数据获取失败: {e}")
    
    print("\n✅ 分析完成")
    w.close()

if __name__ == "__main__":
    stock = sys.argv[1] if len(sys.argv) > 1 else "000338.SZ"
    analyze_stock_sentiment(stock)
