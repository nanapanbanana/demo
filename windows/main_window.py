import os
from pathlib import Path
from PyQt6 import uic
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt
from db import sql
from config import UI, IMG, NO_PHOTO
from windows.product_form import ProductForm
from windows.orders import Orders

class Main(QMainWindow):
    def __init__(self, user):
        super().__init__()
        uic.loadUi(UI / 'products.ui', self)
        self.user = user
        self.role = user['role']
        self.userLabel.setText(f"{user['full_name']} | {self.role}")
        self.supplierBox.addItem('Все поставщики', 0)
        for s in sql('SELECT id, name FROM suppliers ORDER BY name', get=True):
            self.supplierBox.addItem(s['name'], s['id'])
        self.sortBox.addItem('Без сортировки', '')
        self.sortBox.addItem('Название', 'name')
        self.sortBox.addItem('Цена ↑', 'price_asc')
        self.sortBox.addItem('Цена ↓', 'price_desc')
        self.sortBox.addItem('Остаток ↑', 'qty_asc')
        self.sortBox.addItem('Остаток ↓', 'qty_desc')
        can_search = self.role in ('manager', 'admin')
        self.searchEdit.setEnabled(can_search)
        self.supplierBox.setEnabled(can_search)
        self.sortBox.setEnabled(can_search)
        self.addButton.setVisible(self.role == 'admin')
        self.ordersButton.setVisible(self.role in ('manager', 'admin'))
        self.searchEdit.textChanged.connect(self.load)
        self.supplierBox.currentIndexChanged.connect(self.load)
        self.sortBox.currentIndexChanged.connect(self.load)
        self.addButton.clicked.connect(self.add_product)
        self.ordersButton.clicked.connect(self.open_orders)
        self.exitButton.clicked.connect(self.logout)
        self.load()
    def logout(self):
        from windows.login import Login
        self.login = Login()
        self.login.show()
        self.close()
    def clear(self):
        while self.productsLayout.count():
            item = self.productsLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    def load(self):
        self.clear()
        q = '''
            SELECT p.*, c.name category, m.name manufacturer, s.name supplier
            FROM products p
            JOIN categories c ON c.id = p.category_id
            JOIN manufacturers m ON m.id = p.manufacture_id
            JOIN suppliers s ON s.id = p.supplier_id
        '''
        where = []
        params = []
        search = self.searchEdit.text()
        if search:
            search = '%' + search + '%'
            where.append('''
                (
                    p.name LIKE %s OR p.description LIKE %s
                    OR c.name LIKE %s OR m.name LIKE %s OR s.name LIKE %s
                )
            ''')
            params += [search, search, search, search, search]
        supplier = self.supplierBox.currentData()
        if supplier:
            where.append('p.supplier_id=%s')
            params.append(supplier)
        if where:
            q += ' WHERE ' + ' AND '.join(where)
        sort = self.sortBox.currentData()
        orders = {'name': 'p.name', 'price_asc': 'p.price ASC', 'price_desc': 'p.price DESC',
                  'qty_asc': 'p.quantity ASC', 'qty_desc': 'p.quantity DESC'}
        q += ' ORDER BY ' + orders.get(sort, 'p.id DESC')
        try:
            products = sql(q, params, True)
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', str(e))
            return
        self.countLabel.setText(f'Найдено товаров: {len(products)}')
        for p in products:
            self.productsLayout.addWidget(Card(p, self))
        self.productsLayout.addStretch()
    def add_product(self):
        form = ProductForm(self)
        if form.exec():
            self.load()
    def edit_product(self, product):
        form = ProductForm(self, product)
        if form.exec():
            self.load()
    def delete_product(self, product):
        used = sql('SELECT id FROM order_items WHERE product_id=%s', (product['id'],), True)
        if used:
            QMessageBox.critical(self, 'Ошибка', 'Товар есть в заказе. Удаление запрещено.')
            return
        if QMessageBox.question(self, 'Удаление', 'Удалить товар?') == QMessageBox.StandardButton.Yes:
            sql('DELETE FROM products WHERE id=%s', (product['id'],))
            self.load()
    def open_orders(self):
        w = Orders(self.role)
        w.exec()
class Card(QWidget):
    def __init__(self, p, main):
        super().__init__()
        self.setStyleSheet('QWidget { border: 1px solid #bbb; border-radius: 8px; padding: 5px; }')
        box = QHBoxLayout(self)
        photo = QLabel()
        photo.setFixedSize(120, 90)
        photo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        path = IMG / (p['image'] or NO_PHOTO)
        if not path.exists():
            path = IMG / NO_PHOTO
        pix = QPixmap(str(path))
        if pix.isNull():
            photo.setText('Нет фото')
        else:
            photo.setPixmap(pix.scaled(120, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        box.addWidget(photo)
        text = QVBoxLayout()
        name = QLabel(p['name'])
        name.setFont(QFont('Arial', 12, QFont.Weight.Bold))
        text.addWidget(name)
        text.addWidget(QLabel(f"Категория: {p['category']}"))
        text.addWidget(QLabel(f"Производитель: {p['manufacturer']}"))
        text.addWidget(QLabel(f"Поставщик: {p['supplier']}"))
        text.addWidget(QLabel(f"Описание: {p['description']}"))
        price = float(p['price'])
        discount = int(p['discount'])
        if discount:
            new_price = price * (100 - discount) / 100
            price_text = f'<s>{price:.2f}</s> → <b>{new_price:.2f}</b> ₽, скидка {discount}%'
        else:
            price_text = f'<b>{price:.2f}</b> ₽'
        text.addWidget(QLabel(price_text))
        qty = QLabel(f"Остаток: {p['quantity']}")
        if p['quantity'] == 0:
            qty.setStyleSheet('background:#ffcccc;')
        elif p['quantity'] < 5:
            qty.setStyleSheet('background:#fff0b3;')
        elif discount > 15:
            qty.setStyleSheet('background:#ccffcc;')
        text.addWidget(qty)
        box.addLayout(text, 1)
        buttons = QVBoxLayout()
        if main.role == 'admin':
            edit = QPushButton('Редактировать')
            delete = QPushButton('Удалить')
            edit.clicked.connect(lambda: main.edit_product(p))
            delete.clicked.connect(lambda: main.delete_product(p))
            buttons.addWidget(edit)
            buttons.addWidget(delete)
        buttons.addStretch()
        box.addLayout(buttons)