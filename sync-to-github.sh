#!/bin/bash
# OpenClaw Workspace 备份脚本
# 使用方法: ./sync-to-github.sh [commit message]

set -e

cd /Users/qhdh/.openclaw/workspace

# 默认提交信息
COMMIT_MSG="${1:-Update: $(date '+%Y-%m-%d %H:%M')}"

echo "🦞 龙虾正在备份到 GitHub..."
echo "提交信息: $COMMIT_MSG"
echo ""

# 检查是否有变更
if git diff --quiet && git diff --staged --quiet; then
    echo "✅ 没有变更需要提交"
    exit 0
fi

# 添加所有变更
git add -A
echo "📦 已添加变更文件"

# 提交
git commit -m "$COMMIT_MSG"
echo "💾 已提交"

# 推送到 GitHub
git push origin main
echo ""
echo "✅ 备份完成！"
echo "📍 https://github.com/qhdhao13/openclaw-backup"
