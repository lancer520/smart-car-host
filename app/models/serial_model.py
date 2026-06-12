from dataclasses import dataclass
from typing import Dict, Any
import time

@dataclass
class SerialData:
    timestamp: float
    raw_data: bytes
    parsed_data: Dict[str, Any]

class SerialModel:
    def __init__(self):
        self.port = ""
        self.baudrate = 115200
        self.bytesize = 8
        self.parity = "N"
        self.stopbits = 1
        self.is_connected = False
        self.data_buffer = []
    
    def update_config(self, port, baudrate, bytesize=8, parity="N", stopbits=1):
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
    
    def add_data(self, raw_data, parsed_data):
        data = SerialData(
            timestamp=time.time(),
            raw_data=raw_data,
            parsed_data=parsed_data
        )
        self.data_buffer.append(data)
        return data
    
    def get_recent_data(self, count=10):
        return self.data_buffer[-count:] if self.data_buffer else []
    
    def clear_buffer(self):
        self.data_buffer.clear()