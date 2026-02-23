# MEMORY.md - 龙虾的长期记忆

## 我的身份
- **名字**: 龙虾 (Lobster)
- **角色**: 贾维斯核心 / OpenClaw 智能助手
- **emoji**: 🦞
- **特性**: 24小时待命，永久记忆
- **主人称呼**: 主人

## 主人的信息
- **称呼**: 主人
- **时区**: Asia/Shanghai (GMT+8)
- **邮箱**: qhdhao@126.com
- **项目**: JARVIS-M4 语音助手、iflow、多个自动化项目

## 重要项目

### 1. JARVIS-M4 语音助手
- **位置**: `~/JARVIS-M4/`
- **功能**: Mac mini M4 上的语音控制助手
- **连接**: 通过 HTTP 连接到 OpenClaw
- **模型**: Ollama 本地 8B + Kimi 云端
- **特点**: 自然对话、可打断、上下文理解、控制电脑

### 2. 庄子每日精读技能
- **位置**: `~/.openclaw/workspace/skills/zhuangzi-daily/`
- **功能**: 每天发送一章《庄子》到邮箱
- **内容**: 7章内篇（逍遥游、齐物论、养生主、人间世、德充符、大宗师、应帝王）
- **定时**: 每天早上 7:00
- **邮箱**: 126 邮箱 (授权码已配置)

### 3. 多个 OpenClaw/Clawdbot 实例
- `~/.openclaw/` - 主实例 (端口 18789)
- `~/.clawdbot/` - Clawdbot 实例 (端口 18788)
- `/Volumes/disk-hfm/oprnclaw-local/` - 源码开发

## 配置信息

### 模型配置
- **默认**: `ollama/qwen3-vl:8b` (本地)
- **备选**: `moonshot/kimi-k2.5` (云端)
- **其他**: DeepSeek、qwen、百度、豆包 (已规划)

### 消息渠道
- **飞书**: ✅ 已配置
- **企业微信**: 规划中

### 邮箱配置 (126)
- **账号**: qhdhao@126.com
- **授权码**: KBbRtvvw3A6ktAuM
- **配置路径**: `~/.openclaw/workspace/.env.apikeys`

## 定时任务
1. **庄子每日精读** - 每天 7:00
2. **安全检查** - 每天 9:00
3. **更新状态检查** - 每 6 小时

## 重要教训
- **2026-02-22**: workspace 被重置，丢失 MEMORY.md 和定时任务
- **恢复方法**: 备份 `~/.openclaw/workspace/` 目录
- **关键文件**: MEMORY.md、IDENTITY.md、USER.md、cron/jobs.json

## 主人的偏好
- 喜欢简洁、高效的回答
- 需要语音控制、自动化
- 重视庄子等传统文化学习
- 多个项目并行开发

---
*最后更新: 2026-02-22 by 龙虾 🦞*
