from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_from_directory
import sqlite3
import os
import re
import shutil
from datetime import datetime
from functools import wraps
from flasgger import Swagger

# Create app
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

# Initialize Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs/"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "API магазина автозапчастей",
        "description": "REST API для управления магазином автозапчастей с системой заказов и админ-панелью",
        "version": "1.0.0",
        "contact": {
            "email": "info@avtozapchasti.ru"
        }
    },
    "basePath": "/",
    "schemes": ["http"],
    "securityDefinitions": {
        "SessionAuth": {
            "type": "apiKey",
            "name": "session",
            "in": "cookie"
        }
    }
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Setup static files on first run
def setup_static_files():
    """Copy static files to static folder if they don't exist"""
    static_dir = 'static'
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    
    # Copy CSS files
    if os.path.exists('css') and not os.path.exists(os.path.join(static_dir, 'css')):
        shutil.copytree('css', os.path.join(static_dir, 'css'))
    
    # Copy img folder
    if os.path.exists('img') and not os.path.exists(os.path.join(static_dir, 'img')):
        shutil.copytree('img', os.path.join(static_dir, 'img'))
    
    # Copy carsell24x7-main
    if os.path.exists('carsell24x7-main') and not os.path.exists(os.path.join(static_dir, 'carsell24x7-main')):
        shutil.copytree('carsell24x7-main', os.path.join(static_dir, 'carsell24x7-main'))
    
    # Copy HappyNewYearFinish-main
    if os.path.exists('HappyNewYearFinish-main') and not os.path.exists(os.path.join(static_dir, 'HappyNewYearFinish-main')):
        shutil.copytree('HappyNewYearFinish-main', os.path.join(static_dir, 'HappyNewYearFinish-main'))

# Database initialization
def init_db():
    """Initialize database with tables"""
    if not os.path.exists('data.db'):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        
        # Create users table
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
        
        # Create goods table (for car parts)
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
        
        # Create orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fio TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT NOT NULL,
                comment TEXT NOT NULL,
                product_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create services table
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
        
        # Create cart table
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
        
        # Insert car parts data with local images
        parts_data = [
            ('Двигатель V8 5.0L', '450000', '/static/img/engine.svg', 'Мощный бензиновый двигатель V8 с алюминиевым блоком', 'Двигатели', 'BMW, Mercedes, Range Rover', 'Bosch', '5 лет', 8),
            ('Коробка передач автомат 8-ступ', '180000', '/static/img/transmission.svg', 'Надежная автоматическая коробка передач с гидравликой', 'Коробки передач', 'BMW X5, Mercedes GLE, Audi Q7', 'ZF', '3 года', 5),
            ('Тормозные колодки керамика', '12000', '/static/img/brake_pads.svg', 'Керамические тормозные колодки с низким износом', 'Тормозная система', 'Все модели', 'Brembo', '2 года', 25),
            ('Амортизатор пневматический', '85000', '/static/img/shock_absorber.svg', 'Пневматический амортизатор с электроуправлением', 'Подвеска', 'Land Rover, BMW X5, Mercedes', 'Continental', '4 года', 12),
            ('Аккумулятор 12V 100Ah', '35000', '/static/img/battery.svg', 'Высокомощный автомобильный аккумулятор с защитой', 'Электрика', 'Все модели', 'Varta', '3 года', 18),
            ('Генератор 150А', '65000', '/static/img/generator.svg', 'Электрогенератор переменного тока с регулятором', 'Электрика', 'BMW, Mercedes, Audi', 'Bosch', '5 лет', 7),
            ('Турбокомпрессор', '220000', '/static/img/turbo.svg', 'Турбина турбокомпрессора для дизельных двигателей', 'Двигатели', 'Mercedes, Audi, VW', 'Garrett', '5 лет', 4),
            ('Коллектор выпускной', '42000', '/static/img/exhaust_manifold.svg', 'Стальной выпускной коллектор с термозащитой', 'Выхлопная система', 'BMW 3,5 Series', 'Borla', '3 года', 10),
            ('Масляный фильтр Premium', '3500', '/static/img/oil_filter.svg', 'Синтетический масляный фильтр с магнитом', 'Расходники', 'Все модели', 'Mobil', '1 год', 50),
            ('Воздушный фильтр спортивный', '8500', '/static/img/air_filter.svg', 'Спортивный высокопроизводительный воздушный фильтр', 'Воздухоснабжение', 'Все модели', 'K&N', '2 года', 30),
            ('Свечи зажигания иридиевые', '4200', '/static/img/spark_plugs.svg', 'Иридиевые свечи зажигания с расширенным ресурсом', 'Зажигание', 'Все модели', 'NGK', '2 года', 45),
            ('Датчик кислорода O2', '18000', '/static/img/o2_sensor.svg', 'Керамический датчик кислорода для контроля выхлопа', 'Электрика', 'Все модели', 'Bosch', '3 года', 15),
        ]

        cursor.executemany('INSERT INTO goods (name, price, image, description, category, compatibility, manufacturer, warranty, stock) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', parts_data)
        
        # Add admin user
        try:
            cursor.execute(
                'INSERT INTO users (login, password, email, role) VALUES (?, ?, ?, ?)',
                ('admin', '123', 'admin@avtosalon.ru', 'admin')
            )
        except sqlite3.IntegrityError:
            pass
        
        conn.commit()
        conn.close()
    else:
        # Ensure admin exists
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE login = ?', ('admin',))
        if not cursor.fetchone():
            try:
                cursor.execute(
                    'INSERT INTO users (login, password, email, role) VALUES (?, ?, ?, ?)',
                    ('admin', '123', 'admin@avtosalon.ru', 'admin')
                )
                conn.commit()
            except sqlite3.IntegrityError:
                pass
        conn.close()

