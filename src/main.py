import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    app.setApplicationName("ATS CV Analyzer")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("LO-SIENTO Team")
    
    main_window = MainWindow()
    main_window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
