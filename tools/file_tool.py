"""
文件操作工具模块
"""
import os
from pathlib import Path


class FileTool:
    """文件操作工具类"""
    
    @staticmethod
    def read_file(file_path: str) -> str:
        """读取文件内容"""
        try:
            path = Path(file_path)
            if not path.exists():
                return f"❌ 错误：文件不存在 - {file_path}"
            if not path.is_file():
                return f"❌ 错误：路径不是文件 - {file_path}"
            
            # 检查文件大小（限制 10MB）
            if path.stat().st_size > 10 * 1024 * 1024:
                return f"❌ 错误：文件过大（>10MB），无法读取"
            
            # 尝试不同编码
            for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                try:
                    with open(path, 'r', encoding=encoding) as f:
                        content = f.read()
                    return f"✅ 文件读取成功：{file_path}\n\n{'='*50}\n{content}\n{'='*50}"
                except UnicodeDecodeError:
                    continue
            
            return f"❌ 错误：无法解码文件内容"
        except Exception as e:
            return f"❌ 读取文件时出错：{str(e)}"
    
    @staticmethod
    def write_file(file_path: str, content: str) -> str:
        """写入文件内容"""
        try:
            path = Path(file_path)
            
            # 确保父目录存在
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"✅ 文件写入成功：{file_path}"
        except Exception as e:
            return f"❌ 写入文件时出错：{str(e)}"
    
    @staticmethod
    def list_directory(dir_path: str = ".") -> str:
        """列出目录内容"""
        try:
            path = Path(dir_path)
            if not path.exists():
                return f"❌ 错误：目录不存在 - {dir_path}"
            if not path.is_dir():
                return f"❌ 错误：路径不是目录 - {dir_path}"
            
            items = []
            for item in path.iterdir():
                item_type = "📁" if item.is_dir() else "📄"
                size = ""
                if item.is_file():
                    size_bytes = item.stat().st_size
                    if size_bytes < 1024:
                        size = f"{size_bytes}B"
                    elif size_bytes < 1024 * 1024:
                        size = f"{size_bytes/1024:.1f}KB"
                    else:
                        size = f"{size_bytes/(1024*1024):.1f}MB"
                    size = f" ({size})"
                
                items.append(f"{item_type} {item.name}{size}")
            
            if not items:
                return f"📂 目录为空：{path.absolute()}"
            
            items.sort()
            return f"📂 目录内容：{path.absolute()}\n\n" + "\n".join(items)
        except Exception as e:
            return f"❌ 列出目录时出错：{str(e)}"
    
    @staticmethod
    def get_file_info(file_path: str) -> str:
        """获取文件信息"""
        try:
            path = Path(file_path)
            if not path.exists():
                return f"❌ 错误：路径不存在 - {file_path}"
            
            stat = path.stat()
            info = [
                f"📋 文件信息：{file_path}",
                f"{'='*50}",
                f"类型：{'📁 目录' if path.is_dir() else '📄 文件'}",
                f"大小：{stat.st_size} 字节",
                f"创建时间：{stat.st_ctime}",
                f"修改时间：{stat.st_mtime}",
                f"绝对路径：{path.absolute()}",
            ]
            return "\n".join(info)
        except Exception as e:
            return f"❌ 获取文件信息时出错：{str(e)}"
