"""
祖蛙深度分析模块 - 量价关系与资金行为分析
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta


class AdvancedAnalyzer:
    """高级分析器 - 量价关系与资金行为"""
    
    def __init__(self):
        self.ak = None
    
    def _get_akshare(self):
        """延迟加载akshare"""
        if self.ak is None:
            import akshare as ak
            self.ak = ak
        return self.ak
    
    # ============================================
    # 功能1: 历史成交量与股价对应关系分析
    # ============================================
    def analyze_volume_price_relationship(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        分析成交量与股价的关系
        
        返回:
        - 量价配合度
        - 量价背离信号
        - 放量/缩量趋势
        - 关键量价形态
        """
        if df is None or df.empty or len(df) < 20:
            return {"error": "数据不足"}
        
        try:
            # 确保列名正确
            if 'close' not in df.columns:
                df['close'] = df['收盘'] if '收盘' in df.columns else df['close']
            if 'volume' not in df.columns:
                df['volume'] = df['成交量'] if '成交量' in df.columns else df['volume']
            
            # 计算成交量均线
            df['volume_ma5'] = df['volume'].rolling(5).mean()
            df['volume_ma20'] = df['volume'].rolling(20).mean()
            
            # 计算价格变化
            df['price_change'] = df['close'].pct_change()
            df['volume_change'] = df['volume'].pct_change()
            
            # 量价配合度分析
            latest = df.iloc[-1]
            
            # 1. 放量上涨 / 缩量下跌 = 健康
            # 2. 缩量上涨 / 放量下跌 = 警惕
            recent_5d = df.tail(5)
            
            volume_price_signals = []
            
            # 检测放量上涨
            if latest['volume'] > latest['volume_ma5'] * 1.5 and latest['price_change'] > 0:
                volume_price_signals.append({
                    "type": "放量上涨",
                    "strength": "强势",
                    "description": "成交量放大50%以上且价格上涨，资金积极入场"
                })
            
            # 检测缩量上涨
            elif latest['volume'] < latest['volume_ma5'] * 0.8 and latest['price_change'] > 0:
                volume_price_signals.append({
                    "type": "缩量上涨",
                    "strength": "偏弱",
                    "description": "价格上涨但成交量萎缩，上涨动能不足"
                })
            
            # 检测放量下跌
            if latest['volume'] > latest['volume_ma5'] * 1.5 and latest['price_change'] < 0:
                volume_price_signals.append({
                    "type": "放量下跌",
                    "strength": "危险",
                    "description": "成交量放大且价格下跌，资金出逃明显"
                })
            
            # 检测缩量下跌
            elif latest['volume'] < latest['volume_ma5'] * 0.8 and latest['price_change'] < 0:
                volume_price_signals.append({
                    "type": "缩量下跌",
                    "strength": "观察",
                    "description": "价格下跌但成交量萎缩，抛压减轻"
                })
            
            # 量价背离检测
            price_trend = self._calculate_trend(df['close'].tail(20))
            volume_trend = self._calculate_trend(df['volume'].tail(20))
            
            divergence = []
            if price_trend == "UP" and volume_trend == "DOWN":
                divergence.append("顶背离：价格上涨但成交量萎缩，警惕回调")
            elif price_trend == "DOWN" and volume_trend == "UP":
                divergence.append("底背离：价格下跌但成交量放大，可能企稳")
            
            # 成交量分布分析
            volume_percentile = df['volume'].tail(60).rank(pct=True).iloc[-1]
            
            return {
                "current_volume": int(latest['volume']),
                "volume_ma5": int(latest['volume_ma5']),
                "volume_ma20": int(latest['volume_ma20']),
                "volume_ratio": round(latest['volume'] / latest['volume_ma5'], 2) if latest['volume_ma5'] > 0 else 0,
                "volume_percentile": round(volume_percentile, 2),
                "signals": volume_price_signals,
                "divergence": divergence,
                "price_trend": price_trend,
                "volume_trend": volume_trend,
                "health_score": self._calculate_volume_health_score(df)
            }
            
        except Exception as e:
            return {"error": f"分析失败: {e}"}
    
    # ============================================
    # 功能2: 历史股价与股东数量对应关系分析
    # ============================================
    def analyze_price_holder_relationship(self, symbol: str) -> Dict[str, Any]:
        """
        分析股价与股东数量的关系
        
        逻辑:
        - 股东数量减少 + 股价上涨 = 筹码集中，庄股特征
        - 股东数量增加 + 股价下跌 = 筹码分散，散户化
        """
        return {"error": "股东数据接口暂不可用，AKShare接口已变更"}
    
    # ============================================
    # 功能3: 历史股价与融资融券关系分析
    # ============================================
    def analyze_price_margin_relationship(self, symbol: str) -> Dict[str, Any]:
        """
        分析股价与融资融券余额的关系
        
        逻辑:
        - 融资余额增加 + 股价上涨 = 杠杆资金推动，趋势强劲
        - 融资余额减少 + 股价下跌 = 杠杆资金撤离，风险释放
        - 融资余额增加 + 股价下跌 = 抄底资金入场，可能反弹
        """
        return {"error": "融资融券数据接口暂不可用"}
    
    # ============================================
    # 功能4: 当日主动买主动卖明细数据分析
    # ============================================
    def analyze_active_buy_sell(self, symbol: str) -> Dict[str, Any]:
        """
        分析当日主动买卖盘数据
        
        返回:
        - 主动买入/卖出金额
        - 买卖比例
        - 大单/小单分布
        """
        try:
            ak = self._get_akshare()
            code = symbol[2:] if symbol.startswith(('sh', 'sz', 'bj')) else symbol
            
            # 获取当日资金流向明细
            try:
                df = ak.stock_individual_fund_flow(stock=code, market="sh" if code.startswith('6') else "sz")
                
                if df is None or df.empty:
                    return {"error": "无法获取资金流数据"}
                
                latest = df.iloc[0]
                
                # 解析主动买卖数据
                def parse_value(val):
                    if isinstance(val, str):
                        val = val.replace('万', '').replace('亿', '').replace('%', '')
                        try:
                            return float(val)
                        except:
                            return 0
                    return float(val) if val else 0
                
                # 主动买入 = 大单买入 + 超大单买入
                active_buy = parse_value(latest.get('大单流入', 0)) + parse_value(latest.get('超大单流入', 0))
                # 主动卖出 = 大单卖出 + 超大单卖出
                active_sell = parse_value(latest.get('大单流出', 0)) + parse_value(latest.get('超大单流出', 0))
                
                net_flow = active_buy - active_sell
                total = active_buy + active_sell
                
                buy_ratio = (active_buy / total * 100) if total > 0 else 50
                sell_ratio = (active_sell / total * 100) if total > 0 else 50
                
                # 小单数据（散户）
                small_buy = parse_value(latest.get('小单流入', 0))
                small_sell = parse_value(latest.get('小单流出', 0))
                
                return {
                    "active_buy": round(active_buy, 2),
                    "active_sell": round(active_sell, 2),
                    "net_flow": round(net_flow, 2),
                    "buy_ratio": round(buy_ratio, 1),
                    "sell_ratio": round(sell_ratio, 1),
                    "small_buy": round(small_buy, 2),
                    "small_sell": round(small_sell, 2),
                    "signal": "主动买入占优" if buy_ratio > 55 else "主动卖出占优" if sell_ratio > 55 else "买卖均衡"
                }
                
            except Exception as e:
                return {"error": f"获取买卖数据失败: {e}"}
                
        except Exception as e:
            return {"error": f"分析失败: {e}"}
    
    # ============================================
    # 辅助函数
    # ============================================
    def _calculate_trend(self, series: pd.Series) -> str:
        """计算趋势方向"""
        if len(series) < 2:
            return "UNKNOWN"
        
        first = series.iloc[0]
        last = series.iloc[-1]
        
        if last > first * 1.05:
            return "UP"
        elif last < first * 0.95:
            return "DOWN"
        else:
            return "FLAT"
    
    def _calculate_volume_health_score(self, df: pd.DataFrame) -> int:
        """计算量价健康度评分"""
        score = 50
        
        latest = df.iloc[-1]
        
        # 放量上涨加分
        if latest['volume'] > latest['volume_ma5'] and latest['price_change'] > 0:
            score += 20
        
        # 缩量下跌加分
        if latest['volume'] < latest['volume_ma5'] and latest['price_change'] < 0:
            score += 10
        
        # 放量下跌减分
        if latest['volume'] > latest['volume_ma5'] and latest['price_change'] < 0:
            score -= 20
        
        return max(0, min(100, score))


# 全局实例
_advanced_analyzer = None

def get_advanced_analyzer() -> AdvancedAnalyzer:
    """获取高级分析器实例"""
    global _advanced_analyzer
    if _advanced_analyzer is None:
        _advanced_analyzer = AdvancedAnalyzer()
    return _advanced_analyzer
