"""
首席分析师Agent - 决策中枢，综合所有分析生成最终建议
"""
from typing import Dict, Any, List
from datetime import datetime
import asyncio
from src.agents.base import BaseAgent, AgentOutput


class ChiefAnalystAgent(BaseAgent):
    """
    首席分析师 Agent
    职责：
    1. 协调各Agent并行工作
    2. 收集整理各Agent分析结果
    3. 加权计算综合评分
    4. 生成最终投资建议
    """
    
    def __init__(self, config: Dict = None):
        super().__init__("首席分析师", config)
        self.weights = config.get("weights", {
            "technical": 0.20,
            "capital": 0.25,
            "intelligence": 0.20,
            "sector": 0.15,
            "bull_view": 0.10,
            "bear_view": 0.10
        })
        self.thresholds = config.get("thresholds", {
            "strong_buy": 80,
            "buy": 60,
            "hold": 40,
            "sell": 20
        })
    
    async def analyze(self, symbol: str, context: Dict[str, Any]) -> AgentOutput:
        """
        实现抽象方法 - 首席分析师的直接分析
        实际使用时应该调用make_decision
        """
        # 从context中提取其他Agent的输出结果
        agent_outputs = context.get("agent_outputs", {})
        name = context.get("name", "")
        
        if agent_outputs:
            return await self.make_decision(symbol, name, agent_outputs)
        else:
            # 如果没有其他Agent的输出，返回中性结果
            return AgentOutput(
                agent_name=self.name,
                signal="NEUTRAL",
                confidence=50.0,
                summary="缺少其他Agent分析数据，无法做出决策",
                details={},
                timestamp=datetime.now()
            )
    
    async def make_decision(
        self, 
        symbol: str, 
        name: str,
        agent_outputs: Dict[str, AgentOutput]
    ) -> AgentOutput:
        """
        综合所有Agent输出，做出最终决策
        
        Args:
            symbol: 股票代码
            name: 股票名称
            agent_outputs: 各Agent的输出结果
            
        Returns:
            AgentOutput: 最终投资建议
        """
        self.log(f"🧠 首席分析师综合决策: {symbol} {name}")
        
        # 1. 提取各Agent评分
        scores = self._extract_scores(agent_outputs)
        
        # 2. 加权计算综合评分
        composite_score = self._calculate_composite_score(scores)
        
        # 3. 生成投资评级
        rating = self._determine_rating(composite_score)
        
        # 4. 生成投资理由
        reasoning = self._generate_reasoning(agent_outputs, scores)
        
        # 5. 给出具体建议
        recommendation = self._generate_recommendation(
            rating, composite_score, agent_outputs
        )
        
        return AgentOutput(
            agent_name=self.name,
            signal=rating["signal"],
            confidence=rating["confidence"],
            summary=recommendation["summary"],
            details={
                "composite_score": composite_score,
                "rating": rating["label"],
                "individual_scores": scores,
                "recommendation": recommendation,
                "reasoning": reasoning,
                "agent_outputs": {k: v.to_dict() for k, v in agent_outputs.items()}
            },
            timestamp=datetime.now()
        )
    
    def _extract_scores(self, outputs: Dict[str, AgentOutput]) -> Dict[str, float]:
        """提取各Agent的评分"""
        scores = {}
        
        # 基础分析Agent
        if "technical" in outputs:
            tech = outputs["technical"]
            scores["technical"] = self._signal_to_score(tech.signal, tech.confidence)
        
        if "capital" in outputs:
            cap = outputs["capital"]
            scores["capital"] = self._signal_to_score(cap.signal, cap.confidence)
        
        if "intelligence" in outputs:
            intel = outputs["intelligence"]
            scores["intelligence"] = self._signal_to_score(intel.signal, intel.confidence)
        
        if "sector" in outputs:
            sec = outputs["sector"]
            scores["sector"] = self._signal_to_score(sec.signal, sec.confidence)
        
        # 多空辩论Agent
        if "bull" in outputs:
            bull = outputs["bull"]
            scores["bull_view"] = bull.confidence  # 多头信心度直接作为看多分数
        
        if "bear" in outputs:
            bear = outputs["bear"]
            scores["bear_view"] = 100 - bear.confidence  # 空头信心度反向作为分数
        
        # 散户情绪（反向指标）
        if "retail_sentiment" in outputs:
            retail = outputs["retail_sentiment"]
            # 散户看多→我们看空，散户看空→我们看多
            if retail.signal == "BULLISH":
                scores["retail_sentiment"] = 70  # 散户恐慌，我们看多
            elif retail.signal == "BEARISH":
                scores["retail_sentiment"] = 30  # 散户贪婪，我们看跌
            else:
                scores["retail_sentiment"] = 50
        
        return scores
    
    def _signal_to_score(self, signal: str, confidence: float) -> float:
        """将信号转换为分数"""
        base = 50
        
        if signal == "BULLISH":
            return base + confidence / 2
        elif signal == "BEARISH":
            return base - confidence / 2
        else:
            return base
    
    def _calculate_composite_score(self, scores: Dict[str, float]) -> float:
        """计算加权综合评分"""
        total_weight = 0
        weighted_sum = 0
        
        for key, weight in self.weights.items():
            if key in scores:
                weighted_sum += scores[key] * weight
                total_weight += weight
        
        # 散户情绪权重较小
        if "retail_sentiment" in scores:
            weighted_sum += scores["retail_sentiment"] * 0.05
            total_weight += 0.05
        
        if total_weight == 0:
            return 50
        
        return weighted_sum / total_weight
    
    def _determine_rating(self, score: float) -> Dict:
        """根据评分确定投资评级"""
        if score >= self.thresholds["strong_buy"]:
            return {
                "label": "强烈推荐",
                "signal": "STRONG_BUY",
                "confidence": score
            }
        elif score >= self.thresholds["buy"]:
            return {
                "label": "推荐买入",
                "signal": "BUY",
                "confidence": score
            }
        elif score >= self.thresholds["hold"]:
            return {
                "label": "中性持有",
                "signal": "HOLD",
                "confidence": 100 - abs(score - 50) * 2
            }
        elif score >= self.thresholds["sell"]:
            return {
                "label": "建议卖出",
                "signal": "SELL",
                "confidence": 100 - score
            }
        else:
            return {
                "label": "强烈卖出",
                "signal": "STRONG_SELL",
                "confidence": 100 - score
            }
    
    def _generate_reasoning(
        self, 
        outputs: Dict[str, AgentOutput], 
        scores: Dict[str, float]
    ) -> str:
        """生成投资决策理由"""
        reasons = []
        
        # 找出最强的看多和看空理由
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        top_bull = sorted_scores[0] if sorted_scores[0][1] > 55 else None
        top_bear = sorted_scores[-1] if sorted_scores[-1][1] < 45 else None
        
        if top_bull:
            agent_name = self._get_agent_display_name(top_bull[0])
            reasons.append(f"看多因素: {agent_name}评分较高({top_bull[1]:.0f})")
        
        if top_bear:
            agent_name = self._get_agent_display_name(top_bear[0])
            reasons.append(f"看空因素: {agent_name}评分较低({top_bear[1]:.0f})")
        
        # 多空Agent的辩论
        if "bull" in outputs and "bear" in outputs:
            bull_conf = outputs["bull"].confidence
            bear_conf = outputs["bear"].confidence
            
            if bull_conf > bear_conf + 20:
                reasons.append(f"多头观点占优(信心度{bull_conf:.0f}% vs {bear_conf:.0f}%)")
            elif bear_conf > bull_conf + 20:
                reasons.append(f"空头观点占优(信心度{bear_conf:.0f}% vs {bull_conf:.0f}%)")
            else:
                reasons.append("多空观点分歧较大，需保持谨慎")
        
        return "; ".join(reasons)
    
    def _generate_recommendation(
        self, 
        rating: Dict, 
        score: float,
        outputs: Dict[str, AgentOutput]
    ) -> Dict:
        """生成具体投资建议"""
        
        # 仓位建议
        if rating["signal"] == "STRONG_BUY":
            position = "50-70%"
        elif rating["signal"] == "BUY":
            position = "30-50%"
        elif rating["signal"] == "HOLD":
            position = "持有现有仓位"
        elif rating["signal"] == "SELL":
            position = "减仓至10%以下"
        else:
            position = "清仓观望"
        
        # 提取目标价和风险位
        target_price = None
        risk_price = None
        
        if "bull" in outputs:
            details = outputs["bull"].details
            target_price = details.get("target_price")
        
        if "bear" in outputs:
            details = outputs["bear"].details
            risk_price = details.get("risk_price")
        
        summary = f"【{rating['label']}】综合评分{score:.0f}/100 | 建议仓位: {position}"
        
        if target_price:
            summary += f" | 目标价: {target_price}"
        if risk_price:
            summary += f" | 止损位: {risk_price}"
        
        return {
            "position": position,
            "target_price": target_price,
            "stop_loss": risk_price,
            "summary": summary
        }
    
    def _get_agent_display_name(self, key: str) -> str:
        """获取Agent显示名称"""
        names = {
            "technical": "技术面",
            "capital": "资金面",
            "intelligence": "消息面",
            "sector": "行业面",
            "bull_view": "多头观点",
            "bear_view": "空头观点",
            "retail_sentiment": "散户情绪"
        }
        return names.get(key, key)
