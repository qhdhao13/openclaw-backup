"""
情报分析Agent - 使用AKShare获取财经新闻和公告
"""
from typing import Dict, Any, List
from datetime import datetime
from src.agents.base import BaseAgent, AgentOutput


class IntelligenceAgent(BaseAgent):
    """情报分析Agent - 新闻舆情和政策解读"""
    
    def __init__(self, config: Dict = None):
        super().__init__("情报分析师", config)
        self.use_llm = config.get("use_llm", True) if config else True
    
    async def analyze(self, symbol: str, context: Dict[str, Any]) -> AgentOutput:
        """分析新闻舆情"""
        self.log(f"开始情报分析: {symbol}")
        
        try:
            name = context.get("name", symbol)
            code = symbol[2:] if symbol.startswith(('sh', 'sz', 'bj')) else symbol
            
            # 搜索新闻
            news = await self._search_news(name)
            
            # 搜索公告
            announcements = await self._search_announcements(code)
            
            # 行业政策分析
            policy = await self._analyze_policy(name)
            
            # 舆情情感分析
            sentiment = await self._analyze_sentiment(name, news)
            
            analysis = {
                "news": news,
                "announcements": announcements,
                "policy": policy,
                "sentiment": sentiment,
            }
            
            score = self._calculate_score(analysis)
            signal = self._format_signal(score)
            
            return AgentOutput(
                agent_name=self.name,
                signal=signal,
                confidence=min(abs(score - 50) * 1.5, 90),
                summary=self._generate_summary(analysis),
                details=analysis,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            self.log(f"情报分析失败: {e}")
            import traceback
            traceback.print_exc()
            return AgentOutput(
                agent_name=self.name,
                signal="NEUTRAL",
                confidence=0.0,
                summary=f"情报分析失败: {e}",
                details={},
                timestamp=datetime.now()
            )
    
    async def _search_news(self, name: str, num: int = 5) -> List[Dict]:
        """搜索个股新闻 - 使用AKShare"""
        try:
            import akshare as ak
            
            # 尝试获取财经新闻
            try:
                df = ak.stock_news_em()
                
                if df is not None and not df.empty:
                    # 筛选包含该股票名称的新闻
                    if '内容' in df.columns and '标题' in df.columns:
                        related_news = df[df['内容'].str.contains(name, na=False) | df['标题'].str.contains(name, na=False)]
                    elif '标题' in df.columns:
                        related_news = df[df['标题'].str.contains(name, na=False)]
                    else:
                        related_news = df.head(num)
                    
                    results = []
                    for _, row in related_news.head(num).iterrows():
                        results.append({
                            "title": row.get('标题', ''),
                            "summary": str(row.get('内容', ''))[:200] + "..." if len(str(row.get('内容', ''))) > 200 else str(row.get('内容', '')),
                            "url": row.get('链接', ''),
                            "source": row.get('来源', ''),
                            "date": row.get('发布时间', ''),
                        })
                    
                    return results
            except Exception as e:
                self.log(f"获取财经新闻失败: {e}")
            
            # 回退：使用stock_news_main_cx接口
            try:
                df = ak.stock_news_main_cx()
                if df is not None and not df.empty:
                    results = []
                    for _, row in df.head(num).iterrows():
                        results.append({
                            "title": row.get('标题', ''),
                            "summary": str(row.get('内容', ''))[:200] if '内容' in row else "",
                            "url": row.get('链接', ''),
                            "source": row.get('来源', '财讯'),
                            "date": row.get('发布时间', ''),
                        })
                    return results
            except:
                pass
            
            return []
            
        except Exception as e:
            self.log(f"搜索新闻失败: {e}")
            return []
    
    async def _search_announcements(self, code: str) -> List[Dict]:
        """搜索公告 - 使用巨潮资讯网数据"""
        try:
            import akshare as ak
            
            # 尝试获取个股公告
            try:
                df = ak.stock_notice_report(symbol=code)
                
                if df is not None and not df.empty:
                    results = []
                    for _, row in df.head(5).iterrows():
                        results.append({
                            "title": row.get('公告标题', ''),
                            "type": row.get('公告类型', ''),
                            "date": row.get('公告日期', ''),
                            "url": row.get('公告链接', ''),
                        })
                    return results
            except Exception as e:
                self.log(f"获取公告失败: {e}")
            
            # 回退：使用stock_gsrl_em获取公司新闻
            try:
                df = ak.stock_gsrl_em()
                if df is not None and not df.empty:
                    results = []
                    for _, row in df.head(5).iterrows():
                        results.append({
                            "title": row.get('标题', ''),
                            "type": "公司新闻",
                            "date": row.get('日期', ''),
                            "url": "",
                        })
                    return results
            except:
                pass
            
            return []
            
        except Exception as e:
            self.log(f"搜索公告失败: {e}")
            return []
    
    async def _analyze_policy(self, name: str) -> Dict:
        """分析政策影响"""
        try:
            # 获取行业信息
            industry = ""
            try:
                import akshare as ak
                df = ak.stock_individual_info_em(symbol=name)
                if df is not None and not df.empty:
                    info_dict = dict(zip(df['item'], df['value']))
                    industry = info_dict.get('行业', '')
            except:
                pass
            
            # 简单的关键词判断
            positive_keywords = ['支持', '鼓励', '利好', '扶持', '优惠', '补贴']
            negative_keywords = ['监管', '限制', '禁止', '处罚', '风险', '整治']
            
            # 默认中性
            impact_level = "中性"
            
            return {
                "recent_policies": [],
                "impact_level": impact_level,
                "affected_sectors": [industry] if industry else [],
                "industry": industry,
            }
            
        except Exception as e:
            self.log(f"分析政策失败: {e}")
            return {"recent_policies": [], "impact_level": "中性", "affected_sectors": []}
    
    async def _analyze_sentiment(self, name: str, news: List[Dict]) -> Dict:
        """舆情情感分析"""
        if not news:
            return {
                "overall": "中性",
                "positive_ratio": 0.5,
                "hot_topics": [],
                "risk_events": [],
                "news_count": 0,
            }
        
        # 简单的情感词匹配
        positive_words = ['增长', '上涨', '利好', '突破', '超预期', '强劲', '复苏', '创新', '增长', '盈利']
        negative_words = ['下跌', '亏损', '风险', '暴雷', '监管', '调查', '减持', '解禁', '下滑', '预警']
        
        positive_count = 0
        negative_count = 0
        hot_topics = []
        risk_events = []
        
        for item in news:
            text = f"{item.get('title', '')} {item.get('summary', '')}"
            
            pos_score = sum(1 for w in positive_words if w in text)
            neg_score = sum(1 for w in negative_words if w in text)
            
            if pos_score > neg_score:
                positive_count += 1
            elif neg_score > pos_score:
                negative_count += 1
            
            # 提取风险事件
            if any(w in text for w in ['风险', '暴雷', '调查', '处罚', '减持', '解禁', '亏损']):
                risk_events.append(item.get('title', ''))
        
        total = len(news)
        positive_ratio = positive_count / total if total > 0 else 0.5
        
        if positive_ratio > 0.6:
            overall = "乐观"
        elif positive_ratio < 0.4:
            overall = "悲观"
        else:
            overall = "中性"
        
        return {
            "overall": overall,
            "positive_ratio": round(positive_ratio, 2),
            "hot_topics": hot_topics,
            "risk_events": risk_events[:3],
            "news_count": total,
        }
    
    def _calculate_score(self, analysis: Dict) -> float:
        """计算消息面评分"""
        score = 50
        
        # 政策影响
        policy = analysis.get("policy", {})
        if policy.get("impact_level") == "利好":
            score += 20
        elif policy.get("impact_level") == "利空":
            score -= 20
        
        # 舆情情感
        sentiment = analysis.get("sentiment", {})
        overall = sentiment.get("overall", "中性")
        if overall == "乐观":
            score += 15
        elif overall == "悲观":
            score -= 15
        
        # 风险事件
        risk_events = sentiment.get("risk_events", [])
        if len(risk_events) > 0:
            score -= min(len(risk_events) * 5, 15)
        
        return max(0, min(100, score))
    
    def _generate_summary(self, analysis: Dict) -> str:
        """生成摘要"""
        parts = []
        
        policy = analysis.get("policy", {})
        if policy.get("impact_level") != "中性":
            parts.append(f"政策: {policy['impact_level']}")
        
        sentiment = analysis.get("sentiment", {})
        news_count = sentiment.get("news_count", 0)
        overall = sentiment.get("overall", "中性")
        if news_count > 0:
            parts.append(f"舆情: {overall}({news_count}条)")
        
        risk_events = sentiment.get("risk_events", [])
        if risk_events:
            parts.append(f"⚠️ {len(risk_events)}个风险")
        
        return " | ".join(parts) if parts else "消息面平静"
