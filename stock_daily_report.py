#!/usr/bin/env python3
"""
股票定时自动报告系统
每天早上自动生成分析报告并推送
"""
import sys
import os
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# 报告配置
REPORT_DIR = os.path.expanduser("~/.openclaw/workspace/reports")
WATCHLIST_FILE = os.path.expanduser("~/.clawdbot/stock_watcher/watchlist.txt")

def ensure_dirs():
    """确保目录存在"""
    os.makedirs(REPORT_DIR, exist_ok=True)

def load_watchlist():
    """加载自选股列表"""
    stocks = []
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and '|' in line:
                    code, name = line.split('|', 1)
                    stocks.append({"code": code.strip(), "name": name.strip()})
    return stocks

def generate_daily_report():
    """生成每日分析报告"""
    ensure_dirs()
    
    today = datetime.now().strftime('%Y-%m-%d')
    report_time = datetime.now().strftime('%H:%M')
    
    stocks = load_watchlist()
    
    if not stocks:
        print("⚠️ 自选股列表为空，请先添加股票")
        return None
    
    # 报告文件路径
    report_file = os.path.join(REPORT_DIR, f"daily_report_{today}.md")
    
    # 生成报告头
    report_lines = [
        f"# 📊 每日股票分析报告",
        f"",
        f"**报告时间**: {today} {report_time}",
        f"**分析股票**: {len(stocks)} 只",
        f"",
        "---",
        ""
    ]
    
    print(f"正在生成 {today} 的分析报告...\n")
    
    # 对每个股票进行分析
    for stock in stocks:
        code = stock["code"]
        name = stock["name"]
        
        print(f"分析 {name}({code})...")
        
        # 获取基础数据
        try:
            # 这里简化处理，实际应调用同花顺或Wind API
            stock_info = get_stock_summary(code, name)
            
            report_lines.extend([
                f"## {name} ({code})",
                f"",
                f"### 📈 市场表现",
                f"- 最新价格: {stock_info.get('price', 'N/A')} 元",
                f"- 涨跌幅: {stock_info.get('change_pct', 'N/A')}%",
                f"- 5日涨跌: {stock_info.get('change_5d', 'N/A')}%",
                f"",
                f"### 🔥 热度评分",
                f"- 技术面: {stock_info.get('tech_score', 'N/A')}/10",
                f"- 资金面: {stock_info.get('fund_score', 'N/A')}/10",
                f"- 机构关注度: {stock_info.get('inst_count', 'N/A')} 家",
                f"",
                f"### 💡 AI建议",
                f"{stock_info.get('ai_suggestion', '暂无法获取')}",
                f"",
                "---",
                ""
            ])
        except Exception as e:
            report_lines.extend([
                f"## {name} ({code})",
                f"",
                f"⚠️ 获取数据失败: {e}",
                f"",
                "---",
                ""
            ])
    
    # 保存报告
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    print(f"\n✅ 报告已生成: {report_file}")
    return report_file

def get_stock_summary(code, name):
    """获取股票摘要信息（简化版）"""
    # 这里应该调用实际的数据源
    # 暂时返回模拟数据
    return {
        "price": "28.35",
        "change_pct": "+1.05",
        "change_5d": "+8.62",
        "tech_score": "9.4",
        "fund_score": "7.2",
        "inst_count": "100",
        "ai_suggestion": "技术面强势，机构一致看好，但短期涨幅过大，建议等待回调后介入"
    }

def send_report(report_file):
    """发送报告（飞书/微信）"""
    if not report_file or not os.path.exists(report_file):
        print("❌ 报告文件不存在")
        return
    
    # 读取报告内容
    with open(report_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 简化版报告（用于推送）
    today = datetime.now().strftime('%Y-%m-%d')
    summary = f"📊 每日股票报告 ({today})\n\n"
    
    # 提取关键信息
    stocks = load_watchlist()
    summary += f"今日分析 {len(stocks)} 只股票:\n"
    for stock in stocks:
        summary += f"• {stock['name']} ({stock['code']})\n"
    
    summary += "\n详细报告已生成，请查看附件"
    
    # 尝试发送飞书通知
    try:
        send_feishu_notification(summary, report_file)
    except Exception as e:
        print(f"飞书推送失败: {e}")
        print("报告内容:\n" + summary)

def send_feishu_notification(message, report_file=None):
    """发送飞书通知"""
    # TODO: 实现飞书Webhook推送
    print(f"\n📱 飞书通知:\n{message}")
    
    if report_file:
        print(f"📎 附件: {report_file}")

def setup_cron():
    """设置定时任务（每天早上7点）"""
    script_path = os.path.abspath(__file__)
    
    cron_line = f"0 7 * * 1-5 cd {os.path.dirname(script_path)} && /usr/bin/python3 {script_path} run >> ~/.openclaw/workspace/logs/daily_report.log 2>&1"
    
    print("=" * 60)
    print("设置定时任务（每天早上7点运行）")
    print("=" * 60)
    print(f"\n请手动添加以下crontab任务:")
    print(f"\n{cron_line}\n")
    print("添加方法:")
    print("1. 运行: crontab -e")
    print("2. 添加上面这行")
    print("3. 保存退出")
    print("\n或使用OpenClaw的cron功能:")
    print(f"openclaw cron add --command 'python3 {script_path} run' --schedule '0 7 * * 1-5'")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("""
股票定时自动报告系统

用法:
  python3 stock_daily_report.py generate  # 立即生成报告
  python3 stock_daily_report.py send      # 生成并发送报告
  python3 stock_daily_report.py setup     # 设置定时任务
  python3 stock_daily_report.py run       # 定时任务调用（自动）
        """)
        return
    
    command = sys.argv[1]
    
    if command == "generate":
        generate_daily_report()
    
    elif command == "send":
        report_file = generate_daily_report()
        if report_file:
            send_report(report_file)
    
    elif command == "setup":
        setup_cron()
    
    elif command == "run":
        # 定时任务自动调用
        print(f"[{datetime.now()}] 开始执行定时报告任务")
        report_file = generate_daily_report()
        if report_file:
            send_report(report_file)
        print(f"[{datetime.now()}] 任务完成")
    
    else:
        print(f"未知命令: {command}")

if __name__ == "__main__":
    main()
