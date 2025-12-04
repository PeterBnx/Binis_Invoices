import sys
from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel, QPlainTextEdit, QGridLayout, QWidget
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(200, 200, 400, 400)
        self.central_widget = QWidget(self)
        self.layout = QGridLayout()
        self.label = QLabel("Εισαγωγή Παραγγελίας:")
        self.text = QPlainTextEdit(self)
        self.button = QPushButton("Αναζήτηση", self)
        self.initUI()

    def initUI(self):
        self.setGeometry(500, 500, 400, 400)
        self.setCentralWidget(self.central_widget)
        self.layout.addWidget(self.label, 0, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.text, 1, 0)
        self.layout.addWidget(self.button, 1, 1)
        self.central_widget.setLayout(self.layout)
        

if __name__=='__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())