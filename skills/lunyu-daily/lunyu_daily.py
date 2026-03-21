#!/usr/bin/env python3
"""
论语每日精读
每天自动发送一章论语内容到指定邮箱
"""

import json
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

# 配置路径
SKILL_DIR = Path(__file__).parent
CONTENT_FILE = SKILL_DIR / "lunyu_content.json"
PROGRESS_FILE = SKILL_DIR / "progress.json"
ENV_FILE = Path.home() / ".openclaw" / "workspace" / ".env.apikeys"

def load_env():
    """加载环境变量"""
    env = {}
    if ENV_FILE.exists():
        with open(ENV_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env[key] = value
    return env

def load_content():
    """加载论语内容"""
    with open(CONTENT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_progress():
    """加载阅读进度"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"last_sent_id": 0, "total_sent": 0}

def save_progress(progress):
    """保存阅读进度"""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def get_today_chapter(data, progress):
    """获取今天要发送的章节"""
    chapters = data["chapters"]
    last_id = progress.get("last_sent_id", 0)
    next_id = (last_id % len(chapters)) + 1
    for chapter in chapters:
        if chapter["id"] == next_id:
            return chapter
    return chapters[0]

def send_email(subject, content, to_emails, env):
    """发送邮件"""
    smtp_server = "smtp.126.com"
    smtp_port = 465
    from_email = env.get("EMAIL_126_USER")
    password = env.get("EMAIL_126_PASS")
    
    if not from_email or not password:
        print("错误：未找到邮箱配置")
        return False
    
    if isinstance(to_emails, str):
        to_emails = [email.strip() for email in to_emails.split(',')]
    
    success_count = 0
    for to_email in to_emails:
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            server.login(from_email, password)
            server.send_message(msg)
            server.quit()
            
            print(f"✓ 发送成功: {to_email}")
            success_count += 1
        except Exception as e:
            print(f"✗ 发送失败 [{to_email}]: {str(e)}")
    
    return success_count > 0

def format_email(chapter, progress, total):
    """格式化邮件内容"""
    today = datetime.now().strftime("%Y年%m月%d日")
    weekday = datetime.now().strftime("%A")
    
    subject = f"【论语每日精读】第{chapter['id']}篇 · {chapter['title']}"
    
    content = f"""{today} {weekday}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 论语每日精读 · 第{chapter['id']}/{total}篇
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【{chapter['title']}】

📜 原文：
{chapter['content']}

💡 解读：
{chapter['interpretation']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌟 今日金句
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{chapter['quote']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📖 阅读进度：第 {progress['total_sent'] + 1} 天
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

—— 您的智能助手 · 龙虾 🦞
"""
    
    return subject, content

def main():
    print("🦞 论语每日精读")
    print("=" * 40)
    
    if not CONTENT_FILE.exists():
        print(f"错误：找不到内容文件 {CONTENT_FILE}")
        sys.exit(1)
    
    env = load_env()
    data = load_content()
    progress = load_progress()
    
    chapters = data["chapters"]
    print(f"✓ 已加载 {len(chapters)} 篇论语内容")
    
    chapter = get_today_chapter(data, progress)
    print(f"✓ 今日篇章：第{chapter['id']}篇《{chapter['title']}》")
    
    to_emails = env.get("EMAIL_TO") or env.get("EMAIL_126_USER")
    if not to_emails:
        to_emails = "qhdhao@126.com"
    
    subject, content = format_email(chapter, progress, len(chapters))
    
    print(f"\n📤 正在发送邮件...")
    email_list = [email.strip() for email in to_emails.split(',')]
    print(f"收件人: {len(email_list)} 个")
    
    if send_email(subject, content, to_emails, env):
        progress["last_sent_id"] = chapter["id"]
        progress["total_sent"] = progress.get("total_sent", 0) + 1
        progress["last_sent_date"] = datetime.now().isoformat()
        save_progress(progress)
        print(f"✓ 已更新阅读进度：第 {progress['total_sent']} 天")
        print("\n✨ 今日论语精读已发送，请查收邮箱！")
    else:
        print("\n✗ 发送失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
