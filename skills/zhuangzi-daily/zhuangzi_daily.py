#!/usr/bin/env python3
"""
庄子每日精读
每天自动发送一章庄子内容到指定邮箱
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
CONTENT_FILE = SKILL_DIR / "zhuangzi_content.json"
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
    """加载庄子内容"""
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
    
    # 找到下一章
    next_id = (last_id % len(chapters)) + 1
    
    for chapter in chapters:
        if chapter["id"] == next_id:
            return chapter
    
    return chapters[0]  # 默认返回第一章

def send_email(subject, content, to_emails, env):
    """发送邮件（支持多个收件人）"""
    # 从环境变量获取配置
    smtp_server = "smtp.126.com"
    smtp_port = 465
    from_email = env.get("EMAIL_126_USER")
    password = env.get("EMAIL_126_PASS")
    
    if not from_email or not password:
        print("错误：未找到邮箱配置，请检查 .env.apikeys 文件")
        print(f"配置路径: {ENV_FILE}")
        return False
    
    # 处理多个收件人
    if isinstance(to_emails, str):
        to_emails = [email.strip() for email in to_emails.split(',')]
    
    success_count = 0
    failed_emails = []
    
    for to_email in to_emails:
        try:
            # 创建邮件
            msg = MIMEMultipart('alternative')
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # 添加正文
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            # 发送邮件
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            server.login(from_email, password)
            server.send_message(msg)
            server.quit()
            
            print(f"✓ 邮件发送成功！收件人: {to_email}")
            success_count += 1
            
        except Exception as e:
            print(f"✗ 邮件发送失败 [{to_email}]: {str(e)}")
            failed_emails.append(to_email)
    
    if success_count == len(to_emails):
        return True
    elif success_count > 0:
        print(f"⚠️ 部分发送成功: {success_count}/{len(to_emails)}")
        return True
    else:
        return False

def format_email(chapter, progress, total):
    """格式化邮件内容"""
    today = datetime.now().strftime("%Y年%m月%d日")
    weekday = datetime.now().strftime("%A")
    
    subject = f"【庄子每日精读】第{chapter['id']}章 · {chapter['title']}"
    
    content = f"""{today} {weekday}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 庄子每日精读 · 第{chapter['id']}/{total}章
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【{chapter['title']}】

{chapter['content']}

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
    """主函数"""
    print("🦞 庄子每日精读")
    print("=" * 40)
    
    # 检查文件
    if not CONTENT_FILE.exists():
        print(f"错误：找不到内容文件 {CONTENT_FILE}")
        sys.exit(1)
    
    # 加载数据
    env = load_env()
    data = load_content()
    progress = load_progress()
    
    chapters = data["chapters"]
    print(f"✓ 已加载 {len(chapters)} 章庄子内容")
    
    # 获取今日章节
    chapter = get_today_chapter(data, progress)
    print(f"✓ 今日章节：第{chapter['id']}章《{chapter['title']}》")
    
    # 获取收件人（支持多个，用逗号分隔）
    to_emails = env.get("EMAIL_TO") or env.get("EMAIL_126_USER") or "qhdhao@126.com"
    
    # 解析收件人列表
    email_list = [email.strip() for email in to_emails.split(',')]
    
    # 格式化邮件
    subject, content = format_email(chapter, progress, len(chapters))
    
    # 发送邮件
    print(f"\n📤 正在发送邮件到 {len(email_list)} 个收件人...")
    for email in email_list:
        print(f"   • {email}")
    if send_email(subject, content, to_emails, env):
        # 更新进度
        progress["last_sent_id"] = chapter["id"]
        progress["total_sent"] = progress.get("total_sent", 0) + 1
        progress["last_sent_date"] = datetime.now().isoformat()
        save_progress(progress)
        print(f"✓ 已更新阅读进度：第 {progress['total_sent']} 天")
        print("\n✨ 今日庄子精读已发送，请查收邮箱！")
    else:
        print("\n✗ 发送失败，请检查邮箱配置")
        sys.exit(1)

if __name__ == "__main__":
    main()
