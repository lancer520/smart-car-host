import pytest
from app.models.pid_model import PIDModel, PIDData

def test_pid_model_initialization():
    model = PIDModel()
    assert model.p == 1.0
    assert model.i == 0.1
    assert model.d == 0.01

def test_pid_data_creation():
    data = PIDData(timestamp=1234567890, p=1.0, i=0.1, d=0.01, setpoint=100.0, actual=95.0)
    assert data.p == 1.0
    assert data.error == 5.0  # setpoint - actual