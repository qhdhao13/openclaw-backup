#!/usr/bin/env python3
"""
企业微信群机器人消息推送
支持文本、Markdown、图文消息
"""

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime

# Webhook配置
WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=4e1c4b71-d541-47fe-ba1d-e709a8b3b992"

def send_text(content, mentioned_list=None, mentioned_mobile_list=None):
    """发送文本消息"""
    data = {
        "msgtype": "text",
        "text": {
            "content": content
        }
    }
    
    if mentioned_list:
        data["text"]["mentioned_list"] = mentioned_list
    if mentioned_mobile_list:
        data["text"]["mentioned_mobile_list"] = mentioned_mobile_list
    
    return _send_request(data)

def send_markdown(content):
    """发送Markdown消息"""
    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }
    return _send_request(data)

def send_image(base64_data, md5):
    """发送图片消息"""
    data = {
        "msgtype": "image",
        "image": {
            "base64": base64_data,
            "md5": md5
        }
    }
    return _send_request(data)

def send_news(title, description, url, picurl=None):
    """发送图文消息"""
    article = {
        "title": title,
        "description": description,
        "url": url
    }
    if picurl:
        article["picurl"] = picurl
    
    data = {
        "msgtype": "news",
        "news": {
            "articles": [article]
        }
    }
    return _send_request(data)

def send_file(media_id):
    """发送文件消息"""
    data = {
        "msgtype": "file",
        "file": {
            "media_id": media_id
        }
    }
    return _send_request(data)

def send_template_card(card_type, **kwargs):
    """发送模板卡片消息"""
    data = {
        "msgtype": "template_card",
        "template_card": {
            "card_type": card_type
        }
    }
    data["template_card"].update(kwargs)
    return _send_request(data)

def _send_request(data):
    """发送HTTP请求"""
    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }
    
    try:
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            if result.get("errcode") == 0:
                print(f"✓ 消息发送成功")
                return True
            else:
                print(f"✗ 发送失败: {result.get('errmsg')}")
                return False
                
    except urllib.error.URLError as e:
        print(f"✗ 网络错误: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ 错误: {str(e)}")
        return False

def main():
    if len(sys.argv) < 2:
        print("🦞 企业微信群机器人")
        print("=" * 40)
        print("\n用法:")
        print("  python3 wecom_bot.py text <内容>")
        print("  python3 wecom_bot.py markdown '<Markdown内容>'")
        print("  python3 wecom_bot.py news <标题> <描述> <链接> [图片URL]")
        print("\n示例:")
        print('  python3 wecom_bot.py text "早安！今日工作开始"')
        print('  python3 wecom_bot.py markdown "## 日报\\n今日完成：XXX"')
        print('  python3 wecom_bot.py news "新闻标题" "新闻描述" "https://example.com"')
        return
    
    msg_type = sys.argv[1].lower()
    
    if msg_type == "text":
        if len(sys.argv) < 3:
            print("❌ 缺少消息内容")
            return
        content = sys.argv[2]
        send_text(content)
    
    elif msg_type == "markdown":
        if len(sys.argv) < 3:
            print("❌ 缺少Markdown内容")
            return
        content = sys.argv[2]
        send_markdown(content)
    
    elif msg_type == "news":
        if len(sys.argv) < 5:
            print("❌ 参数不足: news <标题> <描述> <链接> [图片URL]")
            return
        title = sys.argv[2]
        description = sys.argv[3]
        url = sys.argv[4]
        picurl = sys.argv[5] if len(sys.argv) > 5 else None
        send_news(title, description, url, picurl)
    
    else:
        print(f"❌ 未知消息类型: {msg_type}")
        print("支持类型: text, markdown, news")

if __name__ == "__main__":
    main()
