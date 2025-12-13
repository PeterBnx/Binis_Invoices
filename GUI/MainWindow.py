from backend.ProductsDataFetcher import ProductsDataFetcher
from backend.Shared import shared_instance
from GUI.CustomDialog import CustomDialog
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

        self.initUI()

    def initUI(self):
        self.setGeometry(500, 500, 400, 400)

        self.stacked_widget.addWidget(self.orders_page)
        self.stacked_widget.addWidget(self.order_products_page)
        self.stacked_widget.addWidget(self.change_creds_page)

        self.setCentralWidget(self.stacked_widget)

        self.setWindowTitle('Τιμολόγια Μπινής')
        
        if (self.are_creds_correct() != 3): #testing
            self.on_wrong_creds()
        else:
            self.orders_page.initUI()
            self.go_to_orders_page()


    # 0: Both are incorrect
    # 1: Only Emp is correct
    # 2: Only Cis is correct
    # 3: Both are correct
    def are_creds_correct(self):
        emp_creds_correct = shared_instance.get_all_orders()
        cis_creds_correct = shared_instance.get_all_registered_products()

        if emp_creds_correct and cis_creds_correct:
            return 3
        if emp_creds_correct and not cis_creds_correct:
            return 1
        if cis_creds_correct and not emp_creds_correct:
            return 2
        return 0
    
    def on_wrong_creds(self):
        dialog = CustomDialog(
            message='Λάθος Πιστοποιητικά. Αλλάξτε τους αποθηκευμένους κωδικούς.',
            type='ok',
            parent=self,
            title='Λάθος Κωδικοί'
        )
        dialog.button.clicked.connect(self.on_dialog_accept)
        dialog.exec()

    def on_dialog_accept(self):
        self.change_creds_page.save_btn.clicked.connect(self.on_save_creds_click)
        self.go_to_change_creds_page()

    def on_save_creds_click(self):
        self.change_creds_page.on_save_btn_click()
        shared_instance.reset_session()

        if (self.are_creds_correct() != 3): #testing
            self.on_wrong_creds()
        else:
            self.orders_page.initUI()
            self.go_to_orders_page()

    def go_to_orders_page(self):
        self.stacked_widget.setCurrentIndex(0)

    def go_to_order_products_page(self):
        self.stacked_widget.setCurrentIndex(1)

    def go_to_change_creds_page(self):
        self.stacked_widget.setCurrentIndex(2)
