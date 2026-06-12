import json
import csv
from datetime import datetime
from typing import Dict, Any, List

class DataRecorder:
    def __init__(self):
        self.is_recording = False
        self.record_file = None
        self.records: List[Dict[str, Any]] = []
        self.raw_data_buffer: List[bytes] = []
    
    def start_recording(self, filename):
        self.is_recording = True
        self.record_file = filename
        self.records.clear()
        self.raw_data_buffer.clear()
        
        # 创建文件头
        with open(filename, 'w', encoding='utf-8') as f:
            if filename.endswith('.csv'):
                writer = csv.writer(f)
                writer.writerow(['timestamp', 'raw_data', 'parsed_data'])
            elif filename.endswith('.json'):
                f.write('[\n')
    
    def stop_recording(self):
        self.is_recording = False
        
        if self.record_file and self.record_file.endswith('.json'):
            with open(self.record_file, 'a', encoding='utf-8') as f:
                f.write('\n]')
        
        self.record_file = None
    
    def record_data(self, raw_data: bytes, parsed_data: Dict[str, Any]):
        if not self.is_recording:
            return
        
        timestamp = datetime.now().isoformat()
        
        record = {
            "timestamp": timestamp,
            "raw_data": raw_data.hex(),
            "parsed_data": parsed_data
        }
        
        self.records.append(record)
        
        # 实时写入文件
        if self.record_file:
            with open(self.record_file, 'a', encoding='utf-8') as f:
                if self.record_file.endswith('.csv'):
                    writer = csv.writer(f)
                    writer.writerow([timestamp, raw_data.hex(), json.dumps(parsed_data)])
                elif self.record_file.endswith('.json'):
                    json.dump(record, f)
                    f.write(',\n')
    
    def record_raw_data(self, data: bytes):
        if self.is_recording:
            self.raw_data_buffer.append(data)
    
    def get_recording_stats(self):
        return {
            "is_recording": self.is_recording,
            "record_count": len(self.records),
            "file": self.record_file
        }
    
    def export_to_format(self, format_type: str, output_file: str):
        if format_type == 'csv':
            self._export_to_csv(output_file)
        elif format_type == 'json':
            self._export_to_json(output_file)
        elif format_type == 'txt':
            self._export_to_txt(output_file)
    
    def _export_to_csv(self, output_file: str):
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'raw_data', 'parsed_P', 'parsed_I', 'parsed_D'])
            
            for record in self.records:
                parsed = record.get('parsed_data', {})
                writer.writerow([
                    record['timestamp'],
                    record['raw_data'],
                    parsed.get('P', ''),
                    parsed.get('I', ''),
                    parsed.get('D', '')
                ])
    
    def _export_to_json(self, output_file: str):
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.records, f, indent=2)
    
    def _export_to_txt(self, output_file: str):
        with open(output_file, 'w', encoding='utf-8') as f:
            for record in self.records:
                f.write(f"{record['timestamp']}: {record['raw_data']}\n")