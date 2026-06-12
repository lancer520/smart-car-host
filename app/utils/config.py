import json
import os

class Config:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return self.get_default_config()
    
    def get_default_config(self):
        return {
            "serial": {
                "port": "COM1",
                "baudrate": 115200,
                "bytesize": 8,
                "parity": "N",
                "stopbits": 1
            },
            "pid": {
                "p_range": [0, 100],
                "i_range": [0, 100],
                "d_range": [0, 100],
                "default_p": 1.0,
                "default_i": 0.1,
                "default_d": 0.01
            },
            "chart": {
                "update_interval": 100,
                "max_points": 1000
            }
        }
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, section, key=None):
        if key is None:
            return self.config.get(section, {})
        return self.config.get(section, {}).get(key)
    
    def set(self, section, key, value):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()