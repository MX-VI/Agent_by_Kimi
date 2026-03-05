"""
系统命令执行工具模块
支持安全的系统命令执行
"""
import subprocess
import shlex
import re
from pathlib import Path


class CommandTool:
    """系统命令执行工具类"""
    
    # 危险命令黑名单（完全禁止）
    DANGEROUS_PATTERNS = [
        r'rm\s+-rf\s+/',
        r'rm\s+-rf\s+\*',
        r'format\s+',
        r'dd\s+if=.*of=/dev/',
        r'mkfs\.',
        r'del\s+/f\s+/s\s+/q',
        r'rmdir\s+/s\s+/q',
    ]
    
    # 需要确认的危险命令
    CAUTION_COMMANDS = [
        'rm', 'del', 'rmdir',
        'format', 'fdisk', 'diskpart',
        'reg', 'regedit',
    ]
    
    @staticmethod
    def is_dangerous(command: str) -> tuple[bool, str]:
        """
        检查命令是否包含危险操作
        
        Returns:
            (是否危险, 原因)
        """
        cmd_lower = command.lower().strip()
        
        # 检查黑名单模式
        for pattern in CommandTool.DANGEROUS_PATTERNS:
            if re.search(pattern, cmd_lower):
                return True, f"检测到危险操作模式: {pattern}"
        
        # 提取命令名
        cmd_parts = shlex.split(command)
        if not cmd_parts:
            return False, ""
        
        base_cmd = Path(cmd_parts[0]).name.lower()
        
        # 检查是否在危险命令列表
        if base_cmd in CommandTool.CAUTION_COMMANDS:
            return True, f"'{base_cmd}' 是危险命令，请谨慎操作"
        
        return False, ""
    
    @staticmethod
    def execute(command: str, timeout: int = 30) -> str:
        """
        执行系统命令
        
        Args:
            command: 要执行的命令
            timeout: 超时时间（秒）
            
        Returns:
            命令执行结果
        """
        if not command.strip():
            return "❌ 错误：命令不能为空"
        
        # 安全检查
        is_dangerous, reason = CommandTool.is_dangerous(command)
        if is_dangerous:
            return f"❌ 安全拦截：{reason}\n系统已阻止执行该命令以保护您的数据安全。"
        
        # 检测平台
        import sys
        is_windows = sys.platform == "win32"
        
        try:
            # 使用 subprocess 执行命令
            if is_windows:
                # Windows 使用 cmd /c
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'
                )
            else:
                # Linux/Mac 使用 sh
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'
                )
            
            # 等待执行结果
            stdout, stderr = process.communicate(timeout=timeout)
            
            # 构建输出
            result = []
            result.append(f"📟 命令: {command}")
            result.append(f"{'='*50}")
            
            if process.returncode == 0:
                result.append(f"✅ 执行成功 (退出码: {process.returncode})")
            else:
                result.append(f"⚠️ 执行完成但返回非零 (退出码: {process.returncode})")
            
            if stdout:
                result.append(f"\n📤 标准输出:\n{stdout}")
            
            if stderr:
                result.append(f"\n⚠️ 标准错误:\n{stderr}")
            
            if not stdout and not stderr:
                result.append("\n(无输出)")
            
            return "\n".join(result)
            
        except subprocess.TimeoutExpired:
            process.kill()
            return f"❌ 命令执行超时（{timeout}秒）: {command}\n进程已被终止。"
        except FileNotFoundError:
            return f"❌ 命令未找到: {command.split()[0]}\n请检查命令是否正确安装。"
        except Exception as e:
            return f"❌ 执行命令时出错: {str(e)}"
    
    @staticmethod
    def get_common_commands_help() -> str:
        """获取常用命令帮助"""
        import sys
        is_windows = sys.platform == "win32"
        
        if is_windows:
            return """
Windows 常用命令示例:
  dir                     - 列出当前目录文件
  dir C:\\Users            - 列出指定目录
  ipconfig                - 查看网络配置
  ping www.baidu.com      - 测试网络连接
  tasklist                - 查看运行中的进程
  systeminfo              - 查看系统信息
  echo %PATH%             - 查看环境变量
  cd /d D:\\              - 切换到 D 盘
"""
        else:
            return """
Linux/Mac 常用命令示例:
  ls -la                  - 列出当前目录文件
  pwd                     - 显示当前路径
  cat file.txt            - 查看文件内容
  ps aux                  - 查看运行中的进程
  ifconfig / ip addr      - 查看网络配置
  ping www.baidu.com      - 测试网络连接
  env                     - 查看环境变量
  df -h                   - 查看磁盘空间
"""
