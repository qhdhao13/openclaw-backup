"""
祖蛙沪深A股分析系统 - 主入口
"""
import asyncio
import argparse
import yaml
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv

from src.agents import (
    DataCollectionAgent,
    TechnicalAnalysisAgent,
    CapitalAnalysisAgent,
    IntelligenceAgent,
    SectorAnalysisAgent,
    BullAnalystAgent,
    BearAnalystAgent,
    RetailSentimentAgent,
    ChiefAnalystAgent,
    AgentOutput
)

# 加载环境变量
load_dotenv()


class ZuwaStockAnalyzer:
    """祖蛙股票分析器"""
    
    def __init__(self, config_path: str = "config/agents.yaml"):
        """初始化分析器"""
        self.config = self._load_config(config_path)
        self.agents = self._init_agents()
        
    def _load_config(self, path: str) -> Dict:
        """加载配置文件"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"⚠️ 无法加载配置文件: {e}")
            return {}
    
    def _init_agents(self) -> Dict:
        """初始化所有Agent"""
        agent_config = self.config.get("agents", {})
        
        return {
            "data": DataCollectionAgent(agent_config.get("data_collector", {})),
            "technical": TechnicalAnalysisAgent(agent_config.get("technical_analyst", {})),
            "capital": CapitalAnalysisAgent(agent_config.get("capital_analyst", {})),
            "intelligence": IntelligenceAgent(agent_config.get("intelligence_analyst", {})),
            "sector": SectorAnalysisAgent(agent_config.get("sector_analyst", {})),
            "bull": BullAnalystAgent(agent_config.get("bull_analyst", {})),
            "bear": BearAnalystAgent(agent_config.get("bear_analyst", {})),
            "retail_sentiment": RetailSentimentAgent(agent_config.get("retail_sentiment", {})),
            "chief": ChiefAnalystAgent(agent_config.get("chief_analyst", {}))
        }
    
    async def analyze_stock(self, symbol: str, name: str = "") -> Dict[str, Any]:
        """
        分析单只股票
        
        Args:
            symbol: 股票代码 (如: 600519)
            name: 股票名称 (如: 贵州茅台)
            
        Returns:
            分析结果字典
        """
        print(f"\n🐸 祖蛙开始分析: {symbol} {name}")
        print("=" * 50)
        
        # Step 1: 数据收集
        print("\n📊 Step 1: 数据收集...")
        data_result = await self.agents["data"].analyze(symbol, {"name": name})
        context = data_result.details
        context["symbol"] = symbol
        context["name"] = name
        
        # Step 2: 并行执行各分析Agent
        print("\n🔍 Step 2: 并行分析...")
        
        tasks = [
            ("technical", self.agents["technical"].analyze(symbol, context)),
            ("capital", self.agents["capital"].analyze(symbol, context)),
            ("intelligence", self.agents["intelligence"].analyze(symbol, context)),
            ("sector", self.agents["sector"].analyze(symbol, context)),
            ("retail_sentiment", self.agents["retail_sentiment"].analyze(symbol, context)),
        ]
        
        agent_outputs = {}
        for key, task in tasks:
            result = await task
            agent_outputs[key] = result
            context[f"{key}_analysis"] = result.details
            print(f"  ✅ {result.agent_name}: {result.summary[:50]}...")
        
        # Step 3: 多空辩论
        print("\n🐂🐻 Step 3: 多空辩论...")
        
        bull_task = self.agents["bull"].analyze(symbol, context)
        bear_task = self.agents["bear"].analyze(symbol, context)
        
        bull_result, bear_result = await asyncio.gather(bull_task, bear_task)
        
        agent_outputs["bull"] = bull_result
        agent_outputs["bear"] = bear_result
        
        print(f"  🐂 多头: {bull_result.summary[:50]}...")
        print(f"  🐻 空头: {bear_result.summary[:50]}...")
        
        # Step 4: 首席决策
        print("\n🧠 Step 4: 首席分析师综合决策...")
        
        final_decision = await self.agents["chief"].make_decision(
            symbol, name, agent_outputs
        )
        
        print("\n" + "=" * 50)
        print(f"📈 最终结论: {final_decision.summary}")
        print("=" * 50)
        
        return {
            "symbol": symbol,
            "name": name,
            "timestamp": datetime.now().isoformat(),
            "final_decision": final_decision.to_dict(),
            "agent_outputs": {k: v.to_dict() for k, v in agent_outputs.items()}
        }
    
    def print_report(self, result: Dict[str, Any]):
        """打印分析报告"""
        print("\n" + "=" * 60)
        print(f"🐸 祖蛙分析报告")
        print("=" * 60)
        
        symbol = result["symbol"]
        name = result["name"]
        decision = result["final_decision"]
        
        print(f"\n股票: {symbol} {name}")
        print(f"时间: {result['timestamp']}")
        
        print(f"\n【综合评级】{decision['details']['rating']}")
        print(f"【综合评分】{decision['details']['composite_score']:.1f}/100")
        print(f"【投资信号】{decision['signal']}")
        print(f"【置信度】{decision['confidence']:.1f}%")
        
        rec = decision['details']['recommendation']
        print(f"\n【仓位建议】{rec['position']}")
        if rec.get('target_price'):
            print(f"【目标价位】{rec['target_price']}")
        if rec.get('stop_loss'):
            print(f"【止损价位】{rec['stop_loss']}")
        
        print(f"\n【决策理由】")
        print(decision['details']['reasoning'])
        
        print("\n【各Agent评分】")
        for agent, score in decision['details']['individual_scores'].items():
            bar = "█" * int(score / 5) + "░" * (20 - int(score / 5))
            print(f"  {agent:15s} {bar} {score:5.1f}")
        
        print("\n" + "=" * 60)
        print("⚠️ 免责声明: 本分析仅供参考，不构成投资建议")
        print("=" * 60)
    
    def print_detailed_report(self, result: Dict[str, Any]):
        """打印详细分析报告"""
        import json
        
        # 先打印基础报告
        self.print_report(result)
        
        print("\n\n" + "=" * 80)
        print("📊 各Agent详细分析数据")
        print("=" * 80)
        
        agent_outputs = result.get("agent_outputs", {})
        
        # 1. 数据Agent
        if "data" in agent_outputs:
            print("\n📈 【数据Agent - 原始数据】")
            data = agent_outputs["data"]
            details = data.get("details", {})
            price = details.get("price_data", {})
            print(f"  当前价格: {price.get('current', 'N/A')}")
            print(f"  开盘价: {price.get('open', 'N/A')}")
            print(f"  最高价: {price.get('high', 'N/A')}")
            print(f"  最低价: {price.get('low', 'N/A')}")
            print(f"  涨跌幅: {price.get('change_pct', 'N/A')}%")
            print(f"  成交量: {price.get('volume', 'N/A')}")
            print(f"  换手率: {price.get('turnover_rate', 'N/A')}%")
            
            basic = details.get("basic_info", {})
            print(f"  行业: {basic.get('industry', 'N/A')}")
            print(f"  市值: {basic.get('market_cap', 'N/A')}")
            print(f"  市盈率: {basic.get('pe_ttm', 'N/A')}")
            print(f"  市净率: {basic.get('pb', 'N/A')}")
        
        # 2. 技术Agent
        if "technical" in agent_outputs:
            print("\n📉 【技术Agent - 技术指标】")
            tech = agent_outputs["technical"]
            details = tech.get("details", {})
            
            trend = details.get("trend", {})
            print(f"  短期趋势: {trend.get('short_term', 'N/A')}")
            print(f"  中期趋势: {trend.get('mid_term', 'N/A')}")
            print(f"  长期趋势: {trend.get('long_term', 'N/A')}")
            print(f"  均线排列: {trend.get('ma_alignment', 'N/A')}")
            
            momentum = details.get("momentum", {})
            print(f"  RSI: {momentum.get('rsi', 'N/A'):.2f} ({momentum.get('rsi_signal', 'N/A')})")
            print(f"  MACD: {momentum.get('macd_signal', 'N/A')}")
            
            sr = details.get("support_resistance", {})
            print(f"  支撑位: {sr.get('support', 'N/A')}")
            print(f"  压力位: {sr.get('resistance', 'N/A')}")
            print(f"  当前位置: {sr.get('position', 'N/A'):.1%}")
            
            patterns = details.get("patterns", [])
            if patterns:
                print(f"  识别形态: {', '.join(patterns)}")
        
        # 3. 资金Agent
        if "capital" in agent_outputs:
            print("\n💰 【资金Agent - 资金流向】")
            capital = agent_outputs["capital"]
            details = capital.get("details", {})
            
            main = details.get("main_force", {})
            print(f"  主力资金净流入: {main.get('net_flow', 'N/A')} 万")
            print(f"  主力流入: {main.get('large_inflow', 'N/A')} 万")
            print(f"  主力流出: {main.get('large_outflow', 'N/A')} 万")
            print(f"  5日净流入: {main.get('flow_5d', 'N/A')} 万")
            
            north = details.get("north_bound", {})
            print(f"  北向资金今日: {north.get('net_today', 'N/A')} 万")
            print(f"  北向持股比例: {north.get('holding_ratio', 'N/A')}%")
            
            dragon = details.get("dragon_tiger", {})
            print(f"  龙虎榜: {'是' if dragon.get('in_list') else '否'}")
            if dragon.get("in_list"):
                print(f"    净买卖额: {dragon.get('net_amount', 'N/A')} 万")
            
            margin = details.get("margin", {})
            print(f"  融资余额: {margin.get('margin_balance', 'N/A')} 万")
        
        # 4. 情报Agent
        if "intelligence" in agent_outputs:
            print("\n📰 【情报Agent - 新闻舆情】")
            intel = agent_outputs["intelligence"]
            details = intel.get("details", {})
            
            sentiment = details.get("sentiment", {})
            print(f"  舆情情感: {sentiment.get('overall', 'N/A')}")
            print(f"  正面比例: {sentiment.get('positive_ratio', 'N/A'):.0%}")
            print(f"  新闻数量: {sentiment.get('news_count', 'N/A')} 条")
            
            risks = sentiment.get("risk_events", [])
            if risks:
                print(f"  ⚠️ 风险事件:")
                for risk in risks:
                    print(f"    - {risk}")
            
            news = details.get("news", [])
            if news:
                print(f"\n  最新新闻:")
                for i, item in enumerate(news[:3], 1):
                    print(f"    {i}. {item.get('title', 'N/A')[:50]}...")
        
        # 5. 多头Agent
        if "bull" in agent_outputs:
            print("\n🐂 【多头Agent - 看涨理由】")
            bull = agent_outputs["bull"]
            details = bull.get("details", {})
            
            cases = details.get("bullish_cases", [])
            print(f"  发现 {len(cases)} 个看涨因素:")
            for case in cases:
                print(f"    ✓ [{case.get('type', 'N/A')}] {case.get('factor', 'N/A')}")
                print(f"      {case.get('description', '')}")
            
            print(f"  目标价位: {details.get('target_price', 'N/A')}")
            print(f"  看多信心度: {bull.get('confidence', 'N/A')}%")
        
        # 6. 空头Agent
        if "bear" in agent_outputs:
            print("\n🐻 【空头Agent - 看空理由】")
            bear = agent_outputs["bear"]
            details = bear.get("details", {})
            
            cases = details.get("bearish_cases", [])
            print(f"  发现 {len(cases)} 个看空因素:")
            for case in cases:
                print(f"    ✗ [{case.get('type', 'N/A')}] {case.get('factor', 'N/A')}")
                print(f"      {case.get('description', '')}")
            
            print(f"  风险价位: {details.get('risk_price', 'N/A')}")
            print(f"  看空信心度: {bear.get('confidence', 'N/A')}%")
        
        # 7. 散户情绪Agent
        if "retail_sentiment" in agent_outputs:
            print("\n👥 【散户情绪Agent - 情绪指标】")
            retail = agent_outputs["retail_sentiment"]
            details = retail.get("details", {})
            print(f"  情绪指数: {details.get('sentiment_index', 'N/A')}/100")
            print(f"  情绪状态: {details.get('sentiment_label', 'N/A')}")
        
        print("\n" + "=" * 80)


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="祖蛙沪深A股分析系统")
    parser.add_argument("--symbol", required=True, help="股票代码 (如: 600519)")
    parser.add_argument("--name", default="", help="股票名称 (如: 贵州茅台)")
    parser.add_argument("--config", default="config/agents.yaml", help="配置文件路径")
    parser.add_argument("--detailed", action="store_true", help="显示详细分析数据")
    parser.add_argument("--output", "-o", help="输出结果到JSON文件")
    
    args = parser.parse_args()
    
    # 初始化分析器
    analyzer = ZuwaStockAnalyzer(args.config)
    
    # 执行分析
    result = await analyzer.analyze_stock(args.symbol, args.name)
    
    # 打印报告
    if args.detailed:
        analyzer.print_detailed_report(result)
    else:
        analyzer.print_report(result)
    
    # 保存到文件
    if args.output:
        import json
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n📁 分析结果已保存到: {args.output}")
    
    return result


if __name__ == "__main__":
    result = asyncio.run(main())
