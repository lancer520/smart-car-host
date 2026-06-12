import pytest
from app.models.serial_model import SerialModel, SerialData

def test_serial_model_initialization():
    model = SerialModel()
    assert model.port == ""
    assert model.baudrate == 115200
    assert model.is_connected == False

def test_serial_data_creation():
    data = SerialData(timestamp=1234567890, raw_data=b"test", parsed_data={"P": 1.0})
    assert data.timestamp == 1234567890
    assert data.raw_data == b"test"
    assert data.parsed_data["P"] == 1.0