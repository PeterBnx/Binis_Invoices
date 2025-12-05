from backend.OrdersDataFetcher import OrdersDataFetcher
from backend.ProductsDataFetcher import ProductsDataFetcher
from GUI.CustomDialog import CustomDialog
from GUI.OrderRow import OrderRow
from functools import partial
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QScrollArea

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(200, 200, 400, 400)
        self.scroll_widget = QWidget()
        self.v_layout = QVBoxLayout()
        self.scroll_area = QScrollArea()
        self.orders_data_fetcher = OrdersDataFetcher()
        self.initUI()

    def initUI(self):
        
        self.setGeometry(500, 500, 400, 400)

        # Set Window
        self.setWindowTitle('Τιμολόγια Μπινής')

        # Set Scroll Area
        self.scroll_area.setWidgetResizable(True)
        self.setCentralWidget(self.scroll_area)
        self.scroll_area.setWidget(self.scroll_widget)


        # Set Layout
        for i in range(len(self.orders_data_fetcher.order_elements)):
            order_number_text = self.orders_data_fetcher.order_elements[i]
            client_text = self.orders_data_fetcher.client_elements[i]
            date_text = self.orders_data_fetcher.date_elements[i]
            order_row = OrderRow(order_number_text, client_text, date_text, self)
            order_row.clicked.connect(partial(self.order_row_clicked, order_number_text))
            self.v_layout.addWidget(order_row)

        self.scroll_widget.setLayout(self.v_layout)

    # Handlers

    def order_row_clicked(self, order_number: str):
        self.products_data_fetcher = ProductsDataFetcher(str(order_number).strip())