"""
Простая утилита для просмотра денормализованной таблицы без зависимостей от pandas
"""

import sqlite3
import os

def view_denormalized_data(limit=20):
    """Показать денормализованные данные в красивом формате"""
    
    if not os.path.exists('data.db'):
        print("❌ База данных data.db не найдена!")
        return
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # Проверяем существует ли таблица
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='denormalized_data'")
    if not cursor.fetchone():
        print("❌ Таблица denormalized_data не найдена!")
        print("   Сначала запустите create_denormalized_table.py")
        conn.close()
        return
    
    print("\n" + "="*130)
    print("📊 ДЕНОРМАЛИЗОВАННЫЕ ДАННЫЕ ДЛЯ ОБУЧЕНИЯ ИИ")
    print("="*130)
    
    # Получаем все данные
    cursor.execute('''
        SELECT 
            order_id, user_login, product_name, order_quantity, 
            total_price, order_status, product_category, 
            product_manufacturer, days_since_order, product_popularity
        FROM denormalized_data
        ORDER BY order_id DESC
        LIMIT ?
    ''', (limit,))
    
    rows = cursor.fetchall()
    
    if not rows:
        print("❌ Нет данных в таблице!")
        conn.close()
        return
    
    # Показываем в табличном формате
    print("\n" + "-"*130)
    print(f"{'#':<3} | {'Заказ':<8} | {'Пользователь':<18} | {'Товар':<28} | {'Кол':<3} | {'Сумма':<12} | {'Статус':<14} | {'Производитель':<15}")
    print("-"*130)
    
    for i, row in enumerate(rows, 1):
        order_id, user, product, qty, total, status, category, mfg, days, pop = row
        user_display = user if user else "Гость"[:13]
        product_short = product[:26] if product else ""
        mfg_short = mfg[:13] if mfg else ""
        print(f"{i:<3} | {str(order_id) if order_id else '-':<8} | {user_display:<18} | {product_short:<28} | {qty:<3} | {total:>10.0f}₽ | {status:<14} | {mfg_short:<15}")
    
    print("-"*130)
    
    # Статистика
    cursor.execute('''
        SELECT 
            COUNT(*) as total_rows,
            COUNT(DISTINCT order_id) as unique_orders,
            COUNT(DISTINCT user_id) as unique_users,
            COUNT(DISTINCT product_id) as unique_products,
            SUM(total_price) as total_revenue,
            AVG(total_price) as avg_order_value,
            AVG(product_popularity) as avg_popularity
        FROM denormalized_data
    ''')
    
    stats = cursor.fetchone()
    
    print("\n📈 ОБЩАЯ СТАТИСТИКА:")
    print("-"*130)
    print(f"  Всего записей в таблице:        {stats[0]:>6}")
    print(f"  Уникальных заказов:              {stats[1]:>6}")
    print(f"  Уникальных пользователей:        {stats[2]:>6}")
    print(f"  Уникальных товаров:              {stats[3]:>6}")
    print(f"  Общая выручка:                   {stats[4]:>10,.0f} ₽")
    print(f"  Средняя стоимость заказа:        {stats[5]:>10,.0f} ₽")
    print(f"  Средняя популярность товара:     {stats[6]:>10.1f} заказов")
    
    # Анализ по статусам
    cursor.execute('''
        SELECT order_status, COUNT(*) as count
        FROM denormalized_data
        WHERE order_status IS NOT NULL
        GROUP BY order_status
        ORDER BY count DESC
    ''')
    
    print("\n📊 РАСПРЕДЕЛЕНИЕ ПО СТАТУСАМ ЗАКАЗОВ:")
    print("-"*130)
    for status, count in cursor.fetchall():
        print(f"  {status:<20} : {count:>6} заказов")
    
    # Анализ по категориям
    cursor.execute('''
        SELECT product_category, COUNT(*) as count, SUM(total_price) as total
        FROM denormalized_data
        WHERE product_category IS NOT NULL
        GROUP BY product_category
        ORDER BY total DESC
    ''')
    
    print("\n🏷️  АНАЛИЗ ПО КАТЕГОРИЯМ ТОВАРОВ:")
    print("-"*130)
    for category, count, total in cursor.fetchall():
        print(f"  {category:<25} : {count:>6} заказов, сумма {total:>12,.0f} ₽")
    
    # Топ товаров по популярности
    cursor.execute('''
        SELECT DISTINCT product_name, product_popularity, COUNT(*) as order_count, SUM(total_price) as revenue
        FROM denormalized_data
        WHERE product_name IS NOT NULL AND product_popularity IS NOT NULL
        GROUP BY product_id
        ORDER BY product_popularity DESC
        LIMIT 5
    ''')
    
    print("\n⭐ ТОП-5 ПОПУЛЯРНЫХ ТОВАРОВ:")
    print("-"*130)
    for product, popularity, orders, revenue in cursor.fetchall():
        product_short = product[:40]
        print(f"  {product_short:<40} : {popularity:>3} заказов, выручка {revenue:>10,.0f} ₽")
    
    # Анализ пользователей
    cursor.execute('''
        SELECT user_login, COUNT(DISTINCT order_id) as orders_count, SUM(total_price) as total_spent
        FROM denormalized_data
        WHERE user_login IS NOT NULL
        GROUP BY user_id
        ORDER BY total_spent DESC
        LIMIT 10
    ''')
    
    print("\n👥 ТОП-10 АКТИВНЫХ ПОКУПАТЕЛЕЙ:")
    print("-"*130)
    results = cursor.fetchall()
    if results:
        for user, orders, spent in results:
            print(f"  {user:<20} : {orders:>3} заказов, потрачено {spent:>10,.0f} ₽")
    
    conn.close()
    print("\n" + "="*130)

