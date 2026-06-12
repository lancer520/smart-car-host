from app.services.performance_analyzer import PerformanceAnalyzer, PerformanceMetrics
from PyQt5.QtCore import QTimer

class AnalysisController:
    def __init__(self):
        self.analyzer = PerformanceAnalyzer()
        self.serial_controller = None
        self.chart_controller = None
        self.view = None
        self.is_analyzing = False
        self.time_counter = 0
        self.last_pid_values = None
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.on_update_timer)
    
    def set_view(self, view, serial_controller, chart_controller):
        self.view = view
        self.serial_controller = serial_controller
        self.chart_controller = chart_controller
        self.connect_signals()
    
    def connect_signals(self):
        if self.view:
            self.view.start_btn.clicked.connect(self.start_analysis)
            self.view.stop_btn.clicked.connect(self.stop_analysis)
            self.view.reset_btn.clicked.connect(self.reset_analysis)
            self.view.setpoint_spin.valueChanged.connect(self.on_setpoint_changed)
            self.view.band_spin.valueChanged.connect(self.on_band_changed)
    
    def on_setpoint_changed(self, value):
        self.analyzer.set_setpoint(value)
    
    def on_band_changed(self, value):
        self.analyzer.set_settling_band(value)
    
    def start_analysis(self):
        """开始分析"""
        self.is_analyzing = True
        self.time_counter = 0
        self.analyzer.clear_data()
        self.analyzer.set_setpoint(self.view.setpoint_spin.value())
        self.analyzer.set_settling_band(self.view.band_spin.value())
        
        if self.view:
            self.view.start_btn.setEnabled(False)
            self.view.stop_btn.setEnabled(True)
            self.view.reset_all()
        
        # 启动定时更新
        self.update_timer.start(100)  # 100ms更新一次
    
    def stop_analysis(self):
        """停止分析"""
        self.is_analyzing = False
        self.update_timer.stop()
        
        if self.view:
            self.view.start_btn.setEnabled(True)
            self.view.stop_btn.setEnabled(False)
        
        # 计算最终结果
        self.calculate_and_display()
    
    def reset_analysis(self):
        """重置分析"""
        self.stop_analysis()
        self.analyzer.clear_data()
        self.time_counter = 0
        
        if self.view:
            self.view.reset_all()
    
    def on_update_timer(self):
        """定时更新"""
        if not self.is_analyzing:
            return
        
        # 从PID历史数据获取当前值
        if self.serial_controller and self.serial_controller.active_service:
            # 获取最新PID值（这里简化处理，实际应从数据流获取）
            pass
    
    def add_data_point(self, time: float, value: float):
        """添加数据点"""
        if self.is_analyzing:
            self.analyzer.add_data_point(time, value)
    
    def add_pid_data(self, p: float, i: float, d: float, actual: float):
        """添加PID数据"""
        if self.is_analyzing:
            self.time_counter += 0.1  # 假设100ms间隔
            self.analyzer.add_data_point(self.time_counter, actual)
            
            # 存储当前PID值
            self.last_pid_values = (p, i, d)
    
    def calculate_and_display(self):
        """计算并显示结果"""
        metrics = self.analyzer.calculate_metrics()
        if metrics and self.view:
            assessment = self.analyzer.get_assessment(metrics)
            self.view.update_metrics(metrics, assessment)
    
    def on_pid_data_received(self, data):
        """接收PID数据时调用"""
        if self.is_analyzing and 'P' in data and 'actual' in data:
            self.add_pid_data(
                data.get('P', 0),
                data.get('I', 0),
                data.get('D', 0),
                data.get('actual', 0)
            )