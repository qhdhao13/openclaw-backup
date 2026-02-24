#!/usr/bin/env python3
"""
测试 LLM 配置
"""
import sys
sys.path.insert(0, '.')

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

print("=" * 60)
print("🔑 API Key 配置检查")
print("=" * 60)

# 检查各 API Key
keys = {
    "MOONSHOT_API_KEY": os.getenv("MOONSHOT_API_KEY"),
    "TUSHARE_TOKEN": os.getenv("TUSHARE_TOKEN"),
    "BAIDU_API_KEY": os.getenv("BAIDU_API_KEY"),
    "EMAIL_126_USER": os.getenv("EMAIL_126_USER"),
}

for key, value in keys.items():
    if value:
        masked = value[:10] + "..." + value[-4:] if len(value) > 20 else "***"
        print(f"✅ {key}: {masked}")
    else:
        print(f"❌ {key}: 未设置")

# 测试 LLM 连接
print("\n" + "=" * 60)
print("🤖 LLM 连接测试")
print("=" * 60)

try:
    from src.utils.llm_helper import get_llm_analyzer
    
    llm = get_llm_analyzer()
    print(f"✅ LLM 分析器初始化成功")
    print(f"   模型: {llm.model}")
    print(f"   API Key: {'已配置' if llm.api_key else '未配置'}")
    print(f"   Base URL: {llm.base_url}")
    
except Exception as e:
    print(f"❌ LLM 初始化失败: {e}")

print("\n" + "=" * 60)
print("✅ 配置检查完成")
print("=" * 60)
