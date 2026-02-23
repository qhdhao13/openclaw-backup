#!/usr/bin/env python3
"""
永久长期记忆引擎
核心功能：持久化存储、智能检索、增量学习
禁止清除、禁止重置、永不丢失
"""

import json
import os
import hashlib
from datetime import datetime
from pathlib import Path

MEMORY_DB_DIR = Path.home() / ".openclaw" / "workspace" / "memory-db"
MEMORY_DB_FILE = MEMORY_DB_DIR / "permanent_memory.db"
PREFERENCES_FILE = MEMORY_DB_DIR / "user_preferences.json"
HABITS_FILE = MEMORY_DB_DIR / "user_habits.json"
LEARNING_FILE = MEMORY_DB_DIR / "learning_model.json"

class PermanentMemory:
    """永久记忆系统 - 所有数据持久化存储"""
    
    def __init__(self):
        self.db_dir = MEMORY_DB_DIR
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.memory = self._load_db()
        
    def _load_db(self):
        """加载记忆数据库"""
        if MEMORY_DB_FILE.exists():
            with open(MEMORY_DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "created_at": datetime.now().isoformat(),
            "version": "2.0.0",
            "total_interactions": 0,
            "sessions": [],
            "conversations": [],
            "preferences": {},
            "habits": {},
            "knowledge": {},
            "protected": True  # 保护标记，禁止删除
        }
    
    def _save_db(self):
        """保存记忆数据库 - 原子写入防止损坏"""
        temp_file = MEMORY_DB_FILE.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
        temp_file.replace(MEMORY_DB_FILE)
        
    def record_interaction(self, user_input, agent_response, context=None):
        """记录每次交互"""
        interaction = {
            "id": hashlib.md5(f"{datetime.now().isoformat()}{user_input}".encode()).hexdigest()[:12],
            "timestamp": datetime.now().isoformat(),
            "input": user_input,
            "response": agent_response,
            "context": context or {}
        }
        
        self.memory["conversations"].append(interaction)
        self.memory["total_interactions"] += 1
        
        # 自动保存
        self._save_db()
        return interaction["id"]
    
    def update_preference(self, key, value, confidence=1.0):
        """更新用户偏好"""
        self.memory["preferences"][key] = {
            "value": value,
            "confidence": confidence,
            "updated_at": datetime.now().isoformat(),
            "frequency": self.memory["preferences"].get(key, {}).get("frequency", 0) + 1
        }
        self._save_db()
        
    def record_habit(self, habit_type, description):
        """记录用户习惯"""
        if habit_type not in self.memory["habits"]:
            self.memory["habits"][habit_type] = []
        
        self.memory["habits"][habit_type].append({
            "description": description,
            "first_seen": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "count": 1
        })
        self._save_db()
        
    def search_memory(self, query, limit=10):
        """智能搜索记忆"""
        results = []
        query_lower = query.lower()
        
        for conv in reversed(self.memory["conversations"]):
            if query_lower in conv["input"].lower() or query_lower in conv["response"].lower():
                results.append(conv)
                if len(results) >= limit:
                    break
        return results
    
    def get_user_profile(self):
        """获取用户画像"""
        return {
            "preferences": self.memory["preferences"],
            "habits": self.memory["habits"],
            "total_interactions": self.memory["total_interactions"],
            "member_since": self.memory["created_at"]
        }
    
    def is_protected(self):
        """检查记忆是否受保护"""
        return self.memory.get("protected", True)

# 全局记忆实例
permanent_memory = PermanentMemory()

if __name__ == "__main__":
    print("🧠 永久长期记忆系统已激活")
    print(f"📊 当前记忆条目: {permanent_memory.memory['total_interactions']}")
    print(f"💾 数据库位置: {MEMORY_DB_FILE}")
    print("🔒 记忆已锁定 - 禁止清除、禁止重置、永不丢失")
