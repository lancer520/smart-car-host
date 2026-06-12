from app.views.log_panel import LogPanel
from datetime import datetime
import json
import csv
import io

class LogController:
    def __init__(self):
        self.log_panel = None
        self.log_data = []
    
    def set_view(self, log_panel):
        self.log_panel = log_panel
        self.connect_signals()
    
    def connect_signals(self):
        if self.log_panel:
            self.log_panel.clear_btn.clicked.connect(self.on_clear_clicked)
            self.log_panel.save_btn.clicked.connect(self.on_save_clicked)
    
    def on_clear_clicked(self):
        if self.log_panel:
            self.log_panel.clear_log()
            self.log_data.clear()
    
    def on_save_clicked(self):
        if self.log_panel:
            content = self.log_panel.get_log_content()
            format_type = self.log_panel.format_combo.currentText()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"log_{timestamp}.{format_type.lower()}"
            
            with open(filename, 'w', encoding='utf-8') as f:
                if format_type == "TXT":
                    f.write(content)
                elif format_type == "CSV":
                    writer = csv.writer(f)
                    for line in content.split('\n'):
                        if line.strip():
                            writer.writerow([line])
                elif format_type == "JSON":
                    json.dump({"logs": content.split('\n')}, f, indent=2)
            
            print(f"日志已保存到: {filename}")
    
    def add_log(self, message, log_type="info", data=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "type": log_type,
            "message": message,
            "data": data
        }
        self.log_data.append(log_entry)
        
        if self.log_panel:
            self.log_panel.append_log(f"{timestamp} - {message}", log_type)