import pytest
import os
import tempfile
from app.services.data_recorder import DataRecorder

def test_data_recorder_initialization():
    recorder = DataRecorder()
    assert recorder.is_recording == False
    assert recorder.record_file is None

def test_data_recorder_start_stop():
    recorder = DataRecorder()
    with tempfile.TemporaryDirectory() as tmpdir:
        recorder.start_recording(os.path.join(tmpdir, "test.log"))
        assert recorder.is_recording == True
        
        recorder.stop_recording()
        assert recorder.is_recording == False

def test_data_recorder_record_data():
    recorder = DataRecorder()
    with tempfile.TemporaryDirectory() as tmpdir:
        recorder.start_recording(os.path.join(tmpdir, "test.log"))
        
        recorder.record_data(b"test data", {"P": 1.0, "I": 0.1, "D": 0.01})
        
        assert len(recorder.records) == 1
        assert recorder.records[0]['parsed_data']['P'] == 1.0
        
        recorder.stop_recording()