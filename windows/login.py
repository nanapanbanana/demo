from PyQt6 import uic
from PyQt6.QtWidgets import *
from db import sql
from config import UI

class Login(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(UI / 'login.ui', self)
        self.loginButton.clicked.connect(self.login)
        self.guestButton.clicked.connect(self.guest)
    def login(self):
        user = sql('''
            SELECT u.*, r.name role
            FROM users u
            JOIN role_id r ON r.id = u.role_id
            WHERE login=%s AND password=%s
        ''', (self.loginEdit.text(), self.passwordEdit.text()), True)
        if not user:
            QMessageBox.critical(self, 'Ошибка', 'Неверный логин или пароль')
            return
        self.open_main(user[0])
    def guest(self):
        self.open_main({'id': None, 'full_name': 'Гость', 'role': 'guest'})
    def open_main(self, user):
        from windows.main_window import Main
        self.w = Main(user)
        self.w.show()
        self.close()
        