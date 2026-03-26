#!/bin/bash

# 复制音乐文件脚本
SOURCE_DIR="/Volumes/disk-hfm/music"
TARGET_DIR="/Volumes/Tesladrive"

# 定义要优先复制的经典英文歌曲（FLAC格式）
CLASSIC_FLAC=(
    "Backstreet Boys - All I Have To Give.flac"
    "Backstreet Boys - Anywhere For You.flac"
    "Backstreet Boys - As Long As You Love Me.flac"
    "Backstreet Boys - Drowning.flac"
    "Backstreet Boys - Everybody.flac"
    "Backstreet Boys - Get Down.flac"
    "Backstreet Boys - I Want It That Way.flac"
    "Backstreet Boys - I'll Never Break Your Heart.flac"
    "Backstreet Boys - Incomplete.flac"
    "Backstreet Boys - Larger Than Life.flac"
    "Backstreet Boys - More Than That.flac"
    "Backstreet Boys - Quit Playing Games.flac"
    "Backstreet Boys - Shape Of My Heart.flac"
    "Backstreet Boys - Show Me The Meaning Of Being Lonely.flac"
    "Backstreet Boys - The One.flac"
    "Eagles - Hotel California.flac"
    "John Lennon - Imagine.flac"
    "Madonna - Like a Prayer.flac"
    "Nirvana - Smells Like Teen Spirit.flac"
    "Oasis - Wonderwall.flac"
    "Queen - Bohemian Rhapsody.flac"
    "The Weeknd - Blinding Lights.flac"
    "Adele - Rolling in the Deep.flac"
    "Ed Sheeran - Shape of You.flac"
    "Michael Jackson - Billie Jean.flac"
    "Westlife - I Lay My Love On You.flac"
    "Westlife - My Love.mp3"
    "Westlife - Nothing's Gonna Change My Love For You.flac"
    "Westlife - Seasons In The Sun.flac"
    "Westlife - You Raise Me Up.flac"
)

# 定义其他MP3歌曲
OTHER_MP3=(
    "001.唐伯虎Annie-落 (花开花落日升日没).mp3"
    "G.E.M. 邓紫棋 - 桃花诺.mp3"
    "I Will Always Love You - Whitney Houston.mp3"
    "Just the Way You Are 火星哥 开场白甜死人.mp3"
    "Perfect 中英字幕 - Ed Sheeran[超清版].mp3"
    "Various Artists - 回家的路.mp3"
    "【1993奥斯卡金曲】A whole new world ——Peabo Bryson & Regina Belle.mp3"
    "【4K120帧】The Beatles《Yesterday》1965纽约现场 AI修复补帧画质增强版.mp3"
    "【4K60FPS】阿黛尔《Hello》火力全开的现场！大气磅礴的一首歌.mp3"
    "【4K60FPS】阿黛尔《Someone Like You》万人大合唱现场！.mp3"
    "【4K修复】迈克尔杰克逊《Heal The World》1991 MV.中英字幕版.mp3"
    "【Ed sheeran】Thinking Out Loud  (不插电).mp3"
    "【纯人声组合】【PTX】Can you feel the love tonight 惊艳翻唱 p01 【纯人声组合】【PTX】Can you feel the love tonight 惊艳翻唱.mp3"
    "七叔（叶泽浩） - 半生雪.mp3"
    "不是鱼 - 今生啊 多相见 (女版).mp3"
    "云朵-化风行万里.mp3"
    "伍佰 - Last Dance.flac"
    "伍佰 - 挪威的森林.flac"
    "伍佰 - 浪人情歌.flac"
    "伍佰 - 爱你一万年.flac"
    "伍佰 - 突然的自我.flac"
    "兄弟们,又要到神曲了《Right Here Waiting》传世名曲-此情可待Richard Marx理查德·马克斯4K120帧 HiRes无损音质.mp3"
    "六小乐 - 大风在刮大雪在下 (别在这个冬把我丢下).mp3"
    "单依纯 - 李白 (Live).mp3"
    "如愿 - 王菲.mp3"
    "崔子格 - 卜卦.mp3"
    "左手指月-萨顶顶.mp3"
    "张含韵 - 一百万个可能.mp3"
    "张钰儿 - 乌兰巴托的夜 (空灵女版).mp3"
    "张韶涵 - 阿刁 (Live).mp3"
    "李彤儿 - 谢谢你的爱 (女声版)(1).mp3"
    "浅影阿、汐音社 - 探故知.mp3"
    "王菲 - 心经.mp3"
    "王菲 - 金刚经.mp3"
    "程响 - 可能.mp3"
    "醉美谋女郎 - 郁可唯《时间煮雨》.mp3"
    "铃花儿 - 这一别是永远 (女版)(1).mp3"
    "阿美呀 - 相逢却匆匆.mp3"
    "陈小春 - 街角的晚风.mp3"
    "陈瑞 - 情罪.mp3"
    "jaycd - 梦中的婚礼(钢琴版).flac"
)

