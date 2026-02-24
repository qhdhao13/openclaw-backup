#!/usr/bin/env python3
"""
祖蛙测试脚本 - 测试数据获取和分析流程 (简化版)
"""
import sys
sys.path.insert(0, '.')

import asyncio
from src.agents.data_agent import DataCollectionAgent
from src.agents.technical_agent import TechnicalAnalysisAgent

async def test_single_stock():
    """测试单只股票数据获取"""
    print("=" * 60)
    print("🐸 祖蛙数据获取测试")
    print("=" * 60)
    
    # 测试股票：贵州茅台
    symbol = "600519"
    name = "贵州茅台"
    
    print(f"\n📊 测试股票: {symbol} {name}")
    
    # 1. 测试数据获取
    print("\n1️⃣ 数据收集Agent测试...")
    data_agent = DataCollectionAgent({})
    data_result = await data_agent.analyze(symbol, {"name": name})
    
    print(f"   状态: {data_result.summary}")
    
    price_data = data_result.details.get("price_data", {})
    print(f"   当前价: {price_data.get('current', 'N/A')}")
    print(f"   开盘价: {price_data.get('open', 'N/A')}")
    print(f"   最高价: {price_data.get('high', 'N/A')}")
    print(f"   最低价: {price_data.get('low', 'N/A')}")
    print(f"   涨跌幅: {price_data.get('change_pct', 'N/A')}%")
    print(f"   成交量: {price_data.get('volume', 'N/A')}")
    print(f"   日期: {price_data.get('date', 'N/A')}")
    
    basic_info = data_result.details.get("basic_info", {})
    print(f"   股票名称: {basic_info.get('name', 'N/A')}")
    print(f"   所属行业: {basic_info.get('industry', 'N/A')}")
    print(f"   总市值: {basic_info.get('market_cap', 'N/A')}")
    print(f"   市盈率: {basic_info.get('pe_ttm', 'N/A')}")
    
    daily_data = data_result.details.get("daily_data")
    if daily_data is not None and hasattr(daily_data, 'shape'):
        print(f"   历史数据: {daily_data.shape[0]} 天")
        if not daily_data.empty:
            print(f"   数据列: {list(daily_data.columns)}")
    
    # 2. 测试技术分析
    print("\n2️⃣ 技术分析Agent测试...")
    if daily_data is not None and not daily_data.empty:
        tech_agent = TechnicalAnalysisAgent({})
        context = {
            "price_data": price_data,
            "daily_data": daily_data
        }
        tech_result = await tech_agent.analyze(symbol, context)
        
        print(f"   信号: {tech_result.signal}")
        print(f"   置信度: {tech_result.confidence:.1f}%")
        print(f"   摘要: {tech_result.summary}")
        
        details = tech_result.details
        if 'trend' in details:
            print(f"   短期趋势: {details['trend'].get('short_term', 'N/A')}")
            print(f"   中期趋势: {details['trend'].get('mid_term', 'N/A')}")
        if 'momentum' in details:
            print(f"   RSI: {details['momentum'].get('rsi', 'N/A'):.2f}")
            print(f"   RSI信号: {details['momentum'].get('rsi_signal', 'N/A')}")
    else:
        print("   ⚠️ 缺少历史数据，跳过技术分析")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_single_stock())
