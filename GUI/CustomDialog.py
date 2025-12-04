from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel

class CustomDialog(QDialog):
    def __init__(self, message:str, parent=None, title='Μπινής'):
        super().__init__(parent)

        self.setWindowTitle(title)

        self.button = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        self.button.rejected.connect(self.close)


        layout = QVBoxLayout()
        message_label = QLabel(message)
        layout.addWidget(message_label)
        layout.addWidget(self.button)
        self.setLayout(layout)