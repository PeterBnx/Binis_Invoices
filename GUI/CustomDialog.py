from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class CustomDialog(QDialog):
    def __init__(self, message:str, type='close', parent=None, title='Μπινής'):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setModal(True)


        if (type == 'close'):
            self.button = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
            self.button.rejected.connect(self.close)
        elif (type == 'ok'):
            self.button = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
            self.button.accepted.connect(self.close)

        layout = QVBoxLayout()
        message_label = QLabel(message)
        layout.addWidget(message_label)
        layout.addWidget(self.button)
        self.setLayout(layout)

        self.adjustSize()
        self.setFixedSize(self.size())