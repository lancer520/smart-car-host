import serial
import serial.tools.list_ports
import threading
import time
from typing import Callable, Optional

class SerialService:
    def __init__(self):
        self.serial = None
        self.is_connected = False
        self.port = ""
        self.read_thread = None
        self.running = False
        self.data_callback: Optional[Callable] = None
    
    def get_available_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def connect(self, port, baudrate, bytesize=8, parity="N", stopbits=1, timeout=1):
        try:
            self.serial = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=bytesize,
                parity=parity,
                stopbits=stopbits,
                timeout=timeout
            )
            self.port = port
            self.is_connected = True
            self.start_reading()
            return True
        except Exception as e:
            print(f"连接失败: {e}")
            return False
    
    def disconnect(self):
        self.stop_reading()
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.is_connected = False
        self.port = ""
    
    def start_reading(self):
        if self.is_connected and not self.running:
            self.running = True
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()
    
    def stop_reading(self):
        self.running = False
        if self.read_thread:
            self.read_thread.join(timeout=1)
    
    def _read_loop(self):
        while self.running and self.is_connected:
            try:
                if self.serial and self.serial.in_waiting:
                    data = self.serial.read(self.serial.in_waiting)
                    if data and self.data_callback:
                        self.data_callback(data)
                time.sleep(0.01)
            except Exception as e:
                print(f"读取数据错误: {e}")
                break
    
    def send_data(self, data):
        if self.is_connected and self.serial:
            try:
                if isinstance(data, str):
                    data = data.encode()
                self.serial.write(data)
                return True
            except Exception as e:
                print(f"发送数据错误: {e}")
                return False
        return False
    
    def set_data_callback(self, callback):
        self.data_callback = callback