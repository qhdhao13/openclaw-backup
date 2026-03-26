#!/usr/bin/env python3
"""
使用 yt-dlp Python API 下载歌曲
"""

import sys
import os

# 使用虚拟环境的 yt-dlp
venv_path = os.path.expanduser("~/.openclaw/venvs/ytdlp/lib/python3.14/site-packages")
if venv_path not in sys.path:
    sys.path.insert(0, venv_path)

import yt_dlp

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
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0',
        }],
        'outtmpl': output_template,
        'quiet': False,
        'no_warnings': False,
        'socket_timeout': 30,
        'retries': 3,
    }
    
    print(f"[下载中] {title} - {artist}")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 搜索并下载
            search_url = f"ytsearch1:{search_query}"
            info = ydl.extract_info(search_url, download=True)
            
            if info and 'entries' in info and len(info['entries']) > 0:
                print(f"[✓ 成功] {title} - {artist}")
                return True
            else:
                print(f"[✗ 失败] {title} - {artist} - 未找到结果")
                return False
    except Exception as e:
        print(f"[✗ 异常] {title} - {artist}: {e}")
        return False

def main():
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"开始下载 {len(SONGS)} 首歌曲到 {OUTPUT_DIR}")
    print("=" * 60)
    
    # 顺序下载
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
    
    return 0 if success_count == len(SONGS) else 1

if __name__ == "__main__":
    sys.exit(main())
