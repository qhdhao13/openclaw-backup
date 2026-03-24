#!/bin/bash
# 复制今天下载的歌曲到U盘

cd /Volumes/disk-hfm/music

echo "开始复制今天下载的歌曲到U盘..."
echo "=========================================="

copied=0

# Backstreet Boys 歌曲
for file in Backstreet*.flac; do
  if [ -f "$file" ]; then
    echo "复制: $file"
    cp "$file" /Volumes/KINGSTON/ && ((copied++))
  fi
done

# Westlife 歌曲
for file in Westlife*.flac Westlife*.mp3; do
  if [ -f "$file" ]; then
    echo "复制: $file"
    cp "$file" /Volumes/KINGSTON/ && ((copied++))
  fi
done

# 伍佰 歌曲
for file in 伍佰*.flac; do
  if [ -f "$file" ]; then
    echo "复制: $file"
    cp "$file" /Volumes/KINGSTON/ && ((copied++))
  fi
done

# 英文经典歌曲
classics=(
  "Eagles - Hotel California.flac"
  "Queen - Bohemian Rhapsody.flac"
  "John Lennon - Imagine.flac"
  "Michael Jackson - Billie Jean.flac"
  "Madonna - Like a Prayer.flac"
  "Nirvana - Smells Like Teen Spirit.flac"
  "Oasis - Wonderwall.flac"
  "Adele - Rolling in the Deep.flac"
  "Ed Sheeran - Shape of You.flac"
  "The Weeknd - Blinding Lights.flac"
)

for file in "${classics[@]}"; do
  if [ -f "$file" ]; then
    echo "复制: $file"
    cp "$file" /Volumes/KINGSTON/ && ((copied++))
  fi
done

echo "=========================================="
echo "✅ 复制完成! 共复制 $copied 首歌曲到U盘"
