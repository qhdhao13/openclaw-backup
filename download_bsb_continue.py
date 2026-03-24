#!/usr/bin/env python3
"""批量下载后街男孩歌曲 - 继续下载剩余歌曲"""
import sys
sys.path.insert(0, '/Users/qhdh/.openclaw/workspace/venv-music/lib/python3.14/site-packages')

from musicdl.modules.sources import NeteaseMusicClient, QQMusicClient, MiguMusicClient, KuwoMusicClient
import os
import requests

# 设置下载目录
save_dir = "/Volumes/disk-hfm/music/Backstreet_Boys"
os.makedirs(save_dir, exist_ok=True)

# 初始化音乐客户端
clients = {
    'netease': NeteaseMusicClient(),
    'qq': QQMusicClient(),
    'migu': MiguMusicClient(),
    'kuwo': KuwoMusicClient()
}

# 后街男孩热门歌曲列表（跳过已下载的）
songs = [
    "Show Me The Meaning Of Being Lonely",
    "Shape Of My Heart",
    "The One",
    "Incomplete",
    "More Than That",
    "Drowning",
    "Quit Playing Games",
    "All I Have To Give",
    "I'll Never Break Your Heart",
    "Anywhere For You",
    "Get Down"
]

print(f"继续下载后街男孩 {len(songs)} 首歌曲到 {save_dir}")
print("="*60)

downloaded = 0
failed = []

for song in songs:
    print(f"\n🎵 搜索: {song}")
    
    # 检查是否已存在
    filename = f"Backstreet Boys - {song}.flac"
    filepath = os.path.join(save_dir, filename)
    if os.path.exists(filepath):
        print(f"   ⏭️  已存在，跳过")
        downloaded += 1
        continue
    
    results = []
    for name, client in clients.items():
        try:
            search_results = client.search(f"Backstreet Boys {song}")
            if search_results:
                results.extend([(name, r) for r in search_results])
        except Exception as e:
            continue
    
    if not results:
        print(f"   ❌ 未找到")
        failed.append(song)
        continue
    
    # 选择第一个结果
    source, best = results[0]
    
    try:
        songname = best.songname if hasattr(best, 'songname') else str(best)
        singers = best.singers if hasattr(best, 'singers') else 'Backstreet Boys'
        filesize = best.filesize if hasattr(best, 'filesize') else 'Unknown'
        
        print(f"   ✅ 找到: {songname}")
        
        # 获取下载链接
        download_url = None
        if hasattr(best, 'download_url'):
            download_url = best.download_url
        elif hasattr(best, 'url'):
            download_url = best.url
            
        if download_url:
            ext = 'flac'
            if hasattr(best, 'ext') and best.ext:
                ext = best.ext
                
            filename = f"Backstreet Boys - {song}.{ext}"
            filepath = os.path.join(save_dir, filename)
            
            print(f"   ⬇️  下载中...")
            try:
                response = requests.get(download_url, timeout=180, stream=True)
                if response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    print(f"   ✅ 已保存: {filename}")
                    downloaded += 1
                else:
                    print(f"   ❌ 下载失败: HTTP {response.status_code}")
                    failed.append(song)
            except Exception as e:
                print(f"   ❌ 下载错误: {e}")
                failed.append(song)
        else:
            print(f"   ❌ 无下载链接")
            failed.append(song)
            
    except Exception as e:
        print(f"   ❌ 处理错误: {e}")
        failed.append(song)

print("\n" + "="*60)
print(f"✅ 本次下载完成! 成功: {downloaded}/{len(songs)}")
if failed:
    print(f"❌ 失败: {len(failed)} 首")
    for s in failed:
        print(f"   - {s}")
