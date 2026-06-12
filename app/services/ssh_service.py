import paramiko
import threading
import time
from typing import Callable, Optional

class SSHService:
    def __init__(self):
        self.client = None
        self.is_connected = False
        self.host = ""
        self.port = 22
        self.read_thread = None
        self.running = False
        self.data_callback: Optional[Callable] = None
        self.shell = None
    
    def connect(self, host, port, username, password=None, key_file=None, timeout=10):
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            connect_kwargs = {
                'hostname': host,
                'port': port,
                'username': username,
                'timeout': timeout
            }
            
            if key_file:
                connect_kwargs['key_filename'] = key_file
            elif password:
                connect_kwargs['password'] = password
            else:
                raise ValueError("必须提供密码或密钥文件")
            
            self.client.connect(**connect_kwargs)
            self.host = host
            self.port = port
            self.is_connected = True
            
            # 获取交互式shell用于实时通信
            self.shell = self.client.invoke_shell()
            self.start_reading()
            
            return True
        except Exception as e:
            print(f"SSH连接失败: {e}")
            return False
    
    def disconnect(self):
        self.stop_reading()
        if self.shell:
            self.shell.close()
        if self.client:
            self.client.close()
        self.is_connected = False
        self.host = ""
    
    def start_reading(self):
        if self.is_connected and not self.running and self.shell:
            self.running = True
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()
    
    def stop_reading(self):
        self.running = False
        if self.read_thread:
            self.read_thread.join(timeout=1)
    
    def _read_loop(self):
        while self.running and self.is_connected and self.shell:
            try:
                if self.shell.recv_ready():
                    data = self.shell.recv(4096)
                    if data and self.data_callback:
                        self.data_callback(data)
                time.sleep(0.01)
            except Exception as e:
                print(f"SSH读取数据错误: {e}")
                break
    
    def send_data(self, data):
        if self.is_connected and self.shell:
            try:
                if isinstance(data, str):
                    data = data.encode()
                self.shell.send(data)
                return True
            except Exception as e:
                print(f"SSH发送数据错误: {e}")
                return False
        return False
    
    def execute_command(self, command):
        if self.is_connected and self.client:
            try:
                stdin, stdout, stderr = self.client.exec_command(command)
                output = stdout.read().decode()
                error = stderr.read().decode()
                return {
                    'success': True,
                    'output': output,
                    'error': error
                }
            except Exception as e:
                return {
                    'success': False,
                    'output': '',
                    'error': str(e)
                }
        return {
            'success': False,
            'output': '',
            'error': '未连接'
        }
    
    def set_data_callback(self, callback):
        self.data_callback = callback