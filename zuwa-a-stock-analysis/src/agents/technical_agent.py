"""
技术分析Agent - 技术指标计算和形态识别
"""
from typing import Dict, Any, List
from datetime import datetime
import pandas as pd
import numpy as np
from src.agents.base import BaseAgent, AgentOutput


class TechnicalAnalysisAgent(BaseAgent):
    """技术分析Agent"""
    
    def __init__(self, config: Dict = None):
        super().__init__("技术分析师", config)
        self.indicators = config.get("indicators", [
            "sma", "ema", "macd", "rsi", "kdj", "bollinger"
        ])
    
    async def analyze(self, symbol: str, context: Dict[str, Any]) -> AgentOutput:
        """执行技术分析"""
        self.log(f"开始技术分析: {symbol}")
        
        # 从context获取数据
        price_data = context.get("price_data", {})
        daily_data = context.get("daily_data", pd.DataFrame())
        
        if daily_data.empty:
            return AgentOutput(
                agent_name=self.name,
                signal="NEUTRAL",
                confidence=0.0,
                summary="缺少价格数据，无法分析",
                details={},
                timestamp=datetime.now()
            )
        
        # 计算技术指标
        analysis = {
            "trend": self._analyze_trend(daily_data),
            "momentum": self._analyze_momentum(daily_data),
            "support_resistance": self._find_support_resistance(daily_data),
            "patterns": self._detect_patterns(daily_data),
        }
        
        # 综合评分
        score = self._calculate_score(analysis)
        signal = self._format_signal(score)
        
        return AgentOutput(
            agent_name=self.name,
            signal=signal,
            confidence=abs(score - 50) * 2,  # 偏离50越远，置信度越高
            summary=self._generate_summary(analysis, signal),
            details=analysis,
            timestamp=datetime.now()
        )
    
    def _analyze_trend(self, df: pd.DataFrame) -> Dict:
        """分析趋势"""
        # 确保close列存在
        if 'close' not in df.columns:
            # 尝试其他可能的列名
            for col in ['收盘', '收盘价', 'latest', 'current']:
                if col in df.columns:
                    df['close'] = df[col]
                    break
        
        if 'close' not in df.columns or df.empty:
            return {
                "short_term": "UNKNOWN",
                "mid_term": "UNKNOWN",
                "long_term": "UNKNOWN",
                "ma_alignment": "未知"
            }
        
        # 计算均线
        df['sma5'] = df['close'].rolling(5, min_periods=1).mean()
        df['sma10'] = df['close'].rolling(10, min_periods=1).mean()
        df['sma20'] = df['close'].rolling(20, min_periods=1).mean()
        df['sma60'] = df['close'].rolling(60, min_periods=1).mean()
        
        latest = df.iloc[-1]
        
        trend = {
            "short_term": "UP" if latest['close'] > latest['sma5'] else "DOWN",
            "mid_term": "UP" if latest['close'] > latest['sma20'] else "DOWN",
            "long_term": "UP" if latest['close'] > latest['sma60'] else "DOWN",
            "ma_alignment": self._check_ma_alignment(df)
        }
        return trend
    
    def _analyze_momentum(self, df: pd.DataFrame) -> Dict:
        """分析动量指标"""
        if 'close' not in df.columns or len(df) < 14:
            return {
                "rsi": 50.0,
                "rsi_signal": "中性",
                "macd": 0.0,
                "macd_signal": "中性"
            }
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14, min_periods=1).mean()
        rs = gain / (loss + 1e-10)  # 避免除零
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12, min_periods=1).mean()
        exp2 = df['close'].ewm(span=26, min_periods=1).mean()
        df['macd'] = exp1 - exp2
        df['signal'] = df['macd'].ewm(span=9, min_periods=1).mean()
        
        latest = df.iloc[-1]
        
        rsi_val = latest['rsi'] if not pd.isna(latest['rsi']) else 50.0
        macd_val = latest['macd'] if not pd.isna(latest['macd']) else 0.0
        signal_val = latest['signal'] if not pd.isna(latest['signal']) else 0.0
        
        return {
            "rsi": float(rsi_val),
            "rsi_signal": "超买" if rsi_val > 70 else "超卖" if rsi_val < 30 else "中性",
            "macd": float(macd_val),
            "macd_signal": "金叉" if macd_val > signal_val else "死叉" if macd_val < signal_val else "中性"
        }
    
    def _find_support_resistance(self, df: pd.DataFrame) -> Dict:
        """寻找支撑压力位"""
        # 确保必要的列存在
        if 'close' not in df.columns:
            return {"support": 0, "resistance": 0, "current": 0, "position": 0.5}
        
        # 处理low/high列名
        low_col = 'low' if 'low' in df.columns else ('最低' if '最低' in df.columns else 'close')
        high_col = 'high' if 'high' in df.columns else ('最高' if '最高' in df.columns else 'close')
        
        recent = df.tail(20)
        
        support = recent[low_col].min() if low_col in recent.columns else recent['close'].min()
        resistance = recent[high_col].max() if high_col in recent.columns else recent['close'].max()
        current = df['close'].iloc[-1]
        
        position = (current - support) / (resistance - support + 1e-10) if resistance != support else 0.5
        
        return {
            "support": round(float(support), 2),
            "resistance": round(float(resistance), 2),
            "current": round(float(current), 2),
            "position": float(position)
        }
    
    def _detect_patterns(self, df: pd.DataFrame) -> List[str]:
        """识别K线形态"""
        patterns = []
        
        # 检查最近5天
        recent = df.tail(5)
        
        # 涨停检测
        if len(recent) > 0:
            last = recent.iloc[-1]
            if 'pct_change' in last and last['pct_change'] >= 9.9:
                patterns.append("涨停")
        
        # 均线多头排列
        if len(df) > 60:
            latest = df.iloc[-1]
            if latest['sma5'] > latest['sma10'] > latest['sma20'] > latest['sma60']:
                patterns.append("均线多头排列")
        
        return patterns
    
    def _check_ma_alignment(self, df: pd.DataFrame) -> str:
        """检查均线排列"""
        latest = df.iloc[-1]
        if latest['sma5'] > latest['sma10'] > latest['sma20']:
            return "多头排列"
        elif latest['sma5'] < latest['sma10'] < latest['sma20']:
            return "空头排列"
        else:
            return "纠缠"
    
    def _calculate_score(self, analysis: Dict) -> float:
        """计算技术评分 0-100"""
        score = 50  # 中性起点
        
        # 趋势加分
        trend = analysis["trend"]
        if trend["short_term"] == "UP":
            score += 10
        if trend["mid_term"] == "UP":
            score += 10
        if trend["ma_alignment"] == "多头排列":
            score += 10
        
        # 动量调整
        momentum = analysis["momentum"]
        if momentum["rsi_signal"] == "超卖":
            score += 15
        elif momentum["rsi_signal"] == "超买":
            score -= 15
        
        if momentum["macd_signal"] == "金叉":
            score += 10
        elif momentum["macd_signal"] == "死叉":
            score -= 10
        
        return max(0, min(100, score))
    
    def _generate_summary(self, analysis: Dict, signal: str) -> str:
        """生成分析摘要"""
        trend = analysis["trend"]
        momentum = analysis["momentum"]
        sr = analysis["support_resistance"]
        
        summaries = []
        summaries.append(f"趋势: {trend['short_term']}/{trend['mid_term']}")
        summaries.append(f"RSI: {momentum['rsi']:.1f} ({momentum['rsi_signal']})")
        summaries.append(f"支撑/压力: {sr['support']}/{sr['resistance']}")
        
        return " | ".join(summaries)
