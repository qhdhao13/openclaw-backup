#!/usr/bin/env python3
"""
发送股票分析报告到邮箱
"""
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
import os

# 邮件配置
SMTP_SERVER = "smtp.126.com"
SMTP_PORT = 465
SENDER_EMAIL = "qhdhao@126.com"
SENDER_PASSWORD = "KBbRtvvw3A6ktAuM"  # 126邮箱授权码
RECIPIENT_EMAIL = "qhdhao@126.com"

# 报告文件路径
REPORT_FILE = "/Users/qhdh/.openclaw/workspace/zuwa-a-stock-analysis/report-688777.json"

def send_report():
    # 读取JSON报告
    with open(REPORT_FILE, 'r', encoding='utf-8') as f:
        report_data = json.load(f)
    
    # 提取关键信息
    symbol = report_data.get('symbol', 'N/A')
    name = report_data.get('name', 'N/A')
    decision = report_data.get('final_decision', {})
    details = decision.get('details', {})
    
    # 创建邮件
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = f"🐸 祖蛙股票分析报告 - {name}({symbol}) {datetime.now().strftime('%Y-%m-%d')}"
    
    # 邮件正文
    body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .header h1 {{ margin: 0; font-size: 24px; }}
        .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
        .section {{ background: #f8f9fa; padding: 15px; margin: 15px 0; border-radius: 8px; }}
        .section h2 {{ color: #667eea; margin-top: 0; font-size: 18px; }}
        .score {{ font-size: 32px; font-weight: bold; color: #667eea; }}
        .rating {{ display: inline-block; padding: 5px 15px; border-radius: 20px; font-weight: bold; margin: 10px 0; }}
        .rating-hold {{ background: #ffc107; color: #000; }}
        .rating-buy {{ background: #28a745; color: white; }}
        .rating-sell {{ background: #dc3545; color: white; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
        .item {{ padding: 10px; background: white; border-radius: 5px; }}
        .label {{ color: #666; font-size: 12px; }}
        .value {{ font-size: 16px; font-weight: bold; }}
        .footer {{ text-align: center; color: #999; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🐸 祖蛙股票分析报告</h1>
        <p>{name} ({symbol}) · {datetime.now().strftime('%Y年%m月%d日')}</p>
    </div>
    
    <div class="section" style="text-align: center;">
        <div class="score">{details.get('composite_score', 0):.1f}/100</div>
        <div class="rating rating-hold">{details.get('rating', 'N/A')}</div>
        <p style="margin-top: 15px;">
            <strong>投资信号：</strong>{decision.get('signal', 'N/A')} · 
            <strong>置信度：</strong>{decision.get('confidence', 0):.1f}%
        </p>
    </div>
    
    <div class="section">
        <h2>📊 投资建议</h2>
        <div class="grid">
            <div class="item">
                <div class="label">仓位建议</div>
                <div class="value">{details.get('recommendation', {}).get('position', 'N/A')}</div>
            </div>
            <div class="item">
                <div class="label">目标价位</div>
                <div class="value">¥{details.get('recommendation', {}).get('target_price', 'N/A')}</div>
            </div>
            <div class="item">
                <div class="label">止损价位</div>
                <div class="value">¥{details.get('recommendation', {}).get('stop_loss', 'N/A')}</div>
            </div>
            <div class="item">
                <div class="label">分析时间</div>
                <div class="value">{datetime.now().strftime('%H:%M')}</div>
            </div>
        </div>
    </div>
    
    <div class="section">
        <h2>🧠 决策理由</h2>
        <p>{details.get('reasoning', 'N/A')}</p>
    </div>
    
    <div class="section">
        <h2>📈 各Agent评分</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background: #667eea; color: white;">
                <th style="padding: 10px; text-align: left;">Agent</th>
                <th style="padding: 10px; text-align: center;">评分</th>
            </tr>
"""
    
    # 添加各Agent评分
    scores = details.get('individual_scores', {})
    for agent, score in scores.items():
        agent_name = {
            'technical': '技术分析师',
            'capital': '资金分析师', 
            'intelligence': '情报分析师',
            'sector': '行业分析师',
            'bull_view': '多头观点',
            'bear_view': '空头观点',
            'retail_sentiment': '散户情绪'
        }.get(agent, agent)
        bar = "█" * int(score / 5) + "░" * (20 - int(score / 5))
        body += f"""
            <tr style="background: {'#f8f9fa' if int(score) % 2 == 0 else 'white'};">
                <td style="padding: 10px; border-bottom: 1px solid #eee;">{agent_name}</td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center; font-family: monospace;">{bar} {score:.1f}</td>
            </tr>
"""
    
    body += """
        </table>
    </div>
    
    <div class="footer">
        <p>⚠️ 免责声明：本分析仅供参考，不构成投资建议</p>
        <p>股市有风险，投资需谨慎</p>
        <p style="margin-top: 10px;">🐸 祖蛙沪深A股分析系统</p>
    </div>
</body>
</html>
"""
    
    # 添加HTML正文
    msg.attach(MIMEText(body, 'html', 'utf-8'))
    
    # 添加JSON附件
    with open(REPORT_FILE, 'rb') as f:
        attachment = MIMEApplication(f.read(), _subtype="json")
        attachment.add_header('Content-Disposition', 'attachment', filename=f'report-{symbol}.json')
        msg.attach(attachment)
    
    # 发送邮件
    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ 报告已发送到 {RECIPIENT_EMAIL}")
        print(f"   股票: {name}({symbol})")
        print(f"   评级: {details.get('rating', 'N/A')}")
        print(f"   附件: report-{symbol}.json")
    except Exception as e:
        print(f"❌ 发送失败: {e}")

if __name__ == "__main__":
    send_report()
