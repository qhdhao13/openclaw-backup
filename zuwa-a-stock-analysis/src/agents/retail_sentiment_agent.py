"""
散户情绪Agent - 监控散户情绪，提供反向指标
"""
from typing import Dict, Any
from datetime import datetime
from src.agents.base import BaseAgent, AgentOutput


class RetailSentimentAgent(BaseAgent):
    """
    散户情绪分析师 Agent
    核心理念：散户是反向指标
    - 极度贪婪时 → 顶部信号 → 看空
    - 极度恐慌时 → 底部信号 → 看多
    """
    
    def __init__(self, config: Dict = None):
        super().__init__("散户情绪分析师", config)
        self.thresholds = {
            "extreme_greed": config.get("sentiment_extreme_greed", 85),
            "greed": config.get("sentiment_greed", 70),
            "fear": config.get("sentiment_fear", 30),
            "extreme_fear": config.get("sentiment_extreme_fear", 15)
        }
    
    async def analyze(self, symbol: str, context: Dict[str, Any]) -> AgentOutput:
        """分析散户情绪"""
        self.log(f"👥 分析散户情绪: {symbol}")
        
        # 收集情绪指标
        sentiment_data = {
            "margin_balance": self._get_margin_balance(symbol),
            "new_accounts": self._get_new_accounts(),
            "search_index": self._get_search_index(symbol),
            "forum_sentiment": self._get_forum_sentiment(symbol),
            "fund_flow": self._get_retail_fund_flow()
        }
        
        # 计算综合情绪指数
        sentiment_index = self._calculate_sentiment_index(sentiment_data)
        
        # 根据情绪指数判断信号（反向指标）
        signal, confidence, recommendation = self._interpret_sentiment(sentiment_index)
        
        return AgentOutput(
            agent_name=self.name,
            signal=signal,
            confidence=confidence,
            summary=self._generate_summary(sentiment_index, recommendation),
            details={
                "sentiment_index": sentiment_index,
                "raw_data": sentiment_data,
                "interpretation": recommendation,
                "thresholds": self.thresholds,
                "reasoning": "散户情绪是反向指标，极度贪婪时看空，极度恐慌时看多"
            },
            timestamp=datetime.now()
        )
    
    def _get_margin_balance(self, symbol: str) -> Dict:
        """融资余额 - 散户加杠杆程度"""
        return {
            "current": 0,           # 当前融资余额
            "change_5d": 0,         # 5日变化
            "change_20d": 0,        # 20日变化
            "leverage_ratio": 0     # 融资买入占比
        }
    
    def _get_new_accounts(self) -> Dict:
        """新增开户数 - 散户入场热情"""
        return {
            "weekly": 0,            # 本周新增
            "monthly": 0,           # 本月新增
            "yoy_change": 0         # 同比变化
        }
    
    def _get_search_index(self, symbol: str) -> Dict:
        """搜索指数 - 散户关注度"""
        return {
            "baidu_index": 0,       # 百度指数
            "wechat_index": 0,      # 微信指数
            "trend": "平稳"          # 趋势
        }
    
    def _get_forum_sentiment(self, symbol: str) -> Dict:
        """论坛情绪 - 散户是贪婪还是恐慌"""
        return {
            "eastmoney_bull_ratio": 0.5,    # 东方财富看多比例
            "xueqiu_bull_ratio": 0.5,        # 雪球看多比例
            "overall_sentiment": "中性",      # 综合情绪
            "hot_keywords": []               # 热词
        }
    
    def _get_retail_fund_flow(self) -> Dict:
        """散户资金流向"""
        return {
            "retail_net_flow": 0,   # 散户净流入
            "small_order_flow": 0,  # 小单流向
            "retail_holdings": 0    # 散户持仓变化
        }
    
    def _calculate_sentiment_index(self, data: Dict) -> float:
        """计算综合情绪指数 (0-100)"""
        score = 50  # 中性起点
        
        # 融资余额权重 30%
        margin = data["margin_balance"]
        if margin.get("change_5d", 0) > 10:
            score += 15
        elif margin.get("change_5d", 0) < -10:
            score -= 15
        
        # 论坛情绪权重 40%
        forum = data["forum_sentiment"]
        bull_ratio = forum.get("eastmoney_bull_ratio", 0.5)
        score += (bull_ratio - 0.5) * 40  # 看多比例越高，情绪指数越高
        
        # 搜索指数权重 20%
        search = data["search_index"]
        if search.get("trend") == "上升":
            score += 10
        elif search.get("trend") == "下降":
            score -= 10
        
        # 散户资金流向权重 10%
        fund = data["fund_flow"]
        if fund.get("retail_net_flow", 0) > 0:
            score += 5
        else:
            score -= 5
        
        return max(0, min(100, score))
    
    def _interpret_sentiment(self, index: float) -> tuple:
        """
        解读情绪指数（反向指标逻辑）
        
        Returns:
            (signal, confidence, recommendation)
        """
        if index >= self.thresholds["extreme_greed"]:
            # 极度贪婪 → 看空（反向）
            return (
                "BEARISH", 
                min(90, index), 
                f"散户极度贪婪({index:.0f})，情绪过热，建议警惕回调风险"
            )
        
        elif index >= self.thresholds["greed"]:
            # 贪婪 → 谨慎看空
            return (
                "BEARISH",
                (index - 50) * 1.5,
                f"散户贪婪({index:.0f})，情绪偏热，保持谨慎"
            )
        
        elif index <= self.thresholds["extreme_fear"]:
            # 极度恐慌 → 看多（反向）
            return (
                "BULLISH",
                min(90, 100 - index),
                f"散户极度恐慌({index:.0f})，情绪冰点，可能接近底部"
            )
        
        elif index <= self.thresholds["fear"]:
            # 恐慌 → 谨慎看多
            return (
                "BULLISH",
                (50 - index) * 1.5,
                f"散户恐慌({index:.0f})，情绪偏冷，关注反弹机会"
            )
        
        else:
            # 中性
            return (
                "NEUTRAL",
                30,
                f"散户情绪中性({index:.0f})，无明确信号"
            )
    
    def _generate_summary(self, index: float, recommendation: str) -> str:
        """生成摘要"""
        # 情绪等级
        if index >= 85:
            level = "极度贪婪🔥"
        elif index >= 70:
            level = "贪婪📈"
        elif index <= 15:
            level = "极度恐慌❄️"
        elif index <= 30:
            level = "恐慌📉"
        else:
            level = "中性😶"
        
        return f"情绪指数: {index:.0f}/100 ({level}) | {recommendation}"
