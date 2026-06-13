import os
import shutil

from PyQt6 import uic
from PyQt6.QtWidgets import *
from db import sql
from config import UI, IMG, NO_PHOTO

class ProductForm(QDialog):
    def __init__(self, parent, product=None):
        super().__init__()
        uic.loadUi(UI / 'product_form.ui', self)
        self.product = product
        self.image = product['image'] if product else NO_PHOTO
        self.fill(self.categoryBox, 'categories')
        self.fill(self.manufacturerBox, 'manufacturers')
        self.fill(self.supplierBox, 'suppliers')
        self.imageButton.clicked.connect(self.choose_image)
        self.saveButton.clicked.connect(self.save)
        self.cancelButton.clicked.connect(self.reject)
        if product:
            self.nameEdit.setText(product['name'])
            self.descriptionEdit.setPlainText(product['description'])
            self.priceSpin.setValue(float(product['price']))
            self.quantitySpin.setValue(product['quantity'])
            self.discountSpin.setValue(product['discount'])
            self.set_value(self.categoryBox, product['category_id'])
            self.set_value(self.manufacturerBox, product['manufacture_id'])
            self.set_value(self.supplierBox, product['supplier_id'])
            self.imageLabel.setText(self.image)
    def fill(self, combo, table):
        for r in sql(f'SELECT id, name FROM {table} ORDER BY name', get=True):
            combo.addItem(r['name'], r['id'])
    def set_value(self, combo, value):
        i = combo.findData(value)
        if i >= 0:
            combo.setCurrentIndex(i)
    def choose_image(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Выберите картинку', '', 'Images (*.png *.jpg *.jpeg)')
        if not file:
            return
        IMG.mkdir(exist_ok=True)
        name = os.path.basename(file)
        shutil.copy(file, IMG / name)
        self.image = name
        self.imageLabel.setText(name)
    def save(self):
        if not self.nameEdit.text():
            QMessageBox.critical(self, 'Ошибка', 'Введите название')
            return
        if self.priceSpin.value() <= 0:
            QMessageBox.critical(self, 'Ошибка', 'Цена должна быть больше 0')
            return
        data = (self.nameEdit.text(), self.categoryBox.currentData(), self.descriptionEdit.toPlainText(),
                self.manufacturerBox.currentData(), self.supplierBox.currentData(), self.priceSpin.value(),
                self.quantitySpin.value(), self.discountSpin.value(), self.image)
        if self.product:
            sql('''
                UPDATE products SET name=%s, category_id=%s, description=%s, manufacture_id=%s,
                supplier_id=%s, price=%s, quantity=%s, discount=%s, image=%s WHERE id=%s
            ''', data + (self.product['id'],))
        else:
            sql('''
                INSERT INTO products(name, category_id, description, manufacture_id, supplier_id, price, quantity, discount, image)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ''', data)
        self.accept()