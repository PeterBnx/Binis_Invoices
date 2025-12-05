import sys
from PyQt6.QtWidgets import QApplication
from GUI.MainWindow import MainWindow
from backend.db import DB
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    
if __name__ == '__main__':
    main()
