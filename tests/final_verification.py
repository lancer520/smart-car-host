import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def verify_all_components():
    print("=== 智能车上位机调试软件最终验证 ===\n")
    
    # 1. 验证模块导入
    print("1. 验证模块导入...")
    try:
        from app.models.serial_model import SerialModel
        from app.models.pid_model import PIDModel
        from app.services.serial_service import SerialService
        from app.services.protocol_parser import ProtocolParser
        from app.services.data_recorder import DataRecorder
        from app.services.auto_tuner import AutoTuner
        print("   [OK] 所有模块导入成功")
    except ImportError as e:
        print(f"   [FAIL] 模块导入失败: {e}")
        return False
    
    # 2. 验证数据模型
    print("\n2. 验证数据模型...")
    try:
        serial_model = SerialModel()
        pid_model = PIDModel()
        
        # 测试串口模型
        serial_model.update_config("COM1", 115200)
        data = serial_model.add_data(b"test", {"P": 1.0})
        assert data.parsed_data["P"] == 1.0
        
        # 测试PID模型
        pid_model.update_params(1.0, 0.1, 0.01)
        assert pid_model.p == 1.0
        
        print("   [OK] 数据模型验证通过")
    except Exception as e:
        print(f"   [FAIL] 数据模型验证失败: {e}")
        return False
    
    # 3. 验证服务
    print("\n3. 验证服务...")
    try:
        # 测试协议解析器
        parser = ProtocolParser()
        result = parser.parse(b"P=1.5,I=0.2,D=0.05")
        assert result["P"] == 1.5
        
        # 测试数据记录器
        recorder = DataRecorder()
        recorder.start_recording("test_verify.log")
        recorder.record_data(b"test", {"P": 1.0})
        assert len(recorder.records) == 1
        recorder.stop_recording()
        
        # 清理测试文件
        if os.path.exists("test_verify.log"):
            os.remove("test_verify.log")
        
        print("   [OK] 服务验证通过")
    except Exception as e:
        print(f"   [FAIL] 服务验证失败: {e}")
        return False
    
    # 4. 验证UI组件（基本导入）
    print("\n4. 验证UI组件...")
    try:
        from PyQt5.QtWidgets import QApplication
        from app.views.main_window import MainWindow
        from app.views.serial_panel import SerialPanel
        from app.views.pid_panel import PIDPanel
        from app.views.chart_panel import ChartPanel
        from app.views.log_panel import LogPanel
        print("   [OK] UI组件验证通过")
    except ImportError as e:
        print(f"   [FAIL] UI组件验证失败: {e}")
        return False
    
    print("\n=== 验证完成 ===")
    print("所有组件验证通过！")
    return True

if __name__ == "__main__":
    success = verify_all_components()
    sys.exit(0 if success else 1)