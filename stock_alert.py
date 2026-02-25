#!/usr/bin/env python3
"""
股票实时预警系统
监控价格、涨跌幅，触发条件时推送通知
"""
import sys
import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path

# 配置文件路径
ALERTS_FILE = os.path.expanduser("~/.openclaw/workspace/stock_alerts.json")
ALERT_HISTORY_FILE = os.path.expanduser("~/.openclaw/workspace/stock_alert_history.json")

def load_alerts():
    """加载预警配置"""
    if os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"alerts": []}

def save_alerts(alerts):
    """保存预警配置"""
    with open(ALERTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(alerts, f, ensure_ascii=False, indent=2)

def load_alert_history():
    """加载预警历史（避免重复推送）"""
    if os.path.exists(ALERT_HISTORY_FILE):
        with open(ALERT_HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"history": []}

def save_alert_history(history):
    """保存预警历史"""
    with open(ALERT_HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def has_recent_alert(stock_code, alert_type, minutes=30):
    """检查最近是否已发送过相同预警"""
    history = load_alert_history()
    now = datetime.now()
    
    for record in history.get("history", []):
        if (record.get("stock_code") == stock_code and 
            record.get("alert_type") == alert_type):
            alert_time = datetime.fromisoformat(record.get("time", "2000-01-01"))
            if (now - alert_time).total_seconds() < minutes * 60:
                return True
    return False

def record_alert(stock_code, stock_name, alert_type, message):
    """记录预警历史"""
    history = load_alert_history()
    history["history"].append({
        "stock_code": stock_code,
        "stock_name": stock_name,
        "alert_type": alert_type,
        "message": message,
        "time": datetime.now().isoformat()
    })
    # 只保留最近100条
    history["history"] = history["history"][-100:]
    save_alert_history(history)

def get_stock_price(stock_code):
    """从同花顺获取实时股价"""
    try:
        url = f"https://stockpage.10jqka.com.cn/{stock_code}/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        # 简单提取价格信息
        import re
        # 尝试匹配价格模式
        price_match = re.search(r'([\d.]+)</span>\s*<span[^>]*>.*?涨跌幅', response.text)
        if price_match:
            price = float(price_match.group(1))
            
        # 尝试提取涨跌幅
        change_match = re.search(r'([\-+]\d+\.\d+)%', response.text)
        change_pct = float(change_match.group(1)) if change_match else 0
        
        return {
            "price": price if 'price' in dir() else None,
            "change_pct": change_pct,
            "success": True
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def check_alert_conditions(alert, stock_data):
    """检查是否触发预警条件"""
    triggered = []
    
    price = stock_data.get("price")
    change_pct = stock_data.get("change_pct")
    
    # 价格条件
    if "price_above" in alert and price:
        if price >= alert["price_above"]:
            triggered.append(f"价格突破 {alert['price_above']}元，当前 {price}元")
    
    if "price_below" in alert and price:
        if price <= alert["price_below"]:
            triggered.append(f"价格跌破 {alert['price_below']}元，当前 {price}元")
    
    # 涨跌幅条件
    if "rise_above" in alert and change_pct:
        if change_pct >= alert["rise_above"]:
            triggered.append(f"涨幅超 {alert['rise_above']}%，当前 {change_pct:+.2f}%")
    
    if "fall_below" in alert and change_pct:
        if change_pct <= alert["fall_below"]:
            triggered.append(f"跌幅超 {abs(alert['fall_below'])}%，当前 {change_pct:+.2f}%")
    
    return triggered

def send_notification(title, message):
    """发送通知（支持多种方式）"""
    print(f"\n🔔 {title}")
    print(f"   {message}")
    
    # 尝试macOS通知
    try:
        os.system(f"osascript -e 'display notification \"{message}\" with title \"{title}\"'")
    except:
        pass
    
    # TODO: 接入飞书/微信推送
    return True

def add_alert():
    """交互式添加预警"""
    print("=== 添加股票预警 ===\n")
    
    stock_code = input("股票代码（如 000338）: ").strip()
    stock_name = input("股票名称（如 潍柴动力）: ").strip()
    
    alert = {
        "stock_code": stock_code,
        "stock_name": stock_name,
        "created_at": datetime.now().isoformat(),
        "enabled": True
    }
    
    print("\n设置预警条件（不需要的直接回车跳过）：")
    
    price_above = input("价格突破预警（元）: ").strip()
    if price_above:
        alert["price_above"] = float(price_above)
    
    price_below = input("价格跌破预警（元）: ").strip()
    if price_below:
        alert["price_below"] = float(price_below)
    
    rise_above = input("涨幅超过（%）: ").strip()
    if rise_above:
        alert["rise_above"] = float(rise_above)
    
    fall_below = input("跌幅超过（%）: ").strip()
    if fall_below:
        alert["fall_below"] = float(fall_below)
    
    alerts = load_alerts()
    alerts["alerts"].append(alert)
    save_alerts(alerts)
    
    print(f"\n✅ 已添加 {stock_name}({stock_code}) 的预警")

def list_alerts():
    """列出所有预警"""
    alerts = load_alerts()
    
    if not alerts["alerts"]:
        print("暂无预警配置")
        return
    
    print("=== 当前预警列表 ===\n")
    for i, alert in enumerate(alerts["alerts"], 1):
        status = "✅" if alert.get("enabled", True) else "❌"
        print(f"{i}. {status} {alert['stock_name']}({alert['stock_code']})")
        
        conditions = []
        if "price_above" in alert:
            conditions.append(f"突破{alert['price_above']}元")
        if "price_below" in alert:
            conditions.append(f"跌破{alert['price_below']}元")
        if "rise_above" in alert:
            conditions.append(f"涨超{alert['rise_above']}%")
        if "fall_below" in alert:
            conditions.append(f"跌超{abs(alert['fall_below'])}%")
        
        if conditions:
            print(f"   条件: {' | '.join(conditions)}")
        print()

def delete_alert():
    """删除预警"""
    list_alerts()
    
    alerts = load_alerts()
    if not alerts["alerts"]:
        return
    
    try:
        idx = int(input("要删除的预警编号: ")) - 1
        if 0 <= idx < len(alerts["alerts"]):
            removed = alerts["alerts"].pop(idx)
            save_alerts(alerts)
            print(f"✅ 已删除 {removed['stock_name']} 的预警")
        else:
            print("❌ 编号错误")
    except ValueError:
        print("❌ 请输入数字")

def check_alerts():
    """检查所有预警"""
    alerts = load_alerts()
    
    if not alerts["alerts"]:
        print("暂无预警配置")
        return
    
    print(f"=== 检查预警 {datetime.now().strftime('%H:%M:%S')} ===\n")
    
    triggered_count = 0
    for alert in alerts["alerts"]:
        if not alert.get("enabled", True):
            continue
        
        stock_code = alert["stock_code"]
        stock_name = alert["stock_name"]
        
        # 获取实时数据
        stock_data = get_stock_price(stock_code)
        
        if not stock_data["success"]:
            print(f"❌ 获取 {stock_name} 数据失败: {stock_data.get('error')}")
            continue
        
        # 检查条件
        triggered = check_alert_conditions(alert, stock_data)
        
        for condition in triggered:
            alert_type = condition.split("，")[0]  # 简单提取类型
            
            # 避免重复推送（30分钟内）
            if has_recent_alert(stock_code, alert_type, minutes=30):
                print(f"⏭️  {stock_name}: {condition} (30分钟内已通知)")
                continue
            
            # 发送通知
            title = f"🚨 {stock_name} 预警触发"
            message = condition
            send_notification(title, message)
            
            # 记录历史
            record_alert(stock_code, stock_name, alert_type, condition)
            triggered_count += 1
    
    if triggered_count == 0:
        print("✅ 暂无预警触发")
    
    print(f"\n检查完成，共 {triggered_count} 条预警")

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("""
股票实时预警系统

用法:
  python3 stock_alert.py add     # 添加预警
  python3 stock_alert.py list    # 列出预警
  python3 stock_alert.py delete  # 删除预警
  python3 stock_alert.py check   # 检查预警（手动运行）
  python3 stock_alert.py daemon  # 后台持续监控
        """)
        return
    
    command = sys.argv[1]
    
    if command == "add":
        add_alert()
    elif command == "list":
        list_alerts()
    elif command == "delete":
        delete_alert()
    elif command == "check":
        check_alerts()
    elif command == "daemon":
        print("启动预警监控后台（每5分钟检查一次）...")
        print("按 Ctrl+C 停止\n")
        try:
            while True:
                check_alerts()
                print("\n等待5分钟...\n")
                time.sleep(300)  # 5分钟
        except KeyboardInterrupt:
            print("\n\n已停止监控")
    else:
        print(f"未知命令: {command}")

if __name__ == "__main__":
    main()
