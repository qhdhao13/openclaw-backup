# 企业微信群机器人配置

## Webhook信息
```
https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=4e1c4b71-d541-47fe-ba1d-e709a8b3b992
```

## 状态
✅ 已配置，测试消息发送成功

## 支持的消息类型
- ✅ 文本消息 (text)
- ✅ Markdown消息 (markdown)
- ✅ 图文消息 (news)
- ✅ 图片消息 (image)
- ✅ 文件消息 (file)
- ✅ 模板卡片 (template_card)

## 使用方法

### 命令行
```bash
# 文本消息
python3 ~/.openclaw/workspace/skills/wecom-webhook/wecom_bot.py text "消息内容"

# Markdown
python3 ~/.openclaw/workspace/skills/wecom-webhook/wecom_bot.py markdown "## 标题\n内容"

# 图文消息
python3 ~/.openclaw/workspace/skills/wecom-webhook/wecom_bot.py news "标题" "描述" "https://example.com"
```

### Python调用
```python
import sys
sys.path.insert(0, '~/.openclaw/workspace/skills/wecom-webhook')
from wecom_bot import send_text, send_markdown, send_news

# 发送文本
send_text("Hello from OpenClaw!")

# 发送Markdown
send_markdown("## 今日日报\n- 任务1：完成\n- 任务2：进行中")

# 发送图文
send_news("新闻标题", "新闻描述", "https://example.com", "https://example.com/image.jpg")
```

## 定时任务示例

添加到 cron jobs:
```json
{
  "id": "daily-wecom-report",
  "name": "企业微信日报",
  "schedule": "0 18 * * *",
  "command": "python3 /Users/qhdh/.openclaw/workspace/skills/wecom-webhook/wecom_bot.py text '下班提醒：今日工作即将结束'",
  "enabled": true
}
```

## 更新时间
2026-02-22 17:23
