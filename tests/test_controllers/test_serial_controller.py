import pytest
from unittest.mock import Mock, patch
from app.controllers.serial_controller import SerialController

def test_serial_controller_initialization():
    controller = SerialController()
    assert controller.serial_service is not None
    assert controller.serial_model is not None

def test_serial_controller_connect():
    controller = SerialController()
    controller.serial_service = Mock()
    controller.serial_service.connect.return_value = True
    
    result = controller.connect("COM1", 115200)
    assert result == True