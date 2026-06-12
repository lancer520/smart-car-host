from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QPushButton, QComboBox, QGroupBox)
from PyQt5.QtCore import Qt

class LogPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 日志控制
        control_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("清除日志")
        self.save_btn = QPushButton("保存日志")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["TXT", "CSV", "JSON"])
        
        control_layout.addWidget(self.clear_btn)
        control_layout.addWidget(self.save_btn)
        control_layout.addWidget(self.format_combo)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # 日志显示
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
    
    def append_log(self, message, log_type="info"):
        if log_type == "error":
            self.log_text.append(f"<font color='red'>[错误] {message}</font>")
        elif log_type == "warning":
            self.log_text.append(f"<font color='orange'>[警告] {message}</font>")
        else:
            self.log_text.append(f"[信息] {message}")
    
    def clear_log(self):
        self.log_text.clear()
    
    def get_log_content(self):
        return self.log_text.toPlainText()