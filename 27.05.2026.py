from pathlib import Path 
ROOT = Path(__file__).parent 
UI = ROOT / 'ui'
IMG = ROOT / 'image'
NO_PHOTO = 'picture.png'

import pymysql
DB = dict(host = '127.0.0.1', user = 'root', password = 'root', 
          database = 'shoes', cursorclass = pymysql.cursors.DictCursor)
def sql(q, p = None, get = False):
    con = pymysql.connect(**DB)
    cur = con.cursor()
    cur.execute(q, p)
    res = cur.fetchall() if get else None
    con.commit()
    con.close()
    return res 

import sys
from PyQt6.QtWidgets import * 
from windows.login import Login 
app = QApplication(sys.argv)
w = Login()
w.show()
sys.exit(app.exec())

from PyQt6 import uic 
from PyQt6.QtWidgets import *
from db import sql
from config import UI
class Login(QDialog):
    def __init__(self):
        super()._init__()
        uic.loadUi(UI / 'login.ui', self)
        self.loginButton.clicked.connect(self.login)
        self.guestButton.clicked.connect(self.guest)
    def login(self):
        user = sql('SELECT u.*, r.name role FROM users u JOIN id_role r ON r.id = u.role_id WHERE login = %s AND password = %s', (self.loginEdit.text(), self.passwordEdit.text()), True)
        if not user:
            QMessageBox.warning(self, 'ошибка', 'неверные логин или пароль')
            return 
        self.open_main(user[0])
    def guest(self):
        self.open_main({'id': None, 'full_name': 'гость', 'role': 'guest'})
    def open_main(self, user):
        from windows.main_window import Main 
        self.w = Main(user)
        self.w.show()
        self.close()