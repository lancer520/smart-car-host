from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QSlider, QDoubleSpinBox, QPushButton, QGroupBox,
                             QComboBox, QLineEdit, QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt

class PIDPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # PID参数组
        group = QGroupBox("PID参数")
        group_layout = QVBoxLayout()
        
        # P参数（范围0-100，步长0.1，滑块精度0.01）
        p_layout = QHBoxLayout()
        p_layout.addWidget(QLabel("P:"))
        self.p_slider = QSlider(Qt.Horizontal)
        self.p_slider.setRange(0, 10000)  # 0-100，精度0.01
        self.p_slider.setValue(100)
        self.p_spinbox = QDoubleSpinBox()
        self.p_spinbox.setRange(0, 100)
        self.p_spinbox.setValue(1.0)
        self.p_spinbox.setSingleStep(0.1)
        self.p_spinbox.setDecimals(2)
        p_layout.addWidget(self.p_slider)
        p_layout.addWidget(self.p_spinbox)
        group_layout.addLayout(p_layout)
        
        # I参数（范围0-10，步长0.01，滑块精度0.001）
        i_layout = QHBoxLayout()
        i_layout.addWidget(QLabel("I:"))
        self.i_slider = QSlider(Qt.Horizontal)
        self.i_slider.setRange(0, 10000)  # 0-10，精度0.001
        self.i_slider.setValue(100)
        self.i_spinbox = QDoubleSpinBox()
        self.i_spinbox.setRange(0, 10)
        self.i_spinbox.setValue(0.1)
        self.i_spinbox.setSingleStep(0.01)
        self.i_spinbox.setDecimals(3)
        i_layout.addWidget(self.i_slider)
        i_layout.addWidget(self.i_spinbox)
        group_layout.addLayout(i_layout)
        
        # D参数（范围0-1，步长0.001，滑块精度0.0001）
        d_layout = QHBoxLayout()
        d_layout.addWidget(QLabel("D:"))
        self.d_slider = QSlider(Qt.Horizontal)
        self.d_slider.setRange(0, 10000)  # 0-1，精度0.0001
        self.d_slider.setValue(100)
        self.d_spinbox = QDoubleSpinBox()
        self.d_spinbox.setRange(0, 1)
        self.d_spinbox.setValue(0.01)
        self.d_spinbox.setSingleStep(0.001)
        self.d_spinbox.setDecimals(4)
        d_layout.addWidget(self.d_slider)
        d_layout.addWidget(self.d_spinbox)
        group_layout.addLayout(d_layout)
        
        # 分隔线
        group_layout.addWidget(QLabel(""))
        
        # 预设管理
        preset_group = QGroupBox("预设管理")
        preset_layout = QVBoxLayout()
        
        # 预设下拉列表
        preset_select_layout = QHBoxLayout()
        preset_select_layout.addWidget(QLabel("预设:"))
        self.preset_combo = QComboBox()
        self.preset_combo.setMinimumWidth(150)
        self.preset_combo.currentTextChanged.connect(self.on_preset_selected)
        preset_select_layout.addWidget(self.preset_combo)
        
        # 预设操作按钮
        self.load_preset_btn = QPushButton("加载")
        self.load_preset_btn.setToolTip("加载选中的预设")
        preset_select_layout.addWidget(self.load_preset_btn)
        
        self.delete_preset_btn = QPushButton("删除")
        self.delete_preset_btn.setToolTip("删除选中的预设")
        preset_select_layout.addWidget(self.delete_preset_btn)
        
        preset_layout.addLayout(preset_select_layout)
        
        # 保存预设
        save_layout = QHBoxLayout()
        save_layout.addWidget(QLabel("名称:"))
        self.preset_name_edit = QLineEdit()
        self.preset_name_edit.setPlaceholderText("输入预设名称")
        save_layout.addWidget(self.preset_name_edit)
        
        self.save_preset_btn = QPushButton("保存")
        self.save_preset_btn.setToolTip("保存当前参数为新预设")
        save_layout.addWidget(self.save_preset_btn)
        
        preset_layout.addLayout(save_layout)
        
        preset_group.setLayout(preset_layout)
        group_layout.addWidget(preset_group)
        
        # 发送按钮
        self.send_btn = QPushButton("发送参数")
        self.send_btn.setMinimumHeight(35)
        self.send_btn.setStyleSheet("font-weight: bold;")
        group_layout.addWidget(self.send_btn)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
        layout.addStretch()
    
    def update_preset_list(self, preset_names):
        """更新预设下拉列表"""
        current = self.preset_combo.currentText()
        self.preset_combo.clear()
        self.preset_combo.addItems(preset_names)
        # 尝试恢复之前选中的项
        index = self.preset_combo.findText(current)
        if index >= 0:
            self.preset_combo.setCurrentIndex(index)
    
    def on_preset_selected(self, name):
        """预设选中事件（由控制器处理）"""
        pass
    
    def get_current_values(self):
        """获取当前PID值"""
        return {
            'p': self.p_spinbox.value(),
            'i': self.i_spinbox.value(),
            'd': self.d_spinbox.value()
        }
    
    def set_values(self, p, i, d):
        """设置PID值"""
        self.p_spinbox.setValue(p)
        self.i_spinbox.setValue(i)
        self.d_spinbox.setValue(d)
    
    def get_preset_name(self):
        """获取预设名称"""
        return self.preset_name_edit.text().strip()
    
    def clear_preset_name(self):
        """清空预设名称输入框"""
        self.preset_name_edit.clear()
    
    def show_message(self, title, message, msg_type="info"):
        """显示消息框"""
        if msg_type == "success":
            QMessageBox.information(self, title, message)
        elif msg_type == "error":
            QMessageBox.warning(self, title, message)
        elif msg_type == "question":
            return QMessageBox.question(self, title, message, 
                                       QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes
        else:
            QMessageBox.information(self, title, message)