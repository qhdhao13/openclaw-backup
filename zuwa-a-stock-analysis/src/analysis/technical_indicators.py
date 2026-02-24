"""
技术指标计算
"""
import pandas as pd
import numpy as np
from typing import Dict, List


class TechnicalIndicators:
    """技术指标计算类"""
    
    @staticmethod
    def sma(data: pd.Series, period: int) -> pd.Series:
        """简单移动平均"""
        return data.rolling(window=period).mean()
    
    @staticmethod
    def ema(data: pd.Series, period: int) -> pd.Series:
        """指数移动平均"""
        return data.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """MACD指标"""
        ema_fast = TechnicalIndicators.ema(data, fast)
        ema_slow = TechnicalIndicators.ema(data, slow)
        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators.ema(macd_line, signal)
        histogram = macd_line - signal_line
        
        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram
        }
    
    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """RSI指标"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    @staticmethod
    def bollinger_bands(data: pd.Series, period: int = 20, std: int = 2) -> Dict:
        """布林带"""
        middle = TechnicalIndicators.sma(data, period)
        band_std = data.rolling(window=period).std()
        upper = middle + (band_std * std)
        lower = middle - (band_std * std)
        
        return {
            "upper": upper,
            "middle": middle,
            "lower": lower
        }
    
    @staticmethod
    def kdj(high: pd.Series, low: pd.Series, close: pd.Series, 
            n: int = 9, m1: int = 3, m2: int = 3) -> Dict:
        """KDJ指标"""
        lowest_low = low.rolling(window=n).min()
        highest_high = high.rolling(window=n).max()
        rsv = (close - lowest_low) / (highest_high - lowest_low) * 100
        
        k = rsv.ewm(com=m1-1, adjust=False).mean()
        d = k.ewm(com=m2-1, adjust=False).mean()
        j = 3 * k - 2 * d
        
        return {"k": k, "d": d, "j": j}
