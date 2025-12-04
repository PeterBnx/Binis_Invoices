from CustomDialog import CustomDialog
import sys
from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel, QLineEdit, QGridLayout, QWidget
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(200, 200, 400, 400)
        self.central_widget = QWidget(self)
        self.grid_layout = QGridLayout()
        self.label = QLabel("Εισαγωγή Παραγγελίας:")
        self.text = QLineEdit(self)
        self.button = QPushButton("Αναζήτηση", self)
        self.initUI()

    def initUI(self):
        self.setHandlers()
        self.setGeometry(500, 500, 400, 400)
        self.setCentralWidget(self.central_widget)

        # Set Window
        self.setWindowTitle('Τιμολόγια Μπινής')

        # Set Layout
        self.grid_layout.addWidget(self.label, 0, 0, 1, 2, Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(self.text, 1, 0)
        self.grid_layout.addWidget(self.button, 1, 1)
        self.central_widget.setLayout(self.grid_layout)

        # Set Line Edit
        self.text.setPlaceholderText('Αριμός Παραγγελίας')

    def setHandlers(self):
        self.button.clicked.connect(self.buttonSearchHandler)

    # Handlers
    def buttonSearchHandler(self):
        order_text = self.text.text()
        if (not order_text.isnumeric()):
            error_dialog = CustomDialog('Η παραγγελία πρέπει να αποτελείται μόνο από αριθμούς', self, 'Προσοχή!')
            error_dialog.show()

if __name__=='__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())