# Helper functions
def get_db():
    """Get database connection"""
    conn = sqlite3.connect('data.db')
    conn.row_factory = sqlite3.Row
    return conn

def validate_login(login):
    """Validate login format"""
    if not login or len(login) < 7 or len(login) > 26:
        return False, "Логин должен быть от 7 до 26 символов"
    
    if not re.search(r'[A-Z]', login):
        return False, "Логин должен содержать хотя бы одну заглавную букву"
    
    if not re.search(r'^[a-zA-Z0-9]+$', login):
        return False, "Логин должен содержать только английские буквы и цифры"
    
    if re.search(r'[a-яА-Я]', login):
        return False, "Логин не должен содержать русских букв"
    
    if not re.search(r'[a-zA-Z]', login):
        return False, "Логин не может состоять только из цифр"
    
    return True, ""

def validate_password(password, sec_password):
    """Validate password"""
    if len(password) < 8:
        return False, "Пароль должен быть не менее 8 символов"
    
    if password != sec_password:
        return False, "Пароли не совпадают"
    
    # Check for repeating characters (more than 4)
    for char in set(password):
        if password.count(char) > 4:
            return False, "Пароль содержит слишком много одинаковых символов"
    
    return True, ""

def login_required(f):
    """Decorator to check if user is logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    """Main page"""
    user_id = session.get('user_id')
    is_admin = session.get('role') == 'admin'
    return render_template('index.html', logged_in=user_id is not None, is_admin=is_admin)

@app.route('/showrooms')
def showrooms():
    """Showrooms page"""
    return render_template('showrooms.html')

@app.route('/catalog')
def catalog():
    """Catalog page with parts"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM goods')
    products = cursor.fetchall()
    conn.close()
    return render_template('catalog.html', goods=products)

