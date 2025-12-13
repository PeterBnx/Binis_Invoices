from backend.ProductsRegister import ProductsRegister
from backend.InvoiceMaker import InvoiceMaker
from GUI.CustomDialog import CustomDialog
from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QScrollArea, QPushButton, QComboBox, QLineEdit
from PyQt6.QtCore import Qt


class OrderProductsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.products_data_fetcher = None
        self.ui_built = False

        # Top layout
        self.top_layout = QHBoxLayout()
        self.back_btn = QPushButton('Πίσω')

        # Invoice type Combobox
        self.invoice_type_combo = QComboBox()
        self.invoice_type_combo.addItem('ΤΔΑ', 'τδα')
        self.invoice_type_combo.addItem('INVE', 'inve')

        self.back_btn.clicked.connect(self.on_back_btn_click)
        self.top_layout.addWidget(self.back_btn)
        self.top_layout.addStretch()
        self.top_layout.addWidget(QLabel('Τύπος Τιμολογίου:'))
        self.top_layout.addWidget(self.invoice_type_combo)

        self.cat_layout = QHBoxLayout()
        self.cat_layout.addWidget(QLabel('Ποσότητα'))
        self.cat_layout.addWidget(QLabel('Κωδικός'))
        self.cat_layout.addWidget(QLabel('Περιγραφή'))
        self.cat_layout.addWidget(QLabel('Τιμή'))
        self.cat_layout.addWidget(QLabel('Καταχωρημένο'))

        self.cat_widget = QWidget()
        self.cat_widget.setLayout(self.cat_layout)


        # Scroll Area
        self.prod_brand_labels = []
        self.scroll_layout = QVBoxLayout()
        self.scroll_widget = QWidget()
        self.scroll_widget.setLayout(self.scroll_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_widget)

        self.register_btn = QPushButton('Καταχώρηση Προϊόντων')
        self.invoice_btn = QPushButton('Εξαγωγή Τιμολογίου')

        self.register_btn.clicked.connect(self.on_register_btn_click)
        self.invoice_btn.clicked.connect(self.on_make_invoice_btn_click)

        self.main_btns_layout = QHBoxLayout()
        self.main_btns_layout.addWidget(self.register_btn)
        self.main_btns_layout.addWidget(self.invoice_btn)

        self.main_btns_widget = QWidget()
        self.main_btns_widget.setLayout(self.main_btns_layout)

        self.gen_layout = QVBoxLayout(self)
        self.gen_layout.addLayout(self.top_layout)
        self.gen_layout.addWidget(self.cat_widget)
        self.gen_layout.addWidget(self.scroll_area)
        self.gen_layout.addWidget(self.main_btns_widget)

    def initUI(self, products_data_fetcher):
        self.products_data_fetcher = products_data_fetcher
        self.populate_products()

    def populate_products(self):
        f = self.products_data_fetcher

        curr_prod_counter = 0
        brand_counter = 0
        i = 0

        while i < len(f.prod_codes):
            if curr_prod_counter == 0:
                brand_edit = QLineEdit(f.brands_full[brand_counter])
                brand_edit.textChanged.connect(lambda text, p=i, b=brand_counter: self.on_brand_edit_change(text, p, b))
                brand_edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.scroll_layout.addWidget(brand_edit)

            if curr_prod_counter < f.brands_number_of_products[brand_counter]:
                self.add_data_row(f, i)
                curr_prod_counter += 1
                i += 1
            else:
                brand_counter += 1
                curr_prod_counter = 0

    def add_data_row(self, f, index):
        layout = QHBoxLayout()

        layout.addWidget(QLabel(str(f.prod_quantities[index])))
        layout.addWidget(QLabel(f.prod_codes[index]))

        # Prod Type
        prod_type_combo = QComboBox()
        prod_type_combo.addItem('Ρολόι', 'watch')
        prod_type_combo.addItem('Κόσμημα', 'jewlery')
        prod_type_combo.addItem('Γυαλιά', 'glasses')
        prod_type_combo.addItem('Άλλο', 'other')
        prod_type_combo.currentTextChanged.connect(lambda text: self.on_prod_type_combo_change(text, index))

        type_dict = {
            'Ρολόι' : 0,
            'Κόσμημα' : 1,
            'Γυαλιά' : 2,
            'Άλλο' : 3
        }
        prod_type_combo.setCurrentIndex(type_dict[f.prod_types[index]])
        layout.addWidget(prod_type_combo)

        # Prod brand
        brand_label = QLabel(f.prod_brands_short[index])
        layout.addWidget(brand_label)
        self.prod_brand_labels.append(brand_label)

        layout.addWidget(QLabel(f.prod_prices[index] + ' €'))
        layout.addWidget(QLabel('Ναι' if f.prod_is_registered[index] else 'Όχι'))

        row_widget = QWidget()
        row_widget.setLayout(layout)
        self.scroll_layout.addWidget(row_widget)

    def reset_order_products_page(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.products_data_fetcher = None
        self.invoice_type_combo.setCurrentIndex(0)

    def set_order_products_page(self, products_data_fetcher):
        self.reset_order_products_page()
        self.initUI(products_data_fetcher)

    def on_back_btn_click(self):
        self.reset_order_products_page()
        if self.products_data_fetcher:
            self.products_data_fetcher.reset_fetcher()
        self.main_window.go_to_orders_page()

    def on_register_btn_click(self):
        if not False in self.products_data_fetcher.prod_is_registered:
            dialog = CustomDialog(
                'Όλα τα προϊόντα της παραγγελίας είναι καταχωρημένα.\n'
                'Μπορείτε να προχωρήσετε στην εξαγωγή τιμολογίου.',
                type='ok',
                parent=self
            )
            dialog.show()
        else:
            ProductsRegister().register(self.products_data_fetcher)

    def on_make_invoice_btn_click(self):
        InvoiceMaker().make_invoice(
            self.products_data_fetcher,
            self.invoice_type_combo.currentData()
        )

    def on_prod_type_combo_change(self, new_text, prod_num):
        prod_fetcher = self.products_data_fetcher
        prod_fetcher.prod_types[prod_num] = new_text
        prod_fetcher.prod_descriptions[prod_num] = new_text + ' ' + prod_fetcher.prod_brands_short[prod_num]
        print(prod_fetcher.prod_descriptions[prod_num])

    def on_brand_edit_change(self, new_text, prod_num, brand_num):
        curr_prod_counter = 0
        prod_fetcher = self.products_data_fetcher
        while (curr_prod_counter < prod_fetcher.brands_number_of_products[brand_num]):
            self.prod_brand_labels[prod_num].setText(new_text)
            prod_fetcher.prod_brands_short[prod_num] = new_text
            prod_fetcher.prod_descriptions[prod_num] = prod_fetcher.prod_types[prod_num] + ' ' + new_text
            curr_prod_counter += 1
            prod_num += 1