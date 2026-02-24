"""
资金分析Agent - 使用AKShare获取真实资金流向数据
"""
from typing import Dict, Any
from datetime import datetime, timedelta
from src.agents.base import BaseAgent, AgentOutput
import pandas as pd


class CapitalAnalysisAgent(BaseAgent):
    """资金分析Agent - A股特色资金流向分析"""
    
    def __init__(self, config: Dict = None):
        super().__init__("资金分析师", config)
    
    async def analyze(self, symbol: str, context: Dict[str, Any]) -> AgentOutput:
        """分析资金流向"""
        self.log(f"开始资金分析: {symbol}")
        
        try:
            # 格式化股票代码
            code = symbol[2:] if symbol.startswith(('sh', 'sz', 'bj')) else symbol
            
            # 获取各类资金数据
            analysis = {
                "main_force": await self._analyze_main_force(code),
                "north_bound": await self._analyze_north_bound(code),
                "dragon_tiger": await self._analyze_dragon_tiger(code),
                "margin": await self._analyze_margin(code),
            }
            
            # 综合评分
            score = self._calculate_score(analysis)
            signal = self._format_signal(score)
            
            return AgentOutput(
                agent_name=self.name,
                signal=signal,
                confidence=min(abs(score - 50) * 2, 100),
                summary=self._generate_summary(analysis),
                details=analysis,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.log(f"资金分析失败: {e}")
            return AgentOutput(
                agent_name=self.name,
                signal="NEUTRAL",
                confidence=0.0,
                summary=f"资金分析失败: {e}",
                details={},
                timestamp=datetime.now()
            )
    
    async def _analyze_main_force(self, code: str) -> Dict:
        """分析主力资金流向 - 使用AKShare"""
        try:
            import akshare as ak
            
            # 获取个股资金流向
            df = ak.stock_individual_fund_flow(stock=code, market="sh" if code.startswith('6') else "sz")
            
            if df is None or df.empty:
                return self._get_default_main_force()
            
            # 获取最新数据
            latest = df.iloc[0]
            
            # 解析数值（去除单位）
            def parse_value(val):
                if isinstance(val, str):
                    val = val.replace('万', '').replace('亿', '').replace('%', '')
                    try:
                        return float(val)
                    except:
                        return 0
                return float(val) if val else 0
            
            # 大单和超大单视为"主力"
            main_inflow = parse_value(latest.get('大单流入', 0)) + parse_value(latest.get('超大单流入', 0))
            main_outflow = parse_value(latest.get('大单流出', 0)) + parse_value(latest.get('超大单流出', 0))
            net_flow = main_inflow - main_outflow
            
            # 5日数据
            flow_5d = 0
            if len(df) >= 5:
                for i in range(min(5, len(df))):
                    row = df.iloc[i]
                    inflow = parse_value(row.get('大单流入', 0)) + parse_value(row.get('超大单流入', 0))
                    outflow = parse_value(row.get('大单流出', 0)) + parse_value(row.get('超大单流出', 0))
                    flow_5d += (inflow - outflow)
            
            return {
                "large_inflow": round(main_inflow, 2),
                "large_outflow": round(main_outflow, 2),
                "net_flow": round(net_flow, 2),
                "flow_5d": round(flow_5d, 2),
                "flow_20d": None,
                "signal": "流入" if net_flow > 0 else "流出" if net_flow < 0 else "中性"
            }
            
        except Exception as e:
            self.log(f"获取主力资金失败: {e}")
            return self._get_default_main_force()
    
    async def _analyze_north_bound(self, code: str) -> Dict:
        """分析北向资金(沪股通/深股通)持股"""
        try:
            import akshare as ak
            
            # 使用stock_gdfx_free_holding_analyse_em接口获取机构持股（包含北向）
            try:
                df = ak.stock_gdfx_free_holding_analyse_em(date=datetime.now().strftime("%Y%m%d"))
                if df is not None and not df.empty:
                    # 筛选该股票
                    stock_data = df[df['股票代码'] == code]
                    if not stock_data.empty:
                        latest = stock_data.iloc[0]
                        hold_ratio = float(latest.get('持股比例', 0)) if latest.get('持股比例') else 0
                        
                        return {
                            "today_buy": None,
                            "today_sell": None,
                            "net_today": 0,
                            "net_5d": None,
                            "holding_ratio": round(hold_ratio, 2),
                            "hold_count": 0,
                            "signal": "中性"
                        }
            except Exception as e:
                self.log(f"获取机构持股失败: {e}")
            
            # 回退：从实时行情获取北向持股比例
            spot_df = ak.stock_zh_a_spot_em()
            stock_row = spot_df[spot_df['代码'] == code]
            if not stock_row.empty:
                row = stock_row.iloc[0]
                # 北向持股数据可能在不同字段
                return {
                    "today_buy": None,
                    "today_sell": None,
                    "net_today": 0,
                    "net_5d": None,
                    "holding_ratio": 0,  # 无法直接获取
                    "signal": "数据暂不可用"
                }
            
            return self._get_default_north_bound()
            
        except Exception as e:
            self.log(f"获取北向资金失败: {e}")
            return self._get_default_north_bound()
    
    async def _analyze_dragon_tiger(self, code: str) -> Dict:
        """分析龙虎榜 - 游资动向"""
        try:
            import akshare as ak
            from datetime import datetime, timedelta
            
            # 获取最近龙虎榜数据
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
            
            try:
                # 尝试使用stock_lhb_daily_detail接口
                df = ak.stock_lhb_daily_detail(start_date=start_date, end_date=end_date)
                
                if df is not None and not df.empty:
                    # 筛选该股票的龙虎榜记录
                    stock_records = df[df['代码'] == code]
                    
                    if not stock_records.empty:
                        latest = stock_records.iloc[0]
                        
                        return {
                            "in_list": True,
                            "list_date": str(latest.get('日期', '')),
                            "buy_seats": [],
                            "sell_seats": [],
                            "net_amount": float(latest.get('净买额', 0)) if latest.get('净买额') else 0,
                            "famous_salons": [],
                            "signal": "游资买入" if float(latest.get('净买额', 0) or 0) > 0 else "游资卖出"
                        }
            except Exception as e:
                self.log(f"获取龙虎榜详情失败: {e}")
            
            # 回退：检查是否在最新龙虎榜列表中
            try:
                lhb_list = ak.stock_lhb_em(start_date=start_date, end_date=end_date)
                if lhb_list is not None and code in lhb_list.get('代码', []).values:
                    return {
                        "in_list": True,
                        "list_date": "近期",
                        "signal": "上榜"
                    }
            except:
                pass
            
            return self._get_default_dragon_tiger()
            
        except Exception as e:
            self.log(f"获取龙虎榜失败: {e}")
            return self._get_default_dragon_tiger()
    
    async def _analyze_margin(self, code: str) -> Dict:
        """分析融资融券"""
        try:
            import akshare as ak
            
            # 根据交易所选择接口
            if code.startswith('6'):
                # 上海
                df = ak.stock_margin_detail_sse(date=datetime.now().strftime("%Y%m%d"))
            else:
                # 深圳
                df = ak.stock_margin_detail_szse(date=datetime.now().strftime("%Y%m%d"))
            
            if df is None or df.empty:
                return self._get_default_margin()
            
            # 筛选该股票
            stock_data = df[df['标的证券代码'] == code] if '标的证券代码' in df.columns else pd.DataFrame()
            
            if stock_data.empty:
                return self._get_default_margin()
            
            latest = stock_data.iloc[0]
            
            # 解析融资余额
            margin_balance = float(latest.get('融资余额', 0)) if latest.get('融资余额') else 0
            
            return {
                "margin_balance": round(margin_balance, 2),
                "short_balance": float(latest.get('融券余额', 0)) if latest.get('融券余额') else 0,
                "margin_change": 0,
                "leverage_ratio": None,
                "signal": "数据获取成功"
            }
            
        except Exception as e:
            self.log(f"获取融资融券失败: {e}")
            return self._get_default_margin()
    
    def _get_default_main_force(self) -> Dict:
        return {"large_inflow": 0, "large_outflow": 0, "net_flow": 0, "flow_5d": 0, "flow_20d": 0, "signal": "中性"}
    
    def _get_default_north_bound(self) -> Dict:
        return {"today_buy": 0, "today_sell": 0, "net_today": 0, "net_5d": 0, "holding_ratio": 0, "signal": "中性"}
    
    def _get_default_dragon_tiger(self) -> Dict:
        return {"in_list": False, "list_date": None, "buy_seats": [], "sell_seats": [], "net_amount": 0, "famous_salons": [], "signal": "中性"}
    
    def _get_default_margin(self) -> Dict:
        return {"margin_balance": 0, "short_balance": 0, "margin_change": 0, "leverage_ratio": 0, "signal": "中性"}
    
    def _calculate_score(self, analysis: Dict) -> float:
        """计算资金评分"""
        score = 50
        
        # 主力资金
        main = analysis.get("main_force", {})
        net_flow = main.get("net_flow", 0)
        if net_flow > 5000:
            score += 25
        elif net_flow > 1000:
            score += 15
        elif net_flow < -5000:
            score -= 25
        elif net_flow < -1000:
            score -= 15
        
        # 北向资金
        north = analysis.get("north_bound", {})
        net_today = north.get("net_today", 0)
        if net_today > 1000:
            score += 20
        elif net_today > 0:
            score += 10
        elif net_today < -1000:
            score -= 20
        elif net_today < 0:
            score -= 10
        
        # 龙虎榜
        dragon = analysis.get("dragon_tiger", {})
        if dragon.get("in_list"):
            net_amount = dragon.get("net_amount", 0)
            if net_amount > 0:
                score += 15
            else:
                score -= 15
        
        # 融资融券
        margin = analysis.get("margin", {})
        margin_change = margin.get("margin_change", 0)
        if margin_change > 1000:
            score += 10
        elif margin_change < -1000:
            score -= 10
        
        return max(0, min(100, score))
    
    def _generate_summary(self, analysis: Dict) -> str:
        """生成摘要"""
        parts = []
        
        main = analysis.get("main_force", {})
        net_flow = main.get("net_flow", 0)
        if net_flow != 0:
            parts.append(f"主力: {'流入' if net_flow > 0 else '流出'} {abs(net_flow):.0f}万")
        
        north = analysis.get("north_bound", {})
        net_today = north.get("net_today", 0)
        hold_ratio = north.get("holding_ratio", 0)
        if net_today != 0:
            parts.append(f"北向: {'增持' if net_today > 0 else '减持'} {abs(net_today):.0f} ({hold_ratio:.2f}%)")
        
        dragon = analysis.get("dragon_tiger", {})
        if dragon.get("in_list"):
            net_amount = dragon.get("net_amount", 0)
            parts.append(f"龙虎榜: {'净买入' if net_amount > 0 else '净卖出'} {abs(net_amount):.0f}万")
        
        margin = analysis.get("margin", {})
        margin_change = margin.get("margin_change", 0)
        if margin_change != 0:
            parts.append(f"融资: {'增加' if margin_change > 0 else '减少'} {abs(margin_change):.0f}万")
        
        return " | ".join(parts) if parts else "资金流向中性"
