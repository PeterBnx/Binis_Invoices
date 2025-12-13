from backend.pathResolver import PathResolver
from backend.Shared import shared_instance
from PyQt6.QtWidgets import QWidget, QLabel,  QLineEdit, QPushButton, QVBoxLayout, QGridLayout, QHBoxLayout
from PyQt6.QtCore import Qt

class ChangeCredentialsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.v_layout = QVBoxLayout()
        self.emp_grid = QGridLayout()
        self.cis_grid = QGridLayout()

        self.emp_widget = QWidget()
        self.cis_widget = QWidget()

        self.emp_label = QLabel('Emporiorologion.gr', self)
        self.cis_label = QLabel('Λογιστικό', self)
        self.emp_username_label = QLabel('Όνομα Χρήστη', self)
        self.emp_passwd_label = QLabel('Κωδικός', self)
        self.cis_username_label = QLabel('Όνομα Χρήστη', self)
        self.cis_passwd_label = QLabel('Κωδικός', self)

        self.emp_username_txt =  QLineEdit(shared_instance.emp_name, self)
        self.emp_passwd_txt =  QLineEdit(shared_instance.emp_passwd, self)
        self.cis_username_txt =  QLineEdit(shared_instance.cis_name, self)
        self.cis_passwd_txt =  QLineEdit(shared_instance.cis_passwd, self)

        self.save_btn = QPushButton('Αποθήκευση', self)

        self.initUI()

    def initUI(self):
        self.emp_grid.addWidget(self.emp_label, 0, 0, 1, 0, Qt.AlignmentFlag.AlignCenter)
        self.emp_grid.addWidget(self.emp_username_label, 1, 0, Qt.AlignmentFlag.AlignCenter)
        self.emp_grid.addWidget(self.emp_passwd_label, 2, 0, Qt.AlignmentFlag.AlignCenter)
        self.emp_grid.addWidget(self.emp_username_txt, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.emp_grid.addWidget(self.emp_passwd_txt, 2, 1, Qt.AlignmentFlag.AlignCenter)

        self.cis_grid.addWidget(self.cis_label, 0, 0, 1, 0, Qt.AlignmentFlag.AlignCenter)
        self.cis_grid.addWidget(self.cis_username_label, 1, 0, Qt.AlignmentFlag.AlignCenter)
        self.cis_grid.addWidget(self.cis_passwd_label, 2, 0, Qt.AlignmentFlag.AlignCenter)
        self.cis_grid.addWidget(self.cis_username_txt, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.cis_grid.addWidget(self.cis_passwd_txt, 2, 1, Qt.AlignmentFlag.AlignCenter)

        self.emp_widget.setLayout(self.emp_grid)
        self.cis_widget.setLayout(self.cis_grid)

        self.v_layout.addWidget(self.emp_widget)
        self.v_layout.addWidget(self.cis_widget)
        self.v_layout.addWidget(self.save_btn)
        self.save_btn.clicked.connect(self.on_save_btn_click)

        self.setLayout(self.v_layout)


    def on_save_btn_click(self):
        emp_username = self.emp_username_txt.text()
        emp_passwd = self.emp_passwd_txt.text()
        cis_username = self.cis_username_txt.text()
        cis_passwd = self.cis_passwd_txt.text()

        with open(PathResolver.get_creds_path(), 'w') as file:
            file.write(emp_username + '\n' + emp_passwd + '\n' + cis_username + '\n' + cis_passwd + '\n')

        shared_instance.emp_name = emp_username
        shared_instance.emp_passwd = emp_passwd
        shared_instance.cis_name = cis_username
        shared_instance.cis_passwd = cis_passwd