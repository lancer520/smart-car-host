from app.services.protocol_parser import ProtocolParser

class DebugController:
    def __init__(self):
        self.serial_controller = None
        self.view = None
        self.protocol_parser = ProtocolParser()
    
    def set_view(self, view, serial_controller):
        self.view = view
        self.serial_controller = serial_controller
        self.connect_signals()
    
    def connect_signals(self):
        if self.view:
            self.view.send_btn.clicked.connect(self.on_send_clicked)
    
    def on_send_clicked(self):
        """发送自定义指令"""
        if not self.view or not self.serial_controller:
            return
        
        text = self.view.get_send_text()
        if not text:
            self.view.append_system_msg("请输入要发送的内容")
            return
        
        # 检查连接状态
        if not self.serial_controller.serial_model.is_connected:
            self.view.append_system_msg("未连接设备，请先连接")
            return
        
        # 准备数据
        if self.view.hex_send_check.isChecked():
            # HEX模式发送
            try:
                data = bytes.fromhex(text.replace(' ', ''))
            except ValueError:
                self.view.append_system_msg("HEX格式错误，请输入有效的十六进制数据")
                return
        else:
            # 文本模式发送
            data = text.encode('utf-8')
            if self.view.add_newline_check.isChecked():
                data += b'\r\n'
        
        # 显示发送内容
        self.view.append_send_data(data, self.view.hex_send_check.isChecked())
        
        # 发送数据
        success = self.serial_controller.send_data(data)
        
        if success:
            self.view.clear_send_input()
        else:
            self.view.append_system_msg("发送失败")
    
    def on_data_received(self, data):
        """处理接收到的数据"""
        if self.view:
            self.view.append_recv_data(data, False)
    
    def on_connection_changed(self, connected):
        """连接状态变化"""
        if self.view:
            if connected:
                self.view.append_system_msg("设备已连接")
                self.view.send_btn.setEnabled(True)
            else:
                self.view.append_system_msg("设备已断开")
                self.view.send_btn.setEnabled(False)