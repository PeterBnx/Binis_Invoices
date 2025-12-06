from backend.ProductsDataFetcher import ProductsDataFetcher
from GUI.OrdersPage import OrdersPage
from GUI.OrderProductsPage import OrderProductsPage
from PyQt6.QtWidgets import QMainWindow, QStackedWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(200, 200, 400, 400)

        self.stacked_widget = QStackedWidget()

        self.orders_page = OrdersPage(self)   #0
        self.order_products_page = OrderProductsPage(self) #1

        self.products_data_fetcher = ProductsDataFetcher()

        self.initUI()

    def initUI(self):
        self.setGeometry(500, 500, 400, 400)

        self.stacked_widget.addWidget(self.orders_page)
        self.stacked_widget.addWidget(self.order_products_page)

        self.setCentralWidget(self.stacked_widget)

        self.setWindowTitle('Τιμολόγια Μπινής')
        self.go_to_orders_page()

    def go_to_orders_page(self):
        self.stacked_widget.setCurrentIndex(0)

    def go_to_order_products_page(self):
        self.stacked_widget.setCurrentIndex(1)
