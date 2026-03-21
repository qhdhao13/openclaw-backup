# 庄子每日精读

每日精选《庄子》一章，发送邮件给用户。

## 使用

```bash
# 直接运行
python3 zhuangzi_daily.py

# 或通过 openclaw
openclaw skill run zhuangzi-daily
```

## 配置

邮件配置读取自 `~/.openclaw/workspace/.env.apikeys`：
```
EMAIL_126_USER=qhdhao@126.com
EMAIL_126_PASS=你的授权码
```

## 定时任务

建议每天早上 7:00 运行：
```
0 7 * * * /usr/bin/python3 ~/.openclaw/workspace/skills/zhuangzi-daily/zhuangzi_daily.py
```
