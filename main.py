import sys
from PyQt6.QtWidgets import QApplication
from windows.login import Login

app = QApplication(sys.argv)
w = Login()
w.show()
sys.exit(app.exec())