from dataclasses import dataclass
from typing import List, Optional
import numpy as np

@dataclass
class PerformanceMetrics:
    """PID性能指标"""
    overshoot: float = 0.0        # 超调量 (%)
    settling_time: float = 0.0    # 调节时间 (s)
    rise_time: float = 0.0        # 上升时间 (s)
    peak_time: float = 0.0        # 峰值时间 (s)
    steady_state_error: float = 0.0  # 稳态误差
    peak_value: float = 0.0       # 峰值
    final_value: float = 0.0      # 最终值
    settling_band: float = 2.0    # 调节时间容差带 (%)

class PerformanceAnalyzer:
    def __init__(self):
        self.setpoint = 0.0
        self.settling_band = 2.0  # 默认2%容差带
        self.time_data: List[float] = []
        self.value_data: List[float] = []
        self.max_history = 10000
    
    def set_setpoint(self, setpoint: float):
        self.setpoint = setpoint
    
    def set_settling_band(self, band: float):
        """设置调节时间容差带(%)"""
        self.settling_band = band
    
    def add_data_point(self, time: float, value: float):
        """添加数据点"""
        self.time_data.append(time)
        self.value_data.append(value)
        
        if len(self.time_data) > self.max_history:
            self.time_data.pop(0)
            self.value_data.pop(0)
    
    def clear_data(self):
        """清空数据"""
        self.time_data.clear()
        self.value_data.clear()
    
    def calculate_metrics(self) -> Optional[PerformanceMetrics]:
        """计算性能指标"""
        if len(self.time_data) < 10 or self.setpoint == 0:
            return None
        
        times = np.array(self.time_data)
        values = np.array(self.value_data)
        
        metrics = PerformanceMetrics()
        metrics.settling_band = self.settling_band
        
        # 基本值
        metrics.peak_value = np.max(values)
        metrics.final_value = np.mean(values[-min(50, len(values)):])  # 最后50个点的平均
        
        # 超调量计算
        if self.setpoint > 0:
            overshoot = (metrics.peak_value - self.setpoint) / self.setpoint * 100
            metrics.overshoot = max(0, overshoot)
        
        # 峰值时间
        peak_idx = np.argmax(values)
        metrics.peak_time = times[peak_idx] - times[0]
        
        # 上升时间 (10% 到 90%)
        lower = self.setpoint * 0.1
        upper = self.setpoint * 0.9
        
        rise_start_idx = None
        rise_end_idx = None
        
        for i, v in enumerate(values):
            if rise_start_idx is None and v >= lower:
                rise_start_idx = i
            if v >= upper:
                rise_end_idx = i
                break
        
        if rise_start_idx is not None and rise_end_idx is not None:
            metrics.rise_time = times[rise_end_idx] - times[rise_start_idx]
        
        # 调节时间 (进入并保持在容差带内)
        band_lower = self.setpoint * (1 - self.settling_band / 100)
        band_upper = self.setpoint * (1 + self.settling_band / 100)
        
        settling_idx = None
        for i in range(len(values) - 1, -1, -1):
            if values[i] < band_lower or values[i] > band_upper:
                settling_idx = i + 1
                break
        
        if settling_idx is not None and settling_idx < len(values):
            metrics.settling_time = times[settling_idx] - times[0]
        else:
            metrics.settling_time = 0.0
        
        # 稳态误差
        metrics.steady_state_error = abs(self.setpoint - metrics.final_value)
        
        return metrics
    
    def get_assessment(self, metrics: PerformanceMetrics) -> dict:
        """评估性能指标，给出建议"""
        assessment = {
            "score": 0,
            "grade": "",
            "issues": [],
            "suggestions": []
        }
        
        score = 100
        issues = []
        suggestions = []
        
        # 超调量评估
        if metrics.overshoot > 25:
            score -= 30
            issues.append(f"超调量过大: {metrics.overshoot:.1f}%")
            suggestions.append("增大I参数或减小P参数")
        elif metrics.overshoot > 10:
            score -= 15
            issues.append(f"超调量偏大: {metrics.overshoot:.1f}%")
            suggestions.append("适当减小P参数")
        elif metrics.overshoot > 0:
            score -= 5
        
        # 调节时间评估
        if metrics.settling_time > 5:
            score -= 25
            issues.append(f"调节时间过长: {metrics.settling_time:.2f}s")
            suggestions.append("增大P参数或I参数")
        elif metrics.settling_time > 2:
            score -= 10
            issues.append(f"调节时间偏长: {metrics.settling_time:.2f}s")
        
        # 稳态误差评估
        if self.setpoint > 0:
            relative_error = metrics.steady_state_error / self.setpoint * 100
            if relative_error > 5:
                score -= 20
                issues.append(f"稳态误差过大: {relative_error:.1f}%")
                suggestions.append("增大I参数以消除稳态误差")
            elif relative_error > 2:
                score -= 10
        
        # 上升时间评估
        if metrics.rise_time > 3:
            score -= 10
            issues.append(f"上升时间过慢: {metrics.rise_time:.2f}s")
            suggestions.append("增大P参数")
        
        # 无超调但响应慢
        if metrics.overshoot == 0 and metrics.rise_time > 2:
            suggestions.append("可适当增大P参数提高响应速度")
        
        # 评分等级
        score = max(0, score)
        if score >= 90:
            grade = "优秀"
        elif score >= 75:
            grade = "良好"
        elif score >= 60:
            grade = "一般"
        else:
            grade = "需改进"
        
        assessment["score"] = score
        assessment["grade"] = grade
        assessment["issues"] = issues
        assessment["suggestions"] = suggestions
        
        return assessment