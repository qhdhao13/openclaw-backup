#!/usr/bin/env python3
"""
Tushare 快速查询工具
"""

import os
import sys
import tushare as ts
from datetime import datetime, timedelta

# Token
TOKEN = "97f10d5f7b6ddedae78d3293caf73a020ab83b00c199883847a9ad5c"

def get_pro_api():
    """获取 Tushare API"""
    return ts.pro_api(TOKEN)

def query_stock_daily(code, days=5):
    """查询股票日线"""
    pro = get_pro_api()
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=days*2)).strftime('%Y%m%d')
    
    df = pro.daily(ts_code=code, start_date=start_date, end_date=end_date)
    return df.sort_values('trade_date', ascending=False).head(days)

def query_stock_info(code):
    """查询股票信息"""
    pro = get_pro_api()
    df = pro.stock_basic(ts_code=code, fields='ts_code,name,industry,area,list_date')
    return df.iloc[0] if not df.empty else None

def query_market_overview():
    """查询市场概况"""
    pro = get_pro_api()
    today = datetime.now().strftime('%Y%m%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    
    # 获取今日数据
    df_today = pro.daily(trade_date=today)
    if df_today.empty:
        df_today = pro.daily(trade_date=yesterday)
        trade_date = yesterday
    else:
        trade_date = today
    
    up = len(df_today[df_today['pct_chg'] > 0])
    down = len(df_today[df_today['pct_chg'] < 0])
    flat = len(df_today[df_today['pct_chg'] == 0])
    
    return {
        'date': trade_date,
        'total': len(df_today),
        'up': up,
        'down': down,
        'flat': flat,
        'limit_up': len(df_today[df_today['pct_chg'] >= 9.9]),
        'limit_down': len(df_today[df_today['pct_chg'] <= -9.9])
    }

def main():
    if len(sys.argv) < 2:
        print("🦞 Tushare 快速查询工具")
        print("=" * 50)
        print("\n用法:")
        print("  python3 tushare_query.py daily <股票代码> [天数]")
        print("  python3 tushare_query.py info <股票代码>")
        print("  python3 tushare_query.py market")
        print("\n示例:")
        print("  python3 tushare_query.py daily 000001.SZ 10")
        print("  python3 tushare_query.py info 000001.SZ")
        print("  python3 tushare_query.py market")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "daily":
        code = sys.argv[2]
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        df = query_stock_daily(code, days)
        print(f"\n📈 {code} 最近{days}天行情:\n")
        print(df[['trade_date', 'open', 'high', 'low', 'close', 'pct_chg', 'vol']].to_string(index=False))
    
    elif cmd == "info":
        code = sys.argv[2]
        info = query_stock_info(code)
        if info:
            print(f"\n📋 {code} 股票信息:")
            print(f"  名称: {info['name']}")
            print(f"  行业: {info['industry']}")
            print(f"  地区: {info['area']}")
            print(f"  上市日期: {info['list_date']}")
        else:
            print(f"❌ 未找到 {code}")
    
    elif cmd == "market":
        overview = query_market_overview()
        print(f"\n📊 市场概况 ({overview['date']}):")
        print(f"  总股票数: {overview['total']}")
        print(f"  上涨: {overview['up']} 📈")
        print(f"  下跌: {overview['down']} 📉")
        print(f"  平盘: {overview['flat']} ➖")
        print(f"  涨停: {overview['limit_up']} 🚀")
        print(f"  跌停: {overview['limit_down']} 💥")
    
    else:
        print(f"❌ 未知命令: {cmd}")

if __name__ == "__main__":
    main()
