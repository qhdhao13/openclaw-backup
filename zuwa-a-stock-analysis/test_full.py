#!/usr/bin/env python3
"""
祖蛙完整流程测试 - 使用真实数据
"""
import sys
sys.path.insert(0, '.')

import asyncio
from main import ZuwaStockAnalyzer

async def test_full_flow():
    """测试完整分析流程"""
    print("=" * 70)
    print("🐸 祖蛙沪深A股分析系统 - 完整流程测试")
    print("=" * 70)
    
    # 初始化分析器
    analyzer = ZuwaStockAnalyzer("config/agents.yaml")
    
    # 分析贵州茅台
    result = await analyzer.analyze_stock("600519", "贵州茅台")
    
    # 打印报告
    analyzer.print_report(result)
    
    print("\n✅ 完整流程测试成功！")

if __name__ == "__main__":
    asyncio.run(test_full_flow())
