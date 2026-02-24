"""
数据收集Agent - 使用AKShare获取真实A股数据 (优化版)
"""
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from src.agents.base import BaseAgent, AgentOutput


class DataCollectionAgent(BaseAgent):
    """数据收集Agent - 负责获取和清洗股票数据"""
    
    def __init__(self, config: Dict = None):
        super().__init__("数据收集员", config)
        self.data_cache = {}
    
    async def analyze(self, symbol: str, context: Dict[str, Any]) -> AgentOutput:
        """收集股票基础数据"""
        self.log(f"开始收集 {symbol} 数据")
        
        try:
            # 统一股票代码格式
            formatted_symbol = self._format_symbol(symbol)
            
            # 获取各类数据
            daily_data = await self._get_daily_data(formatted_symbol)
            
            # 从历史数据提取最新价格信息
            price_data = self._extract_price_from_daily(daily_data)
            basic_info = await self._get_basic_info(formatted_symbol, price_data)
            
            data = {
                "symbol": symbol,
                "name": context.get("name", basic_info.get("name", "")),
                "price_data": price_data,
                "basic_info": basic_info,
                "daily_data": daily_data,
                "timestamp": datetime.now()
            }
            
            self.log(f"✅ 数据收集完成: {symbol} 当前价: {price_data.get('current', 'N/A')}")
            
            return AgentOutput(
                agent_name=self.name,
                signal="NEUTRAL",
                confidence=100.0,
                summary=f"成功获取 {symbol} 数据，当前价 {price_data.get('current', 'N/A')}",
                details=data,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.log(f"❌ 数据收集失败: {e}")
            import traceback
            traceback.print_exc()
            return AgentOutput(
                agent_name=self.name,
                signal="NEUTRAL",
                confidence=0.0,
                summary=f"数据收集失败: {e}",
                details={},
                timestamp=datetime.now()
            )
    
    def _format_symbol(self, symbol: str) -> str:
        """
        统一股票代码格式
        输入: 600519 或 sh600519
        输出: 600519 (纯数字)
        """
        symbol = symbol.strip().lower()
        # 去掉前缀
        if symbol.startswith(('sh', 'sz', 'bj')):
            return symbol[2:]
        return symbol
    
    async def _get_daily_data(self, symbol: str, days: int = 120) -> pd.DataFrame:
        """获取历史日线数据 - 使用AKShare"""
        try:
            import akshare as ak
            
            # 使用stock_zh_a_hist接口获取个股历史数据（更稳定）
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily",
                start_date=(datetime.now() - timedelta(days=days)).strftime("%Y%m%d"),
                end_date=datetime.now().strftime("%Y%m%d"),
                adjust="qfq"  # 前复权
            )
            
            if df is None or df.empty:
                self.log(f"⚠️ 未获取到 {symbol} 的历史数据")
                return pd.DataFrame()
            
            # 标准化列名（AKShare返回中文列名）
            column_mapping = {
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'turnover',
                '振幅': 'amplitude',
                '涨跌幅': 'pct_change',
                '涨跌额': 'change_amount',
                '换手率': 'turnover_rate',
            }
            
            # 重命名列
            for old_col, new_col in column_mapping.items():
                if old_col in df.columns:
                    df[new_col] = df[old_col]
            
            # 确保数值类型正确
            numeric_cols = ['open', 'high', 'low', 'close', 'volume', 'turnover', 'pct_change']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 按日期排序
            if 'date' in df.columns:
                df = df.sort_values('date').reset_index(drop=True)
            
            self.log(f"获取到 {symbol} 历史数据 {len(df)} 条")
            return df
            
        except Exception as e:
            self.log(f"⚠️ 获取历史数据失败: {e}")
            return pd.DataFrame()
    
    def _extract_price_from_daily(self, df: pd.DataFrame) -> Dict[str, Any]:
        """从历史数据提取最新价格信息"""
        if df is None or df.empty:
            return self._get_default_price_data()
        
        try:
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            return {
                "current": float(latest.get('close', 0)),
                "open": float(latest.get('open', 0)),
                "high": float(latest.get('high', 0)),
                "low": float(latest.get('low', 0)),
                "close": float(latest.get('close', 0)),
                "volume": int(latest.get('volume', 0)),
                "turnover": float(latest.get('turnover', 0)),
                "change_pct": float(latest.get('pct_change', 0)),
                "change_amount": float(latest.get('change_amount', 0)),
                "turnover_rate": float(latest.get('turnover_rate', 0)),
                "date": str(latest.get('date', '')),
            }
        except Exception as e:
            self.log(f"⚠️ 提取价格信息失败: {e}")
            return self._get_default_price_data()
    
    async def _get_basic_info(self, symbol: str, price_data: Dict) -> Dict[str, Any]:
        """获取股票基本信息"""
        try:
            import akshare as ak
            
            # 尝试获取个股信息
            try:
                info_df = ak.stock_individual_info_em(symbol=symbol)
                if info_df is not None and not info_df.empty:
                    # 转换为字典
                    info_dict = dict(zip(info_df['item'], info_df['value']))
                    
                    return {
                        "name": info_dict.get('股票简称', ''),
                        "industry": info_dict.get('行业', ''),
                        "market_cap": float(info_dict.get('总市值', 0)) if info_dict.get('总市值') else 0,
                        "float_cap": float(info_dict.get('流通市值', 0)) if info_dict.get('流通市值') else 0,
                        "pe_ttm": float(info_dict.get('市盈率-动态', 0)) if info_dict.get('市盈率-动态') else price_data.get('pe_ttm', 0),
                        "pb": float(info_dict.get('市净率', 0)) if info_dict.get('市净率') else price_data.get('pb', 0),
                        "total_shares": float(info_dict.get('总股本', 0)) if info_dict.get('总股本') else 0,
                        "float_shares": float(info_dict.get('流通股', 0)) if info_dict.get('流通股') else 0,
                    }
            except Exception as e:
                self.log(f"获取个股信息失败: {e}")
            
            # 回退：从price_data提取
            return {
                "name": "",
                "industry": "",
                "market_cap": price_data.get('market_cap', 0),
                "float_cap": price_data.get('float_cap', 0),
                "pe_ttm": price_data.get('pe_ttm', 0),
                "pb": price_data.get('pb', 0),
                "total_shares": 0,
                "float_shares": 0,
            }
            
        except Exception as e:
            self.log(f"⚠️ 获取基本信息失败: {e}")
            return self._get_default_basic_info()
    
    def _get_default_price_data(self) -> Dict[str, Any]:
        """默认价格数据"""
        return {
            "current": 0.0, "open": 0.0, "high": 0.0, "low": 0.0, "close": 0.0,
            "volume": 0, "turnover": 0.0, "change_pct": 0.0, "change_amount": 0.0,
            "turnover_rate": 0.0, "date": "",
        }
    
    def _get_default_basic_info(self) -> Dict[str, Any]:
        """默认基本信息"""
        return {
            "name": "", "industry": "", "market_cap": 0.0, "float_cap": 0.0,
            "pe_ttm": 0.0, "pb": 0.0, "total_shares": 0, "float_shares": 0,
        }
