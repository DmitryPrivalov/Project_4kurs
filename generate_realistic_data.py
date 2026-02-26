"""
Скрипт для генерации большого количества реалистичных данных
для обучения моделей машинного обучения
"""

import sqlite3
import os
import random
from datetime import datetime, timedelta

def generate_test_data(num_users=100, num_orders=500, num_cart_items=200):
    """Генерирует реалистичные тестовые данные"""
    
    if not os.path.exists('data.db'):
        print("❌ База данных data.db не найдена!")
        print("   Сначала запустите init_db.py")
        return
    
    print("="*70)
    print("🔄 Генерация реалистичных тестовых данных")
    print("="*70)
    print(f"\n📊 Будет создано:")
    print(f"   👥 Пользователей: {num_users}")
    print(f"   📦 Заказов: {num_orders}")
    print(f"   🛒 Товаров в корзине: {num_cart_items}")
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # Получаем все товары
    cursor.execute('SELECT id, price FROM goods')
    products = cursor.fetchall()
    
    if not products:
        print("❌ В базе нет товаров!")
        conn.close()
        return
    
    print(f"\n📝 Создание {num_users} пользователей...")
    
    # Генерируем пользователей
    user_logins = []
    for i in range(num_users):
        login = f"user_{i+1:04d}"
        email = f"user{i+1}@autoshop.ru"
        password = "password123"
        
        try:
            cursor.execute(
                'INSERT INTO users (login, password, email, role) VALUES (?, ?, ?, ?)',
                (login, password, email, 'user')
            )
            user_logins.append(login)
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    
    # Получаем все user_id
    cursor.execute('SELECT id FROM users WHERE role = "user"')
    user_ids = [row[0] for row in cursor.fetchall()]
    
    print(f"✅ Пользователей в базе: {len(user_ids)}")
    
    # Статусы заказов
    statuses = ['в разработке', 'в пути', 'выполнен', 'отменен', 'ожидает оплату']
    
    # Типичные комментарии
    comments = [
        'Доставка после 18:00',
        'Срочно нужно',
        'Стандартная доставка',
        'Подгонка размера требуется',
        'Оригинальная деталь',
        'Запасная часть',
        'Для ремонта',
        'Для замены',
        'Дешевле если возможно',
        'Спешу на работу',
        'Подарок для друга',
        'Для коллекции',
        'Запасной вариант',
        'Вторая попытка заказа',
        'По рекомендации'
    ]
    
    print(f"\n📦 Создание {num_orders} заказов...")
    
    # Генерируем заказы
    for i in range(num_orders):
        user_id = random.choice(user_ids) if random.random() > 0.3 else None  # 30% без user_id
        product_id, product_price = random.choice(products)
        quantity = random.randint(1, 5)
        status = random.choice(statuses)
        
        # Случайная дата в последние 365 дней
        days_ago = random.randint(1, 365)
        created_at = datetime.now() - timedelta(days=days_ago)
        
        cursor.execute('''
            INSERT INTO orders (fio, phone, email, comment, product_id, user_id, quantity, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            f'Клиент_{i+1:05d}',
            f'+79{random.randint(100000000, 999999999)}',
            f'client{i+1}@email.ru',
            random.choice(comments),
            product_id,
            user_id,
            quantity,
            status,
            created_at
        ))
        
        if (i + 1) % 50 == 0:
            print(f"   ✓ {i+1}/{num_orders} заказов создано")
    
    conn.commit()
    
    print(f"✅ Заказы созданы")
    
    # Генерируем товары в корзине
    print(f"\n🛒 Создание {num_cart_items} товаров в корзине...")
    
    for i in range(num_cart_items):
        user_id = random.choice(user_ids)
        product_id, _ = random.choice(products)
        quantity = random.randint(1, 3)
        
        # Случайная дата добавления в корзину (недавно)
        days_ago = random.randint(0, 30)
        created_at = datetime.now() - timedelta(days=days_ago)
        
        try:
            cursor.execute('''
                INSERT INTO cart (user_id, product_id, quantity, created_at)
                VALUES (?, ?, ?, ?)
            ''', (user_id, product_id, quantity, created_at))
        except sqlite3.IntegrityError:
            pass
        
        if (i + 1) % 50 == 0:
            print(f"   ✓ {i+1}/{num_cart_items} товаров добавлено")
    
    conn.commit()
    print(f"✅ Товары в корзине добавлены")
    
    # Выводим статистику
    print("\n" + "="*70)
    print("📊 СТАТИСТИКА СОЗДАННЫХ ДАННЫХ:")
    print("-"*70)
    
    cursor.execute('SELECT COUNT(*) FROM users WHERE role = "user"')
    total_users = cursor.fetchone()[0]
    print(f"  👥 Всего пользователей: {total_users}")
    
    cursor.execute('SELECT COUNT(*) FROM goods')
    total_products = cursor.fetchone()[0]
    print(f"  🔧 Товаров в каталоге: {total_products}")
    
    cursor.execute('SELECT COUNT(*) FROM orders')
    total_orders = cursor.fetchone()[0]
    print(f"  📦 Всего заказов: {total_orders}")
    
    cursor.execute('SELECT COUNT(*) FROM cart')
    total_cart = cursor.fetchone()[0]
    print(f"  🛒 Товаров в корзинах: {total_cart}")
    
    cursor.execute('SELECT SUM(CAST(g.price AS REAL) * o.quantity) FROM orders o JOIN goods g ON o.product_id = g.id')
    total_revenue = cursor.fetchone()[0] or 0
    print(f"  💰 Общая сумма заказов: {total_revenue:,.0f} ₽")
    
    cursor.execute('SELECT AVG(CAST(g.price AS REAL) * o.quantity) FROM orders o JOIN goods g ON o.product_id = g.id')
    avg_order = cursor.fetchone()[0] or 0
    print(f"  📈 Средняя стоимость заказа: {avg_order:,.0f} ₽")
    
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM orders')
    unique_buyers = cursor.fetchone()[0]
    print(f"  👤 Уникальных покупателей: {unique_buyers}")
    
    cursor.execute('SELECT AVG(order_count) FROM (SELECT user_id, COUNT(*) as order_count FROM orders GROUP BY user_id)')
    avg_orders_per_user = cursor.fetchone()[0] or 0
    print(f"  📊 Среднее заказов на пользователя: {avg_orders_per_user:.1f}")
    
    conn.close()
    
    print("\n" + "="*70)
    print("✅ Данные успешно созданы!")
    print("="*70)
    print("\n💡 Далее запустите:")
    print("   python create_denormalized_table.py")
    print("="*70)

if __name__ == '__main__':
    import sys
    
    num_users = 100
    num_orders = 500
    num_cart = 200
    
    if len(sys.argv) > 1:
        try:
            num_users = int(sys.argv[1])
            num_orders = int(sys.argv[2]) if len(sys.argv) > 2 else num_orders
            num_cart = int(sys.argv[3]) if len(sys.argv) > 3 else num_cart
        except ValueError:
            print("❌ Неверные аргументы")
            print("Использование: python generate_realistic_data.py [users] [orders] [cart_items]")
            print("По умолчанию: python generate_realistic_data.py 100 500 200")
            sys.exit(1)
    
    generate_test_data(num_users, num_orders, num_cart)
