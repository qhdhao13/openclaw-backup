#!/usr/bin/env python3
"""
自学习引擎
每日自动总结对话，提取偏好、习惯、目标，构建专属个人模型
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter, defaultdict

MEMORY_DB_DIR = Path.home() / ".openclaw" / "workspace" / "memory-db"
LEARNING_FILE = MEMORY_DB_DIR / "learning_model.json"
DAILY_SUMMARY_FILE = MEMORY_DB_DIR / "daily_summaries.json"

class SelfLearningEngine:
    """自学习引擎 - 持续进化"""
    
    def __init__(self):
        self.db_dir = MEMORY_DB_DIR
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.learning_model = self._load_model()
        
    def _load_model(self):
        """加载学习模型"""
        if LEARNING_FILE.exists():
            with open(LEARNING_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "created_at": datetime.now().isoformat(),
            "version": "2.0.0",
            "user_profile": {
                "preferences": {},
                "habits": {},
                "communication_style": {},
                "common_tasks": [],
                "goals": [],
                "avoid_patterns": []
            },
            "learning_stats": {
                "total_days": 0,
                "total_conversations": 0,
                "insights_extracted": 0
            }
        }
    
    def _save_model(self):
        """保存学习模型"""
        with open(LEARNING_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.learning_model, f, ensure_ascii=False, indent=2)
    
    def daily_summary(self, conversations):
        """每日对话总结"""
        if not conversations:
            return None
        
        summary = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_interactions": len(conversations),
            "topics": self._extract_topics(conversations),
            "preferences": self._extract_preferences(conversations),
            "habits": self._extract_habits(conversations),
            "insights": self._generate_insights(conversations),
            "mood_trend": self._analyze_mood(conversations)
        }
        
        # 更新学习模型
        self._update_learning_model(summary)
        
        # 保存每日总结
        self._save_daily_summary(summary)
        
        return summary
    
    def _extract_topics(self, conversations):
        """提取话题"""
        all_text = " ".join([c["input"] for c in conversations])
        # 简单的关键词提取
        keywords = []
        important_words = [
            "代码", "项目", "邮件", "日程", "提醒", "定时", "配置",
            "openclaw", "龙虾", "贾维斯", "技能", "记忆", "备份"
        ]
        for word in important_words:
            if word in all_text:
                keywords.append(word)
        return list(set(keywords))[:10]
    
    def _extract_preferences(self, conversations):
        """提取偏好"""
        prefs = {}
        
        # 分析用户喜欢的响应方式
        for conv in conversations:
            input_text = conv["input"].lower()
            
            # 检测简洁偏好
            if any(word in input_text for word in ["简洁", "简短", "不要废话"]):
                prefs["response_length"] = "brief"
            
            # 检测详细偏好
            if any(word in input_text for word in ["详细", "完整", "展开"]):
                prefs["response_length"] = "detailed"
            
            # 检测主动偏好
            if any(word in input_text for word in ["主动", "提醒", "提前"]):
                prefs["proactive"] = True
        
        return prefs
    
    def _extract_habits(self, conversations):
        """提取习惯"""
        habits = defaultdict(lambda: {"count": 0, "last_time": None})
        
        for conv in conversations:
            input_text = conv["input"].lower()
            timestamp = conv.get("timestamp", datetime.now().isoformat())
            
            # 检测高频操作
            if "检查" in input_text:
                habits["checking"]["count"] += 1
                habits["checking"]["last_time"] = timestamp
            
            if "发送" in input_text or "邮件" in input_text:
                habits["email"]["count"] += 1
                habits["email"]["last_time"] = timestamp
            
            if "定时" in input_text or "cron" in input_text:
                habits["scheduling"]["count"] += 1
                habits["scheduling"]["last_time"] = timestamp
        
        return dict(habits)
    
    def _generate_insights(self, conversations):
        """生成洞察"""
        insights = []
        
        # 分析常见问题
        questions = [c["input"] for c in conversations if "?" in c["input"] or "？" in c["input"]]
        if len(questions) > 5:
            insights.append(f"用户今日提问 {len(questions)} 次，表现出较强的探索和学习意愿")
        
        # 分析任务完成度
        tasks = [c for c in conversations if any(word in c["input"] for word in ["完成", "做好", "搞定"])]
        if len(tasks) > 3:
            insights.append(f"今日完成了 {len(tasks)} 项任务，执行效率高")
        
        return insights
    
    def _analyze_mood(self, conversations):
        """分析情绪趋势"""
        # 简单的情绪关键词检测
        positive_words = ["好", "棒", "优秀", "完美", "谢谢", "感谢"]
        negative_words = ["错", "问题", "慢", "卡", "失败", "错误"]
        
        positive_count = sum(1 for c in conversations if any(w in c["input"] for w in positive_words))
        negative_count = sum(1 for c in conversations if any(w in c["input"] for w in negative_words))
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "concerned"
        return "neutral"
    
    def _update_learning_model(self, summary):
        """更新学习模型"""
        profile = self.learning_model["user_profile"]
        
        # 更新偏好
        for key, value in summary.get("preferences", {}).items():
            profile["preferences"][key] = value
        
        # 更新习惯
        for key, value in summary.get("habits", {}).items():
            profile["habits"][key] = value
        
        # 更新统计
        self.learning_model["learning_stats"]["total_days"] += 1
        self.learning_model["learning_stats"]["total_conversations"] += summary["total_interactions"]
        self.learning_model["learning_stats"]["insights_extracted"] += len(summary.get("insights", []))
        
        self._save_model()
    
    def _save_daily_summary(self, summary):
        """保存每日总结"""
        summaries = []
        if DAILY_SUMMARY_FILE.exists():
            with open(DAILY_SUMMARY_FILE, 'r', encoding='utf-8') as f:
                summaries = json.load(f)
        
        summaries.append(summary)
        
        with open(DAILY_SUMMARY_FILE, 'w', encoding='utf-8') as f:
            json.dump(summaries, f, ensure_ascii=False, indent=2)
    
    def get_user_model(self):
        """获取用户专属模型"""
        return self.learning_model["user_profile"]
    
    def get_learning_stats(self):
        """获取学习统计"""
        return self.learning_model["learning_stats"]

# 全局实例
learning_engine = SelfLearningEngine()

if __name__ == "__main__":
    print("🧬 自学习引擎")
    print("=" * 40)
    stats = learning_engine.get_learning_stats()
    print(f"学习天数: {stats['total_days']}")
    print(f"对话总数: {stats['total_conversations']}")
    print(f"洞察提取: {stats['insights_extracted']}")
    print("=" * 40)
    print("\n📊 用户专属模型构建中...")
    print("💡 每日23:00自动总结，持续优化")
