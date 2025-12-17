from PyQt6.QtWidgets import (
    QDialog, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit
)
from PyQt6.QtCore import Qt


class AddProdTypeBox(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Προσθήκη Τύπου Προϊόντος')
        self.setFixedSize(400, 120)
        self.setModal(True)

        layout = QVBoxLayout(self)

        label = QLabel('Εισάγετε τον νέο τύπο προϊόντος για καταχώρηση:')
        self.line_edit = QLineEdit()

        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton('Ακύρωση')
        add_btn = QPushButton('Προσθήκη')

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(add_btn)

        layout.addWidget(label)
        layout.addWidget(self.line_edit)
        layout.addLayout(btn_layout)

        cancel_btn.clicked.connect(self.reject)
        add_btn.clicked.connect(self.accept)
