from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QRect
from PyQt6.QtGui import QPainter, QColor, QFont, QPen


class OrderRow(QWidget):
    clicked = pyqtSignal()         # emits when clicked
    hovered = pyqtSignal(bool)     # emits on hover enter/leave

    def __init__(self, order_number_text="Αριθμός Παραγγελίας", client_text="Πελάτης", date_text="Ημερομηνία", parent=None):
        super().__init__(parent)
        self.h_layout = QHBoxLayout()
        self.order_number_text = QLabel(order_number_text, self)
        self.client_text = QLabel(client_text, self)
        self.date_text = QLabel(date_text, self)
        self.hovering = False
        self.setMouseTracking(True)


    def paintEvent(self, event):
        painter = QPainter(self)
        # painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background color (changes on hover)
        if self.hovering:
            color = QColor("#3f6ad8")
        else:
            color = QColor("#2f4c81")

        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 12, 12)

        # Text Align
        self.order_number_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.client_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.h_layout.addWidget(self.order_number_text)
        self.h_layout.addWidget(self.client_text)
        self.h_layout.addWidget(self.date_text)
        self.setLayout(self.h_layout)


    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def enterEvent(self, event):
        self.hovering = True
        self.hovered.emit(True)
        self.update()

    def leaveEvent(self, event):
        self.hovering = False
        self.hovered.emit(False)
        self.update()
