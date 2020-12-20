from PySide2.QtCore import QSize
from PySide2.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QGridLayout, QMessageBox

from logic.credentialManager import CredentialManager


class Login(QDialog):
    def __init__(self, icon, moodle_scrapper, parent=None):
        super(Login, self).__init__(parent)
        self.setWindowTitle("Login")
        self.setMinimumSize(QSize(260, 120))
        self.setWindowIcon(icon)

        self.label_name = QLabel("Username", self)
        self.label_password = QLabel("Password", self)

        self.text_name = QLineEdit(self)
        self.text_pass = QLineEdit(self)
        self.button_login = QPushButton("Login", self)

        self.text_name.setPlaceholderText("Please enter your username")
        self.text_pass.setPlaceholderText("Please enter your password")
        self.text_pass.setEchoMode(QLineEdit.EchoMode.Password)

        self.button_login.clicked.connect(self.handle_login)

        layout = QGridLayout(self)
        layout.addWidget(self.label_name, 0, 0)
        layout.addWidget(self.text_name, 0, 1)
        layout.addWidget(self.label_password, 1, 0)
        layout.addWidget(self.text_pass, 1, 1)
        layout.addWidget(self.button_login, 2, 0, 1, 2)

        self.moodle_scrapper = moodle_scrapper

    def handle_login(self):
        username = self.text_name.text()
        password = self.text_pass.text()
        is_logged = self.moodle_scrapper.login(
            self.text_name.text(), self.text_pass.text()
        )
        CredentialManager.set_moodle_cred(username, password)
        if is_logged:
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Bad user or password")
