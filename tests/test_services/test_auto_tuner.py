import pytest
from app.services.auto_tuner import AutoTuner

def test_auto_tuner_initialization():
    tuner = AutoTuner()
    assert tuner.is_tuning == False
    assert tuner.algorithm == "ziegler_nichols"

def test_auto_tuner_set_algorithm():
    tuner = AutoTuner()
    tuner.set_algorithm("cohen_coon")
    assert tuner.algorithm == "cohen_coon"

def test_auto_tuner_full_process():
    tuner = AutoTuner()
    tuner.set_algorithm("ziegler_nichols")
    
    # 模拟调参过程
    tuner.start_tuning(100.0)
    
    # 模拟数据点
    for i in range(20):
        tuner.add_data_point(i * 0.1, 100.0 + (i % 5) * 2)
    
    result = tuner.calculate_tuning_params()
    
    assert result is not None
    assert result.p > 0
    assert result.i > 0
    assert result.d > 0
    assert result.algorithm == "ziegler_nichols"