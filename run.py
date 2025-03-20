#!/usr/bin/env python3
"""
DeepSeek Chat 启动脚本
用于启动已构建的应用
"""
import os
import sys
import subprocess
from pathlib import Path

# 项目根目录
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / 'backend'
STATIC_DIR = BACKEND_DIR / 'static'

def main():
    # 检查后端目录是否存在
    if not BACKEND_DIR.exists():
        print(f"错误: 后端目录不存在 - {BACKEND_DIR}")
        return False
    
    # 检查是否已经构建前端
    if not STATIC_DIR.exists() or not list(STATIC_DIR.glob('*')):
        print("警告: 前端文件不存在，尝试先构建...")
        try:
            build_script = ROOT_DIR / 'build.py'
            if build_script.exists():
                subprocess.run([sys.executable, str(build_script)], check=True)
            else:
                print(f"错误: 构建脚本不存在 - {build_script}")
                return False
        except subprocess.CalledProcessError as e:
            print(f"构建失败: {e}")
            return False
    
    # 启动后端应用
    print("启动 DeepSeek Chat 应用...")
    os.chdir(BACKEND_DIR)
    
    # 检查环境变量
    env_file = BACKEND_DIR / '.env'
    if not env_file.exists():
        print("警告: .env 文件不存在，应用可能无法正常工作")
        print("请在 backend/.env 文件中配置 DEEPSEEK_API_KEY 和 DEEPSEEK_BASE_URL")
    
    # 检查依赖
    try:
        subprocess.run([
            sys.executable, "-c", 
            "import flask, flask_cors, openai, duckdb, dotenv"
        ], check=True)
    except subprocess.CalledProcessError:
        print("安装缺失的依赖...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", 
            str(BACKEND_DIR / "requirements.txt")
        ])
    
    # 启动应用
    try:
        print("\n🚀 DeepSeek Chat 应用已启动!")
        print("在浏览器中访问 http://localhost:5000 开始使用")
        print("按 Ctrl+C 停止服务\n")
        subprocess.run([sys.executable, "app.py"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"启动失败: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 