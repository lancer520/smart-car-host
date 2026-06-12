from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGroupBox, QPushButton, QGridLayout, QFrame,
                             QSpinBox, QDoubleSpinBox, QFormLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette, QFont

class MetricCard(QFrame):
    """指标卡片组件"""
    def __init__(self, title, unit="", parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setMinimumHeight(100)
        self.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        
        # 标题
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #6c757d; font-size: 14px; font-weight: bold;")
        layout.addWidget(self.title_label)
        
        # 数值
        self.value_label = QLabel("--")
        self.value_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #495057;")
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        # 单位
        if unit:
            unit_label = QLabel(unit)
            unit_label.setStyleSheet("color: #6c757d; font-size: 12px;")
            unit_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(unit_label)
        
        self.setLayout(layout)
    
    def set_value(self, value, decimals=2):
        self.value_label.setText(f"{value:.{decimals}f}")
    
    def set_color(self, color):
        self.value_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color};")
    
    def reset(self):
        self.value_label.setText("--")
        self.value_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #495057;")


class AnalysisPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 性能指标卡片
        metrics_group = QGroupBox("性能指标")
        metrics_group.setStyleSheet("QGroupBox { font-size: 14px; font-weight: bold; }")
        metrics_grid = QGridLayout()
        metrics_grid.setSpacing(10)
        
        # 创建指标卡片
        self.overshoot_card = MetricCard("超调量", "%")
        self.settling_card = MetricCard("调节时间", "秒")
        self.rise_card = MetricCard("上升时间", "秒")
        self.peak_card = MetricCard("峰值时间", "秒")
        self.error_card = MetricCard("稳态误差", "")
        self.score_card = MetricCard("综合评分", "分")
        
        metrics_grid.addWidget(self.overshoot_card, 0, 0)
        metrics_grid.addWidget(self.settling_card, 0, 1)
        metrics_grid.addWidget(self.rise_card, 0, 2)
        metrics_grid.addWidget(self.peak_card, 1, 0)
        metrics_grid.addWidget(self.error_card, 1, 1)
        metrics_grid.addWidget(self.score_card, 1, 2)
        
        metrics_group.setLayout(metrics_grid)
        layout.addWidget(metrics_group)
        
        # 设置区域
        settings_group = QGroupBox("分析设置")
        settings_group.setStyleSheet("QGroupBox { font-size: 14px; font-weight: bold; }")
        settings_layout = QFormLayout()
        settings_layout.setSpacing(8)
        
        self.setpoint_spin = QDoubleSpinBox()
        self.setpoint_spin.setRange(0, 1000)
        self.setpoint_spin.setValue(100)
        self.setpoint_spin.setSuffix(" ")
        self.setpoint_spin.setStyleSheet("font-size: 13px; padding: 5px;")
        settings_layout.addRow("设定值:", self.setpoint_spin)
        
        self.band_spin = QDoubleSpinBox()
        self.band_spin.setRange(0.5, 20)
        self.band_spin.setValue(2)
        self.band_spin.setSuffix(" %")
        self.band_spin.setStyleSheet("font-size: 13px; padding: 5px;")
        settings_layout.addRow("容差带:", self.band_spin)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # 控制按钮
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.start_btn = QPushButton("开始分析")
        self.start_btn.setMinimumHeight(40)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745; 
                color: white; 
                font-size: 14px;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #218838; }
        """)
        btn_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("停止分析")
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545; 
                color: white; 
                font-size: 14px;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #c82333; }
            QPushButton:disabled { background-color: #6c757d; }
        """)
        self.stop_btn.setEnabled(False)
        btn_layout.addWidget(self.stop_btn)
        
        self.reset_btn = QPushButton("重置")
        self.reset_btn.setMinimumHeight(40)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d; 
                color: white; 
                font-size: 14px;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #5a6268; }
        """)
        btn_layout.addWidget(self.reset_btn)
        
        layout.addLayout(btn_layout)
        
        # 评估结果
        assess_group = QGroupBox("评估结果")
        assess_group.setStyleSheet("QGroupBox { font-size: 14px; font-weight: bold; }")
        assess_layout = QVBoxLayout()
        assess_layout.setSpacing(10)
        
        # 等级标签
        self.grade_label = QLabel("--")
        self.grade_label.setAlignment(Qt.AlignCenter)
        self.grade_label.setMinimumHeight(60)
        self.grade_label.setStyleSheet("""
            font-size: 32px; 
            font-weight: bold; 
            padding: 15px;
            border-radius: 8px;
            background-color: #e9ecef;
        """)
        assess_layout.addWidget(self.grade_label)
        
        # 问题列表
        self.issues_label = QLabel("暂无数据")
        self.issues_label.setWordWrap(True)
        self.issues_label.setMinimumHeight(50)
        self.issues_label.setStyleSheet("color: #dc3545; padding: 8px; font-size: 13px;")
        assess_layout.addWidget(self.issues_label)
        
        # 建议列表
        self.suggestions_label = QLabel("")
        self.suggestions_label.setWordWrap(True)
        self.suggestions_label.setMinimumHeight(50)
        self.suggestions_label.setStyleSheet("color: #28a745; padding: 8px; font-size: 13px;")
        assess_layout.addWidget(self.suggestions_label)
        
        assess_group.setLayout(assess_layout)
        layout.addWidget(assess_group)
        
        layout.addStretch()
    
    def update_metrics(self, metrics, assessment=None):
        """更新性能指标显示"""
        if metrics is None:
            return
        
        # 更新卡片
        self.overshoot_card.set_value(metrics.overshoot)
        self.settling_card.set_value(metrics.settling_time)
        self.rise_card.set_value(metrics.rise_time)
        self.peak_card.set_value(metrics.peak_time)
        self.error_card.set_value(metrics.steady_state_error)
        
        # 超调量颜色
        if metrics.overshoot > 25:
            self.overshoot_card.set_color("#dc3545")  # 红
        elif metrics.overshoot > 10:
            self.overshoot_card.set_color("#ffc107")  # 黄
        else:
            self.overshoot_card.set_color("#28a745")  # 绿
        
        # 调节时间颜色
        if metrics.settling_time > 5:
            self.settling_card.set_color("#dc3545")
        elif metrics.settling_time > 2:
            self.settling_card.set_color("#ffc107")
        else:
            self.settling_card.set_color("#28a745")
        
        # 更新评估
        if assessment:
            score = assessment["score"]
            grade = assessment["grade"]
            
            self.score_card.set_value(score, 0)
            
            # 分数颜色
            if score >= 90:
                self.score_card.set_color("#28a745")
                self.grade_label.setStyleSheet("""
                    font-size: 32px; font-weight: bold; padding: 15px;
                    border-radius: 8px; background-color: #d4edda; color: #155724;
                """)
            elif score >= 75:
                self.score_card.set_color("#ffc107")
                self.grade_label.setStyleSheet("""
                    font-size: 32px; font-weight: bold; padding: 15px;
                    border-radius: 8px; background-color: #fff3cd; color: #856404;
                """)
            else:
                self.score_card.set_color("#dc3545")
                self.grade_label.setStyleSheet("""
                    font-size: 32px; font-weight: bold; padding: 15px;
                    border-radius: 8px; background-color: #f8d7da; color: #721c24;
                """)
            
            self.grade_label.setText(f"{grade} ({score}分)")
            
            # 问题
            if assessment["issues"]:
                self.issues_label.setText("⚠ 问题:\n" + "\n".join(f"• {i}" for i in assessment["issues"]))
            else:
                self.issues_label.setText("✓ 无明显问题")
            
            # 建议
            if assessment["suggestions"]:
                self.suggestions_label.setText("💡 建议:\n" + "\n".join(f"• {s}" for s in assessment["suggestions"]))
            else:
                self.suggestions_label.setText("")
    
    def reset_all(self):
        """重置所有显示"""
        self.overshoot_card.reset()
        self.settling_card.reset()
        self.rise_card.reset()
        self.peak_card.reset()
        self.error_card.reset()
        self.score_card.reset()
        
        self.grade_label.setText("--")
        self.grade_label.setStyleSheet("""
            font-size: 32px; font-weight: bold; padding: 15px;
            border-radius: 8px; background-color: #e9ecef;
        """)
        self.issues_label.setText("暂无数据")
        self.suggestions_label.setText("")