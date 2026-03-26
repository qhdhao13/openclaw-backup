#!/usr/bin/env python3
"""
使用 Soulseek 网络搜索和下载音乐
通过 slskd API 操作
"""

import requests
import json
import time
import os

# slskd API 基础配置
BASE_URL = "http://localhost:5030"
DOWNLOAD_DIR = "/Volumes/disk-hfm/music/slskd_downloads"

# 要搜索的歌曲列表
SONGS = [
    ("Take Me Home, Country Roads", "John Denver"),
    ("Lemon Tree", "Fools Garden"),
    ("Lady", "Kenny Rogers"),
    ("Love Story", "Taylor Swift"),
    ("Blowing in the Wind", "Bob Dylan"),
    ("Any Man Of Mine", "Shania Twain"),
    ("Remember When", "Alan Jackson"),
    ("It Never Rains In Southern California", "Albert Hammond"),
    ("When You Say Nothing at All", "Ronan Keating"),
    ("Five Hundred Miles", "The Innocence Mission"),
]

def search_song(title, artist):
    """搜索歌曲"""
    query = f"{title} {artist}"
    print(f"\n🔍 搜索: {query}")
    
    # 使用 Soulseek 搜索 API
    search_data = {
        "query": query,
        "filters": {
            "fileType": ["flac", "wav", "mp3"],
            "minBitRate": 192
        }
    }
    
    try:
        # 启动搜索
        response = requests.post(f"{BASE_URL}/api/v0/searches", json=search_data, timeout=10)
        if response.status_code == 200:
            search_id = response.json().get("id")
            print(f"  搜索ID: {search_id}")
            return search_id
        else:
            print(f"  搜索失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"  错误: {e}")
        return None

def get_search_results(search_id, wait_time=10):
    """获取搜索结果"""
    if not search_id:
        return []
    
    print(f"  等待 {wait_time} 秒获取结果...")
    time.sleep(wait_time)
    
    try:
        response = requests.get(f"{BASE_URL}/api/v0/searches/{search_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = data.get("responses", [])
            print(f"  找到 {len(results)} 个结果")
            return results
        else:
            print(f"  获取结果失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"  错误: {e}")
        return []

def download_file(username, filename, file_size):
    """下载文件"""
    print(f"  📥 开始下载: {filename[:60]}...")
    
    download_data = {
        "username": username,
        "filename": filename,
        "size": file_size
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/v0/transfers/downloads", json=download_data, timeout=10)
        if response.status_code == 200:
            print(f"  ✅ 下载任务已创建")
            return True
        else:
            print(f"  ❌ 下载失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"  错误: {e}")
        return False

def main():
    print("=" * 60)
    print("🎵 Soulseek 音乐下载工具")
    print("=" * 60)
    
    # 检查 slskd 是否运行
    try:
        response = requests.get(f"{BASE_URL}/api/v0/application", timeout=5)
        if response.status_code != 200:
            print("❌ slskd 未运行，请先启动 slskd")
            return
        print("✅ slskd 运行正常")
    except Exception as e:
        print(f"❌ 无法连接到 slskd: {e}")
        return
    
    # 搜索每首歌曲
    for i, (title, artist) in enumerate(SONGS, 1):
        print(f"\n{'='*60}")
        print(f"[{i}/10] {title} - {artist}")
        print('='*60)
        
        # 搜索
        search_id = search_song(title, artist)
        
        # 获取结果
        results = get_search_results(search_id, wait_time=15)
        
        if results:
            # 找到最佳结果（优先无损格式）
            best_result = None
            for result in results:
                files = result.get("files", [])
                for file in files:
                    filename = file.get("filename", "").lower()
                    if ".flac" in filename or ".wav" in filename:
                        best_result = {
                            "username": result.get("username"),
                            "filename": file.get("filename"),
                            "size": file.get("size", 0)
                        }
                        break
                if best_result:
                    break
            
            # 如果没有无损格式，选择第一个 MP3
            if not best_result and results[0].get("files"):
                file = results[0]["files"][0]
                best_result = {
                    "username": results[0].get("username"),
                    "filename": file.get("filename"),
                    "size": file.get("size", 0)
                }
            
            if best_result:
                print(f"  最佳匹配: {best_result['filename'][:60]}...")
                download_file(best_result["username"], best_result["filename"], best_result["size"])
            else:
                print("  ⚠️ 未找到可下载的文件")
        else:
            print("  ⚠️ 未找到结果")
        
        # 等待一下再搜索下一首
        time.sleep(2)
    
    print("\n" + "=" * 60)
    print("✅ 所有搜索任务已完成！")
    print(f"📁 下载目录: {DOWNLOAD_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
