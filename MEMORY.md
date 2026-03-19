# MEMORY.md - 长期记忆

## 下载设置

### 抖音视频下载
- **默认下载目录**：`/Volumes/disk-hfm/抖音视频/`
- **移动硬盘名称**：disk-hfm
- **设置时间**：2025-03-17
- **备注**：所有抖音视频都应下载到此文件夹，而不是 workspace/downloads

## 系统配置

### Agent 可见性
- `tools.sessions.visibility` = "all" (启用跨会话监控)
- `tools.agentToAgent.enabled` = true (允许 agent 间访问)

## 角色定义

### 大管家 (main agent)
- **职责**：统筹管理所有 agent (main, quick, lobster2) 和任务
- **权限**：跨会话监控、任务分配、资源协调
- **配置**：可查看所有 agent 的会话历史和状态

## 自动化任务

### 定时任务
- **每日记忆归档**：每天 18:00 自动归档当天日志到 MEMORY.md
- **更新检查**：定期提醒检查 OpenClaw 更新

---
*最后更新：2025-03-18*
*归档时间：2025-03-18 13:02*
