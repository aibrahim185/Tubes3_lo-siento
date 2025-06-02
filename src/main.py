import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    app.setApplicationName("ATS CV Analyzer")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("LO-SIENTO Team")
    
    try:
        # Create and show main window
        main_window = MainWindow()
        main_window.show()
        
        # Start application event loop
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
