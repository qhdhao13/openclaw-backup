#!/usr/bin/env python3
"""
检查网络环境并尝试下载歌曲
"""

import subprocess
import socket
import ssl
import sys

def check_connectivity():
    """检查网络连接状态"""
    print("=" * 60)
    print("网络连接检查")
    print("=" * 60)
    
    # 检查 DNS 解析
    sites = ['www.youtube.com', 'www.google.com', 'github.com', 'www.baidu.com']
    for site in sites:
        try:
            ip = socket.gethostbyname(site)
            print(f"✓ {site} -> {ip}")
        except Exception as e:
            print(f"✗ {site} -> DNS失败: {e}")
    
    print()
    
    # 检查 HTTP 连接
    print("HTTP 连接测试:")
    import urllib.request
    
    test_urls = [
        ('https://www.baidu.com', '百度'),
        ('https://github.com', 'GitHub'),
    ]
    
    for url, name in test_urls:
        try:
            req = urllib.request.Request(url, method='HEAD')
            req.add_header('User-Agent', 'Mozilla/5.0')
            response = urllib.request.urlopen(req, timeout=10)
            print(f"✓ {name} ({url}): HTTP {response.status}")
        except Exception as e:
            print(f"✗ {name} ({url}): {type(e).__name__}")
    
    print()
    print("=" * 60)

def check_yt_dlp():
    """检查 yt-dlp 状态"""
    print("yt-dlp 检查:")
    try:
        result = subprocess.run(['yt-dlp', '--version'], 
                              capture_output=True, text=True, timeout=10)
        print(f"✓ yt-dlp 版本: {result.stdout.strip()}")
    except Exception as e:
        print(f"✗ yt-dlp 检查失败: {e}")
    print()

def try_download_with_options():
    """尝试使用不同选项下载"""
    print("尝试下载测试:")
    
    # 测试歌曲
    test_song = ("Perfect", "Ed Sheeran")
    title, artist = test_song
    search_query = f"{title} {artist} official audio"
    output_file = f"/Volumes/disk-hfm/music/test_{title.replace(' ', '_')}.mp3"
    
    # 方法1: 直接下载
    print(f"\n方法1: 直接下载 {title} - {artist}")
    cmd = [
        "yt-dlp",
        "--socket-timeout", "30",
        "--retries", "3",
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "-o", output_file,
        f"ytsearch1:{search_query}"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            print(f"✓ 下载成功!")
            return True
        else:
            print(f"✗ 下载失败")
            print(f"错误: {result.stderr[:500]}")
    except subprocess.TimeoutExpired:
        print(f"✗ 下载超时")
    except Exception as e:
        print(f"✗ 异常: {e}")
    
    return False

if __name__ == "__main__":
    check_connectivity()
    check_yt_dlp()
    
    print("\n由于网络限制，无法直接连接到 YouTube。")
    print("可能的解决方案:")
    print("1. 配置系统代理")
    print("2. 使用 VPN")
    print("3. 使用其他音乐源")
