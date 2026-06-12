import sys
from PyQt5.QtWidgets import QApplication
from app.views.main_window import MainWindow
from app.utils.config import Config
from app.utils.logger import setup_logger

def main():
    setup_logger()
    config = Config()
    
    app = QApplication(sys.argv)
    window = MainWindow(config)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()