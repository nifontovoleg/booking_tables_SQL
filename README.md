# Postgres HW — Запуск
Приложение для управления бронированием столов в кафе или ресторане. Пользовательский слой — Tkinter с вкладками для пользователей, столов и броней. Бизнес-логика и SQL-запросы вынесены в backend-модуль. Подключение к БД через psycopg2 и переменные окружения (.env). Класс PostgresDriver генерирует DDL из Python-моделей и выполняет транзакции. Подходит как практика работы с SQL, CRUD и desktop-приложениями на Python.
Короткая инструкция по запуску проекта на Windows.

## Требования

- Python 3.10+ (рекомендуется в виртуальном окружении)
- PostgreSQL доступный локально или удалённо

## Установка

1. Создайте и активируйте виртуальное окружение (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Установите зависимости:

```powershell
pip install -r requirements.txt
```

3. Создайте файл `.env` в корне проекта (пример уже есть) и укажите параметры подключения (не храните секреты в репозитории):

```
DB_NAME=shop_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

## Настройка базы данных (если требуется)

Если база `shop_db` или пользователь `user` ещё не созданы, выполните от имени суперпользователя Postgres:

```bash
# Создать базу (если нужно)
psql -U postgres -c "CREATE DATABASE shop_db;"

# Дать доступ к схеме public пользователю
psql -U postgres -d shop_db -c "GRANT ALL ON SCHEMA public TO \"user\";"

# Или сменить владельца схемы
psql -U postgres -d shop_db -c "ALTER SCHEMA public OWNER TO \"user\";"
```

Замените `postgres`/данные на ваши суперпользовательские учётные данные.

## Запуск

```powershell
# из корня проекта, в активированном venv
python main.py
```

Скрипт создаст таблицы, добавит тестовых пользователей и заказы, затем выведет суммарные суммы по пользователям.

## Что делать при ошибках прав доступа

- Если видите ошибку `psycopg2.errors.InsufficientPrivilege: нет доступа к схеме public`, выполните шаги из раздела "Настройка базы данных" от суперпользователя.
- Если видите `ModuleNotFoundError: No module named 'psycopg2'`, убедитесь, что вы установили зависимости в активированном venv: `pip install -r requirements.txt`.

---

Файлы:
- `main.py` — пример использования `PostgresDriver` (точки входа)
- `postgres_driver.py` — класс `PostgresDriver` с методами `create_tables`, `add_user`, `add_order`, `get_user_totals`
