#!/usr/bin/env python3
"""
下载14首经典英文情歌 - 使用替代方法
由于 YouTube 访问受限，尝试使用其他方式
"""

import os
import sys
import subprocess
import json

# 歌曲列表
SONGS = [
    ("Perfect", "Ed Sheeran"),
    ("Thinking Out Loud", "Ed Sheeran"),
    ("Just The Way You Are", "Bruno Mars"),
    ("Someone Like You", "Adele"),
    ("Hello", "Adele"),
    ("My Love", "Westlife"),
    ("You Raise Me Up", "Westlife"),
    ("Right Here Waiting", "Richard Marx"),
    ("Nothing's Gonna Change My Love For You", "George Benson"),
    ("I Will Always Love You", "Whitney Houston"),
    ("Yesterday", "The Beatles"),
    ("Heal The World", "Michael Jackson"),
    ("Can You Feel the Love Tonight", "Elton John"),
    ("A Whole New World", "Peabo Bryson & Regina Belle"),
]

OUTPUT_DIR = "/Volumes/disk-hfm/music"

def check_existing_files():
    """检查已存在的音乐文件"""
    print("检查已存在的音乐文件...")
    existing = []
    
    try:
        files = os.listdir(OUTPUT_DIR)
        for title, artist in SONGS:
            # 检查各种可能的文件名格式
            possible_names = [
                f"{title}",
                f"{title} - {artist}",
                f"{artist} - {title}",
                title.lower(),
                artist.lower(),
            ]
            
            for f in files:
                f_lower = f.lower()
                if any(name.lower() in f_lower for name in possible_names):
                    if f.endswith(('.mp3', '.flac', '.m4a', '.wav')):
                        existing.append((title, artist, f))
                        break
    except Exception as e:
        print(f"检查文件时出错: {e}")
    
    return existing

def try_yt_dlp_with_options(title, artist):
    """尝试使用 yt-dlp 下载，带多种选项"""
    search_query = f"{title} {artist} official audio"
    output_template = f"{OUTPUT_DIR}/%(title)s.%(ext)s"
    
    # 尝试不同的配置
    attempts = [
        # 标准配置
        ["yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "0", 
         "--socket-timeout", "60", "--retries", "5",
         "-o", output_template, f"ytsearch1:{search_query}"],
        
        # 使用 IPv4
        ["yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "0",
         "--force-ipv4", "--socket-timeout", "60", "--retries", "5",
         "-o", output_template, f"ytsearch1:{search_query}"],
        
        # 使用 cookies
        ["yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "0",
         "--cookies-from-browser", "chrome",
         "--socket-timeout", "60", "--retries", "5",
         "-o", output_template, f"ytsearch1:{search_query}"],
    ]
    
    for i, cmd in enumerate(attempts):
        try:
            print(f"  尝试方法 {i+1}...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                return True
        except Exception as e:
            print(f"  方法 {i+1} 失败: {e}")
            continue
    
    return False

def main():
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("=" * 60)
    print("经典英文情歌下载工具")
    print("=" * 60)
    
    # 检查已存在的文件
    existing = check_existing_files()
    print(f"\n已存在的歌曲: {len(existing)} 首")
    for title, artist, filename in existing:
        print(f"  ✓ {title} - {artist} ({filename})")
    
    # 需要下载的歌曲
    to_download = [(t, a) for t, a in SONGS if not any(t == e[0] and a == e[1] for e in existing)]
    
    print(f"\n需要下载的歌曲: {len(to_download)} 首")
    for title, artist in to_download:
        print(f"  - {title} - {artist}")
    
    if not to_download:
        print("\n所有歌曲已存在，无需下载！")
        return 0
    
    print("\n" + "=" * 60)
    print("开始下载...")
    print("=" * 60)
    
    # 尝试下载
    success_count = 0
    failed_songs = []
    
    for i, (title, artist) in enumerate(to_download, 1):
        print(f"\n[{i}/{len(to_download)}] {title} - {artist}")
        
        if try_yt_dlp_with_options(title, artist):
            print(f"  ✓ 成功")
            success_count += 1
        else:
            print(f"  ✗ 失败")
            failed_songs.append((title, artist))
    
    # 报告结果
    print("\n" + "=" * 60)
    print(f"下载结果: {success_count}/{len(to_download)} 首成功")
    print(f"总计: {len(existing) + success_count}/{len(SONGS)} 首")
    
    if failed_songs:
        print(f"\n失败的歌曲:")
        for title, artist in failed_songs:
            print(f"  - {title} - {artist}")
        print("\n注意: 由于网络限制，无法连接到 YouTube。")
        print("建议:")
        print("1. 配置系统代理后重试")
        print("2. 使用 VPN 连接")
        print("3. 手动下载这些歌曲")
    
    # 列出所有文件
    print(f"\n{OUTPUT_DIR} 中的音乐文件:")
    try:
        files = sorted(os.listdir(OUTPUT_DIR))
        music_files = [f for f in files if f.endswith(('.mp3', '.flac', '.m4a', '.wav'))]
        for f in music_files:
            filepath = os.path.join(OUTPUT_DIR, f)
            size = os.path.getsize(filepath)
            size_mb = size / (1024 * 1024)
            print(f"  {f} ({size_mb:.1f} MB)")
        print(f"\n共 {len(music_files)} 个音乐文件")
    except Exception as e:
        print(f"  无法列出文件: {e}")
    
    return 0 if not failed_songs else 1

if __name__ == "__main__":
    sys.exit(main())
