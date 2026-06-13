from PyQt6 import uic
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import *
from db import sql
from config import UI

class Orders(QDialog):
    def __init__(self, role):
        super().__init__()
        uic.loadUi(UI / 'orders.ui', self)
        self.role = role
        self.order_id = None
        today = QDate.currentDate()
        self.orderDate.setMinimumDate(today)
        self.deliveryDate.setMinimumDate(today)
        self.orderDate.setDate(today)
        self.deliveryDate.setDate(today.addDays(3))
        admin = role == 'admin'
        self.userBox.setVisible(admin)
        self.label_6.setVisible(admin)
        self.userBox.addItem('Без пользователя', None)
        for u in sql("SELECT u.id, u.full_name FROM users u JOIN role_id r ON r.id = u.role_id WHERE r.name = 'client' ORDER BY u.full_name", get=True):
            self.userBox.addItem(u['full_name'], u['id'])
        self.label_2.setVisible(admin)
        self.statusEdit.setVisible(admin)
        self.label_3.setVisible(admin)
        self.addressEdit.setVisible(admin)
        self.label_4.setVisible(admin)
        self.orderDate.setVisible(admin)
        self.label_5.setVisible(admin)
        self.deliveryDate.setVisible(admin)
        self.addButton.setVisible(admin)
        self.saveButton.setVisible(admin)
        self.deleteButton.setVisible(admin)
        self.table.cellClicked.connect(self.select)
        self.addButton.clicked.connect(self.clear)
        self.saveButton.clicked.connect(self.save)
        self.deleteButton.clicked.connect(self.delete)
        self.closeButton.clicked.connect(self.close)
        self.load()
    def load(self):
        orders = sql('SELECT o.*, u.full_name user_name FROM orders o LEFT JOIN users u ON u.id = o.user_id ORDER BY o.id DESC', get=True)
        self.table.setColumnCount(6)
        self.table.setRowCount(len(orders))
        self.table.setHorizontalHeaderLabels(['ID', 'Пользователь', 'Статус', 'Адрес', 'Дата заказа', 'Дата доставки'])
        if self.role in ('client', 'manager'):
            self.table.hideColumn(0)  # ID
            self.table.hideColumn(3)  # дата заказа
            self.table.hideColumn(4)  # дата доставки
        for row, o in enumerate(orders):
            values = [o['id'], o['user_name'] or 'Без пользователя', o['status'], o['address'], o['order_date'], o['delivery_date']]
            for col, value in enumerate(values):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))
            self.table.item(row, 0).setData(Qt.ItemDataRole.UserRole, o)
        self.table.resizeColumnsToContents()
    def select(self, row, col):
        o = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        self.order_id = o['id']
        self.statusEdit.setText(str(o['status'] or ''))
        self.addressEdit.setText(str(o['address'] or ''))
        self.orderDate.setMinimumDate(QDate.currentDate())
        self.deliveryDate.setMinimumDate(QDate.currentDate())
        if self.deliveryDate.date() < self.orderDate.date():
            QMessageBox.critical(self, 'Ошибка', 'Дата доставки не может быть раньше даты заказа')
            return
        i = self.userBox.findData(o['user_id'])
        if i >= 0:
            self.userBox.setCurrentIndex(i)
        else:
            self.userBox.setCurrentIndex(0)
    def clear(self):
        self.order_id = None
        self.statusEdit.clear()
        self.addressEdit.clear()
        today = QDate.currentDate()
        self.orderDate.setDate(today)
        self.deliveryDate.setDate(today.addDays(3))
        self.userBox.setCurrentIndex(0)
    def save(self):
        if not self.statusEdit.text() or not self.addressEdit.text():
            QMessageBox.critical(self, 'Ошибка', 'Заполните статус и адрес')
            return
        if self.deliveryDate.date() < self.orderDate.date():
            QMessageBox.critical(
                self,
                'Ошибка',
                'Дата доставки не может быть раньше даты заказа'
            )
            return
        data = (self.statusEdit.text(), self.addressEdit.text(), self.orderDate.date().toString('yyyy-MM-dd'), 
                self.deliveryDate.date().toString('yyyy-MM-dd'), self.userBox.currentData())
        if self.order_id:
            sql('''
                UPDATE orders SET status=%s, address=%s, order_date=%s, delivery_date=%s, user_id=%s WHERE id=%s
            ''', data + (self.order_id,))
        else:
            sql('''
                INSERT INTO orders(status, address, order_date, delivery_date, user_id)
                VALUES (%s,%s,%s,%s,%s)
            ''', data)
        self.clear()
        self.load()
    def delete(self):
        if not self.order_id:
            QMessageBox.critical(self, 'Ошибка', 'Выберите заказ')
            return
        if QMessageBox.question(self, 'Удаление', 'Удалить заказ?') == QMessageBox.StandardButton.Yes:
            sql('DELETE FROM orders WHERE id=%s', (self.order_id,))
            self.clear()
            self.load()