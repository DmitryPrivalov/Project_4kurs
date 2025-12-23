"""
Скрипт для инициализации базы данных
Автоматически создает таблицы и заполняет тестовыми данными
"""

import sqlite3
import os

def init_database():
    """Создание и инициализация базы данных с тестовыми данными"""
    
    # Удаляем старую базу если она существует
    if os.path.exists('data.db'):
        print("⚠️  Найдена существующая база данных")
        response = input("Удалить и создать новую? (y/n): ")
        if response.lower() != 'y':
            print("❌ Отменено")
            return
        os.remove('data.db')
        print("🗑️  Старая база данных удалена")
    
    print("📦 Создание новой базы данных...")
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # Создание таблицы пользователей
    print("👥 Создание таблицы users...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Создание таблицы товаров (автозапчасти)
    print("🛒 Создание таблицы goods...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS goods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price TEXT NOT NULL,
            image TEXT NOT NULL,
            description TEXT,
            category TEXT,
            compatibility TEXT,
            manufacturer TEXT,
            warranty TEXT,
            stock INTEGER
        )
    ''')
    
    # Создание таблицы заказов
    print("📋 Создание таблицы orders...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fio TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            comment TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            user_id INTEGER,
            quantity INTEGER DEFAULT 1,
            status TEXT DEFAULT 'в разработке',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (product_id) REFERENCES goods (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Создание таблицы услуг/салонов
    print("🏢 Создание таблицы services...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            phone TEXT NOT NULL,
            services TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Создание таблицы корзины
    print("🛒 Создание таблицы cart...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cart (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES goods (id)
        )
    ''')
    
    # Добавление администратора
    print("👤 Добавление администратора...")
    cursor.execute(
        'INSERT INTO users (login, password, email, role) VALUES (?, ?, ?, ?)',
        ('admin', '123', 'admin@avtosalon.ru', 'admin')
    )
    
    # Добавление тестового пользователя
    print("👤 Добавление тестового пользователя...")
    cursor.execute(
        'INSERT INTO users (login, password, email, role) VALUES (?, ?, ?, ?)',
        ('TestUser123', 'testpass123', 'user@test.ru', 'user')
    )
    
    # Добавление автозапчастей
    print("🔧 Добавление автозапчастей...")
    parts_data = [
        ('Двигатель V8 5.0L', '450000', '/static/img/engine.svg', 
         'Мощный бензиновый двигатель V8 с алюминиевым блоком', 
         'Двигатели', 'BMW, Mercedes, Range Rover', 'Bosch', '5 лет', 8),
        
        ('Коробка передач автомат 8-ступ', '180000', '/static/img/transmission.svg', 
         'Надежная автоматическая коробка передач с гидравликой', 
         'Коробки передач', 'BMW X5, Mercedes GLE, Audi Q7', 'ZF', '3 года', 5),
        
        ('Тормозные колодки керамика', '12000', '/static/img/brake_pads.svg', 
         'Керамические тормозные колодки с низким износом', 
         'Тормозная система', 'Все модели', 'Brembo', '2 года', 25),
        
        ('Амортизатор пневматический', '85000', '/static/img/shock_absorber.svg', 
         'Пневматический амортизатор с электроуправлением', 
         'Подвеска', 'Land Rover, BMW X5, Mercedes', 'Continental', '4 года', 12),
        
        ('Аккумулятор 12V 100Ah', '35000', '/static/img/battery.svg', 
         'Высокомощный автомобильный аккумулятор с защитой', 
         'Электрика', 'Все модели', 'Varta', '3 года', 18),
        
        ('Генератор 150А', '65000', '/static/img/generator.svg', 
         'Электрогенератор переменного тока с регулятором', 
         'Электрика', 'BMW, Mercedes, Audi', 'Bosch', '5 лет', 7),
        
        ('Турбокомпрессор', '220000', '/static/img/turbo.svg', 
         'Турбина турбокомпрессора для дизельных двигателей', 
         'Двигатели', 'Mercedes, Audi, VW', 'Garrett', '5 лет', 4),
        
        ('Коллектор выпускной', '42000', '/static/img/exhaust_manifold.svg', 
         'Стальной выпускной коллектор с термозащитой', 
         'Выхлопная система', 'BMW 3,5 Series', 'Borla', '3 года', 10),
        
        ('Масляный фильтр Premium', '3500', '/static/img/oil_filter.svg', 
         'Синтетический масляный фильтр с магнитом', 
         'Расходники', 'Все модели', 'Mobil', '1 год', 50),
        
        ('Воздушный фильтр спортивный', '8500', '/static/img/air_filter.svg', 
         'Спортивный высокопроизводительный воздушный фильтр', 
         'Воздухоснабжение', 'Все модели', 'K&N', '2 года', 30),
        
        ('Свечи зажигания иридиевые', '4200', '/static/img/spark_plugs.svg', 
         'Иридиевые свечи зажигания с расширенным ресурсом', 
         'Зажигание', 'Все модели', 'NGK', '2 года', 45),
        
        ('Датчик кислорода O2', '18000', '/static/img/o2_sensor.svg', 
         'Керамический датчик кислорода для контроля выхлопа', 
         'Электрика', 'Все модели', 'Bosch', '3 года', 15),
    ]
    
    cursor.executemany('''
        INSERT INTO goods (name, price, image, description, category, compatibility, manufacturer, warranty, stock) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', parts_data)
    
    # Добавление тестовых салонов
    print("🏢 Добавление салонов...")
    services_data = [
        ('Автосалон "Центральный"', 'Москва, ул. Ленина, 123', '+7 (495) 123-45-67',
         'Продажа автозапчастей, ремонт, диагностика', 
         'Крупнейший салон в центре Москвы с полным спектром услуг'),
        
        ('Сервис "Автомастер"', 'Москва, Рублевское шоссе, 45', '+7 (495) 987-65-43',
         'Техническое обслуживание, ремонт подвески, замена масла', 
         'Профессиональный сервис с опытными мастерами'),
        
        ('Магазин "Запчасти+"', 'Санкт-Петербург, Невский пр., 200', '+7 (812) 555-12-34',
         'Продажа оригинальных и неоригинальных запчастей', 
         'Широкий ассортимент запчастей для всех марок'),
    ]
    
    cursor.executemany('''
        INSERT INTO services (name, address, phone, services, description) 
        VALUES (?, ?, ?, ?, ?)
    ''', services_data)
    
    # Добавление тестовых заказов
    print("📦 Добавление тестовых заказов...")
    cursor.execute('''
        INSERT INTO orders (fio, phone, email, comment, product_id, user_id, quantity, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('Иван Иванов', '+79991234567', 'ivan@test.ru', 'Доставка после 18:00', 1, 2, 1, 'в разработке'))
    
    cursor.execute('''
        INSERT INTO orders (fio, phone, email, comment, product_id, user_id, quantity, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ('Петр Петров', '+79997654321', 'petr@test.ru', 'Срочно', 3, 2, 2, 'выполнен'))
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*50)
    print("✅ База данных успешно создана и заполнена!")
    print("="*50)
    print("\n📊 Статистика:")
    print(f"   👥 Пользователи: 2 (admin, TestUser123)")
    print(f"   🔧 Автозапчасти: {len(parts_data)}")
    print(f"   🏢 Салоны: {len(services_data)}")
    print(f"   📦 Тестовые заказы: 2")
    print("\n🔑 Учетные данные:")
    print("   Администратор:")
    print("      Логин: admin")
    print("      Пароль: 123")
    print("   Пользователь:")
    print("      Логин: TestUser123")
    print("      Пароль: testpass123")
    print("\n🚀 Запустите приложение: python app.py")
    print("   или дважды кликните на run.bat")
    print("="*50)

if __name__ == '__main__':
    init_database()
