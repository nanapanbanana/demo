# PyQt6 + Qt Designer вариант под ДЭ на «4»

Файлы:
- `main.py` — вся логика приложения.
- `ui/login.ui`
- `ui/products.ui`
- `ui/product_form.ui`
- `ui/orders.ui`

Установка:
```bash
pip install PyQt6 pymysql
python main.py
```

Что реализовано:
- авторизация и вход гостем;
- роли: guest, client, manager, admin;
- просмотр товаров;
- поиск, фильтрация по поставщику, сортировка;
- карточки товаров с изображением, ценой, скидкой и остатком;
- CRUD товаров для администратора;
- валидация товара;
- запрет удаления товара, если он есть в `order_items`;
- просмотр заказов для менеджера и администратора;
- CRUD заказов для администратора.

Важно:
- Код рассчитан на таблицы `users`, `role_id`, `products`, `categories`, `manufacturers`, `suppliers`, `orders`, `order_items`.
- Если в твоей БД немного другие имена столбцов, меняются только SQL-запросы в классе `DB`.
- `.ui` файлы можно открыть и редактировать в Qt Designer.


БД:
Импортируй `database.sql` в MySQL/MariaDB. Тестовые логины: admin/admin, manager/manager, client/client.
