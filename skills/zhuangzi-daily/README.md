# 庄子每日精读

## 描述
每日精选《庄子》一章，发送邮件给用户，帮助用户每天学习庄子智慧。

## 用法
```
zhuangzi-daily
```

## 配置
- 邮件发送使用 `workspace/.env.apikeys` 中的 126 邮箱配置
- 每日内容存储在 `zhuangzi_content.json`
- 阅读进度自动记录

## 定时任务
建议设置为每天早上 7:00 运行：
```
0 7 * * * zhuangzi-daily
```
