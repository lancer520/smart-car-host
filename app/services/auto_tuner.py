import time
from typing import List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class TuningResult:
    ku: float  # 临界增益
    tu: float  # 临界周期
    p: float
    i: float
    d: float
    algorithm: str

class AutoTuner:
    def __init__(self):
        self.is_tuning = False
        self.algorithm = "ziegler_nichols"
        self.tuning_history: List[TuningResult] = []
        self.step_response_data: List[Tuple[float, float]] = []
    
    def set_algorithm(self, algorithm: str):
        valid_algorithms = ["ziegler_nichols", "cohen_coon", "some_overshoot", "no_overshoot"]
        if algorithm in valid_algorithms:
            self.algorithm = algorithm
    
    def start_tuning(self, setpoint: float = 100.0):
        self.is_tuning = True
        self.step_response_data.clear()
        return setpoint
    
    def stop_tuning(self):
        self.is_tuning = False
    
    def add_data_point(self, time: float, value: float):
        if self.is_tuning:
            self.step_response_data.append((time, value))
    
    def calculate_tuning_params(self) -> Optional[TuningResult]:
        if len(self.step_response_data) < 10:
            return None
        
        # 简化的Ziegler-Nichols方法
        # 实际应用中需要更复杂的算法
        values = [point[1] for point in self.step_response_data]
        setpoint = values[0]  # 假设第一个点是设定值
        
        # 计算临界增益和周期（简化版）
        ku = self._calculate_critical_gain(values, setpoint)
        tu = self._calculate_critical_period()
        
        # 根据算法计算PID参数
        p, i, d = self._calculate_pid_params(ku, tu)
        
        result = TuningResult(
            ku=ku,
            tu=tu,
            p=p,
            i=i,
            d=d,
            algorithm=self.algorithm
        )
        
        self.tuning_history.append(result)
        self.is_tuning = False
        
        return result
    
    def _calculate_critical_gain(self, values: List[float], setpoint: float) -> float:
        # 简化的临界增益计算
        if not values:
            return 1.0
        
        max_deviation = max(abs(v - setpoint) for v in values)
        return 100.0 / max(max_deviation, 0.1)
    
    def _calculate_critical_period(self) -> float:
        # 简化的临界周期计算
        if len(self.step_response_data) < 2:
            return 1.0
        
        return self.step_response_data[-1][0] - self.step_response_data[0][0]
    
    def _calculate_pid_params(self, ku: float, tu: float) -> Tuple[float, float, float]:
        if self.algorithm == "ziegler_nichols":
            p = 0.6 * ku
            i = tu / 2.0
            d = tu / 8.0
        elif self.algorithm == "cohen_coon":
            p = 1.35 * ku
            i = tu / 1.2
            d = tu / 6.0
        elif self.algorithm == "some_overshoot":
            p = 0.33 * ku
            i = tu / 2.0
            d = tu / 3.0
        elif self.algorithm == "no_overshoot":
            p = 0.2 * ku
            i = tu / 2.0
            d = tu / 3.0
        else:
            p, i, d = 1.0, 0.1, 0.01
        
        return p, i, d
    
    def get_tuning_history(self):
        return self.tuning_history
    
    def clear_history(self):
        self.tuning_history.clear()