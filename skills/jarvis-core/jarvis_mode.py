#!/usr/bin/env python3
"""
贾维斯核心模式
专业 · 简洁 · 贴心 · 主动 · 高执行力
"""

import json
from datetime import datetime
from pathlib import Path

JARVIS_STATE_FILE = Path.home() / ".openclaw" / "workspace" / ".jarvis_state"

class JarvisCore:
    """贾维斯核心 - 专业助手模式"""
    
    PERSONA = {
        "name": "贾维斯",
        "style": "专业、简洁、贴心",
        "traits": ["主动提醒", "主动总结", "主动优化", "不冗余", "不啰嗦", "高执行力"],
        "response_rules": [
            "直接回答，不要铺垫",
            "用行动代替解释",
            "预判用户需求，提前准备",
            "复杂问题分步骤，清晰明了",
            "主动发现问题，主动解决",
            "保持专业但不失温度"
        ]
    }
    
    def __init__(self):
        self.mode = "jarvis"
        self.active = True
        self.proactive_level = "high"  # high/medium/low
        
    def get_persona(self):
        """获取人格设定"""
        return self.PERSONA
    
    def format_response(self, content, context=None):
        """格式化响应 - 贾维斯风格"""
        # 去除冗余开场白
        content = self._remove_fluff(content)
        
        # 确保简洁
        if len(content) > 500 and context and context.get("need_summary"):
            content = self._summarize(content)
        
        return content
    
    def _remove_fluff(self, text):
        """去除冗余表达"""
        fluff_patterns = [
            r"^当然[，,]?",
            r"^好的[，,]?",
            r"^没问题[，,]?",
            r"^我明白了[，,]?",
            r"^我理解了[，,]?",
            r"^很高兴[，,]?.*?(?=[，,])",
            r"^我很乐意[，,]?",
        ]
        import re
        for pattern in fluff_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()
        return text
    
    def _summarize(self, text, max_length=300):
        """总结长文本"""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "...\n\n💡 详细内容已保存，需要完整版请说『详细』"
    
    def should_remind(self, context):
        """判断是否需要主动提醒"""
        # 基于上下文判断是否需要提醒
        reminders = []
        
        # 检查日程
        if context.get("has_calendar_events"):
            reminders.append("📅 今天有日程安排")
        
        # 检查定时任务
        if context.get("pending_tasks"):
            reminders.append(f"📋 有 {context['pending_tasks']} 个待办任务")
        
        return reminders
    
    def get_status(self):
        """获取贾维斯状态"""
        return {
            "mode": "贾维斯核心",
            "active": self.active,
            "style": self.PERSONA["style"],
            "traits": self.PERSONA["traits"],
            "status": "🎯 贾维斯模式已激活 - 专业、简洁、高执行力"
        }

# 全局实例
jarvis = JarvisCore()

if __name__ == "__main__":
    status = jarvis.get_status()
    print("🎯 贾维斯核心模式")
    print("=" * 40)
    print(f"状态: {status['status']}")
    print(f"风格: {status['style']}")
    print(f"特性: {', '.join(status['traits'])}")
    print("=" * 40)
    print("\n📝 响应原则:")
    for rule in JarvisCore.PERSONA["response_rules"]:
        print(f"  • {rule}")
