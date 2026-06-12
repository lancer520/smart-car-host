from app.views.chart_panel import ChartPanel

class ChartController:
    def __init__(self):
        self.chart_panel = None
        self.is_paused = False
    
    def set_view(self, chart_panel):
        self.chart_panel = chart_panel
        self.connect_signals()
    
    def connect_signals(self):
        if self.chart_panel:
            self.chart_panel.clear_btn.clicked.connect(self.on_clear_clicked)
            self.chart_panel.pause_btn.clicked.connect(self.on_pause_clicked)
    
    def on_clear_clicked(self):
        if self.chart_panel:
            self.chart_panel.clear_data()
    
    def on_pause_clicked(self):
        self.is_paused = not self.is_paused
        if self.chart_panel:
            if self.is_paused:
                self.chart_panel.pause_btn.setText("继续")
            else:
                self.chart_panel.pause_btn.setText("暂停")
    
    def update_data(self, p, i, d):
        if self.chart_panel and not self.is_paused:
            self.chart_panel.update_data(p, i, d)