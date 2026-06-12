from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTextEdit, QLineEdit, QPushButton, QGroupBox,
                             QComboBox, QCheckBox, QSplitter)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QTextCharFormat, QBrush
from datetime import datetime

class DebugPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.auto_scroll = True
        self.show_timestamp = True
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 选项区域
        options_layout = QHBoxLayout()
        
        self.auto_scroll_check = QCheckBox("自动滚动")
        self.auto_scroll_check.setChecked(True)
        self.auto_scroll_check.stateChanged.connect(self.on_auto_scroll_changed)
        options_layout.addWidget(self.auto_scroll_check)
        
        self.timestamp_check = QCheckBox("显示时间戳")
        self.timestamp_check.setChecked(True)
        self.timestamp_check.stateChanged.connect(self.on_timestamp_changed)
        options_layout.addWidget(self.timestamp_check)
        
        options_layout.addStretch()
        
        self.clear_btn = QPushButton("清空")
        self.clear_btn.clicked.connect(self.clear_log)
        options_layout.addWidget(self.clear_btn)
        
        layout.addLayout(options_layout)
        
        # 接收显示区域
        recv_group = QGroupBox("接收数据")
        recv_layout = QVBoxLayout()
        
        self.recv_text = QTextEdit()
        self.recv_text.setReadOnly(True)
        self.recv_text.setStyleSheet("font-family: Consolas, monospace; font-size: 12px;")
        recv_layout.addWidget(self.recv_text)
        
        recv_group.setLayout(recv_layout)
        layout.addWidget(recv_group)
        
        # 发送区域
        send_group = QGroupBox("发送指令")
        send_layout = QVBoxLayout()
        
        # 发送输入
        input_layout = QHBoxLayout()
        
        self.send_input = QLineEdit()
        self.send_input.setPlaceholderText("输入要发送的指令...")
        self.send_input.returnPressed.connect(self.on_send_clicked)
        input_layout.addWidget(self.send_input)
        
        self.send_btn = QPushButton("发送")
        self.send_btn.clicked.connect(self.on_send_clicked)
        input_layout.addWidget(self.send_btn)
        
        send_layout.addLayout(input_layout)
        
        # 发送选项
        send_options_layout = QHBoxLayout()
        
        self.hex_send_check = QCheckBox("HEX发送")
        send_options_layout.addWidget(self.hex_send_check)
        
        self.add_newline_check = QCheckBox("添加换行")
        self.add_newline_check.setChecked(True)
        send_options_layout.addWidget(self.add_newline_check)
        
        send_options_layout.addStretch()
        
        # 快捷指令
        send_options_layout.addWidget(QLabel("快捷指令:"))
        self.quick_cmd_combo = QComboBox()
        self.quick_cmd_combo.addItems([
            "P=1.00,I=0.10,D=0.01",
            "P=2.00,I=0.20,D=0.02",
            "P=0.50,I=0.05,D=0.005",
            "STATUS",
            "RESET",
            "HELP"
        ])
        self.quick_cmd_combo.setEditable(True)
        self.quick_cmd_combo.currentTextChanged.connect(self.on_quick_cmd_selected)
        send_options_layout.addWidget(self.quick_cmd_combo)
        
        send_layout.addLayout(send_options_layout)
        
        send_group.setLayout(send_layout)
        layout.addWidget(send_group)
    
    def on_auto_scroll_changed(self, state):
        self.auto_scroll = state == Qt.Checked
    
    def on_timestamp_changed(self, state):
        self.show_timestamp = state == Qt.Checked
    
    def on_send_clicked(self):
        """发送按钮点击事件（由控制器处理）"""
        pass
    
    def on_quick_cmd_selected(self, cmd):
        """快捷指令选中"""
        if cmd:
            self.send_input.setText(cmd)
            self.send_input.setFocus()
    
    def get_send_text(self):
        """获取发送文本"""
        return self.send_input.text()
    
    def clear_send_input(self):
        """清空发送输入框"""
        self.send_input.clear()
    
    def append_recv_data(self, data, is_hex=False):
        """添加接收数据"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3] if self.show_timestamp else ""
        
        if isinstance(data, bytes):
            if is_hex:
                display = data.hex(' ')
            else:
                try:
                    display = data.decode('utf-8', errors='replace')
                except:
                    display = data.hex(' ')
        else:
            display = str(data)
        
        # 添加带颜色的文本
        cursor = self.recv_text.textCursor()
        cursor.movePosition(cursor.End)
        
        # 时间戳（灰色）
        if timestamp:
            format_gray = QTextCharFormat()
            format_gray.setForeground(QBrush(QColor("#888888")))
            cursor.setCharFormat(format_gray)
            cursor.insertText(f"[{timestamp}] ")
        
        # 数据（绿色）
        format_green = QTextCharFormat()
        format_green.setForeground(QBrush(QColor("#2ecc71")))
        cursor.setCharFormat(format_green)
        cursor.insertText(f"← {display}\n")
        
        if self.auto_scroll:
            self.recv_text.setTextCursor(cursor)
            self.recv_text.ensureCursorVisible()
    
    def append_send_data(self, data, is_hex=False):
        """添加发送数据"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3] if self.show_timestamp else ""
        
        if isinstance(data, bytes):
            if is_hex:
                display = data.hex(' ')
            else:
                try:
                    display = data.decode('utf-8', errors='replace')
                except:
                    display = data.hex(' ')
        else:
            display = str(data)
        
        # 添加带颜色的文本
        cursor = self.recv_text.textCursor()
        cursor.movePosition(cursor.End)
        
        # 时间戳（灰色）
        if timestamp:
            format_gray = QTextCharFormat()
            format_gray.setForeground(QBrush(QColor("#888888")))
            cursor.setCharFormat(format_gray)
            cursor.insertText(f"[{timestamp}] ")
        
        # 数据（蓝色）
        format_blue = QTextCharFormat()
        format_blue.setForeground(QBrush(QColor("#3498db")))
        cursor.setCharFormat(format_blue)
        cursor.insertText(f"→ {display}\n")
        
        if self.auto_scroll:
            self.recv_text.setTextCursor(cursor)
            self.recv_text.ensureCursorVisible()
    
    def append_system_msg(self, msg):
        """添加系统消息"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3] if self.show_timestamp else ""
        
        cursor = self.recv_text.textCursor()
        cursor.movePosition(cursor.End)
        
        if timestamp:
            format_gray = QTextCharFormat()
            format_gray.setForeground(QBrush(QColor("#888888")))
            cursor.setCharFormat(format_gray)
            cursor.insertText(f"[{timestamp}] ")
        
        # 系统消息（黄色）
        format_yellow = QTextCharFormat()
        format_yellow.setForeground(QBrush(QColor("#f39c12")))
        cursor.setCharFormat(format_yellow)
        cursor.insertText(f"● {msg}\n")
        
        if self.auto_scroll:
            self.recv_text.setTextCursor(cursor)
            self.recv_text.ensureCursorVisible()
    
    def clear_log(self):
        """清空日志"""
        self.recv_text.clear()