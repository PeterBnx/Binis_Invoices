from CustomDialog import CustomDialog
from OrderRow import OrderRow
import sys
from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel, QLineEdit, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(200, 200, 400, 400)
        self.central_widget = QWidget(self)
        self.v_layout = QVBoxLayout()
        self.initUI()

    def initUI(self):
        self.setGeometry(500, 500, 400, 400)
        self.setCentralWidget(self.central_widget)

        # Set Window
        self.setWindowTitle('Τιμολόγια Μπινής')

        # Set Layout
        order_row = OrderRow("11111", "Πελάτης", "12/10/2025", self)
        order_row.clicked.connect(lambda: self.order_row_clicked(order_row.order_number_text.text()))
        self.v_layout.addWidget(order_row)

        self.central_widget.setLayout(self.v_layout)

    # Handlers

    def order_row_clicked(self, order_number):
        print(order_number)

if __name__=='__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())