def export_to_csv(filename='denormalized_data.csv'):
    """Экспортировать данные в CSV"""
    
    if not os.path.exists('data.db'):
        print("❌ База данных data.db не найдена!")
        return
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM denormalized_data')
        rows = cursor.fetchall()
        
        if not rows:
            print("❌ Нет данных для экспорта!")
            conn.close()
            return
        
        # Получаем заголовки колонок
        columns = [description[0] for description in cursor.description]
        
        # Записываем в CSV
        with open(filename, 'w', encoding='utf-8') as f:
            # Заголовок
            f.write(','.join(columns) + '\n')
            # Данные
            for row in rows:
                # Экранируем кавычки и преобразуем в строку
                row_str = []
                for val in row:
                    if val is None:
                        row_str.append('')
                    elif isinstance(val, str):
                        # Экранируем кавычки
                        val = val.replace('"', '""')
                        row_str.append(f'"{val}"')
                    else:
                        row_str.append(str(val))
                f.write(','.join(row_str) + '\n')
        
        print(f"✅ Данные экспортированы в файл: {filename}")
        print(f"   Строк: {len(rows)}")
        print(f"   Столбцов: {len(columns)}")
    except Exception as e:
        print(f"❌ Ошибка при экспорте: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    import sys
    
    print("\n" + "="*130)
    print("УТИЛИТА ДЛЯ АНАЛИЗА ДЕНОРМАЛИЗОВАННОЙ ТАБЛИЦЫ")
    print("="*130)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'view':
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            view_denormalized_data(limit)
        elif command == 'csv':
            filename = sys.argv[2] if len(sys.argv) > 2 else 'denormalized_data.csv'
            export_to_csv(filename)
        else:
            print(f"❌ Неизвестная команда: {command}")
            print("\nДоступные команды:")
            print("  view [limit]       - Показать данные (по умолчанию 20 строк)")
            print("  csv [filename]     - Экспортировать в CSV")
    else:
        view_denormalized_data(20)
    
    print("="*130 + "\n")