@app.route('/api/products')
def api_products():
    """
    Получить все товары
    ---
    tags:
      - Products
    responses:
      200:
        description: Список всех товаров
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: ID товара
              name:
                type: string
                description: Название товара
              price:
                type: string
                description: Цена
              image:
                type: string
                description: URL изображения
              description:
                type: string
                description: Описание
              category:
                type: string
                description: Категория
              manufacturer:
                type: string
                description: Производитель
              stock:
                type: integer
                description: Остаток на складе
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM goods')
    products = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(products)

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """Login page"""
    if request.method == 'POST':
        login = request.form.get('login', '').strip()
        password = request.form.get('password', '').strip()
        
        if not login or not password:
            return render_template('login.html', error='Заполните все поля')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE login = ? AND password = ?', (login, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['login'] = user['login']
            session['role'] = user['role']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Неправильный логин или пароль')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registration page"""
    if request.method == 'POST':
        login = request.form.get('login', '').strip()
        password = request.form.get('password', '').strip()
        sec_password = request.form.get('sec_password', '').strip()
        email = request.form.get('email', '').strip()
        
        # Validate all fields
        if not login or not password or not sec_password or not email:
            return render_template('register.html', error='Заполните все поля')
        
        # Validate login
        valid, msg = validate_login(login)
        if not valid:
            return render_template('register.html', error=msg)
        
        # Validate password
        valid, msg = validate_password(password, sec_password)
        if not valid:
            return render_template('register.html', error=msg)
        
        # Check if login exists
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE login = ?', (login,))
        if cursor.fetchone():
            conn.close()
            return render_template('register.html', error='Этот логин уже занят')
        
        # Check if email exists
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return render_template('register.html', error='Этот email уже зарегистрирован')
        
        # Register user
        try:
            cursor.execute(
                'INSERT INTO users (login, password, email, role) VALUES (?, ?, ?, ?)',
                (login, password, email, 'user')
            )
            conn.commit()
            conn.close()
            return render_template('register.html', success='Регистрация успешна! Вы можете войти.')
        except sqlite3.Error:
            conn.close()
            return render_template('register.html', error='Ошибка регистрации')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """
    Авторизация пользователя
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - login
            - password
          properties:
            login:
              type: string
              description: Логин пользователя
              example: "admin"
            password:
              type: string
              description: Пароль пользователя
              example: "admin"
    responses:
      200:
        description: Успешная авторизация
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Авторизация успешна"
            user:
              type: object
              properties:
                id:
                  type: integer
                login:
                  type: string
                role:
                  type: string
      401:
        description: Неверные учетные данные
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: false
            message:
              type: string
              example: "Неправильный логин или пароль"
      400:
        description: Отсутствуют обязательные поля
    """
    data = request.get_json()
    login = data.get('login', '').strip()
    password = data.get('password', '').strip()
    
    if not login or not password:
        return jsonify({'success': False, 'message': 'Заполните все поля'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, login, role FROM users WHERE login = ? AND password = ?', (login, password))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        session['user_id'] = user['id']
        session['login'] = user['login']
        session['role'] = user['role']
        return jsonify({
            'success': True,
            'message': 'Авторизация успешна',
            'user': {
                'id': user['id'],
                'login': user['login'],
                'role': user['role']
            }
        })
    else:
        return jsonify({'success': False, 'message': 'Неправильный логин или пароль'}), 401

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    """
    Регистрация нового пользователя
    ---
    tags:
      - Authentication
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - login
            - password
            - email
          properties:
            login:
              type: string
              description: Логин (3-20 символов, только буквы и цифры)
              example: "newuser"
            password:
              type: string
              description: Пароль (минимум 6 символов)
              example: "password123"
            email:
              type: string
              description: Email адрес
              example: "user@example.com"
    responses:
      201:
        description: Успешная регистрация
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Регистрация успешна"
            user:
              type: object
              properties:
                id:
                  type: integer
                login:
                  type: string
      400:
        description: Ошибка валидации данных
      409:
        description: Пользователь уже существует
    """
    data = request.get_json()
    login = data.get('login', '').strip()
    password = data.get('password', '').strip()
    email = data.get('email', '').strip()
    
    if not login or not password or not email:
        return jsonify({'success': False, 'message': 'Заполните все поля'}), 400
    
    # Validate login
    valid, msg = validate_login(login)
    if not valid:
        return jsonify({'success': False, 'message': msg}), 400
    
    # Validate password length
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Пароль должен быть не менее 6 символов'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if login exists
    cursor.execute('SELECT id FROM users WHERE login = ?', (login,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'Этот логин уже занят'}), 409
    
    # Check if email exists
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'Этот email уже зарегистрирован'}), 409
    
    # Register user
    try:
        cursor.execute(
            'INSERT INTO users (login, password, email) VALUES (?, ?, ?)',
            (login, password, email)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        
        # Auto-login after registration
        session['user_id'] = user_id
        session['login'] = login
        session['role'] = 'user'
        
        return jsonify({
            'success': True,
            'message': 'Регистрация успешна',
            'user': {
                'id': user_id,
                'login': login
            }
        }), 201
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    """
    Выход из системы
    ---
    tags:
      - Authentication
    security:
      - SessionAuth: []
    responses:
      200:
        description: Успешный выход
        schema:
          type: object
          properties:
            success:
              type: boolean
              example: true
            message:
              type: string
              example: "Выход выполнен успешно"
    """
    session.clear()
    return jsonify({'success': True, 'message': 'Выход выполнен успешно'})

@app.route('/api/auth/status', methods=['GET'])
def api_auth_status():
    """
    Проверить статус авторизации
    ---
    tags:
      - Authentication
    responses:
      200:
        description: Статус авторизации
        schema:
          type: object
          properties:
            authenticated:
              type: boolean
              example: true
            user:
              type: object
              properties:
                id:
                  type: integer
                login:
                  type: string
                role:
                  type: string
    """
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': session.get('user_id'),
                'login': session.get('login'),
                'role': session.get('role')
            }
        })
    else:
        return jsonify({'authenticated': False})

