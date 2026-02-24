"""
工具函数模块
"""
import json
from datetime import datetime, date
from typing import Any


class DateTimeEncoder(json.JSONEncoder):
    """JSON编码器，支持datetime类型"""
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


def format_number(num: float, decimal: int = 2) -> str:
    """格式化数字"""
    if num is None:
        return "--"
    return f"{num:.{decimal}f}"


def format_percent(num: float) -> str:
    """格式化百分比"""
    if num is None:
        return "--"
    return f"{num:.2f}%"


def get_signal_emoji(signal: str) -> str:
    """获取信号对应的emoji"""
    emojis = {
        "STRONG_BUY": "🔥",
        "BUY": "📈",
        "HOLD": "➖",
        "SELL": "📉",
        "STRONG_SELL": "❄️",
        "BULLISH": "🐂",
        "BEARISH": "🐻",
        "NEUTRAL": "⚖️"
    }
    return emojis.get(signal, "❓")
