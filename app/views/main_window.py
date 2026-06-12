from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTabWidget
from PyQt5.QtCore import Qt
from app.views.serial_panel import SerialPanel
from app.views.pid_panel import PIDPanel
from app.views.chart_panel import ChartPanel
from app.views.log_panel import LogPanel
from app.views.debug_panel import DebugPanel
from app.views.analysis_panel import AnalysisPanel
from app.controllers.serial_controller import SerialController
from app.controllers.pid_controller import PIDController
from app.controllers.chart_controller import ChartController
from app.controllers.log_controller import LogController
from app.controllers.debug_controller import DebugController
from app.controllers.analysis_controller import AnalysisController

class MainWindow(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setWindowTitle("智能车上位机调试软件")
        self.setGeometry(100, 100, 1400, 900)
        
        # 初始化控制器
        self.serial_controller = SerialController()
        self.pid_controller = PIDController()
        self.chart_controller = ChartController()
        self.log_controller = LogController()
        self.debug_controller = DebugController()
        self.analysis_controller = AnalysisController()
        
        self.setup_ui()
        self.setup_controllers()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # 创建主分割器（水平）
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：连接和PID设置
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        self.serial_panel = SerialPanel()
        self.pid_panel = PIDPanel()
        
        left_layout.addWidget(self.serial_panel)
        left_layout.addWidget(self.pid_panel)
        
        # 右侧：选项卡（图表、分析、调试、日志）
        right_tabs = QTabWidget()
        
        # 图表面板
        self.chart_panel = ChartPanel()
        right_tabs.addTab(self.chart_panel, "实时曲线")
        
        # 分析面板
        self.analysis_panel = AnalysisPanel()
        right_tabs.addTab(self.analysis_panel, "调参分析")
        
        # 调试面板
        self.debug_panel = DebugPanel()
        right_tabs.addTab(self.debug_panel, "串口调试")
        
        # 日志面板
        self.log_panel = LogPanel()
        right_tabs.addTab(self.log_panel, "数据日志")
        
        # 添加到分割器
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_tabs)
        
        # 设置分割器比例（左侧窄，右侧宽）
        main_splitter.setSizes([320, 1080])
        
        main_layout.addWidget(main_splitter)
    
    def setup_controllers(self):
        """设置控制器并连接视图"""
        # 串口控制器
        self.serial_controller.set_view(self.serial_panel)
        
        # PID控制器
        self.pid_controller.set_view(self.pid_panel, self.serial_controller)
        
        # 图表控制器
        self.chart_controller.set_view(self.chart_panel)
        
        # 日志控制器
        self.log_controller.set_view(self.log_panel)
        
        # 调试控制器
        self.debug_controller.set_view(self.debug_panel, self.serial_controller)
        
        # 分析控制器
        self.analysis_controller.set_view(
            self.analysis_panel, 
            self.serial_controller,
            self.chart_controller
        )
        
        # 连接串口控制器的数据回调
        original_callback = self.serial_controller.on_data_received
        def enhanced_data_received(data):
            original_callback(data)
            self.debug_controller.on_data_received(data)
            
            # 解析PID数据并传递给分析控制器
            if isinstance(data, dict):
                self.analysis_controller.on_pid_data_received(data)
            elif isinstance(data, bytes):
                # 尝试解析文本数据
                try:
                    text = data.decode('utf-8', errors='ignore')
                    if 'P=' in text and 'I=' in text:
                        parsed = self.parse_pid_text(text)
                        if parsed:
                            self.analysis_controller.on_pid_data_received(parsed)
                except:
                    pass
        self.serial_controller.on_data_received = enhanced_data_received
    
    def parse_pid_text(self, text):
        """解析PID文本数据"""
        import re
        result = {}
        
        # 解析P、I、D值
        p_match = re.search(r'P=([+-]?\d*\.?\d+)', text)
        i_match = re.search(r'I=([+-]?\d*\.?\d+)', text)
        d_match = re.search(r'D=([+-]?\d*\.?\d+)', text)
        
        if p_match:
            result['P'] = float(p_match.group(1))
        if i_match:
            result['I'] = float(i_match.group(1))
        if d_match:
            result['D'] = float(d_match.group(1))
        
        # 解析实际值
        actual_match = re.search(r'actual=([+-]?\d*\.?\d+)', text, re.IGNORECASE)
        if actual_match:
            result['actual'] = float(actual_match.group(1))
        elif 'speed=' in text.lower():
            speed_match = re.search(r'speed=([+-]?\d*\.?\d+)', text, re.IGNORECASE)
            if speed_match:
                result['actual'] = float(speed_match.group(1))
        
        return result if result else None