from dataclasses import dataclass
from typing import List
import time

@dataclass
class PIDData:
    timestamp: float
    p: float
    i: float
    d: float
    setpoint: float
    actual: float
    
    @property
    def error(self):
        return self.setpoint - self.actual

class PIDModel:
    def __init__(self):
        self.p = 1.0
        self.i = 0.1
        self.d = 0.01
        self.setpoint = 0.0
        self.history: List[PIDData] = []
        self.max_history = 1000
    
    def update_params(self, p, i, d):
        self.p = p
        self.i = i
        self.d = d
    
    def set_setpoint(self, setpoint):
        self.setpoint = setpoint
    
    def add_data(self, actual):
        data = PIDData(
            timestamp=time.time(),
            p=self.p,
            i=self.i,
            d=self.d,
            setpoint=self.setpoint,
            actual=actual
        )
        self.history.append(data)
        
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        return data
    
    def get_history(self, count=100):
        return self.history[-count:] if self.history else []
    
    def clear_history(self):
        self.history.clear()