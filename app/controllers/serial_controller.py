from app.services.serial_service import SerialService
from app.services.ssh_service import SSHService
from app.models.serial_model import SerialModel

class SerialController:
    def __init__(self):
        self.serial_service = SerialService()
        self.ssh_service = SSHService()
        self.serial_model = SerialModel()
        self.view = None
        self.active_service = None
    
    def set_view(self, view):
        self.view = view
        self.connect_signals()
        self.update_ports_list()
    
    def connect_signals(self):
        if self.view:
            self.view.connect_btn.clicked.connect(self.on_connect_btn_clicked)
    
    def update_ports_list(self):
        if self.view:
            ports = self.serial_service.get_available_ports()
            self.view.set_ports(ports)
    
    def on_connect_btn_clicked(self):
        """连接/断开按钮点击事件"""
        if self.serial_model.is_connected:
            self.disconnect()
        else:
            self.connect()
    
    def connect(self):
        """根据当前选择的连接类型进行连接"""
        if self.view:
            params = self.view.get_connection_params()
            if params['type'] == 'serial':
                self.connect_serial(params)
            else:
                self.connect_ssh(params)
    
    def connect_serial(self, params):
        success = self.serial_service.connect(
            port=params['port'],
            baudrate=params['baudrate'],
            bytesize=params['bytesize'],
            parity=params['parity'],
            stopbits=params['stopbits']
        )
        if success:
            self.serial_model.is_connected = True
            self.active_service = self.serial_service
            self.update_view_status(f"已连接 - {params['port']}", True, True)
            self.serial_service.set_data_callback(self.on_data_received)
        else:
            self.update_view_status("串口连接失败", False, False)
        return success
    
    def connect_ssh(self, params):
        success = self.ssh_service.connect(
            host=params['host'],
            port=params['port'],
            username=params['username'],
            password=params['password'],
            key_file=params['key_file']
        )
        if success:
            self.serial_model.is_connected = True
            self.active_service = self.ssh_service
            self.update_view_status(f"已连接SSH - {params['host']}", True, True)
            self.ssh_service.set_data_callback(self.on_data_received)
        else:
            self.update_view_status("SSH连接失败", False, False)
        return success
    
    def disconnect(self):
        if self.active_service:
            self.active_service.disconnect()
        self.serial_model.is_connected = False
        self.active_service = None
        self.update_view_status("已断开", False, None)
    
    def on_data_received(self, data):
        # 解析数据并更新模型
        parsed_data = {"P": 1.0, "I": 0.1, "D": 0.01}  # 简化示例
        self.serial_model.add_data(data, parsed_data)
        
        # 更新UI
        if self.view:
            self.view.update_status(f"已连接 - 收到 {len(data)} 字节", True, True)
    
    def update_view_status(self, status, connected=False, success=None):
        if self.view:
            self.view.update_status(status, connected, success)
    
    def send_data(self, data):
        if self.active_service:
            return self.active_service.send_data(data)
        return False
    
    def execute_ssh_command(self, command):
        if self.active_service and isinstance(self.active_service, SSHService):
            return self.active_service.execute_command(command)
        return None