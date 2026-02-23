#!/bin/bash
# 庄子每日精读快捷命令

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/zhuangzi_daily.py" "$@"
