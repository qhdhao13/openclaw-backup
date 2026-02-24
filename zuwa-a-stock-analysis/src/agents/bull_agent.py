"""
多头分析Agent - 使用LLM进行智能看涨分析
"""
from typing import Dict, Any, List
from datetime import datetime
from src.agents.base import BaseAgent, AgentOutput


class BullAnalystAgent(BaseAgent):
    """
    多头分析师 Agent
    性格：乐观、激进、看长做长
    口头禅："回调就是买入机会"
    """
    
    def __init__(self, config: Dict = None):
        super().__init__("多头分析师", config)
        self.personality = {
            "optimism": config.get("optimism", 0.8),
            "risk_appetite": config.get("risk_appetite", "激进"),
            "holding_period": config.get("holding_period", "中长线")
        }
        self.use_llm = config.get("use_llm", True)
    
    async def analyze(self, symbol: str, context: Dict[str, Any]) -> AgentOutput:
        """寻找看涨理由"""
        self.log(f"🐂 多头视角分析: {symbol}")
        
        try:
            # 收集所有看涨逻辑
            bullish_cases = []
            
            # 1. 技术面看涨逻辑
            tech_bull = self._analyze_technical_bullish(context)
            if tech_bull:
                bullish_cases.extend(tech_bull)
            
            # 2. 资金面看涨逻辑
            capital_bull = self._analyze_capital_bullish(context)
            if capital_bull:
                bullish_cases.extend(capital_bull)
            
            # 3. 基本面看涨逻辑
            fundamental_bull = self._analyze_fundamental_bullish(context)
            if fundamental_bull:
                bullish_cases.extend(fundamental_bull)
            
            # 4. 消息面/催化剂
            catalyst_bull = self._analyze_catalysts(context)
            if catalyst_bull:
                bullish_cases.extend(catalyst_bull)
            
            # 5. LLM深度分析（可选）
            llm_analysis = {}
            if self.use_llm:
                llm_analysis = await self._llm_bullish_analysis(symbol, context, bullish_cases)
            
            # 计算看涨信心度
            confidence = self._calculate_bullish_confidence(bullish_cases, context, llm_analysis)
            
            # 生成目标价
            target_price = self._estimate_target_price(context, confidence)
            
            return AgentOutput(
                agent_name=self.name,
                signal="BULLISH",
                confidence=confidence,
                summary=self._generate_summary(bullish_cases, target_price, llm_analysis),
                details={
                    "bullish_cases": bullish_cases,
                    "target_price": target_price,
                    "personality": self.personality,
                    "llm_analysis": llm_analysis,
                    "reasoning": "基于技术面突破、资金流入、基本面改善等多维度分析"
                },
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.log(f"❌ 多头分析失败: {e}")
            return AgentOutput(
                agent_name=self.name,
                signal="NEUTRAL",
                confidence=30.0,
                summary=f"分析失败: {e}",
                details={},
                timestamp=datetime.now()
            )
    
    async def _llm_bullish_analysis(self, symbol: str, context: Dict, cases: List[Dict]) -> Dict:
        """使用LLM进行深度看涨分析"""
        try:
            from src.utils.llm_helper import get_llm_analyzer
            
            llm = get_llm_analyzer()
            result = await llm.analyze_stock(
                symbol=symbol,
                name=context.get("name", symbol),
                context=context,
                analysis_type="comprehensive"
            )
            
            # 如果是看涨信号，返回分析结果
            if result.get("signal") in ["BUY", "STRONG_BUY"]:
                return {
                    "llm_bullish": True,
                    "llm_confidence": result.get("confidence", 50),
                    "llm_reasoning": result.get("reasoning", ""),
                    "llm_target": result.get("target_price"),
                }
            else:
                return {"llm_bullish": False}
                
        except Exception as e:
            self.log(f"LLM分析失败: {e}")
            return {}
    
    def _analyze_technical_bullish(self, context: Dict) -> List[Dict]:
        """技术面看涨逻辑"""
        cases = []
        
        tech = context.get("technical_analysis", {})
        
        # 趋势向上
        trend = tech.get("trend", {})
        if trend.get("short_term") == "UP":
            cases.append({
                "type": "技术面",
                "factor": "短期趋势向上",
                "weight": 0.15,
                "description": "股价站上短期均线，动能强劲"
            })
        
        if trend.get("ma_alignment") == "多头排列":
            cases.append({
                "type": "技术面",
                "factor": "均线多头排列",
                "weight": 0.20,
                "description": "5日>10日>20日>60日，经典上涨趋势"
            })
        
        # 动量指标
        momentum = tech.get("momentum", {})
        if momentum.get("rsi_signal") == "超卖":
            cases.append({
                "type": "技术面",
                "factor": "RSI超卖反弹",
                "weight": 0.15,
                "description": f"RSI={momentum.get('rsi', 0):.1f}，技术性反弹需求"
            })
        
        if momentum.get("macd_signal") == "金叉":
            cases.append({
                "type": "技术面",
                "factor": "MACD金叉",
                "weight": 0.15,
                "description": "DIF上穿DEA，买入信号"
            })
        
        # 形态
        patterns = tech.get("patterns", [])
        if "涨停" in patterns:
            cases.append({
                "type": "技术面",
                "factor": "涨停突破",
                "weight": 0.25,
                "description": "强势涨停，资金抢筹明显"
            })
        
        return cases
    
    def _analyze_capital_bullish(self, context: Dict) -> List[Dict]:
        """资金面看涨逻辑"""
        cases = []
        
        capital = context.get("capital_analysis", {})
        
        # 主力资金
        main = capital.get("main_force", {})
        net_flow = main.get("net_flow") or 0
        if net_flow > 5000:
            cases.append({
                "type": "资金面",
                "factor": "主力资金大幅流入",
                "weight": 0.25,
                "description": f"主力净流入{net_flow}万，机构建仓"
            })
        
        if (main.get("flow_5d") or 0) > 10000:
            cases.append({
                "type": "资金面",
                "factor": "5日持续流入",
                "weight": 0.20,
                "description": "短期资金持续看好"
            })
        
        # 北向资金
        north = capital.get("north_bound", {})
        if (north.get("net_today") or 0) > 1000:
            cases.append({
                "type": "资金面",
                "factor": "北向资金增持",
                "weight": 0.20,
                "description": "聪明钱持续买入，外资看好"
            })
        
        # 龙虎榜
        dragon = capital.get("dragon_tiger", {})
        if dragon.get("in_list") and (dragon.get("net_amount") or 0) > 0:
            famous = dragon.get("famous_salons", [])
            cases.append({
                "type": "资金面",
                "factor": "龙虎榜游资抢筹",
                "weight": 0.20,
                "description": f"知名游资{famous}介入"
            })
        
        return cases
    
    def _analyze_fundamental_bullish(self, context: Dict) -> List[Dict]:
        """基本面看涨逻辑"""
        cases = []
        
        basic = context.get("basic_info", {})
        
        pe = basic.get("pe_ttm", 0)
        if 0 < pe < 20:
            cases.append({
                "type": "基本面",
                "factor": "估值偏低",
                "weight": 0.15,
                "description": f"PE={pe}，低于历史均值"
            })
        
        roe = basic.get("roe", 0)
        if roe > 15:
            cases.append({
                "type": "基本面",
                "factor": "高ROE",
                "weight": 0.15,
                "description": f"ROE={roe}%，盈利能力强"
            })
        
        return cases
    
    def _analyze_catalysts(self, context: Dict) -> List[Dict]:
        """催化剂分析"""
        cases = []
        
        intel = context.get("intelligence_analysis", {})
        
        policy = intel.get("policy", {})
        if policy.get("impact_level") == "利好":
            cases.append({
                "type": "催化剂",
                "factor": "政策利好",
                "weight": 0.20,
                "description": "行业政策支持"
            })
        
        sentiment = intel.get("sentiment", {})
        if sentiment.get("overall") == "乐观":
            cases.append({
                "type": "催化剂",
                "factor": "市场情绪回暖",
                "weight": 0.15,
                "description": "舆情向好"
            })
        
        return cases
    
    def _calculate_bullish_confidence(self, cases: List[Dict], context: Dict, llm: Dict) -> float:
        """计算看涨信心度"""
        if not cases and not llm.get("llm_bullish"):
            return 30  # 无看涨理由，低信心
        
        total_weight = sum(case["weight"] for case in cases)
        
        # 根据权重计算基础信心度
        base_confidence = min(85, 40 + total_weight * 100)
        
        # 性格加成：乐观派 +10%
        base_confidence += 10
        
        # LLM加成
        if llm.get("llm_bullish"):
            base_confidence += 10
            base_confidence = max(base_confidence, llm.get("llm_confidence", 0))
        
        return min(95, base_confidence)
    
    def _estimate_target_price(self, context: Dict, confidence: float) -> float:
        """估算目标价"""
        price_data = context.get("price_data", {})
        current = price_data.get("current", 0)
        
        if current <= 0:
            return 0
        
        # 根据信心度估算上涨空间
        if confidence >= 80:
            upside = 0.25  # 25%上涨空间
        elif confidence >= 60:
            upside = 0.15
        else:
            upside = 0.08
        
        return round(current * (1 + upside), 2)
    
    def _generate_summary(self, cases: List[Dict], target_price: float, llm: Dict) -> str:
        """生成摘要"""
        if not cases and not llm.get("llm_bullish"):
            return "暂未发现明显看涨逻辑"
        
        # 取权重最高的3个理由
        top_cases = sorted(cases, key=lambda x: x["weight"], reverse=True)[:3]
        
        reasons = [f"{c['factor']}(+{int(c['weight']*100)}%)" for c in top_cases]
        
        summary = f"看涨理由: {' | '.join(reasons)} | 目标价: {target_price}"
        
        if llm.get("llm_bullish"):
            summary += f" | LLM看好({llm.get('llm_confidence', 0):.0f}%)"
        
        return summary
