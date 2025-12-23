"""
Конфигурация Flask приложения для автосалона

Используется для настройки параметров приложения
"""

# Использовать DEBUG режим
DEBUG = True

# Секретный ключ для сессий
# Для продакшена генерируйте новый ключ!
SECRET_KEY = 'dev-key-change-in-production'

# Конфигурация базы данных
DATABASE = 'data.db'

# Flask конфигурация
FLASK_ENV = 'development'
FLASK_APP = 'app.py'

# Параметры сервера
HOST = 'localhost'
PORT = 5000

# Параметры сессии
PERMANENT_SESSION_LIFETIME = 3600  # 1 час
SESSION_COOKIE_SECURE = False  # True для HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Логирование
LOG_TO_STDOUT = True
LOG_LEVEL = 'DEBUG'
