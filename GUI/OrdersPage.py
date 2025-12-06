from backend.OrdersDataFetcher import OrdersDataFetcher
from backend.ProductsDataFetcher import ProductsDataFetcher
from backend.Shared import shared_instance
from GUI.OrderRow import OrderRow
from functools import partial
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea

class OrdersPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.scroll_widget = QWidget()
        self.v_layout = QVBoxLayout()
        self.scroll_area = QScrollArea()
        self.orders_data_fetcher = OrdersDataFetcher()

        self.initUI()

    def initUI(self):
        # Set Scroll Area
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)


        # Set Layout
        for i in range(len(self.orders_data_fetcher.order_elements)):
            order_number_text = self.orders_data_fetcher.order_elements[i]
            client_text = self.orders_data_fetcher.client_elements[i]
            date_text = self.orders_data_fetcher.date_elements[i]
            order_row = OrderRow(order_number_text, client_text, date_text, self)

            # connect button handlers
            order_row.clicked.connect(partial(self.order_row_clicked, order_number_text))

            # add to layout
            self.v_layout.addWidget(order_row)

        layout = QVBoxLayout()
        layout.addWidget(self.scroll_area)
        self.setLayout(layout)
        self.scroll_widget.setLayout(self.v_layout)

    
    def order_row_clicked(self, order_number: str):
        self.main_window.products_data_fetcher.fetch_order_products_data(order_number) # fetches products data
        self.main_window.order_products_page.set_order_products_page(self.main_window.products_data_fetcher) # sets products data page using fetcher
        self.main_window.go_to_order_products_page() # directs to products data page