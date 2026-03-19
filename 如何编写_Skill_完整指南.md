# 如何编写 Agent Skill - 完整指南

## 一、Skill 是什么？

Skill 是 AI Agent 的**功能扩展插件**，让 AI 获得特定能力：
- 下载抖音视频
- 分析代码质量
- 生成图表
- 连接外部 API
- ...无限可能

类比：就像给手机安装 App，让手机获得新功能。

---

## 二、Skill 的文件结构

一个标准的 Skill 包含以下文件：

```
my-skill/
├── SKILL.md          # 技能描述文件（必须）
├── scripts/          # 核心脚本目录
│   └── main.py       # 主实现脚本
├── requirements.txt  # Python 依赖（可选）
└── README.md         # 详细文档（可选）
```

---

## 三、SKILL.md 编写规范

SKILL.md 是 Skill 的"身份证"，必须包含：

```markdown
---
name: skill-name                    # 技能名称（英文，小写，短横线连接）
description: 简短描述技能功能      # 一句话描述，30字以内
---

# Skill 名称

## 概述

详细描述这个 Skill 能做什么，解决什么问题。

## 何时使用

- 场景1：具体使用场景描述
- 场景2：另一个使用场景
- 场景3：更多场景...

## 使用方法

### 方式一：命令行调用
```bash
python scripts/main.py [参数]
```

### 方式二：自然语言调用
直接告诉 AI："使用 [skill-name] 做 [任务]"

## 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| param1 | string | 是 | 参数说明 |
| param2 | int | 否 | 参数说明，默认值：10 |

## 输出

描述 Skill 的输出格式和内容。

## 注意事项

- 重要提示1
- 重要提示2
- 安全警告（如有）

## 依赖

- Python 3.8+
- 依赖包1
- 依赖包2
```

---

## 四、核心脚本编写

### 4.1 基础模板

```python
#!/usr/bin/env python3
"""
Skill 主脚本
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description='Skill 描述')
    parser.add_argument('input', help='输入参数')
    parser.add_argument('--output', '-o', help='输出路径')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 核心逻辑
    result = process(args.input, args.output, args.verbose)
    
    # 输出结果
    print(result)
    return 0 if result else 1


def process(input_path, output_path=None, verbose=False):
    """
    核心处理函数
    
    Args:
        input_path: 输入路径
        output_path: 输出路径（可选）
        verbose: 是否详细输出
    
    Returns:
        bool: 是否成功
    """
    try:
        # 1. 读取输入
        # 2. 处理逻辑
        # 3. 保存输出
        # 4. 返回结果
        return True
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        return False


if __name__ == '__main__':
    sys.exit(main())
```

### 4.2 进阶模板（带进度显示）

```python
#!/usr/bin/env python3
"""
带进度显示的 Skill 模板
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Skill 描述')
    parser.add_argument('input', help='输入参数')
    parser.add_argument('--output-dir', '-o', default='./output', help='输出目录')
    parser.add_argument('--format', choices=['json', 'txt', 'md'], default='json', help='输出格式')
    
    args = parser.parse_args()
    
    # 确保输出目录存在
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 执行处理
    results = process_with_progress(args.input, output_dir, args.format)
    
    # 汇总输出
    print(f"\n处理完成: {len(results)} 项")
    for r in results:
        print(f"  - {r}")
    
    return 0


def process_with_progress(input_path, output_dir, format_type):
    """带进度显示的处理"""
    items = get_items(input_path)
    results = []
    
    for i, item in enumerate(items, 1):
        print(f"[{i}/{len(items)}] 处理: {item}...", end=' ')
        try:
            result = process_item(item, output_dir, format_type)
            results.append(result)
            print("✓")
        except Exception as e:
            print(f"✗ ({e})")
    
    return results


def get_items(input_path):
    """获取待处理项目列表"""
    # 实现逻辑
    return []


def process_item(item, output_dir, format_type):
    """处理单个项目"""
    # 实现逻辑
    return output_dir / f"{item}.{format_type}"


if __name__ == '__main__':
    sys.exit(main())
```

---

## 五、Skill 开发最佳实践

### 5.1 命名规范

