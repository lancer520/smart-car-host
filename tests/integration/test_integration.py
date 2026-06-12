import pytest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.models.serial_model import SerialModel
from app.models.pid_model import PIDModel
from app.services.serial_service import SerialService
from app.services.protocol_parser import ProtocolParser
from app.services.data_recorder import DataRecorder

def test_model_serialization():
    # 测试数据模型序列化
    model = SerialModel()
    model.update_config("COM1", 115200)
    
    data = model.add_data(b"test", {"P": 1.0})
    assert data.raw_data == b"test"
    assert data.parsed_data["P"] == 1.0

def test_protocol_parsing():
    # 测试协议解析
    parser = ProtocolParser()
    data = b"P=1.5,I=0.2,D=0.05"
    result = parser.parse(data)
    
    assert result["P"] == 1.5
    assert result["I"] == 0.2
    assert result["D"] == 0.05

def test_data_recording():
    # 测试数据记录
    recorder = DataRecorder()
    recorder.start_recording("test_integration.log")
    
    recorder.record_data(b"test", {"P": 1.0})
    assert len(recorder.record_data) == 1
    
    recorder.stop_recording()
    
    # 清理测试文件
    if os.path.exists("test_integration.log"):
        os.remove("test_integration.log")