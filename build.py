import subprocess
import sys
import os

def build_executable():
    print("构建可执行文件...")
    
    # 使用PyInstaller构建
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "SmartCarDebugger",
        "main.py"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("构建成功！")
        print(f"可执行文件位置: {os.path.join('dist', 'SmartCarDebugger')}")
    else:
        print("构建失败！")
        print(result.stderr)
        return False
    
    return True

if __name__ == "__main__":
    build_executable()