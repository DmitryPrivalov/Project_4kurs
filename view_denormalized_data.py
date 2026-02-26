"""
Утилита для просмотра и экспорта денормализованной таблицы
"""

import sqlite3
import csv
import json
import os
from datetime import datetime
import pandas as pd

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
    
    print("="*120)
    print("📊 ДЕНОРМАЛИЗОВАННЫЕ ДАННЫЕ ДЛЯ ОБУЧЕНИЯ ИИ")
    print("="*120)
    
    # Получаем все данные
    cursor.execute('''
        SELECT 
            order_id, user_login, product_name, order_quantity, 
            total_price, order_status, product_category, 
            product_manufacturer, days_since_order, product_popularity,
            product_price, product_stock
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
    print("\n" + "-"*120)
    print(f"{'#':<3} | {'Заказ':<8} | {'Пользователь':<15} | {'Товар':<30} | {'Кол-во':<6} | {'Сумма':<12} | {'Статус':<15} | {'Категория':<20}")
    print("-"*120)
    
    for i, row in enumerate(rows, 1):
        order_id, user, product, qty, total, status, category, mfg, days, pop, price, stock = row
        user_display = user if user else "Гость"
        print(f"{i:<3} | {order_id:<8} | {user_display:<15} | {product[:28]:<30} | {qty:<6} | {total:>11.0f}₽ | {status:<15} | {category:<20}")
    
    print("-"*120)
    
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
    
    print("\n📈 СТАТИСТИКА:")
    print("-"*120)
    print(f"  Всего записей: {stats[0]}")
    print(f"  Уникальных заказов: {stats[1]}")
    print(f"  Уникальных пользователей: {stats[2]}")
    print(f"  Уникальных товаров: {stats[3]}")
    print(f"  Общая выручка: {stats[4]:,.0f} ₽")
    print(f"  Средняя стоимость заказа: {stats[5]:,.0f} ₽")
    print(f"  Средняя популярность товара: {stats[6]:.1f} заказов")
    
    conn.close()
    print("="*120)

def export_to_csv(filename='denormalized_data.csv'):
    """Экспортировать данные в CSV"""
    
    if not os.path.exists('data.db'):
        print("❌ База данных data.db не найдена!")
        return
    
    conn = sqlite3.connect('data.db')
    
    try:
        df = pd.read_sql_query('SELECT * FROM denormalized_data', conn)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"✅ Данные экспортированы в файл: {filename}")
        print(f"   Строк: {len(df)}")
        print(f"   Столбцов: {len(df.columns)}")
    except Exception as e:
        print(f"❌ Ошибка при экспорте: {e}")
    finally:
        conn.close()

def export_to_json(filename='denormalized_data.json'):
    """Экспортировать данные в JSON"""
    
    if not os.path.exists('data.db'):
        print("❌ База данных data.db не найдена!")
        return
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM denormalized_data')
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        data = []
        for row in rows:
            data.append(dict(zip(columns, row)))
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ Данные экспортированы в файл: {filename}")
        print(f"   Записей: {len(data)}")
    except Exception as e:
        print(f"❌ Ошибка при экспорте: {e}")
    finally:
        conn.close()

def analyze_by_category():
    """Анализ данных по категориям товаров"""
    
    if not os.path.exists('data.db'):
        print("❌ База данных data.db не найдена!")
        return
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    print("\n📊 АНАЛИЗ ПО КАТЕГОРИЯМ:")
    print("-"*80)
    print(f"{'Категория':<25} | {'Заказов':<8} | {'Сумма на категорию':<20} | {'Среднее значение':<16}")
    print("-"*80)
    
    cursor.execute('''
        SELECT 
            product_category,
            COUNT(*) as count,
            SUM(total_price) as total,
            AVG(total_price) as average
        FROM denormalized_data
        WHERE product_category IS NOT NULL
        GROUP BY product_category
        ORDER BY total DESC
    ''')
    
    for row in cursor.fetchall():
        category, count, total, average = row
        print(f"{category:<25} | {count:<8} | {total:>18.0f}₽ | {average:>15.0f}₽")
    
    conn.close()
    print("-"*80)

def analyze_by_manufacturer():
    """Анализ данных по производителям"""
    
    if not os.path.exists('data.db'):
        print("❌ База данных data.db не найдена!")
        return
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    print("\n🏭 АНАЛИЗ ПО ПРОИЗВОДИТЕЛЯМ:")
    print("-"*80)
    print(f"{'Производитель':<25} | {'Заказов':<8} | {'Сумма':<18} | {'Среднее':<15}")
    print("-"*80)
    
    cursor.execute('''
        SELECT 
            product_manufacturer,
            COUNT(*) as count,
            SUM(total_price) as total,
            AVG(total_price) as average
        FROM denormalized_data
        WHERE product_manufacturer IS NOT NULL
        GROUP BY product_manufacturer
        ORDER BY total DESC
    ''')
    
    for row in cursor.fetchall():
        mfg, count, total, average = row
        print(f"{mfg:<25} | {count:<8} | {total:>16.0f}₽ | {average:>14.0f}₽")
    
    conn.close()
    print("-"*80)

def analyze_user_behavior():
    """Анализ поведения пользователей"""
    
    if not os.path.exists('data.db'):
        print("❌ База данных data.db не найдена!")
        return
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    print("\n👥 АНАЛИЗ ПОВЕДЕНИЯ ПОЛЬЗОВАТЕЛЕЙ:")
    print("-"*80)
    print(f"{'Пользователь':<20} | {'Заказов':<8} | {'Сумма расходов':<16} | {'Среднее на заказ':<16}")
    print("-"*80)
    
    cursor.execute('''
        SELECT 
            COALESCE(user_login, 'Гость'),
            COUNT(DISTINCT order_id) as orders_count,
            SUM(total_price) as total_spent,
            AVG(total_price) as avg_order
        FROM denormalized_data
        GROUP BY user_login
        ORDER BY total_spent DESC
    ''')
    
    for row in cursor.fetchall():
        user, count, total, average = row
        print(f"{user:<20} | {count:<8} | {total:>14.0f}₽ | {average:>15.0f}₽")
    
    conn.close()
    print("-"*80)

if __name__ == '__main__':
    import sys
    
    print("\n" + "="*120)
    print("УТИЛИТА ДЛЯ АНАЛИЗА ДЕНОРМАЛИЗОВАННОЙ ТАБЛИЦЫ")
    print("="*120)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'view':
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
            view_denormalized_data(limit)
        elif command == 'csv':
            filename = sys.argv[2] if len(sys.argv) > 2 else 'denormalized_data.csv'
            export_to_csv(filename)
        elif command == 'json':
            filename = sys.argv[2] if len(sys.argv) > 2 else 'denormalized_data.json'
            export_to_json(filename)
        elif command == 'category':
            analyze_by_category()
        elif command == 'manufacturer':
            analyze_by_manufacturer()
        elif command == 'users':
            analyze_user_behavior()
        elif command == 'all':
            view_denormalized_data(20)
            analyze_by_category()
            analyze_by_manufacturer()
            analyze_user_behavior()
        else:
            print(f"❌ Неизвестная команда: {command}")
            print("\nДоступные команды:")
            print("  view [limit]       - Показать данные (по умолчанию 20 строк)")
            print("  csv [filename]     - Экспортировать в CSV")
            print("  json [filename]    - Экспортировать в JSON")
            print("  category           - Анализ по категориям")
            print("  manufacturer       - Анализ по производителям")
            print("  users              - Анализ поведения пользователей")
            print("  all                - Показать всю информацию")
    else:
        print("\nПримеры использования:")
        print("  python view_denormalized_data.py view")
        print("  python view_denormalized_data.py view 50")
        print("  python view_denormalized_data.py csv")
        print("  python view_denormalized_data.py json")
        print("  python view_denormalized_data.py category")
        print("  python view_denormalized_data.py manufacturer")
        print("  python view_denormalized_data.py users")
        print("  python view_denormalized_data.py all")
        print("\n" + "="*120)
