from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QPushButton
import pyqtgraph as pg

class ChartPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setup_chart()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        
        self.p_check = QCheckBox("P曲线")
        self.p_check.setChecked(True)
        self.i_check = QCheckBox("I曲线")
        self.i_check.setChecked(True)
        self.d_check = QCheckBox("D曲线")
        self.d_check.setChecked(True)
        
        self.clear_btn = QPushButton("清除数据")
        self.pause_btn = QPushButton("暂停")
        
        control_layout.addWidget(self.p_check)
        control_layout.addWidget(self.i_check)
        control_layout.addWidget(self.d_check)
        control_layout.addWidget(self.clear_btn)
        control_layout.addWidget(self.pause_btn)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # 图表
        self.chart_widget = pg.PlotWidget()
        layout.addWidget(self.chart_widget)
    
    def setup_chart(self):
        self.chart_widget.setBackground('w')
        self.chart_widget.showGrid(x=True, y=True)
        self.chart_widget.setLabel('left', '数值')
        self.chart_widget.setLabel('bottom', '时间')
        
        # 创建曲线
        self.p_curve = self.chart_widget.plot(pen='r', name='P')
        self.i_curve = self.chart_widget.plot(pen='g', name='I')
        self.d_curve = self.chart_widget.plot(pen='b', name='D')
        
        # 数据存储
        self.p_data = []
        self.i_data = []
        self.d_data = []
        self.time_data = []
        self.time_counter = 0
    
    def update_data(self, p, i, d):
        self.time_counter += 1
        self.time_data.append(self.time_counter)
        self.p_data.append(p)
        self.i_data.append(i)
        self.d_data.append(d)
        
        # 限制数据点数量
        max_points = 1000
        if len(self.time_data) > max_points:
            self.time_data = self.time_data[-max_points:]
            self.p_data = self.p_data[-max_points:]
            self.i_data = self.i_data[-max_points:]
            self.d_data = self.d_data[-max_points:]
        
        # 更新曲线
        if self.p_check.isChecked():
            self.p_curve.setData(self.time_data, self.p_data)
        else:
            self.p_curve.setData([], [])
        
        if self.i_check.isChecked():
            self.i_curve.setData(self.time_data, self.i_data)
        else:
            self.i_curve.setData([], [])
        
        if self.d_check.isChecked():
            self.d_curve.setData(self.time_data, self.d_data)
        else:
            self.d_curve.setData([], [])
    
    def clear_data(self):
        self.p_data.clear()
        self.i_data.clear()
        self.d_data.clear()
        self.time_data.clear()
        self.time_counter = 0
        self.p_curve.setData([], [])
        self.i_curve.setData([], [])
        self.d_curve.setData([], [])