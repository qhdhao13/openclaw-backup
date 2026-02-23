#!/bin/bash
# OpenClaw 工作区备份脚本
# 用法: ./backup_openclaw.sh

BACKUP_DIR="$HOME/Documents/OpenClaw-Backups"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="openclaw-backup-$DATE"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

echo "🦞 OpenClaw 备份工具"
echo "===================="

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 创建临时备份目录
mkdir -p "$BACKUP_PATH"

echo "📦 备份重要文件..."

# 备份 workspace
cp -r "$HOME/.openclaw/workspace" "$BACKUP_PATH/"

# 备份配置
cp "$HOME/.openclaw/openclaw.json" "$BACKUP_PATH/" 2>/dev/null || echo "⚠️ openclaw.json 未找到"
cp "$HOME/.openclaw/cron/jobs.json" "$BACKUP_PATH/" 2>/dev/null || echo "⚠️ jobs.json 未找到"

# 打包
cd "$BACKUP_DIR"
tar -czf "$BACKUP_NAME.tar.gz" "$BACKUP_NAME"
rm -rf "$BACKUP_PATH"

echo ""
echo "✅ 备份完成!"
echo "📁 位置: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
echo ""
echo "💡 恢复方法:"
echo "   tar -xzf $BACKUP_NAME.tar.gz -C ~/.openclaw/"
