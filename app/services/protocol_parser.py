import re
from typing import Dict, Any, Optional

class ProtocolParser:
    def __init__(self):
        self.parsers = {
            'text': self.parse_text_format,
            'json': self.parse_json_format,
            'binary': self.parse_binary_format
        }
        self.current_parser = 'text'
    
    def parse(self, data: bytes) -> Optional[Dict[str, Any]]:
        parser = self.parsers.get(self.current_parser)
        if parser:
            return parser(data)
        return None
    
    def parse_text_format(self, data: bytes) -> Optional[Dict[str, Any]]:
        try:
            text = data.decode('utf-8').strip()
            result = {}
            
            # 解析 "P=1.2,I=0.5,D=0.1" 格式
            pattern = r'([PID])=([+-]?\d*\.?\d+)'
            matches = re.findall(pattern, text)
            
            for key, value in matches:
                result[key] = float(value)
            
            # 解析速度值 "S=100.5"
            speed_match = re.search(r'S=([+-]?\d*\.?\d+)', text)
            if speed_match:
                result['speed'] = float(speed_match.group(1))
            
            return result if result else None
        except Exception:
            return None
    
    def parse_json_format(self, data: bytes) -> Optional[Dict[str, Any]]:
        try:
            import json
            text = data.decode('utf-8').strip()
            return json.loads(text)
        except Exception:
            return None
    
    def parse_binary_format(self, data: bytes) -> Optional[Dict[str, Any]]:
        # 简单的二进制协议示例
        if len(data) < 8:
            return None
        
        try:
            # 假设格式: [0xAA][长度][P_high][P_low][I_high][I_low][D_high][D_low]
            if data[0] != 0xAA:
                return None
            
            length = data[1]
            if len(data) < length + 2:
                return None
            
            p = (data[2] << 8 | data[3]) / 100.0
            i = (data[4] << 8 | data[5]) / 100.0
            d = (data[6] << 8 | data[7]) / 100.0
            
            return {'P': p, 'I': i, 'D': d}
        except Exception:
            return None
    
    def set_parser(self, parser_type):
        if parser_type in self.parsers:
            self.current_parser = parser_type
    
    def create_pid_command(self, p, i, d, format_type='text'):
        if format_type == 'text':
            return f"P={p:.2f},I={i:.2f},D={d:.2f}".encode()
        elif format_type == 'binary':
            # 二进制格式
            cmd = bytearray([0xAA, 0x08])
            cmd.extend([(int(p*100) >> 8) & 0xFF, int(p*100) & 0xFF])
            cmd.extend([(int(i*100) >> 8) & 0xFF, int(i*100) & 0xFF])
            cmd.extend([(int(d*100) >> 8) & 0xFF, int(d*100) & 0xFF])
            return bytes(cmd)
        return None