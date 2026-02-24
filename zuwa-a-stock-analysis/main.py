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


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="祖蛙沪深A股分析系统")
    parser.add_argument("--symbol", required=True, help="股票代码 (如: 600519)")
    parser.add_argument("--name", default="", help="股票名称 (如: 贵州茅台)")
    parser.add_argument("--config", default="config/agents.yaml", help="配置文件路径")
    
    args = parser.parse_args()
    
    # 初始化分析器
    analyzer = ZuwaStockAnalyzer(args.config)
    
    # 执行分析
    result = await analyzer.analyze_stock(args.symbol, args.name)
    
    # 打印报告
    analyzer.print_report(result)
    
    return result


if __name__ == "__main__":
    result = asyncio.run(main())
