"""
ГЛАВНЫЙ СКРИПТ для полной подготовки денормализованной базы данных
Выполняет все шаги за один раз
"""

import os
import subprocess
import sqlite3

def check_db_exists():
    """Проверка наличия БД"""
    return os.path.exists('data.db')

def run_script(script_name, description):
    """Запуск python скрипта"""
    print(f"\n{'='*80}")
    print(f"⏳ {description}...")
    print(f"{'='*80}")
    
    try:
        subprocess.run([f"python", script_name], check=True)
        print(f"✅ {description} завершено!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при выполнении {script_name}: {e}")
        return False

def full_pipeline(users=200, orders=1000, cart=300):
    """Полный цикл подготовки данных"""
    
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  🤖 ПОЛНАЯ АВТОМАТИЧЕСКАЯ ПОДГОТОВКА ДЕНОРМАЛИЗОВАННОЙ БД  ".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)
    
    # Шаг 1: Инициализация БД
    if not check_db_exists():
        print("\n📚 База данных не найдена, создаём новую...")
        if not run_script('init_db.py', 'Инициализация базы данных'):
            return False
    else:
        print("\n✅ База данных уже существует")
    
    # Шаг 2: Генерация реалистичных данных
    print(f"\n📊 Генерируем реалистичные данные:")
    print(f"   - Пользователей: {users}")
    print(f"   - Заказов: {orders}")
    print(f"   - Товаров в корзине: {cart}")
    
    if not run_script(
        f'generate_realistic_data.py {users} {orders} {cart}',
        'Генерация реалистичных тестовых данных'
    ):
        return False
    
    # Шаг 3: Создание базовой денормализованной таблицы
    if not run_script(
        'create_denormalized_table.py',
        'Создание основной денормализованной таблицы'
    ):
        return False
    
    # Шаг 4: Создание ML таблицы
    if not run_script(
        'create_ml_training_table.py',
        'Создание ML-таблицы с готовыми признаками'
    ):
        return False
    
    # Шаг 5: Показываем результаты
    print("\n" + "="*80)
    print("📊 ПОКАЗЫВАЕМ РЕЗУЛЬТАТЫ...")
    print("="*80)
    
    if not run_script(
        'view_simple.py view 10',
        'Просмотр первых 10 записей'
    ):
        return False
    
    # Итоговая статистика
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + "  ✅ ВСЕ ШАГИ ВЫПОЛНЕНЫ УСПЕШНО!  ".center(78) + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)
    
    # Выводим финальную информацию
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    print("\n📈 ИТОГОВАЯ СТАТИСТИКА:")
    print("-"*80)
    
    tables_info = [
        ('users', 'Пользователи'),
        ('goods', 'Товары'),
        ('orders', 'Заказы'),
        ('services', 'Салоны/Услуги'),
        ('cart', 'Корзины'),
        ('denormalized_data', '📌 Денормализованная таблица (основная)'),
        ('ml_training_data', '🤖 ML таблица с признаками'),
    ]
    
    for table_name, description in tables_info:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            count = cursor.fetchone()[0]
            
            # Получаем кол-во столбцов
            cursor.execute(f'PRAGMA table_info({table_name})')
            cols = len(cursor.fetchall())
            
            print(f"  {description:<40} : {count:>6} строк × {cols:>2} столбцов")
        except:
            pass
    
    conn.close()
    
    print("\n💡 СЛЕДУЮЩИЕ ШАГИ:")
    print("-"*80)
    print("  1. Просмотр данных:")
    print("     python view_simple.py view")
    print("     python view_simple.py view 50    # показать 50 строк")
    print("")
    print("  2. Экспорт в CSV:")
    print("     python view_simple.py csv")
    print("")
    print("  3. Обучение моделей ИИ:")
    print("     import pandas as pd")
    print("     df = pd.read_csv('denormalized_data.csv')")
    print("     # Ваш код ML...")
    print("")
    print("  4. Документация:")
    print("     - DENORMALIZED_TABLE_README.md")
    print("     - COMPLETE_ML_GUIDE.md")
    print("")
    print("🎓 Все данные готовы для обучения ИИ моделей!\n")
    
    return True

if __name__ == '__main__':
    import sys
    
    # Параметры по умолчанию или из аргументов
    users = 200
    orders = 1000
    cart = 300
    
    if len(sys.argv) > 1:
        try:
            users = int(sys.argv[1])
            orders = int(sys.argv[2]) if len(sys.argv) > 2 else orders
            cart = int(sys.argv[3]) if len(sys.argv) > 3 else cart
        except ValueError:
            pass
    
    success = full_pipeline(users, orders, cart)
    
    if success:
        print("\n✅ УСПЕШНО! Система полностью подготовлена к работе.")
        print("   Запустите: python view_simple.py view\n")
    else:
        print("\n❌ Произошла ошибка. Проверьте логи выше.\n")
