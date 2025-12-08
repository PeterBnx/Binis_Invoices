from backend.ProductsDataFetcher import ProductsDataFetcher
from backend.Shared import shared_instance
from GUI.OrdersPage import OrdersPage
from GUI.OrderProductsPage import OrderProductsPage
from GUI.ChangeCredentialsPage import ChangeCredentialsPage
from PyQt6.QtWidgets import QMainWindow, QStackedWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(200, 200, 400, 400)

        self.stacked_widget = QStackedWidget()

        self.orders_page = OrdersPage(self)   #0
        self.order_products_page = OrderProductsPage(self) #1
        self.change_creds_page = ChangeCredentialsPage() #2

        self.products_data_fetcher = ProductsDataFetcher()

        if (self.are_creds_correct != 3):
            self.on_wrong_creds()

        self.initUI()

    def initUI(self):
        self.setGeometry(500, 500, 400, 400)

        self.stacked_widget.addWidget(self.orders_page)
        self.stacked_widget.addWidget(self.order_products_page)
        self.stacked_widget.addWidget(self.change_creds_page)

        self.setCentralWidget(self.stacked_widget)

        self.setWindowTitle('Τιμολόγια Μπινής')
        self.go_to_orders_page()


    # 0: Both are incorrect
    # 1: Only Emp is correct
    # 2: Only Cis is correct
    # 3: Both are correct
    def are_creds_correct(self):
        if (not shared_instance.cis_creds_correct and not self.orders_page.orders_data_fetcher.creds_correct): return 0
        elif (shared_instance.cis_creds_correct < self.orders_page.orders_data_fetcher.creds_correct): return 1
        elif (shared_instance.cis_creds_correct > self.orders_page.orders_data_fetcher.creds_correct): return 2
        else: return 3

    def on_wrong_creds(self):
        print(self.are_creds_correct())

    def go_to_orders_page(self):
        self.stacked_widget.setCurrentIndex(0)

    def go_to_order_products_page(self):
        self.stacked_widget.setCurrentIndex(1)

    def go_to_change_creds_page(self):
        self.stacked_widget.setCurrentIndex(2)