@app.route('/api/order', methods=['POST'])
def create_order():
    """
    Создать заказ
    ---
    tags:
      - Orders
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - product_id
            - name
            - email
            - phone
          properties:
            product_id:
              type: integer
              description: ID товара
              example: 1
            name:
              type: string
              description: ФИО заказчика
              example: "Иван Иванов"
            email:
              type: string
              description: Email
              example: "ivan@example.com"
            phone:
              type: string
              description: Телефон
              example: "+79991234567"
            comment:
              type: string
              description: Комментарий
              example: "Доставка после 18:00"
    responses:
      200:
        description: Заказ успешно создан
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
      400:
        description: Неверные данные
      500:
        description: Ошибка сервера
    """
    data = request.get_json()
    
    # Support both 'name' and 'fio' field names
    name = data.get('name') or data.get('fio')
    
    if not all(k in data for k in ['product_id', 'email', 'phone']) or not name:
        return jsonify({'success': False, 'message': 'Missing fields'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO orders (fio, phone, email, comment, product_id) VALUES (?, ?, ?, ?, ?)',
            (name, data.get('phone'), data.get('email'), data.get('comment', ''), data.get('product_id'))
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Заказ создан успешно'})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/users')
def admin_users():
    """Admin panel - view users"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('index'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, login, email, role, created_at FROM users ORDER BY created_at DESC')
    users = cursor.fetchall()
    conn.close()
    
    return render_template('admin_users.html', users=users)

@app.route('/api/admin/delete-user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """Delete user (admin only)"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Нет прав доступа'}), 403
    
    # Prevent deleting admin
    if user_id == 1:  # Assuming admin is always id=1
        return jsonify({'success': False, 'message': 'Нельзя удалить админа'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Пользователь удален'})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/products')
def admin_products():
    """Admin panel - manage products"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('index'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM goods ORDER BY id DESC')
    products = cursor.fetchall()
    conn.close()
    
    return render_template('admin_products.html', products=products)

@app.route('/api/admin/add-product', methods=['POST'])
def add_product():
    """
    Добавить новый товар (только админ)
    ---
    tags:
      - Admin - Products
    security:
      - SessionAuth: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - price
            - image
            - description
            - category
            - manufacturer
            - stock
          properties:
            name:
              type: string
              example: "Двигатель V8 5.0L"
            price:
              type: string
              example: "450000"
            image:
              type: string
              example: "/static/img/engine.svg"
            description:
              type: string
              example: "Мощный бензиновый двигатель"
            category:
              type: string
              example: "Двигатели"
            compatibility:
              type: string
              example: "BMW, Mercedes, Audi"
            manufacturer:
              type: string
              example: "Bosch"
            warranty:
              type: string
              example: "5 лет"
            stock:
              type: integer
              example: 10
    responses:
      200:
        description: Товар успешно добавлен
      403:
        description: Нет прав доступа
      500:
        description: Ошибка сервера
    """
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Нет прав доступа'}), 403
    
    data = request.get_json()
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO goods (name, price, image, description, category, compatibility, manufacturer, warranty, stock)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data['price'],
            data['image'],
            data['description'],
            data['category'],
            data['compatibility'],
            data['manufacturer'],
            data['warranty'],
            data['stock']
        ))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Товар добавлен'})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/delete-product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    """
    Удалить товар (только админ)
    ---
    tags:
      - Admin - Products
    security:
      - SessionAuth: []
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        description: ID товара
    responses:
      200:
        description: Товар удален
      403:
        description: Нет прав доступа
      500:
        description: Ошибка сервера
    """
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Нет прав доступа'}), 403
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM goods WHERE id = ?', (product_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Товар удален'})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/services')
def admin_services():
    """Admin panel - manage services"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('index'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM services ORDER BY id DESC')
    services = cursor.fetchall()
    conn.close()
    
    return render_template('admin_services.html', services=services)

@app.route('/admin/orders')
def admin_orders():
    """Admin panel - manage orders"""
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('index'))
    
    return render_template('admin_orders.html')

@app.route('/api/admin/orders', methods=['GET'])
def get_admin_orders():
    """
    Получить все заказы для админа
    ---
    tags:
      - Admin
    security:
      - SessionAuth: []
    responses:
      200:
        description: Список заказов
      401:
        description: Не авторизован
    """
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Нет доступа'}), 401
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT o.*, g.name as product_name
        FROM orders o
        LEFT JOIN goods g ON o.product_id = g.id
        ORDER BY o.created_at DESC
    ''')
    
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'success': True, 'orders': orders})

@app.route('/api/admin/orders/<int:order_id>/status', methods=['POST'])
def update_order_status(order_id):
    """
    Обновить статус заказа
    ---
    tags:
      - Admin
    security:
      - SessionAuth: []
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: ID заказа
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - status
          properties:
            status:
              type: string
              description: Новый статус
              enum: ["в разработке", "в пути", "выдан", "отменен"]
              example: "в пути"
    responses:
      200:
        description: Статус обновлен
      401:
        description: Не авторизован
    """
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Нет доступа'}), 401
    
    data = request.get_json()
    status = data.get('status')
    
    valid_statuses = ['в разработке', 'в пути', 'выдан', 'отменен']
    if status not in valid_statuses:
        return jsonify({'success': False, 'message': 'Неверный статус'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Статус обновлен'})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/add-service', methods=['POST'])
def add_service():
    """
    Добавить новый автосервис (только админ)
    ---
    tags:
      - Admin - Services
    security:
      - SessionAuth: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - address
            - phone
            - services
          properties:
            name:
              type: string
              example: "Автосервис Профи"
            address:
              type: string
              example: "ул. Ленина, 100"
            phone:
              type: string
              example: "+7-999-123-45-67"
            services:
              type: string
              example: "Ремонт, Диагностика, ТО"
            description:
              type: string
              example: "Профессиональный ремонт автомобилей"
    responses:
      200:
        description: Автосервис добавлен
      403:
        description: Нет прав доступа
    """
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Нет прав доступа'}), 403
    
    data = request.get_json()
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO services (name, address, phone, services, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['name'], data['address'], data['phone'], data['services'], data.get('description', '')))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Автосервис добавлен'})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/update-service/<int:service_id>', methods=['POST'])
def update_service(service_id):
    """
    Обновить автосервис (только админ)
    ---
    tags:
      - Admin - Services
    security:
      - SessionAuth: []
    parameters:
      - name: service_id
        in: path
        type: integer
        required: true
        description: ID автосервиса
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            address:
              type: string
            phone:
              type: string
            services:
              type: string
            description:
              type: string
    responses:
      200:
        description: Автосервис обновлен
      403:
        description: Нет прав доступа
    """
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Нет прав доступа'}), 403
    
    data = request.get_json()
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE services 
            SET name = ?, address = ?, phone = ?, services = ?, description = ?
            WHERE id = ?
        ''', (data['name'], data['address'], data['phone'], data['services'], data.get('description', ''), service_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Автосервис обновлен'})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/delete-service/<int:service_id>', methods=['POST'])
def delete_service(service_id):
    """
    Удалить автосервис (только админ)
    ---
    tags:
      - Admin - Services
    security:
      - SessionAuth: []
    parameters:
      - name: service_id
        in: path
        type: integer
        required: true
        description: ID автосервиса
    responses:
      200:
        description: Автосервис удален
      403:
        description: Нет прав доступа
    """
    if 'user_id' not in session or session.get('role') != 'admin':
        return jsonify({'success': False, 'message': 'Нет прав доступа'}), 403
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM services WHERE id = ?', (service_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Автосервис удален'})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/contact', methods=['POST'])
def send_contact():
    """
    Отправить сообщение через форму контактов
    ---
    tags:
      - Contact
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - surname
            - email
            - phone
            - message
          properties:
            name:
              type: string
              example: "Иван"
            surname:
              type: string
              example: "Иванов"
            email:
              type: string
              example: "ivan@example.com"
            phone:
              type: string
              example: "+79991234567"
            message:
              type: string
              example: "Хочу узнать о ваших услугах"
    responses:
      200:
        description: Сообщение отправлено
      400:
        description: Неверные данные
    """
    data = request.get_json()
    
    if not all(k in data for k in ['name', 'surname', 'email', 'phone', 'message']):
        return jsonify({'success': False, 'message': 'Missing fields'}), 400
    
    # Here you can save to database or send email
    # For now, just return success
    return jsonify({'success': True, 'message': 'Спасибо! Мы скоро с вами свяжемся'})

