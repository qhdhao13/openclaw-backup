"""
空头分析Agent - 寻找风险隐患的谨慎派
"""
from typing import Dict, Any, List
from datetime import datetime
from src.agents.base import BaseAgent, AgentOutput


class BearAnalystAgent(BaseAgent):
    """
    空头分析师 Agent
    性格：谨慎、风险厌恶、严格止损
    口头禅："保住本金第一"
    """
    
    def __init__(self, config: Dict = None):
        super().__init__("空头分析师", config)
        self.personality = {
            "caution": config.get("caution", 0.9),
            "risk_aversion": config.get("risk_aversion", "高"),
            "stop_loss": config.get("stop_loss", "严格")
        }
    
    async def analyze(self, symbol: str, context: Dict[str, Any]) -> AgentOutput:
        """寻找看空理由"""
        self.log(f"🐻 空头视角分析: {symbol}")
        
        # 收集所有看空逻辑
        bearish_cases = []
        
        # 1. 技术面看空逻辑
        tech_bear = self._analyze_technical_bearish(context)
        if tech_bear:
            bearish_cases.extend(tech_bear)
        
        # 2. 资金面看空逻辑
        capital_bear = self._analyze_capital_bearish(context)
        if capital_bear:
            bearish_cases.extend(capital_bear)
        
        # 3. 基本面看空逻辑
        fundamental_bear = self._analyze_fundamental_bearish(context)
        if fundamental_bear:
            bearish_cases.extend(fundamental_bear)
        
        # 4. 风险警示
        risks = self._analyze_risks(context)
        if risks:
            bearish_cases.extend(risks)
        
        # 计算看空信心度
        confidence = self._calculate_bearish_confidence(bearish_cases, context)
        
        # 生成风险位
        risk_price = self._estimate_risk_price(context, confidence)
        
        return AgentOutput(
            agent_name=self.name,
            signal="BEARISH",
            confidence=confidence,
            summary=self._generate_summary(bearish_cases, risk_price),
            details={
                "bearish_cases": bearish_cases,
                "risk_price": risk_price,
                "personality": self.personality,
                "reasoning": "基于技术面风险、资金流出、基本面恶化等多维度分析"
            },
            timestamp=datetime.now()
        )
    
    def _analyze_technical_bearish(self, context: Dict) -> List[Dict]:
        """技术面看空逻辑"""
        cases = []
        
        tech = context.get("technical_analysis", {})
        
        # 趋势向下
        trend = tech.get("trend", {})
        if trend.get("short_term") == "DOWN":
            cases.append({
                "type": "技术面",
                "factor": "短期趋势向下",
                "weight": 0.15,
                "description": "股价跌破短期均线，动能转弱"
            })
        
        if trend.get("ma_alignment") == "空头排列":
            cases.append({
                "type": "技术面",
                "factor": "均线空头排列",
                "weight": 0.20,
                "description": "5日<10日<20日<60日，下跌趋势确立"
            })
        
        # 动量指标
        momentum = tech.get("momentum", {})
        if momentum.get("rsi_signal") == "超买":
            cases.append({
                "type": "技术面",
                "factor": "RSI超买回调",
                "weight": 0.15,
                "description": f"RSI={momentum.get('rsi', 0):.1f}，技术性回调风险"
            })
        
        if momentum.get("macd_signal") == "死叉":
            cases.append({
                "type": "技术面",
                "factor": "MACD死叉",
                "weight": 0.15,
                "description": "DIF下穿DEA，卖出信号"
            })
        
        # 支撑压力
        sr = tech.get("support_resistance", {})
        position = sr.get("position", 0.5)
        if position > 0.9:
            cases.append({
                "type": "技术面",
                "factor": "接近压力位",
                "weight": 0.15,
                "description": f"接近压力位{sr.get('resistance')}，回调风险大"
            })
        
        return cases
    
    def _analyze_capital_bearish(self, context: Dict) -> List[Dict]:
        """资金面看空逻辑"""
        cases = []
        
        capital = context.get("capital_analysis", {})
        
        # 主力资金
        main = capital.get("main_force", {})
        if (main.get("net_flow") or 0) < -5000:
            cases.append({
                "type": "资金面",
                "factor": "主力资金大幅流出",
                "weight": 0.25,
                "description": f"主力净流出{abs(main['net_flow'])}万，机构减持"
            })
        
        if (main.get("flow_5d") or 0) < -10000:
            cases.append({
                "type": "资金面",
                "factor": "5日持续流出",
                "weight": 0.20,
                "description": "短期资金持续撤离"
            })
        
        # 北向资金
        north = capital.get("north_bound", {})
        if (north.get("net_5d") or 0) < -1000:
            cases.append({
                "type": "资金面",
                "factor": "北向资金减持",
                "weight": 0.20,
                "description": "聪明钱持续卖出，外资看空"
            })
        
        # 龙虎榜
        dragon = capital.get("dragon_tiger", {})
        if dragon.get("in_list") and (dragon.get("net_amount") or 0) < 0:
            cases.append({
                "type": "资金面",
                "factor": "龙虎榜游资出货",
                "weight": 0.20,
                "description": "游资席位大卖，短期承压"
            })
        
        return cases
    
    def _analyze_fundamental_bearish(self, context: Dict) -> List[Dict]:
        """基本面看空逻辑"""
        cases = []
        
        basic = context.get("basic_info", {})
        
        pe = basic.get("pe_ttm", 0)
        if pe > 50:
            cases.append({
                "type": "基本面",
                "factor": "估值过高",
                "weight": 0.20,
                "description": f"PE={pe}，高于历史均值，存在估值回归风险"
            })
        
        roe = basic.get("roe", 0)
        if 0 < roe < 5:
            cases.append({
                "type": "基本面",
                "factor": "盈利能力弱",
                "weight": 0.15,
                "description": f"ROE={roe}%，盈利能力较差"
            })
        
        return cases
    
    def _analyze_risks(self, context: Dict) -> List[Dict]:
        """风险警示"""
        cases = []
        
        intel = context.get("intelligence_analysis", {})
        
        policy = intel.get("policy", {})
        if policy.get("impact_level") == "利空":
            cases.append({
                "type": "风险",
                "factor": "政策风险",
                "weight": 0.25,
                "description": "行业政策不利"
            })
        
        sentiment = intel.get("sentiment", {})
        risk_events = sentiment.get("risk_events", [])
        for event in risk_events:
            cases.append({
                "type": "风险",
                "factor": event.get("type", "事件风险"),
                "weight": event.get("severity", 0.2),
                "description": event.get("description", "")
            })
        
        return cases
    
    def _calculate_bearish_confidence(self, cases: List[Dict], context: Dict) -> float:
        """计算看空信心度"""
        if not cases:
            return 30  # 无看空理由，低信心
        
        total_weight = sum(case["weight"] for case in cases)
        
        # 根据权重计算基础信心度
        base_confidence = min(85, 40 + total_weight * 100)
        
        # 性格加成：谨慎派 +10%
        base_confidence += 10
        
        return min(95, base_confidence)
    
    def _estimate_risk_price(self, context: Dict, confidence: float) -> float:
        """估算风险位/止损位"""
        price_data = context.get("price_data", {})
        current = price_data.get("current", 0)
        
        # 根据信心度估算下跌风险
        if confidence >= 80:
            downside = 0.20  # 20%下跌风险
        elif confidence >= 60:
            downside = 0.12
        else:
            downside = 0.05
        
        return round(current * (1 - downside), 2)
    
    def _generate_summary(self, cases: List[Dict], risk_price: float) -> str:
        """生成摘要"""
        if not cases:
            return "暂未发现明显看空逻辑"
        
        # 取权重最高的3个理由
        top_cases = sorted(cases, key=lambda x: x["weight"], reverse=True)[:3]
        
        reasons = [f"{c['factor']}(-{int(c['weight']*100)}%)" for c in top_cases]
        
        return f"看空理由: {' | '.join(reasons)} | 风险位: {risk_price}"
