#!/usr/bin/env python3
"""下载伍佰传唱度前五的歌曲"""
import sys
sys.path.insert(0, '/Users/qhdh/.openclaw/workspace/venv-music/lib/python3.14/site-packages')

from musicdl.modules.sources import NeteaseMusicClient, QQMusicClient, MiguMusicClient, KuwoMusicClient
import os
import requests

# 设置下载目录
save_dir = "/Volumes/disk-hfm/music/伍佰"
os.makedirs(save_dir, exist_ok=True)

# 初始化音乐客户端
clients = {
    'netease': NeteaseMusicClient(),
    'qq': QQMusicClient(),
    'migu': MiguMusicClient(),
    'kuwo': KuwoMusicClient()
}

# 伍佰传唱度前五的歌曲
songs = [
    "挪威的森林",
    "Last Dance",
    "浪人情歌",
    "突然的自我",
    "爱你一万年"
]

print(f"开始下载伍佰 {len(songs)} 首传唱歌曲到 {save_dir}")
print("="*60)

downloaded = 0
failed = []

for song in songs:
    print(f"\n🎵 搜索: {song}")
    
    # 检查是否已存在
    filepath_flac = os.path.join(save_dir, f"伍佰 - {song}.flac")
    filepath_mp3 = os.path.join(save_dir, f"伍佰 - {song}.mp3")
    if os.path.exists(filepath_flac) or os.path.exists(filepath_mp3):
        print(f"   ⏭️  已存在，跳过")
        downloaded += 1
        continue
    
    results = []
    for name, client in clients.items():
        try:
            search_results = client.search(f"伍佰 {song}")
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
        singers = best.singers if hasattr(best, 'singers') else '伍佰'
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
                
            filename = f"伍佰 - {song}.{ext}"
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
print(f"✅ 下载完成! 成功: {downloaded}/{len(songs)}")
if failed:
    print(f"❌ 失败: {len(failed)} 首")
    for s in failed:
        print(f"   - {s}")
