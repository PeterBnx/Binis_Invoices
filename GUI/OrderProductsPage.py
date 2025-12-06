from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QPushButton

class OrderProductsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Products Labels
        self.quantity_labels = []
        self.code_labels = []
        self.description_labels = []
        self.price_labels = []
        self.is_registered_labels = []

        # Row widgets
        self.row_widgets = []

        # Layouts
        self.gen_layout = QVBoxLayout()
        self.scroll_layout = QVBoxLayout()

        # ScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()

        # Buttons
        self.back_btn = QPushButton('Πίσω')


    def showEvent(self, event):
        super().showEvent(event)


        # Now you can use:
        # products_fetcher.product_names
        # products_fetcher.product_prices
        # etc

    def initUI(self, products_data_fetcher):
        # Set Back Button
        self.gen_layout.addWidget(self.back_btn)
        self.back_btn.clicked.connect(self.on_back_btn_click)

        # ScrollArea
        for i in range(len(products_data_fetcher.prod_codes)):
            self.add_data_row(products_data_fetcher, i)

        for row_widget in self.row_widgets:
            self.scroll_layout.addWidget(row_widget)

        self.scroll_widget.setLayout(self.scroll_layout)
        
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)

        self.gen_layout.addWidget(self.scroll_area)
        self.setLayout(self.gen_layout)


    def add_data_row(self, products_data_fetcher, index):
        quantity_label = QLabel(products_data_fetcher.prod_quantities[index])
        code_label = QLabel(products_data_fetcher.prod_codes[index])
        description_label = QLabel(products_data_fetcher.prod_descriptions[index])
        price_label = QLabel(products_data_fetcher.prod_prices[index])
        is_registered_label = QLabel(str(products_data_fetcher.prod_is_registered[index]))

        layout = QHBoxLayout()
        layout.addWidget(quantity_label)
        layout.addWidget(code_label)
        layout.addWidget(description_label)
        layout.addWidget(price_label)
        layout.addWidget(is_registered_label)
        # self.quantity_labels.append(quantity_label)
        # self.code_labels.append(code_label)
        # self.description_labels.append(description_label)
        # self.price_labels.append(price_label)
        # self.is_registered_labels.append(is_registered_label)
        row_widget = QWidget()
        row_widget.setLayout(layout)
        self.row_widgets.append(row_widget)
    
    def set_order_products_page(self, products_data_fetcher):
        self.initUI(products_data_fetcher)

    
    # Button Handlers
    def on_back_btn_click(self):
        self.main_window.go_to_orders_page()