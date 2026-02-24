"""
祖蛙系统 - Agent基类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AgentOutput:
    """Agent输出标准格式"""
    agent_name: str
    signal: str  # BULLISH, BEARISH, NEUTRAL
    confidence: float  # 0-100
    summary: str
    details: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "signal": self.signal,
            "confidence": self.confidence,
            "summary": self.summary,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }


class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, name: str, config: Optional[Dict] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"Agent.{name}")
    
    @abstractmethod
    async def analyze(self, symbol: str, context: Dict[str, Any]) -> AgentOutput:
        """
        执行分析
        
        Args:
            symbol: 股票代码
            context: 上下文数据
            
        Returns:
            AgentOutput: 分析结果
        """
        pass
    
    def log(self, message: str):
        """记录日志"""
        self.logger.info(f"[{self.name}] {message}")
    
    def _format_signal(self, score: float) -> str:
        """将分数转换为信号"""
        if score >= 60:
            return "BULLISH"
        elif score <= 40:
            return "BEARISH"
        else:
            return "NEUTRAL"
