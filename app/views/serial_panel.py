from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QGroupBox, QLineEdit,
                             QTabWidget, QFormLayout, QSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette

class SerialPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 连接类型选择
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("连接类型:"))
        self.connection_type = QComboBox()
        self.connection_type.addItems(["串口", "SSH"])
        type_layout.addWidget(self.connection_type)
        layout.addLayout(type_layout)
        
        # 创建选项卡
        self.tabs = QTabWidget()
        
        # 串口选项卡
        self.serial_tab = QWidget()
        self.setup_serial_tab()
        self.tabs.addTab(self.serial_tab, "串口设置")
        
        # SSH选项卡
        self.ssh_tab = QWidget()
        self.setup_ssh_tab()
        self.tabs.addTab(self.ssh_tab, "SSH设置")
        
        layout.addWidget(self.tabs)
        
        # 连接按钮（单按钮，互斥切换）
        button_layout = QHBoxLayout()
        self.connect_btn = QPushButton("连接")
        self.connect_btn.setMinimumHeight(35)
        button_layout.addWidget(self.connect_btn)
        layout.addLayout(button_layout)
        
        # 连接状态（带颜色）
        self.status_label = QLabel("● 未连接")
        self.status_label.setStyleSheet("color: gray; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # 连接类型变化时切换选项卡
        self.connection_type.currentTextChanged.connect(self.on_connection_type_changed)
    
    def setup_serial_tab(self):
        layout = QFormLayout(self.serial_tab)
        
        # 串口选择
        self.port_combo = QComboBox()
        layout.addRow("串口:", self.port_combo)
        
        # 波特率选择
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(["9600", "19200", "38400", "57600", "115200", "230400"])
        self.baud_combo.setCurrentText("115200")
        layout.addRow("波特率:", self.baud_combo)
        
        # 数据位
        self.databits_combo = QComboBox()
        self.databits_combo.addItems(["5", "6", "7", "8"])
        self.databits_combo.setCurrentText("8")
        layout.addRow("数据位:", self.databits_combo)
        
        # 停止位
        self.stopbits_combo = QComboBox()
        self.stopbits_combo.addItems(["1", "1.5", "2"])
        self.stopbits_combo.setCurrentText("1")
        layout.addRow("停止位:", self.stopbits_combo)
        
        # 校验位
        self.parity_combo = QComboBox()
        self.parity_combo.addItems(["无", "奇校验", "偶校验"])
        layout.addRow("校验位:", self.parity_combo)
    
    def setup_ssh_tab(self):
        layout = QFormLayout(self.ssh_tab)
        
        # 主机地址
        self.ssh_host = QLineEdit()
        self.ssh_host.setPlaceholderText("例如: 192.168.1.100")
        layout.addRow("主机:", self.ssh_host)
        
        # 端口
        self.ssh_port = QSpinBox()
        self.ssh_port.setRange(1, 65535)
        self.ssh_port.setValue(22)
        layout.addRow("端口:", self.ssh_port)
        
        # 用户名
        self.ssh_username = QLineEdit()
        self.ssh_username.setPlaceholderText("例如: root")
        layout.addRow("用户名:", self.ssh_username)
        
        # 密码
        self.ssh_password = QLineEdit()
        self.ssh_password.setEchoMode(QLineEdit.Password)
        self.ssh_password.setPlaceholderText("密码")
        layout.addRow("密码:", self.ssh_password)
        
        # 密钥文件
        self.ssh_keyfile = QLineEdit()
        self.ssh_keyfile.setPlaceholderText("密钥文件路径（可选）")
        layout.addRow("密钥文件:", self.ssh_keyfile)
    
    def on_connection_type_changed(self, connection_type):
        if connection_type == "串口":
            self.tabs.setCurrentIndex(0)
        else:
            self.tabs.setCurrentIndex(1)
    
    def get_connection_params(self):
        if self.connection_type.currentText() == "串口":
            parity_map = {"无": "N", "奇校验": "O", "偶校验": "E"}
            return {
                'type': 'serial',
                'port': self.port_combo.currentText(),
                'baudrate': int(self.baud_combo.currentText()),
                'bytesize': int(self.databits_combo.currentText()),
                'stopbits': float(self.stopbits_combo.currentText()),
                'parity': parity_map.get(self.parity_combo.currentText(), "N")
            }
        else:
            return {
                'type': 'ssh',
                'host': self.ssh_host.text(),
                'port': self.ssh_port.value(),
                'username': self.ssh_username.text(),
                'password': self.ssh_password.text(),
                'key_file': self.ssh_keyfile.text() or None
            }
    
    def set_ports(self, ports):
        self.port_combo.clear()
        self.port_combo.addItems(ports)
    
    def update_status(self, status, connected=False, success=None):
        """
        更新状态显示
        :param status: 状态文本
        :param connected: 是否已连接
        :param success: None=默认灰色, True=绿色, False=红色
        """
        # 更新按钮文字和状态
        if connected:
            self.connect_btn.setText("断开")
            self.connect_btn.setStyleSheet("background-color: #ff6b6b; color: white; font-weight: bold;")
        else:
            self.connect_btn.setText("连接")
            self.connect_btn.setStyleSheet("background-color: #51cf66; color: white; font-weight: bold;")
        
        # 更新状态标签颜色
        if success is True:
            # 绿色 - 连接成功
            self.status_label.setText(f"● {status}")
            self.status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        elif success is False:
            # 红色 - 连接失败
            self.status_label.setText(f"● {status}")
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        else:
            # 灰色 - 默认状态
            self.status_label.setText(f"● {status}")
            self.status_label.setStyleSheet("color: #95a5a6; font-weight: bold;")