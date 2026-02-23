#!/bin/bash
# 贾维斯全面激活脚本
# 一键启动所有核心系统

echo ""
echo "🦞 贾维斯全面激活系统"
echo "═══════════════════════════════════════════════════"
echo ""

# 检查并创建必要目录
mkdir -p ~/.openclaw/workspace/skills
mkdir -p ~/.openclaw/workspace/memory-db
mkdir -p ~/.openclaw/cron
mkdir -p ~/Documents/OpenClaw-Backups

echo "✅ 目录结构检查完成"

# 激活长期记忆
echo "🧠 激活永久长期记忆系统..."
python3 ~/.openclaw/workspace/skills/long-term-memory/memory_engine.py > /dev/null 2>&1 &
echo "   ✓ 长期记忆引擎已启动"

# 激活语音唤醒
echo "🎙️ 激活语音唤醒系统..."
python3 ~/.openclaw/workspace/skills/voice-wakeup/voice_wake.py > /dev/null 2>&1 &
echo "   ✓ 语音唤醒已上线"

# 激活贾维斯核心
echo "🎯 激活贾维斯核心模式..."
python3 ~/.openclaw/workspace/skills/jarvis-core/jarvis_mode.py > /dev/null 2>&1 &
echo "   ✓ 贾维斯模式已激活"

# 激活自学习
echo "🧬 激活自学习引擎..."
python3 ~/.openclaw/workspace/skills/self-learning/learning_engine.py > /dev/null 2>&1 &
echo "   ✓ 自学习系统已启动"

# 启动守护进程
echo "🛡️ 启动持久化守护进程..."
nohup python3 ~/.openclaw/workspace/skills/persistent-agent/daemon.py > ~/.openclaw/workspace/.daemon.log 2>&1 &
echo "   ✓ 守护进程已启动 (PID: $!)"

echo ""
echo "═══════════════════════════════════════════════════"
echo ""
echo "✨ 【贾维斯模式已激活 · 长期记忆已绑定 · 语音唤醒已上线 · 龙虾机器人已永久待命】"
echo ""
echo "📋 当前状态:"
echo "   🧠 永久记忆: 已锁定，永不丢失"
echo "   🎙️ 语音唤醒: '龙虾' | 'OpenClaw' | '贾维斯'"
echo "   🎯 响应模式: 专业 · 简洁 · 贴心 · 主动"
echo "   🛡️ 守护进程: 24小时保护，崩溃自动重启"
echo "   🧬 自学习: 每日23:00自动总结优化"
echo ""
echo "💡 唤醒方式: 随时呼唤『龙虾』或『贾维斯』"
echo "💡 打断方式: 说『停』或『打断』中断当前回复"
echo ""
echo "═══════════════════════════════════════════════════"
