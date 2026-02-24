#!/usr/bin/env python3
"""
高级分析功能测试
"""
import sys
sys.path.insert(0, '.')

import asyncio
import pandas as pd
from src.analysis.advanced_analyzer import get_advanced_analyzer
from src.agents.data_agent import DataCollectionAgent

async def test_advanced_analysis():
    """测试高级分析功能"""
    print("=" * 80)
    print("🐸 祖蛙高级分析功能测试")
    print("=" * 80)
    
    symbol = "600519"
    name = "贵州茅台"
    
    print(f"\n📊 测试股票: {symbol} {name}\n")
    
    # 获取基础数据
    data_agent = DataCollectionAgent({})
    data_result = await data_agent.analyze(symbol, {"name": name})
    daily_data = data_result.details.get("daily_data", pd.DataFrame())
    
    analyzer = get_advanced_analyzer()
    
    # ============================================
    # 功能1: 量价关系分析
    # ============================================
    print("-" * 80)
    print("📈 功能1: 成交量与股价对应关系分析")
    print("-" * 80)
    
    if not daily_data.empty:
        vp_analysis = analyzer.analyze_volume_price_relationship(daily_data)
        
        if "error" not in vp_analysis:
            print(f"✅ 当前成交量: {vp_analysis.get('current_volume', 'N/A'):,}")
            print(f"✅ 5日均量: {vp_analysis.get('volume_ma5', 'N/A'):,}")
            print(f"✅ 量比: {vp_analysis.get('volume_ratio', 'N/A')}")
            print(f"✅ 成交量百分位: {vp_analysis.get('volume_percentile', 'N/A')}")
            print(f"✅ 价格趋势: {vp_analysis.get('price_trend', 'N/A')}")
            print(f"✅ 量能趋势: {vp_analysis.get('volume_trend', 'N/A')}")
            print(f"✅ 健康度评分: {vp_analysis.get('health_score', 'N/A')}")
            
            signals = vp_analysis.get('signals', [])
            if signals:
                print(f"\n📍 量价信号:")
                for sig in signals:
                    print(f"   {sig.get('type', '')} - {sig.get('description', '')}")
            
            divergence = vp_analysis.get('divergence', [])
            if divergence:
                print(f"\n⚠️ 背离信号:")
                for div in divergence:
                    print(f"   {div}")
        else:
            print(f"❌ 分析失败: {vp_analysis.get('error')}")
    else:
        print("❌ 缺少历史数据")
    
    # ============================================
    # 功能2: 股东数量分析
    # ============================================
    print("\n" + "-" * 80)
    print("👥 功能2: 历史股价与股东数量对应关系分析")
    print("-" * 80)
    
    holder_analysis = analyzer.analyze_price_holder_relationship(symbol)
    
    if "error" not in holder_analysis:
        print(f"✅ 当前股东数: {holder_analysis.get('current_holders', 'N/A'):,}")
        print(f"✅ 上期股东数: {holder_analysis.get('previous_holders', 'N/A'):,}")
        print(f"✅ 变化: {holder_analysis.get('change_pct', 'N/A')}%")
        print(f"✅ 户均市值: {holder_analysis.get('avg_market_value', 'N/A')}")
        print(f"✅ 信号: {holder_analysis.get('signal', 'N/A')}")
        
        analysis_list = holder_analysis.get('analysis', [])
        if analysis_list:
            print(f"\n📍 分析结论:")
            for item in analysis_list:
                print(f"   {item}")
    else:
        print(f"❌ 分析失败: {holder_analysis.get('error')}")
    
    # ============================================
    # 功能3: 融资融券关系分析
    # ============================================
    print("\n" + "-" * 80)
    print("💰 功能3: 历史股价与融资融券关系分析")
    print("-" * 80)
    
    margin_analysis = analyzer.analyze_price_margin_relationship(symbol)
    
    if "error" not in margin_analysis:
        print(f"✅ 融资余额: {margin_analysis.get('margin_balance', 'N/A'):,.0f} 万元")
        print(f"✅ 融券余额: {margin_analysis.get('short_balance', 'N/A'):,.0f} 万元")
        print(f"✅ 5日融资变化: {margin_analysis.get('margin_change_5d', 'N/A')}%")
        print(f"✅ 杠杆占比: {margin_analysis.get('leverage_ratio', 'N/A')}")
        print(f"✅ 信号: {margin_analysis.get('signal', 'N/A')}")
        
        analysis_list = margin_analysis.get('analysis', [])
        if analysis_list:
            print(f"\n📍 分析结论:")
            for item in analysis_list:
                print(f"   {item}")
    else:
        print(f"❌ 分析失败: {margin_analysis.get('error')}")
    
    # ============================================
    # 功能4: 主动买卖分析
    # ============================================
    print("\n" + "-" * 80)
    print("🎯 功能4: 当日主动买主动卖明细数据分析")
    print("-" * 80)
    
    buy_sell_analysis = analyzer.analyze_active_buy_sell(symbol)
    
    if "error" not in buy_sell_analysis:
        print(f"✅ 主动买入: {buy_sell_analysis.get('active_buy', 'N/A'):,.0f} 万元")
        print(f"✅ 主动卖出: {buy_sell_analysis.get('active_sell', 'N/A'):,.0f} 万元")
        print(f"✅ 净流入: {buy_sell_analysis.get('net_flow', 'N/A'):,.0f} 万元")
        print(f"✅ 买入占比: {buy_sell_analysis.get('buy_ratio', 'N/A')}%")
        print(f"✅ 卖出占比: {buy_sell_analysis.get('sell_ratio', 'N/A')}%")
        print(f"✅ 散户买入: {buy_sell_analysis.get('small_buy', 'N/A'):,.0f} 万元")
        print(f"✅ 散户卖出: {buy_sell_analysis.get('small_sell', 'N/A'):,.0f} 万元")
        print(f"✅ 信号: {buy_sell_analysis.get('signal', 'N/A')}")
    else:
        print(f"❌ 分析失败: {buy_sell_analysis.get('error')}")
    
    print("\n" + "=" * 80)
    print("✅ 高级分析功能测试完成")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_advanced_analysis())
