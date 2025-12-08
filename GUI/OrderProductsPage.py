from backend.ProductsRegister import ProductsRegister
from backend.InvoiceMaker import InvoiceMaker
from GUI.CustomDialog import CustomDialog
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QPushButton

class OrderProductsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Row widgets
        self.row_widgets = []
        self.is_registered_labels = []

        # Layouts
        self.gen_layout = QVBoxLayout()
        self.scroll_layout = QVBoxLayout()
        self.main_btns_layout = QHBoxLayout()

        # ScrollArea
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()

        # Buttons
        self.back_btn = QPushButton('Πίσω')

        # Main buttons
        self.register_btn = QPushButton('Καταχώρηση Προϊόντων')
        self.invoice_btn = QPushButton('Εξαγωγή Τιμολογίου')
        self.main_btns_widget = QWidget()


    def initUI(self, products_data_fetcher):
        self.products_data_fetcher = products_data_fetcher

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

        # Set main buttons
        self.register_btn.clicked.connect(self.on_register_btn_click)
        self.invoice_btn.clicked.connect(self.on_make_invoice_btn_click)
        self.main_btns_layout.addWidget(self.register_btn)
        self.main_btns_layout.addWidget(self.invoice_btn)
        self.main_btns_widget.setLayout(self.main_btns_layout)
        self.gen_layout.addWidget(self.main_btns_widget)

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

        self.is_registered_labels.append(is_registered_label)

        row_widget = QWidget()
        row_widget.setLayout(layout)
        self.row_widgets.append(row_widget)
    
    def set_order_products_page(self, products_data_fetcher):
        self.initUI(products_data_fetcher)

    def set_prod_is_registered_labels(self):
        for i in range(len(self.is_registered_labels)):
            self.is_registered_labels[i] = str(self.products_data_fetcher.prod_is_registered[i])

    def reset_order_products_page(self):
        self.row_widgets.clear()
        self.is_registered_labels.clear()

        for i in reversed(range(self.scroll_layout.count())): 
            self.scroll_layout.itemAt(i).widget().setParent(None)

        for i in reversed(range(self.gen_layout.count())): 
            self.gen_layout.itemAt(i).widget().setParent(None)


    
    # Button Handlers
    def on_back_btn_click(self):
        self.reset_order_products_page()
        self.products_data_fetcher.reset_fetcher()
        self.main_window.go_to_orders_page()

    def on_register_btn_click(self):
        if (not False in self.products_data_fetcher.prod_is_registered):
            dialog = CustomDialog('Όλα τα προϊόντα της παραγγελίας είναι καταχωρημένα.\nΜπορείτε να προχωρήσετε στην εξαγωγή τιμολογίου.',
                                  type='ok', parent=self)
            dialog.show()
        else:
            products_register = ProductsRegister()
            products_register.register(self.products_data_fetcher)

    def on_make_invoice_btn_click(self):
        invoice_maker = InvoiceMaker()
        invoice_maker.make_invoice(self.products_data_fetcher)