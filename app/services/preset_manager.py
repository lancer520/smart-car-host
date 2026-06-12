import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class PIDPreset:
    name: str
    p: float
    i: float
    d: float
    description: str = ""

class PresetManager:
    def __init__(self, preset_file="pid_presets.json"):
        self.preset_file = preset_file
        self.presets: Dict[str, PIDPreset] = {}
        self.load_presets()
    
    def load_presets(self):
        if os.path.exists(self.preset_file):
            try:
                with open(self.preset_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for name, preset_data in data.items():
                        self.presets[name] = PIDPreset(
                            name=name,
                            p=preset_data['p'],
                            i=preset_data['i'],
                            d=preset_data['d'],
                            description=preset_data.get('description', '')
                        )
            except Exception as e:
                print(f"加载预设失败: {e}")
    
    def save_presets(self):
        try:
            data = {}
            for name, preset in self.presets.items():
                data[name] = {
                    'p': preset.p,
                    'i': preset.i,
                    'd': preset.d,
                    'description': preset.description
                }
            with open(self.preset_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存预设失败: {e}")
            return False
    
    def add_preset(self, name: str, p: float, i: float, d: float, description: str = ""):
        self.presets[name] = PIDPreset(name=name, p=p, i=i, d=d, description=description)
        return self.save_presets()
    
    def remove_preset(self, name: str):
        if name in self.presets:
            del self.presets[name]
            return self.save_presets()
        return False
    
    def get_preset(self, name: str) -> Optional[PIDPreset]:
        return self.presets.get(name)
    
    def get_preset_names(self) -> List[str]:
        return list(self.presets.keys())
    
    def get_all_presets(self) -> Dict[str, PIDPreset]:
        return self.presets.copy()