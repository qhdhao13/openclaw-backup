#!/bin/bash
# OpenClaw API Keys 备份脚本
# 将敏感配置文件同步到移动硬盘

set -e

# 配置
SOURCE_DIR="$HOME/.openclaw"
# 自动检测移动硬盘（优先使用 disk-hfm，否则让用户选择）
if [ -d "/Volumes/disk-hfm" ]; then
    BACKUP_DIR="/Volumes/disk-hfm/openclaw-backup"
else
    # 列出可用的卷
    echo "可用移动硬盘:"
    ls -1 /Volumes/ | grep -v "Macintosh HD" | nl
    echo ""
    read -p "请选择移动硬盘编号: " choice
    DISK=$(ls -1 /Volumes/ | grep -v "Macintosh HD" | sed -n "${choice}p")
    BACKUP_DIR="/Volumes/$DISK/openclaw-backup"
fi

BACKUP_NAME="openclaw-apikeys-$(date +%Y%m%d-%H%M%S)"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

echo "🦞 龙虾正在备份 API Keys 到移动硬盘..."
echo "备份位置: $BACKUP_PATH"
echo ""

# 创建备份目录
mkdir -p "$BACKUP_PATH"

# 备份 API Keys 文件
echo "📦 备份文件..."

# 1. 主 API Keys 文件
if [ -f "$SOURCE_DIR/workspace/.env.apikeys" ]; then
    cp "$SOURCE_DIR/workspace/.env.apikeys" "$BACKUP_PATH/"
    echo "  ✅ .env.apikeys"
fi

# 2. 代理认证文件
if [ -f "$SOURCE_DIR/agents/main/agent/auth.json" ]; then
    cp "$SOURCE_DIR/agents/main/agent/auth.json" "$BACKUP_PATH/"
    echo "  ✅ auth.json (Kimi API)"
fi

# 3. 主配置（包含 Gateway）
if [ -f "$SOURCE_DIR/openclaw.json" ]; then
    cp "$SOURCE_DIR/openclaw.json" "$BACKUP_PATH/"
    echo "  ✅ openclaw.json"
fi

# 4. 设备认证
if [ -f "$SOURCE_DIR/identity/device-auth.json" ]; then
    cp "$SOURCE_DIR/identity/device-auth.json" "$BACKUP_PATH/"
    echo "  ✅ device-auth.json"
fi

# 5. SSH 配置（如果存在）
if [ -f "$HOME/.ssh/config" ]; then
    cp "$HOME/.ssh/config" "$BACKUP_PATH/ssh-config.bak" 2>/dev/null || true
    echo "  ✅ ssh-config.bak"
fi

# 6. 创建恢复说明
cat > "$BACKUP_PATH/README.txt" << 'EOF'
OpenClaw API Keys 备份
========================
备份时间: $(date)

包含文件:
1. .env.apikeys - 百度/Tushare/飞书等 API Key
2. auth.json - Kimi API Key
3. openclaw.json - Gateway 配置
4. device-auth.json - 设备认证
5. ssh-config.bak - SSH 配置备份

恢复方法:
将文件复制回 ~/.openclaw/ 对应目录即可
EOF

echo ""
echo "✅ 备份完成！"
echo "📍 位置: $BACKUP_PATH"
echo ""
echo "备份内容:"
ls -la "$BACKUP_PATH/"

# 可选：创建最新备份的软链接
LATEST_LINK="$BACKUP_DIR/latest"
rm -f "$LATEST_LINK"
ln -s "$BACKUP_NAME" "$LATEST_LINK"
echo ""
echo "🔗 已创建快捷方式: $LATEST_LINK"
