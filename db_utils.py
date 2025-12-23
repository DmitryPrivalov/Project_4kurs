"""
Утилиты для управления базой данных
Используется для инициализации и миграций
"""

import sqlite3
import os

def reset_database():
    """Полностью сбросить базу данных"""
    if os.path.exists('data.db'):
        os.remove('data.db')
        print("✓ База данных удалена")

def add_test_user():
    """Добавить тестового пользователя"""
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO users (login, password, email) VALUES (?, ?, ?)',
            ('TestUser123', 'password123', 'test@example.com')
        )
        conn.commit()
        print("✓ Тестовый пользователь добавлен")
        print("  Логин: TestUser123")
        print("  Пароль: password123")
    except sqlite3.IntegrityError:
        print("⚠ Тестовый пользователь уже существует")
    finally:
        conn.close()

def list_users():
    """Вывести всех пользователей"""
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, login, email FROM users')
    users = cursor.fetchall()
    conn.close()
    
    if users:
        print("\nПользователи в базе:")
        for user in users:
            print(f"  ID: {user[0]}, Логин: {user[1]}, Email: {user[2]}")
    else:
        print("Пользователей не найдено")

def list_cars():
    """Вывести все автомобили"""
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, price FROM goods')
    cars = cursor.fetchall()
    conn.close()
    
    if cars:
        print("\nАвтомобили в каталоге:")
        for car in cars:
            print(f"  ID: {car[0]}, Название: {car[1]}, Цена: {car[2]} ₽")
    else:
        print("Автомобили не найдены")

def list_orders():
    """Вывести все заказы"""
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, fio, phone, email, product_id FROM orders')
    orders = cursor.fetchall()
    conn.close()
    
    if orders:
        print("\nЗаказы:")
        for order in orders:
            print(f"  ID: {order[0]}, ФИО: {order[1]}, Телефон: {order[2]}, Email: {order[3]}, Товар ID: {order[4]}")
    else:
        print("Заказов не найдено")

if __name__ == '__main__':
    import sys
    
    print("=" * 50)
    print("Утилита управления базой данных")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'reset':
            reset_database()
        elif command == 'test-user':
            add_test_user()
        elif command == 'users':
            list_users()
        elif command == 'cars':
            list_cars()
        elif command == 'orders':
            list_orders()
        else:
            print(f"Неизвестная команда: {command}")
    
    print("\nДоступные команды:")
    print("  python db_utils.py reset       - Удалить и пересоздать БД")
    print("  python db_utils.py test-user   - Добавить тестового пользователя")
    print("  python db_utils.py users       - Вывести всех пользователей")
    print("  python db_utils.py cars        - Вывести все автомобили")
    print("  python db_utils.py orders      - Вывести все заказы")
