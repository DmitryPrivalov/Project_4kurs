#!/usr/bin/env python
"""
Добавляет тестовую учётную запись в существующую базу `data.db`.
Запускайте из корня проекта: `python add_test_user.py`
"""
import sqlite3
import os

DB_PATH = 'data.db'
TEST_LOGIN = 'test_auto'
TEST_PASSWORD = 'password123'
TEST_EMAIL = 'test_auto@example.com'
TEST_ROLE = 'user'


def main():
    if not os.path.exists(DB_PATH):
        print(f"❌ База данных '{DB_PATH}' не найдена. Запустите init_db.py сначала.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute('SELECT id FROM users WHERE login = ? OR email = ?', (TEST_LOGIN, TEST_EMAIL))
    if cur.fetchone():
        print(f"ℹ️  Пользователь с логином '{TEST_LOGIN}' или email '{TEST_EMAIL}' уже существует.")
    else:
        cur.execute(
            'INSERT INTO users (login, password, email, role) VALUES (?, ?, ?, ?)',
            (TEST_LOGIN, TEST_PASSWORD, TEST_EMAIL, TEST_ROLE)
        )
        conn.commit()
        print(f"✅ Тестовая учётная запись создана: логин='{TEST_LOGIN}', пароль='{TEST_PASSWORD}'")

    conn.close()


if __name__ == '__main__':
    main()
