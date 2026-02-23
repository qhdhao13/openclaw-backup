#!/usr/bin/env python3
"""
河北省秦皇岛、唐山市核准项目信息汇总
数据时间范围：2025年1月-2026年2月
按投资金额排序，取前50名
"""

import sys
import os

# 添加企业微信技能路径
sys.path.insert(0, os.path.expanduser('~/.openclaw/workspace/skills/wecom-webhook'))
from wecom_bot import send_text, send_markdown

# 秦皇岛市项目（2025-2026年核准/重点项目）
qhd_projects = [
    {"name": "秦皇岛海上风电一期项目", "amount": 220, "type": "新能源", "location": "秦皇岛市", "status": "2026年机组安装"},
    {"name": "中车秦皇岛新能源商用车生产基地", "amount": 200, "type": "新能源汽车", "location": "秦皇岛市", "status": "2026年一期投产"},
    {"name": "秦唐高速秦皇岛段改扩建工程", "amount": 180, "type": "交通基础设施", "location": "秦皇岛市", "status": "2026年3月开工"},
    {"name": "光伏组件及储能产业园", "amount": 150, "type": "新能源", "location": "秦皇岛市", "status": "建设中"},
    {"name": "秦皇岛宏腾科技1150mm冷轧新材料项目", "amount": 80, "type": "新材料", "location": "昌黎县", "status": "省重点项目"},
    {"name": "分布式光伏整县推进项目", "amount": 45, "type": "新能源", "location": "秦皇岛市6个县区", "status": "2026年完成"},
    {"name": "秦皇岛耀盛上海电能青龙凉水河100MW风光储一体化", "amount": 40, "type": "新能源", "location": "青龙县", "status": "省重点项目"},
    {"name": "宏兴如是海国际滨海康养度假区C区", "amount": 35, "type": "康养文旅", "location": "北戴河新区", "status": "已核准"},
    {"name": "晶科海港区10万千瓦风力发电项目", "amount": 30, "type": "新能源", "location": "海港区", "status": "已核准"},
    {"name": "天津市肿瘤医院秦皇岛医院", "amount": 25, "type": "医疗卫生", "location": "北戴河新区", "status": "省重点项目"},
    {"name": "秦皇岛市金海达矿业大宾沟铁矿地下开采工程", "amount": 15, "type": "矿业", "location": "秦皇岛市", "status": "2025年核准"},
]

# 唐山市项目（2025-2026年核准/重点项目）
ts_projects = [
    {"name": "唐山市2025年重点项目集中开工(828个项目)", "amount": 6530.6, "type": "综合", "location": "唐山市", "status": "2025年2月开工"},
    {"name": "钢铁产业绿色转型项目", "amount": 400, "type": "钢铁", "location": "唐山市", "status": "2026年完成"},
    {"name": "海上风电基地(二期)", "amount": 250, "type": "新能源", "location": "唐山市", "status": "建设中"},
    {"name": "唐山鸿昇年产125万吨高级表面镀层钢板项目", "amount": 120, "type": "钢铁", "location": "丰南区", "status": "省重点项目"},
    {"name": "大金重工曹妃甸区95万千瓦陆上风力发电项目", "amount": 95, "type": "新能源", "location": "曹妃甸区", "status": "2025年核准"},
    {"name": "海上风电集群项目(顺桓、祥云岛250MW及乐亭月坨岛一期)", "amount": 93.4, "type": "新能源", "location": "唐山海港开发区", "status": "建设中"},
    {"name": "河北燕山钢铁高强钢、耐磨钢项目", "amount": 85, "type": "钢铁", "location": "迁安市", "status": "省重点项目"},
    {"name": "大金重工曹妃甸区70万千瓦陆上风力发电项目", "amount": 70, "type": "新能源", "location": "曹妃甸区", "status": "2025年核准"},
    {"name": "唐山市蓝保物流铁路专用线工程", "amount": 45, "type": "物流交通", "location": "唐山市", "status": "2025年核准"},
    {"name": "首钢京唐、河钢唐钢超低排放改造", "amount": 35, "type": "钢铁", "location": "唐山市", "status": "2026年完成"},
    {"name": "唐山海港经济开发区扩疆铁塔智能建造项目", "amount": 25, "type": "装备制造", "location": "海港经济开发区", "status": "省重点项目"},
    {"name": "首钢氢能炼钢示范线", "amount": 20, "type": "钢铁", "location": "唐山市", "status": "2026年完成"},
]

# 合并所有项目
all_projects = qhd_projects + ts_projects

# 按投资金额降序排序
all_projects.sort(key=lambda x: x['amount'], reverse=True)

# 取前50名
all_projects = all_projects[:50]

# 统计
total = len(all_projects)
total_amount = sum(p['amount'] for p in all_projects)
qhd_projects_list = [p for p in all_projects if p['location'].startswith('秦皇岛')]
ts_projects_list = [p for p in all_projects if p['location'].startswith('唐山')]
qhd_count = len(qhd_projects_list)
ts_count = len(ts_projects_list)
qhd_amount = sum(p['amount'] for p in qhd_projects_list)
ts_amount = sum(p['amount'] for p in ts_projects_list)

# 控制台输出
print("=" * 60)
print("河北省秦皇岛、唐山市核准/重点项目报告")
print("=" * 60)
print(f"数据时间: 2025年1月 - 2026年2月")
print(f"统计项目: {total} 个")
print(f"总投资额: {total_amount:.1f} 亿元")
print("-" * 60)
print(f"秦皇岛: {qhd_count}个项目, {qhd_amount:.1f}亿元")
print(f"唐山市: {ts_count}个项目, {ts_amount:.1f}亿元")
print("=" * 60)
print("\n投资金额排名:\n")

for i, p in enumerate(all_projects, 1):
    print(f"{i}. {p['name']}")
    print(f"   投资: {p['amount']}亿元 | 地点: {p['location']} | 类型: {p['type']}")
    print()

# 发送到企业微信
print("=" * 60)
print("正在发送企业微信消息...")

# 摘要
summary = f"""📊 河北省秦皇岛、唐山市核准/重点项目报告

📅 数据时间: 2025年1月-2026年2月
📈 统计项目: {total} 个
💰 总投资额: {total_amount:.1f} 亿元

📍 按城市统计:
• 秦皇岛市: {qhd_count}个项目, {qhd_amount:.1f}亿元
• 唐山市: {ts_count}个项目, {ts_amount:.1f}亿元

💎 投资金额TOP5:
"""

for i, p in enumerate(all_projects[:5], 1):
    summary += f"{i}. {p['name']}({p['amount']}亿元)\n"

summary += "\n📄 详细项目列表见下方消息"

send_text(summary)

# 详细列表（分段发送）
details = "📋 详细项目列表（按投资金额排序）\n\n"
for i, p in enumerate(all_projects, 1):
    line = f"{i}. {p['name']}\n"
    line += f"   💵 {p['amount']}亿元 | 📍 {p['location']}\n"
    line += f"   🏷️ {p['type']} | 📌 {p['status']}\n\n"
    
    if len(details) + len(line) > 1500:
        send_markdown(details)
        details = line
    else:
        details += line

if details:
    send_markdown(details)

print("✅ 企业微信发送完成！")