@app.route('/cabinet')
def cabinet():
    """Personal cabinet page"""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, login, email, role, created_at FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        session.clear()
        return redirect(url_for('login_page'))
    
    return render_template('cabinet.html', user=user)

@app.route('/api/user/orders', methods=['GET'])
def get_user_orders():
    """
    Получить заказы текущего пользователя
    ---
    tags:
      - User
    security:
      - SessionAuth: []
    responses:
      200:
        description: Список заказов пользователя
      401:
        description: Не авторизован
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Необходима авторизация'}), 401
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT o.*, g.name as product_name
        FROM orders o
        LEFT JOIN goods g ON o.product_id = g.id
        WHERE o.user_id = ?
        ORDER BY o.created_at DESC
    ''', (session['user_id'],))
    
    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({'success': True, 'orders': orders})

@app.route('/api/update-profile', methods=['POST'])
def update_profile():
    """
    Обновить профиль пользователя
    ---
    tags:
      - User Profile
    security:
      - SessionAuth: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - email
          properties:
            email:
              type: string
              description: Новый email
              example: "newemail@example.com"
            password:
              type: string
              description: Новый пароль (опционально)
              example: "newpassword123"
    responses:
      200:
        description: Профиль успешно обновлен
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
      400:
        description: Неверные данные
      401:
        description: Не авторизован
      500:
        description: Ошибка сервера
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Не авторизован'}), 401
    
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password')
    
    if not email:
        return jsonify({'success': False, 'message': 'Email обязателен'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if email is already taken by another user
    cursor.execute('SELECT id FROM users WHERE email = ? AND id != ?', (email, session['user_id']))
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'Этот email уже используется'}), 400
    
    try:
        # Update email and password (if provided)
        if password:
            cursor.execute('UPDATE users SET email = ?, password = ? WHERE id = ?', 
                         (email, password, session['user_id']))
        else:
            cursor.execute('UPDATE users SET email = ? WHERE id = ?', 
                         (email, session['user_id']))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Профиль обновлен'})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    """
    Добавить товар в корзину
    ---
    tags:
      - Cart
    security:
      - SessionAuth: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - product_id
          properties:
            product_id:
              type: integer
              description: ID товара
              example: 1
            quantity:
              type: integer
              description: Количество
              example: 1
    responses:
      200:
        description: Товар добавлен в корзину
      401:
        description: Не авторизован
      500:
        description: Ошибка сервера
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Необходима авторизация'}), 401
    
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)
    
    if not product_id:
        return jsonify({'success': False, 'message': 'Не указан товар'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Check if product exists and get stock
        cursor.execute('SELECT id, stock, name FROM goods WHERE id = ?', (product_id,))
        product = cursor.fetchone()
        if not product:
            conn.close()
            return jsonify({'success': False, 'message': 'Товар не найден'}), 404
        
        # Check if already in cart
        cursor.execute('SELECT id, quantity FROM cart WHERE user_id = ? AND product_id = ?', 
                      (session['user_id'], product_id))
        existing = cursor.fetchone()
        
        if existing:
            # Update quantity
            new_quantity = existing['quantity'] + quantity
            # Check stock availability
            if new_quantity > product['stock']:
                conn.close()
                return jsonify({
                    'success': False, 
                    'message': f'Недостаточно товара на складе. Доступно: {product["stock"]} шт.'
                }), 400
            cursor.execute('UPDATE cart SET quantity = ? WHERE id = ?', (new_quantity, existing['id']))
        else:
            # Check stock availability for new item
            if quantity > product['stock']:
                conn.close()
                return jsonify({
                    'success': False, 
                    'message': f'Недостаточно товара на складе. Доступно: {product["stock"]} шт.'
                }), 400
            # Add new item
            cursor.execute('INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, ?)',
                         (session['user_id'], product_id, quantity))
        
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Товар добавлен в корзину'})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/cart', methods=['GET'])
def get_cart():
    """
    Получить корзину пользователя
    ---
    tags:
      - Cart
    security:
      - SessionAuth: []
    responses:
      200:
        description: Содержимое корзины
        schema:
          type: object
          properties:
            items:
              type: array
              items:
                type: object
                properties:
                  cart_id:
                    type: integer
                  product_id:
                    type: integer
                  name:
                    type: string
                  price:
                    type: string
                  image:
                    type: string
                  quantity:
                    type: integer
            total:
              type: number
              description: Общая сумма
      401:
        description: Не авторизован
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Необходима авторизация'}), 401
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT c.id as cart_id, c.quantity, g.id as product_id, g.name, g.price, g.image, g.stock
        FROM cart c
        JOIN goods g ON c.product_id = g.id
        WHERE c.user_id = ?
    ''', (session['user_id'],))
    
    items = []
    total = 0
    
    for row in cursor.fetchall():
        item = dict(row)
        item_total = float(item['price']) * item['quantity']
        total += item_total
        items.append(item)
    
    conn.close()
    
    return jsonify({
        'success': True,
        'items': items,
        'total': total
    })

@app.route('/api/cart/update/<int:cart_id>', methods=['POST'])
def update_cart_quantity(cart_id):
    """
    Обновить количество товара в корзине
    ---
    tags:
      - Cart
    security:
      - SessionAuth: []
    parameters:
      - name: cart_id
        in: path
        type: integer
        required: true
        description: ID записи в корзине
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - quantity
          properties:
            quantity:
              type: integer
              description: Новое количество
              example: 2
    responses:
      200:
        description: Количество обновлено
      400:
        description: Недостаточно товара
      401:
        description: Не авторизован
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Необходима авторизация'}), 401
    
    data = request.get_json()
    quantity = data.get('quantity', 1)
    
    if quantity < 1:
        return jsonify({'success': False, 'message': 'Количество должно быть больше 0'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Get cart item and product
        cursor.execute('''
            SELECT c.id, c.product_id, g.stock, g.name 
            FROM cart c
            JOIN goods g ON c.product_id = g.id
            WHERE c.id = ? AND c.user_id = ?
        ''', (cart_id, session['user_id']))
        
        cart_item = cursor.fetchone()
        if not cart_item:
            conn.close()
            return jsonify({'success': False, 'message': 'Товар не найден в корзине'}), 404
        
        # Check stock availability
        if quantity > cart_item['stock']:
            conn.close()
            return jsonify({
                'success': False,
                'message': f'Недостаточно товара на складе. Доступно: {cart_item["stock"]} шт.'
            }), 400
        
        # Update quantity
        cursor.execute('UPDATE cart SET quantity = ? WHERE id = ?', (quantity, cart_id))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Количество обновлено'})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/cart/remove/<int:cart_id>', methods=['POST'])
def remove_from_cart(cart_id):
    """
    Удалить товар из корзины
    ---
    tags:
      - Cart
    security:
      - SessionAuth: []
    parameters:
      - name: cart_id
        in: path
        type: integer
        required: true
        description: ID записи в корзине
    responses:
      200:
        description: Товар удален из корзины
      401:
        description: Не авторизован
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Необходима авторизация'}), 401
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('DELETE FROM cart WHERE id = ? AND user_id = ?', (cart_id, session['user_id']))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Товар удален из корзины'})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/cart/checkout', methods=['POST'])
def checkout_cart():
    """
    Оформить заказ из корзины
    ---
    tags:
      - Cart
    security:
      - SessionAuth: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - phone
            - email
          properties:
            name:
              type: string
              example: "Иван Иванов"
            phone:
              type: string
              example: "+79991234567"
            email:
              type: string
              example: "ivan@example.com"
            comment:
              type: string
              example: "Доставка после 18:00"
    responses:
      200:
        description: Заказ успешно оформлен
      401:
        description: Не авторизован
      400:
        description: Корзина пуста
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Необходима авторизация'}), 401
    
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    comment = data.get('comment', '')
    
    if not all([name, phone, email]):
        return jsonify({'success': False, 'message': 'Заполните все обязательные поля'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Get cart items
        cursor.execute('SELECT product_id, quantity FROM cart WHERE user_id = ?', (session['user_id'],))
        cart_items = cursor.fetchall()
        
        if not cart_items:
            conn.close()
            return jsonify({'success': False, 'message': 'Корзина пуста'}), 400
        
        # Create orders for each item
        for item in cart_items:
            cursor.execute('''
                INSERT INTO orders (fio, phone, email, comment, product_id, user_id, quantity, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, phone, email, comment, item['product_id'], session['user_id'], item['quantity'], 'в разработке'))
        
        # Clear cart
        cursor.execute('DELETE FROM cart WHERE user_id = ?', (session['user_id'],))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Заказ успешно оформлен! Мы свяжемся с вами в ближайшее время.'})
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/product/<int:product_id>/buy', methods=['POST'])
def buy_product_by_id(product_id):
    """
    Купить товар по ID (быстрая покупка)
    ---
    tags:
      - Products
    security:
      - SessionAuth: []
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        description: ID товара
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - name
            - phone
            - email
          properties:
            name:
              type: string
              example: "Иван Иванов"
            phone:
              type: string
              example: "+79991234567"
            email:
              type: string
              example: "ivan@example.com"
            comment:
              type: string
              example: "Срочная доставка"
            quantity:
              type: integer
              example: 1
              description: Количество товара
    responses:
      200:
        description: Товар успешно куплен
      401:
        description: Не авторизован
      404:
        description: Товар не найден
    """
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Необходима авторизация'}), 401
    
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    comment = data.get('comment', '')
    quantity = data.get('quantity', 1)
    
    if not all([name, phone, email]):
        return jsonify({'success': False, 'message': 'Заполните все обязательные поля'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Check if product exists
        cursor.execute('SELECT id, name FROM goods WHERE id = ?', (product_id,))
        product = cursor.fetchone()
        
        if not product:
            conn.close()
            return jsonify({'success': False, 'message': 'Товар не найден'}), 404
        
        # Create orders
        for _ in range(quantity):
            cursor.execute('''
                INSERT INTO orders (fio, phone, email, comment, product_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, phone, email, comment, product_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True, 
            'message': f'Заказ на {quantity} шт. товара "{product["name"]}" успешно оформлен!'
        })
    except sqlite3.Error as e:
        conn.close()
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    setup_static_files()
    init_db()
    print("=" * 50)
    print("Автосалон на Python Flask")
    print("=" * 50)
    print("🚀 Приложение запускается на http://localhost:5000")
    print("💾 База данных: data.db")
    print("📁 Статические файлы: static/")
    print("=" * 50)
    app.run(debug=True, host='localhost', port=5000)
