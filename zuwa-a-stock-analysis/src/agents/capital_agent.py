"""
资金分析Agent - 监控主力资金、北向资金、龙虎榜
"""
from typing import Dict, Any
from datetime import datetime
from src.agents.base import BaseAgent, AgentOutput


class CapitalAnalysisAgent(BaseAgent):
    """资金分析Agent - A股特色"""
    
    def __init__(self, config: Dict = None):
        super().__init__("资金分析师", config)
    
    async def analyze(self, symbol: str, context: Dict[str, Any]) -> AgentOutput:
        """分析资金流向"""
        self.log(f"开始资金分析: {symbol}")
        
        # 这里会接入真实数据源
        analysis = {
            "main_force": self._analyze_main_force(symbol),
            "north_bound": self._analyze_north_bound(symbol),
            "dragon_tiger": self._analyze_dragon_tiger(symbol),
            "margin": self._analyze_margin(symbol),
        }
        
        # 综合评分
        score = self._calculate_score(analysis)
        signal = self._format_signal(score)
        
        return AgentOutput(
            agent_name=self.name,
            signal=signal,
            confidence=abs(score - 50) * 2,
            summary=self._generate_summary(analysis),
            details=analysis,
            timestamp=datetime.now()
        )
    
    def _analyze_main_force(self, symbol: str) -> Dict:
        """分析主力资金"""
        # 大单/超大单资金流向
        return {
            "large_inflow": 0,      # 大单流入(万元)
            "large_outflow": 0,     # 大单流出(万元)
            "net_flow": 0,          # 净流入(万元)
            "flow_5d": 0,           # 5日净流入
            "flow_20d": 0,          # 20日净流入
            "signal": "中性"
        }
    
    def _analyze_north_bound(self, symbol: str) -> Dict:
        """分析北向资金(沪股通/深股通)"""
        return {
            "today_buy": 0,         # 今日买入(万元)
            "today_sell": 0,        # 今日卖出(万元)
            "net_today": 0,         # 今日净买入
            "net_5d": 0,            # 5日净买入
            "holding_ratio": 0,     # 北向持股比例
            "signal": "中性"
        }
    
    def _analyze_dragon_tiger(self, symbol: str) -> Dict:
        """分析龙虎榜 - 游资动向"""
        return {
            "in_list": False,       # 是否上榜
            "list_date": None,      # 上榜日期
            "buy_seats": [],        # 买入席位
            "sell_seats": [],       # 卖出席位
            "net_amount": 0,        # 净买卖额
            "famous_salons": [],    # 知名游资
            "signal": "中性"
        }
    
    def _analyze_margin(self, symbol: str) -> Dict:
        """分析融资融券"""
        return {
            "margin_balance": 0,    # 融资余额
            "short_balance": 0,     # 融券余额
            "margin_change": 0,     # 融资余额变化
            "leverage_ratio": 0,    # 杠杆比例
            "signal": "中性"
        }
    
    def _calculate_score(self, analysis: Dict) -> float:
        """计算资金评分"""
        score = 50
        
        # 主力资金
        main = analysis["main_force"]
        if main["net_flow"] > 1000:  # 大幅流入
            score += 20
        elif main["net_flow"] < -1000:  # 大幅流出
            score -= 20
        
        # 北向资金
        north = analysis["north_bound"]
        if north["net_5d"] > 500:
            score += 15
        elif north["net_5d"] < -500:
            score -= 15
        
        # 龙虎榜
        dragon = analysis["dragon_tiger"]
        if dragon["in_list"] and dragon["net_amount"] > 0:
            score += 10
        
        return max(0, min(100, score))
    
    def _generate_summary(self, analysis: Dict) -> str:
        """生成摘要"""
        main = analysis["main_force"]
        north = analysis["north_bound"]
        
        parts = []
        if main["net_flow"] != 0:
            parts.append(f"主力: {'流入' if main['net_flow'] > 0 else '流出'} {abs(main['net_flow'])}万")
        if north["net_today"] != 0:
            parts.append(f"北向: {'买入' if north['net_today'] > 0 else '卖出'} {abs(north['net_today'])}万")
        
        return " | ".join(parts) if parts else "资金流向中性"
