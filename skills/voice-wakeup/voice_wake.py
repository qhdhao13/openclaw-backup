#!/usr/bin/env python3
"""
语音唤醒系统
支持唤醒词：龙虾、OpenClaw、贾维斯、lobster
特性：随时打断、随时响应、Always On
"""

import re
import sys
from pathlib import Path

# 唤醒词配置
WAKE_WORDS = ["龙虾", "openclaw", "贾维斯", "lobster", "洛布斯特"]
INTERRUPT_WORDS = ["打断", "停", "等等", "等一下", "暂停", "安静"]

class VoiceWakeSystem:
    """语音唤醒与打断系统"""
    
    def __init__(self):
        self.enabled = True
        self.is_speaking = False
        self.current_task = None
        
    def check_wake_word(self, text):
        """检测唤醒词"""
        text_lower = text.lower().strip()
        for word in WAKE_WORDS:
            if word.lower() in text_lower:
                return True, word
        return False, None
    
    def check_interrupt(self, text):
        """检测打断指令"""
        text_lower = text.lower().strip()
        for word in INTERRUPT_WORDS:
            if word in text_lower:
                return True
        return False
    
    def process_input(self, user_input):
        """处理用户输入"""
        # 检测唤醒
        is_wake, wake_word = self.check_wake_word(user_input)
        
        # 检测打断
        is_interrupt = self.check_interrupt(user_input)
        
        result = {
            "is_wake": is_wake,
            "wake_word": wake_word,
            "is_interrupt": is_interrupt,
            "original_input": user_input,
            "clean_input": self._clean_input(user_input)
        }
        
        return result
    
    def _clean_input(self, text):
        """清理输入（去除唤醒词）"""
        clean = text
        for word in WAKE_WORDS:
            clean = clean.lower().replace(word.lower(), "")
        return clean.strip()
    
    def get_status(self):
        """获取唤醒系统状态"""
        return {
            "enabled": self.enabled,
            "wake_words": WAKE_WORDS,
            "interrupt_words": INTERRUPT_WORDS,
            "status": "🎤 语音唤醒已上线 - 随时呼唤",
            "commands": {
                "唤醒": WAKE_WORDS,
                "打断": INTERRUPT_WORDS
            }
        }

# 全局实例
voice_wake = VoiceWakeSystem()

if __name__ == "__main__":
    status = voice_wake.get_status()
    print("🎙️ 语音唤醒系统")
    print("=" * 40)
    print(f"状态: {status['status']}")
    print(f"唤醒词: {', '.join(status['wake_words'])}")
    print(f"打断词: {', '.join(status['interrupt_words'])}")
    print("=" * 40)
    print("\n💡 使用方式:")
    print("  • 说『龙虾』或『贾维斯』唤醒我")
    print("  • 随时说『停』或『打断』中断当前回复")
    print("  • 支持自然对话，无需重复唤醒词")