copied_count=0
total_size=0

# 检查磁盘空间函数（返回可用KB）
check_space() {
    df -k "$TARGET_DIR" | awk 'NR==2 {print $4}'
}

# 复制文件函数
copy_file() {
    local file="$1"
    local src="$SOURCE_DIR/$file"
    local dst="$TARGET_DIR/$file"
    
    # 检查源文件是否存在
    if [[ ! -f "$src" ]]; then
        echo "跳过: $file (源文件不存在)"
        return
    fi
    
    # 检查目标文件是否已存在
    if [[ -f "$dst" ]]; then
        echo "跳过: $file (已存在)"
        return
    fi
    
    # 获取文件大小
    local file_size=$(stat -f%z "$src" 2>/dev/null || stat -c%s "$src" 2>/dev/null)
    local file_size_mb=$((file_size / 1024 / 1024))
    
    # 检查磁盘空间
    local available_kb=$(check_space)
    local file_size_kb=$((file_size / 1024))
    
    # 预留10MB空间作为缓冲
    if [[ $((available_kb - file_size_kb)) -lt 10240 ]]; then
        echo "磁盘空间不足，停止复制"
        echo "需要: ${file_size_mb}MB, 可用: $((available_kb / 1024))MB"
        return 1
    fi
    
    # 复制文件
    echo "复制: $file (${file_size_mb}MB)"
    if cp "$src" "$dst"; then
        copied_count=$((copied_count + 1))
        total_size=$((total_size + file_size))
        echo "  ✓ 成功复制 ($copied_count 首)"
    else
        echo "  ✗ 复制失败"
    fi
    
    # 显示剩余空间
    local remaining=$(check_space)
    echo "  剩余空间: $((remaining / 1024 / 1024)).$(((remaining / 1024) % 1024 / 100)) GB"
}

echo "=========================================="
echo "开始复制音乐文件"
echo "源目录: $SOURCE_DIR"
echo "目标目录: $TARGET_DIR"
echo "=========================================="
echo ""

# 首先复制经典英文歌曲（FLAC优先）
echo "【阶段1】复制经典英文歌曲..."
echo "------------------------------------------"
for file in "${CLASSIC_FLAC[@]}"; do
    if ! copy_file "$file"; then
        break
    fi
done

echo ""
echo "【阶段2】复制其他MP3歌曲..."
echo "------------------------------------------"
for file in "${OTHER_MP3[@]}"; do
    if ! copy_file "$file"; then
        break
    fi
done

echo ""
echo "=========================================="
echo "复制完成！"
echo "=========================================="
echo "成功复制歌曲数: $copied_count 首"
echo "总共占用空间: $((total_size / 1024 / 1024)).$(((total_size / 1024) % 1024 / 100)) MB ($((total_size / 1024 / 1024 / 1024)).$(((total_size / 1024 / 1024) % 1024 / 100)) GB)"

# 显示最终磁盘空间
df -h "$TARGET_DIR"
