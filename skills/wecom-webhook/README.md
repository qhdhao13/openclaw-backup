# 企业微信群机器人

通过企业微信Webhook向群聊发送消息。

## 配置

Webhook已配置：
```
https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=4e1c4b71-d541-47fe-ba1d-e709a8b3b992
```

## 使用方法

### 发送文本消息
```bash
python3 ~/.openclaw/workspace/skills/wecom-webhook/wecom_bot.py text "消息内容"
```

### 发送Markdown消息
```bash
python3 ~/.openclaw/workspace/skills/wecom-webhook/wecom_bot.py markdown "## 标题\n内容"
```

### 发送图文消息
```bash
python3 ~/.openclaw/workspace/skills/wecom-webhook/wecom_bot.py news "标题" "描述" "https://example.com" "https://example.com/image.jpg"
```

## 定时任务示例

每天早上发送日报：
```bash
0 9 * * * python3 ~/.openclaw/workspace/skills/wecom-webhook/wecom_bot.py text "早安！今日工作开始"
```