- **Skill 名称**：小写字母 + 短横线，如 `video-downloader`
- **脚本名称**：描述性强，如 `download.py`, `analyze.py`
- **变量命名**：snake_case，如 `output_dir`, `max_retries`

### 5.2 错误处理

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def safe_process(input_path):
    try:
        result = process(input_path)
        logger.info(f"成功处理: {input_path}")
        return result
    except FileNotFoundError:
        logger.error(f"文件不存在: {input_path}")
        return None
    except Exception as e:
        logger.exception(f"处理失败: {e}")
        return None
```

### 5.3 输入验证

```python
from pathlib import Path

def validate_input(input_path):
    """验证输入"""
    path = Path(input_path)
    
    if not path.exists():
        raise FileNotFoundError(f"路径不存在: {input_path}")
    
    if not path.is_file():
        raise ValueError(f"不是文件: {input_path}")
    
    # 检查文件大小
    max_size = 100 * 1024 * 1024  # 100MB
    if path.stat().st_size > max_size:
        raise ValueError(f"文件过大: {path.stat().st_size} bytes")
    
    return path
```

### 5.4 输出规范

```python
import json
from datetime import datetime

def format_output(data, format_type='json'):
    """格式化输出"""
    result = {
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'data': data
    }
    
    if format_type == 'json':
        return json.dumps(result, ensure_ascii=False, indent=2)
    elif format_type == 'txt':
        return f"成功: {data}"
    else:
        return str(data)
```

---

## 六、Skill 安装与测试

### 6.1 本地测试

```bash
# 1. 进入 Skill 目录
cd my-skill

# 2. 安装依赖
pip install -r requirements.txt

# 3. 测试运行
python scripts/main.py --help
python scripts/main.py test-input.txt --output-dir ./test-output
```

### 6.2 发布到 Skills 生态

```bash
# 1. 初始化 Skill 仓库
npx skills init my-skill

# 2. 发布到 GitHub
# 创建仓库，推送代码

# 3. 安装使用
npx skills add username/repo@skill-name
```

---

## 七、完整示例：抖音视频下载 Skill

### SKILL.md

```markdown
---
name: douyin-video-fetch
description: 下载抖音视频到本地（无水印优先）
---

# Douyin Video Fetch

## 概述

把抖音链接下载成可分析的本地 mp4。

## 何时使用

- 需要把目标视频落地到本地做拆解
- 拿到的是 video_id，想直接下载
- 要批量下载一组抖音视频做样本库

## 使用方法

```bash
python scripts/fetch_video.py "https://www.douyin.com/video/xxx"
```

## 输出

- 默认输出目录：`./downloads`
- 文件名：`<video_id>.mp4`

## 依赖

- Python 3.8+
- playwright
- aiohttp
```

### scripts/fetch_video.py

```python
#!/usr/bin/env python3
"""抖音视频下载脚本"""

import asyncio
import argparse
import os
from pathlib import Path

async def download_video(url, output_dir):
    """下载视频核心逻辑"""
    # 实现下载逻辑
    pass

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='抖音视频链接')
    parser.add_argument('--output-dir', default='./downloads')
    args = parser.parse_args()
    
    os.makedirs(args.output_dir, exist_ok=True)
    asyncio.run(download_video(args.url, args.output_dir))

if __name__ == '__main__':
    main()
```

---

## 八、安全检查清单

发布 Skill 前，检查以下事项：

- [ ] **权限最小化**：只请求必要的权限
- [ ] **输入验证**：所有用户输入都经过验证
- [ ] **错误处理**：所有异常都被捕获和处理
- [ ] **日志记录**：关键操作有日志记录
- [ ] **文档完整**：SKILL.md 描述清晰完整
- [ ] **代码审查**：没有硬编码的密钥或敏感信息
- [ ] **测试通过**：本地测试通过

---

## 九、参考资源

- **Skills 官方文档**：https://skills.sh/
- **示例 Skills**：https://github.com/vercel-labs/agent-skills
- **MCP 协议**：https://modelcontextprotocol.io/

---

**总结**：编写 Skill 的核心是清晰的接口定义（SKILL.md）+ 健壮的实现（scripts）+ 完善的安全考虑。遵循这些规范，你的 Skill 就能被 AI Agent 轻松调用！
