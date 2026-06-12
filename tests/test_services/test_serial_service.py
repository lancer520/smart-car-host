import pytest
from unittest.mock import Mock, patch
from app.services.serial_service import SerialService

def test_serial_service_initialization():
    service = SerialService()
    assert service.is_connected == False
    assert service.port == ""

@patch('serial.Serial')
def test_serial_service_connect(mock_serial):
    mock_serial.return_value.is_open = True
    service = SerialService()
    result = service.connect("COM1", 115200)
    assert result == True
    assert service.is_connected == True

def test_serial_service_disconnect():
    service = SerialService()
    service.is_connected = True
    service.serial = Mock()
    service.disconnect()
    assert service.is_connected == False

def test_protocol_parser_text_format():
    from app.services.protocol_parser import ProtocolParser
    
    parser = ProtocolParser()
    data = b"P=1.5,I=0.2,D=0.05,S=100.0"
    result = parser.parse(data)
    
    assert result['P'] == 1.5
    assert result['I'] == 0.2
    assert result['D'] == 0.05
    assert result['speed'] == 100.0