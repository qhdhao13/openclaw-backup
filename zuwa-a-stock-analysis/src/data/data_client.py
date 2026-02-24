"""
数据源模块 - 封装Tushare和AKShare
"""
import os
import pandas as pd
from typing import Optional, Dict


class TushareClient:
    """Tushare数据客户端"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv("TUSHARE_TOKEN")
        self.pro = None
        
        if self.token:
            try:
                import tushare as ts
                self.pro = ts.pro_api(self.token)
            except Exception as e:
                print(f"Tushare初始化失败: {e}")
    
    def get_daily_data(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取日线数据"""
        if not self.pro:
            return pd.DataFrame()
        
        try:
            # 转换股票代码格式
            ts_code = self._to_ts_code(symbol)
            
            df = self.pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            return df
        except Exception as e:
            print(f"获取数据失败: {e}")
            return pd.DataFrame()
    
    def get_stock_basic(self, symbol: str) -> Dict:
        """获取股票基本信息"""
        if not self.pro:
            return {}
        
        try:
            ts_code = self._to_ts_code(symbol)
            df = self.pro.stock_basic(ts_code=ts_code)
            if not df.empty:
                return df.iloc[0].to_dict()
            return {}
        except Exception as e:
            print(f"获取基本信息失败: {e}")
            return {}
    
    def _to_ts_code(self, symbol: str) -> str:
        """转换为Tushare代码格式"""
        symbol = str(symbol).replace(".SH", "").replace(".SZ", "")
        if symbol.startswith("6"):
            return f"{symbol}.SH"
        else:
            return f"{symbol}.SZ"


class AKShareClient:
    """AKShare数据客户端"""
    
    def __init__(self):
        self.ak = None
        try:
            import akshare as ak
            self.ak = ak
        except Exception as e:
            print(f"AKShare初始化失败: {e}")
    
    def get_realtime_data(self, symbol: str) -> Dict:
        """获取实时行情"""
        if not self.ak:
            return {}
        
        try:
            df = self.ak.stock_zh_a_spot_em()
            row = df[df['代码'] == symbol]
            if not row.empty:
                return row.iloc[0].to_dict()
            return {}
        except Exception as e:
            print(f"获取实时数据失败: {e}")
            return {}
    
    def get_capital_flow(self, symbol: str) -> pd.DataFrame:
        """获取资金流向"""
        if not self.ak:
            return pd.DataFrame()
        
        try:
            df = self.ak.stock_individual_fund_flow(stock=symbol, market="sh" if symbol.startswith("6") else "sz")
            return df
        except Exception as e:
            print(f"获取资金流向失败: {e}")
            return pd.DataFrame()


class DataManager:
    """数据管理器"""
    
    def __init__(self):
        self.tushare = TushareClient()
        self.akshare = AKShareClient()
    
    def get_full_data(self, symbol: str) -> Dict:
        """获取完整数据"""
        data = {
            "symbol": symbol,
            "basic_info": self.tushare.get_stock_basic(symbol),
            "realtime": self.akshare.get_realtime_data(symbol),
            "daily": self.tushare.get_daily_data(symbol),
            "capital_flow": self.akshare.get_capital_flow(symbol)
        }
        return data
