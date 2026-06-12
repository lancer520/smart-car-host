from app.models.pid_model import PIDModel
from app.services.protocol_parser import ProtocolParser
from app.services.preset_manager import PresetManager

class PIDController:
    def __init__(self):
        self.pid_model = PIDModel()
        self.protocol_parser = ProtocolParser()
        self.preset_manager = PresetManager()
        self.serial_controller = None
        self.view = None
    
    def set_view(self, view, serial_controller):
        self.view = view
        self.serial_controller = serial_controller
        self.connect_signals()
        self.refresh_preset_list()
    
    def connect_signals(self):
        if self.view:
            self.view.send_btn.clicked.connect(self.on_send_clicked)
            self.view.save_preset_btn.clicked.connect(self.on_save_preset)
            self.view.load_preset_btn.clicked.connect(self.on_load_preset)
            self.view.delete_preset_btn.clicked.connect(self.on_delete_preset)
            self.view.preset_combo.currentTextChanged.connect(self.on_preset_selected)
            
            # 滑块和数值框联动
            self.view.p_slider.valueChanged.connect(self.on_p_slider_changed)
            self.view.p_spinbox.valueChanged.connect(self.on_p_spinbox_changed)
            self.view.i_slider.valueChanged.connect(self.on_i_slider_changed)
            self.view.i_spinbox.valueChanged.connect(self.on_i_spinbox_changed)
            self.view.d_slider.valueChanged.connect(self.on_d_slider_changed)
            self.view.d_spinbox.valueChanged.connect(self.on_d_spinbox_changed)
    
    def on_p_slider_changed(self, value):
        if self.view:
            # P: 滑块范围0-10000对应0-100，精度0.01
            self.view.p_spinbox.blockSignals(True)
            self.view.p_spinbox.setValue(value / 100.0)
            self.view.p_spinbox.blockSignals(False)
    
    def on_p_spinbox_changed(self, value):
        if self.view:
            # P: 数值0-100对应滑块0-10000
            self.view.p_slider.blockSignals(True)
            self.view.p_slider.setValue(int(value * 100))
            self.view.p_slider.blockSignals(False)
    
    def on_i_slider_changed(self, value):
        if self.view:
            # I: 滑块范围0-10000对应0-10，精度0.001
            self.view.i_spinbox.blockSignals(True)
            self.view.i_spinbox.setValue(value / 1000.0)
            self.view.i_spinbox.blockSignals(False)
    
    def on_i_spinbox_changed(self, value):
        if self.view:
            # I: 数值0-10对应滑块0-10000
            self.view.i_slider.blockSignals(True)
            self.view.i_slider.setValue(int(value * 1000))
            self.view.i_slider.blockSignals(False)
    
    def on_d_slider_changed(self, value):
        if self.view:
            # D: 滑块范围0-10000对应0-1，精度0.0001
            self.view.d_spinbox.blockSignals(True)
            self.view.d_spinbox.setValue(value / 10000.0)
            self.view.d_spinbox.blockSignals(False)
    
    def on_d_spinbox_changed(self, value):
        if self.view:
            # D: 数值0-1对应滑块0-10000
            self.view.d_slider.blockSignals(True)
            self.view.d_slider.setValue(int(value * 10000))
            self.view.d_slider.blockSignals(False)
    
    def on_preset_selected(self, name):
        """预设选中时自动加载"""
        if name:
            preset = self.preset_manager.get_preset(name)
            if preset and self.view:
                self.view.set_values(preset.p, preset.i, preset.d)
    
    def on_send_clicked(self):
        if self.view and self.serial_controller:
            values = self.view.get_current_values()
            p, i, d = values['p'], values['i'], values['d']
            
            self.pid_model.update_params(p, i, d)
            
            # 检查连接类型
            if self.serial_controller.active_service:
                from app.services.ssh_service import SSHService
                if isinstance(self.serial_controller.active_service, SSHService):
                    # SSH连接：通过命令行发送参数
                    command = f"echo 'P={p:.2f},I={i:.2f},D={d:.2f}' > /dev/ttyUSB0"
                    result = self.serial_controller.execute_ssh_command(command)
                    if result and result['success']:
                        print(f"通过SSH发送PID参数: P={p}, I={i}, D={d}")
                    else:
                        print(f"SSH发送失败: {result.get('error', '未知错误')}")
                else:
                    # 串口连接：直接发送数据
                    command = self.protocol_parser.create_pid_command(p, i, d)
                    if command:
                        success = self.serial_controller.send_data(command)
                        if success:
                            print(f"已发送PID参数: P={p}, I={i}, D={d}")
                        else:
                            print("发送失败")
            else:
                print("未连接")
    
    def on_save_preset(self):
        """保存预设"""
        if not self.view:
            return
        
        name = self.view.get_preset_name()
        if not name:
            self.view.show_message("错误", "请输入预设名称", "error")
            return
        
        values = self.view.get_current_values()
        success = self.preset_manager.add_preset(
            name=name,
            p=values['p'],
            i=values['i'],
            d=values['d']
        )
        
        if success:
            self.refresh_preset_list()
            self.view.clear_preset_name()
            self.view.show_message("成功", f"预设 '{name}' 已保存", "success")
        else:
            self.view.show_message("错误", "保存预设失败", "error")
    
    def on_load_preset(self):
        """加载预设"""
        if not self.view:
            return
        
        name = self.view.preset_combo.currentText()
        if not name:
            self.view.show_message("错误", "请选择一个预设", "error")
            return
        
        preset = self.preset_manager.get_preset(name)
        if preset:
            self.view.set_values(preset.p, preset.i, preset.d)
            self.view.show_message("成功", f"已加载预设 '{name}'", "success")
    
    def on_delete_preset(self):
        """删除预设"""
        if not self.view:
            return
        
        name = self.view.preset_combo.currentText()
        if not name:
            self.view.show_message("错误", "请选择要删除的预设", "error")
            return
        
        if self.view.show_message("确认", f"确定要删除预设 '{name}' 吗？", "question"):
            success = self.preset_manager.remove_preset(name)
            if success:
                self.refresh_preset_list()
                self.view.show_message("成功", f"预设 '{name}' 已删除", "success")
            else:
                self.view.show_message("错误", "删除预设失败", "error")
    
    def refresh_preset_list(self):
        """刷新预设列表"""
        if self.view:
            names = self.preset_manager.get_preset_names()
            self.view.update_preset_list(names)
    
    def update_from_data(self, data):
        if 'P' in data and 'I' in data and 'D' in data:
            self.pid_model.update_params(data['P'], data['I'], data['D'])
            if self.view:
                self.view.set_values(data['P'], data['I'], data['D'])