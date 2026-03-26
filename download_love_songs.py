#!/usr/bin/env python3
"""
下载14首经典英文情歌
使用 yt-dlp 从 YouTube 下载音频
"""

import subprocess
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

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

def download_song(title, artist):
    """下载单首歌曲"""
    search_query = f"{title} {artist} official audio"
    output_template = f"{OUTPUT_DIR}/%(title)s.%(ext)s"
    
    cmd = [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "-o", output_template,
        f"ytsearch1:{search_query}"
    ]
    
    print(f"[下载中] {title} - {artist}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print(f"[✓ 成功] {title} - {artist}")
            return True
        else:
            print(f"[✗ 失败] {title} - {artist}")
            print(f"  错误: {result.stderr[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"[✗ 超时] {title} - {artist}")
        return False
    except Exception as e:
        print(f"[✗ 异常] {title} - {artist}: {e}")
        return False

def main():
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"开始下载 {len(SONGS)} 首歌曲到 {OUTPUT_DIR}")
    print("=" * 60)
    
    # 顺序下载（避免网络拥堵）
    success_count = 0
    failed_songs = []
    
    for i, (title, artist) in enumerate(SONGS, 1):
        print(f"\n[{i}/{len(SONGS)}] ", end="")
        if download_song(title, artist):
            success_count += 1
        else:
            failed_songs.append((title, artist))
    
    # 报告结果
    print("\n" + "=" * 60)
    print(f"下载完成: {success_count}/{len(SONGS)} 首成功")
    
    if failed_songs:
        print(f"\n失败的歌曲:")
        for title, artist in failed_songs:
            print(f"  - {title} - {artist}")
    
    # 列出所有文件
    print(f"\n{OUTPUT_DIR} 中的文件:")
    try:
        files = sorted(os.listdir(OUTPUT_DIR))
        for f in files:
            if f.endswith(('.mp3', '.flac', '.m4a', '.wav')):
                filepath = os.path.join(OUTPUT_DIR, f)
                size = os.path.getsize(filepath)
                size_mb = size / (1024 * 1024)
                print(f"  {f} ({size_mb:.1f} MB)")
    except Exception as e:
        print(f"  无法列出文件: {e}")
    
    return 0 if success_count == len(SONGS) else 1

if __name__ == "__main__":
    sys.exit(main())
