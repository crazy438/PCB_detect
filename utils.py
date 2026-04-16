import pathlib
import socket
import subprocess
import sys
import time


def is_img(file_path):
    return pathlib.Path(file_path).suffix in (".jpg", ".png", ".bmp") if file_path else False

def is_video(file_path):
    return pathlib.Path(file_path).suffix in (".mp4", ".avi", ".mkv") if file_path else False

def is_ollama_running(host, port, timeout):
    """检测 ollama server 是否在运行"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def start_ollama_server(host="localhost", port=11434, timeout=1):
    """后台启动 ollama serve，不显示黑窗口"""
    if is_ollama_running(host, port, timeout):
        print("ollama 已运行，无需启动")
        return

    try:
        # 后台静默启动，不弹窗
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0

        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        )
        print("已启动 ollama server")

        # 等待服务就绪
        for _ in range(10):
            if is_ollama_running(host, port, timeout):
                break
            time.sleep(0.5)
    except:
        print("启动 ollama 失败，请确保已安装 ollama")