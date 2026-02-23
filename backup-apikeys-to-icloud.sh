#!/bin/bash
# OpenClaw API Keys iCloud 备份脚本

set -e

# iCloud 路径（macOS 标准路径）
ICLOUD_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs"

# 如果标准路径不存在，尝试其他路径
if [ ! -d "$ICLOUD_DIR" ]; then
    ICLOUD_DIR="$HOME/iCloud Drive"
fi

if [ ! -d "$ICLOUD_DIR" ]; then
    echo "❌ 未找到 iCloud 目录"
    echo "请确保 iCloud Drive 已启用"
    exit 1
fi

BACKUP_DIR="$ICLOUD_DIR/OpenClaw-Backup"
BACKUP_NAME="apikeys-$(date +%Y%m%d-%H%M%S)"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

SOURCE_DIR="$HOME/.openclaw"

echo "🦞 龙虾正在备份 API Keys 到 iCloud..."
echo "iCloud 路径: $ICLOUD_DIR"
echo "备份位置: $BACKUP_PATH"
echo ""

# 创建备份目录
mkdir -p "$BACKUP_PATH"

# 备份 API Keys 文件
echo "📦 备份敏感文件到 iCloud..."

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

# 3. 主配置
if [ -f "$SOURCE_DIR/openclaw.json" ]; then
    cp "$SOURCE_DIR/openclaw.json" "$BACKUP_PATH/"
    echo "  ✅ openclaw.json"
fi

# 4. 设备认证
if [ -f "$SOURCE_DIR/identity/device-auth.json" ]; then
    cp "$SOURCE_DIR/identity/device-auth.json" "$BACKUP_PATH/"
    echo "  ✅ device-auth.json"
fi

# 5. 创建恢复说明
cat > "$BACKUP_PATH/README.txt" << EOF
OpenClaw API Keys iCloud 备份
=============================
备份时间: $(date)
设备: $(hostname)

包含的 API Keys:
- 百度千帆 (Baidu Qianfan)
- Moonshot/Kimi
- 飞书 (Feishu/Lark)
- Tushare 金融数据
- 126/QQ 邮箱

恢复方法:
1. 从 iCloud 下载此文件夹
2. 将文件复制到 ~/.openclaw/ 对应目录

⚠️ 安全提醒：
- 这些文件包含敏感 API Key
- 请勿分享给他人
- 定期检查备份完整性
EOF

echo ""
echo "✅ iCloud 备份完成！"
echo "📍 位置: $BACKUP_PATH"
echo ""
echo "备份内容:"
ls -la "$BACKUP_PATH/"

# 创建最新备份快捷方式
LATEST_LINK="$BACKUP_DIR/latest"
rm -f "$LATEST_LINK"
ln -s "$BACKUP_NAME" "$LATEST_LINK"
echo ""
echo "🔗 快捷方式: iCloud Drive/OpenClaw-Backup/latest"

echo ""
echo "⏳ 正在同步到 iCloud..."
echo "   (根据网络情况可能需要几分钟)"

# 等待 iCloud 同步（可选）
if command -v brctl &> /dev/null; then
    brctl upload "$BACKUP_PATH" 2>/dev/null || true
fi

echo "✅ 同步已启动！"
echo ""
echo "💡 提示："
echo "   - 在 Finder 中打开 iCloud Drive 可查看备份"
echo "   - 所有 Apple 设备都会自动同步此备份"
