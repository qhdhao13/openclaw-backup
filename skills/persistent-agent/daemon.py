#!/usr/bin/env python3
"""
持久化代理守护进程
24小时常驻 · 开机自启 · 崩溃自动重启
"""

import os
import sys
import time
import signal
import subprocess
from pathlib import Path

PID_FILE = Path.home() / ".openclaw" / "workspace" / ".daemon.pid"
LOG_FILE = Path.home() / ".openclaw" / "workspace" / ".daemon.log"

def log(message):
    """记录日志"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

class PersistentDaemon:
    """持久化守护进程"""
    
    def __init__(self):
        self.running = False
        self.restart_count = 0
        self.max_restarts = 100  # 防止无限重启
        
    def start(self):
        """启动守护进程"""
        self.running = True
        
        # 写入PID文件
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))
        
        log("🤖 持久化守护进程已启动")
        log("📌 PID: " + str(os.getpid()))
        log("🔒 24小时持续运行模式")
        
        # 注册信号处理
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)
        
        # 主循环
        self._main_loop()
    
    def _main_loop(self):
        """主循环 - 保持运行"""
        while self.running:
            try:
                # 检查OpenClaw网关状态
                self._check_gateway()
                
                # 检查技能状态
                self._check_skills()
                
                # 等待下一轮检查
                time.sleep(60)  # 每分钟检查一次
                
            except Exception as e:
                log(f"❌ 错误: {str(e)}")
                self._handle_error()
    
    def _check_gateway(self):
        """检查网关状态"""
        try:
            # 检查端口18789
            result = subprocess.run(
                ["lsof", "-i", ":18789"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if "openclaw" not in result.stdout.lower():
                log("⚠️ 网关未运行，尝试重启...")
                self._restart_gateway()
        except:
            pass
    
    def _check_skills(self):
        """检查技能状态"""
        # 检查核心技能文件是否存在
        skills_dir = Path.home() / ".openclaw" / "workspace" / "skills"
        core_skills = ["long-term-memory", "voice-wakeup", "jarvis-core", "persistent-agent", "self-learning"]
        
        for skill in core_skills:
            skill_file = skills_dir / skill / "skill.json"
            if not skill_file.exists():
                log(f"⚠️ 核心技能缺失: {skill}")
    
    def _restart_gateway(self):
        """重启网关"""
        if self.restart_count >= self.max_restarts:
            log("❌ 重启次数过多，停止尝试")
            return
        
        try:
            subprocess.run(["openclaw", "gateway", "restart"], timeout=30)
            self.restart_count += 1
            log(f"✅ 网关已重启 (第{self.restart_count}次)")
        except Exception as e:
            log(f"❌ 网关重启失败: {str(e)}")
    
    def _handle_error(self):
        """处理错误"""
        if self.restart_count < self.max_restarts:
            log("🔄 遇到错误，准备自动恢复...")
            time.sleep(5)
            self.restart_count += 1
        else:
            log("❌ 错误处理失败，守护进程退出")
            self.running = False
    
    def _handle_signal(self, signum, frame):
        """处理信号"""
        log(f"📡 收到信号: {signum}")
        self.running = False
        
        # 清理PID文件
        if PID_FILE.exists():
            PID_FILE.unlink()
        
        log("👋 守护进程已安全退出")
        sys.exit(0)
    
    def get_status(self):
        """获取守护进程状态"""
        if PID_FILE.exists():
            with open(PID_FILE, 'r') as f:
                pid = f.read().strip()
            return {
                "running": True,
                "pid": pid,
                "status": "🛡️ 守护进程运行中 - 24小时保护",
                "auto_restart": True,
                "restart_count": self.restart_count
            }
        return {
            "running": False,
            "status": "⚠️ 守护进程未运行"
        }

# 全局实例
daemon = PersistentDaemon()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        status = daemon.get_status()
        print(status["status"])
        sys.exit(0 if status["running"] else 1)
    
    daemon.start()
