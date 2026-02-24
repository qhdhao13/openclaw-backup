"""
形态识别
"""
import pandas as pd
import numpy as np
from typing import List, Dict


class PatternRecognition:
    """K线形态识别"""
    
    @staticmethod
    def detect_patterns(df: pd.DataFrame) -> List[str]:
        """检测K线形态"""
        patterns = []
        
        if len(df) < 5:
            return patterns
        
        # 涨停检测
        if PatternRecognition.is_limit_up(df):
            patterns.append("涨停")
        
        # 跌停检测
        if PatternRecognition.is_limit_down(df):
            patterns.append("跌停")
        
        # 锤子线
        if PatternRecognition.is_hammer(df):
            patterns.append("锤子线")
        
        # 十字星
        if PatternRecognition.is_doji(df):
            patterns.append("十字星")
        
        # 多头排列
        if PatternRecognition.is_bullish_alignment(df):
            patterns.append("均线多头排列")
        
        return patterns
    
    @staticmethod
    def is_limit_up(df: pd.DataFrame, threshold: float = 9.9) -> bool:
        """检测涨停"""
        if 'pct_change' in df.columns:
            return df['pct_change'].iloc[-1] >= threshold
        return False
    
    @staticmethod
    def is_limit_down(df: pd.DataFrame, threshold: float = -9.9) -> bool:
        """检测跌停"""
        if 'pct_change' in df.columns:
            return df['pct_change'].iloc[-1] <= threshold
        return False
    
    @staticmethod
    def is_hammer(df: pd.DataFrame) -> bool:
        """检测锤子线"""
        if len(df) < 1:
            return False
        
        candle = df.iloc[-1]
        body = abs(candle['close'] - candle['open'])
        lower_shadow = min(candle['open'], candle['close']) - candle['low']
        upper_shadow = candle['high'] - max(candle['open'], candle['close'])
        
        # 下影线长，上影线短，实体小
        return lower_shadow > 2 * body and upper_shadow < body
    
    @staticmethod
    def is_doji(df: pd.DataFrame) -> bool:
        """检测十字星"""
        if len(df) < 1:
            return False
        
        candle = df.iloc[-1]
        body = abs(candle['close'] - candle['open'])
        range_total = candle['high'] - candle['low']
        
        # 实体很小
        return body < 0.1 * range_total
    
    @staticmethod
    def is_bullish_alignment(df: pd.DataFrame) -> bool:
        """检测均线多头排列"""
        if len(df) < 60:
            return False
        
        latest = df.iloc[-1]
        if 'sma5' in latest and 'sma10' in latest and 'sma20' in latest and 'sma60' in latest:
            return (latest['sma5'] > latest['sma10'] > 
                    latest['sma20'] > latest['sma60'])
        return False
