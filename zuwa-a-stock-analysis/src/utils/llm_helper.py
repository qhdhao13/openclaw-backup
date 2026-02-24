"""
LLM分析模块 - 为各Agent提供智能分析能力
"""
import os
from typing import Dict, Any, Optional
import json


class LLMAnalyzer:
    """LLM分析器 - 使用Moonshot/Kimi进行智能分析"""
    
    def __init__(self, model: str = "moonshot/kimi-k2.5"):
        self.model = model
        self.api_key = os.getenv("MOONSHOT_API_KEY")
        self.base_url = "https://api.moonshot.cn/v1"
    
    async def analyze_stock(
        self,
        symbol: str,
        name: str,
        context: Dict[str, Any],
        analysis_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        使用LLM分析股票
        
        Args:
            symbol: 股票代码
            name: 股票名称
            context: 上下文数据（价格、技术指标等）
            analysis_type: 分析类型 (comprehensive/technical/fundamental/sentiment)
        """
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            # 构建提示
            prompt = self._build_prompt(symbol, name, context, analysis_type)
            
            response = await client.chat.completions.create(
                model="kimi-k2.5",
                messages=[
                    {"role": "system", "content": "你是一位专业的股票分析师，擅长A股市场分析。请提供客观、专业的分析意见。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            
            # 尝试解析JSON
            try:
                result = json.loads(content)
                return result
            except:
                # 如果不是JSON，包装成标准格式
                return {
                    "analysis": content,
                    "signal": "NEUTRAL",
                    "confidence": 50,
                    "raw_response": content
                }
                
        except Exception as e:
            print(f"LLM分析失败: {e}")
            return {
                "error": str(e),
                "signal": "NEUTRAL",
                "confidence": 0
            }
    
    def _build_prompt(
        self,
        symbol: str,
        name: str,
        context: Dict[str, Any],
        analysis_type: str
    ) -> str:
        """构建分析提示"""
        
        price_data = context.get("price_data", {})
        technical = context.get("technical_analysis", {})
        
        base_prompt = f"""请分析股票 {name} ({symbol}) 的投资价值：

【基本信息】
- 当前价格: {price_data.get('current', 'N/A')}
- 涨跌幅: {price_data.get('change_pct', 'N/A')}%
- 成交量: {price_data.get('volume', 'N/A')}
- 市值: {context.get('basic_info', {}).get('market_cap', 'N/A')}
"""
        
        if analysis_type == "comprehensive":
            return base_prompt + f"""
【技术面】
- RSI: {technical.get('momentum', {}).get('rsi', 'N/A')}
- MACD: {technical.get('momentum', {}).get('macd_signal', 'N/A')}
- 趋势: {technical.get('trend', {}).get('ma_alignment', 'N/A')}

请从技术面、资金面、消息面综合分析，给出：
1. 投资评级 (STRONG_BUY/BUY/HOLD/SELL/STRONG_SELL)
2. 置信度 (0-100)
3. 分析理由
4. 目标价位
5. 风险提醒

请以JSON格式输出：
{{
    "signal": "BUY",
    "confidence": 75,
    "reasoning": "分析理由...",
    "target_price": 100.0,
    "stop_loss": 80.0,
    "risks": ["风险1", "风险2"]
}}
"""
        
        elif analysis_type == "sentiment":
            news = context.get("news", [])
            news_text = "\n".join([f"- {n.get('title', '')}" for n in news[:5]])
            
            return base_prompt + f"""
【最新新闻】
{news_text}

请分析新闻舆情，给出：
1. 整体情感 (积极/消极/中性)
2. 关键话题
3. 潜在风险
4. 对股价的影响

请以JSON格式输出：
{{
    "sentiment": "中性",
    "key_topics": ["话题1"],
    "risks": ["风险1"],
    "impact": "短期影响..."
}}
"""
        
        return base_prompt


# 全局LLM分析器实例
_llm_analyzer = None

def get_llm_analyzer() -> LLMAnalyzer:
    """获取LLM分析器实例"""
    global _llm_analyzer
    if _llm_analyzer is None:
        _llm_analyzer = LLMAnalyzer()
    return _llm_analyzer
