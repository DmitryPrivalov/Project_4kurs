#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для загрузки тестовых данных в базу данных autosalon-flask
Практическое занятие №5: Заполнение базы данных тестовыми данными

Использование:
    python data_loader.py                # Загрузить из test_data.json
    python data_loader.py --file data.json  # Загрузить из конкретного файла
    python data_loader.py --sql test_data.sql  # Загрузить из SQL файла
"""

import sqlite3
import json
import csv
import sys
import os
from datetime import datetime
from pathlib import Path


class DataLoader:
    """Загрузчик тестовых данных в SQLite базу"""
    
    def __init__(self, db_path='data.db'):
        """Инициализация загрузчика
        
        Args:
            db_path (str): Путь к файлу базы данных
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.stats = {
            'goods': 0,
            'users': 0,
            'orders': 0,
            'services': 0,
            'cart': 0
        }
    
    def connect(self):
        """Подключиться к базе данных"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"✓ Подключение к БД: {self.db_path}")
            return True
        except sqlite3.Error as e:
            print(f"✗ Ошибка подключения: {e}")
            return False
    
    def disconnect(self):
        """Отключиться от базы данных"""
        if self.conn:
            self.conn.close()
            print("✓ Отключение от БД")
    
    def load_from_json(self, json_file='test_data.json'):
        """Загрузить данные из JSON файла
        
        Args:
            json_file (str): Путь к JSON файлу
            
        Returns:
            bool: True если успешно, False если ошибка
        """
        if not os.path.exists(json_file):
            print(f"✗ Файл не найден: {json_file}")
            return False
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"✓ JSON файл загружен: {json_file}")
            
            # Загружаем товары
            if 'goods' in data:
                self._load_goods(data['goods'])
            
            # Загружаем пользователей
            if 'users' in data:
                self._load_users(data['users'])
            
            # Загружаем услуги
            if 'services' in data:
                self._load_services(data['services'])
            
            # Загружаем заказы
            if 'orders' in data:
                self._load_orders(data['orders'])
            
            # Загружаем корзину
            if 'cart' in data:
                self._load_cart(data['cart'])
            
            self.conn.commit()
            return True
            
        except json.JSONDecodeError as e:
            print(f"✗ Ошибка парсинга JSON: {e}")
            return False
        except sqlite3.Error as e:
            print(f"✗ Ошибка БД: {e}")
            self.conn.rollback()
            return False
    
    def load_from_sql(self, sql_file='test_data.sql'):
        """Загрузить данные из SQL файла
        
        Args:
            sql_file (str): Путь к SQL файлу
            
        Returns:
            bool: True если успешно, False если ошибка
        """
        if not os.path.exists(sql_file):
            print(f"✗ Файл не найден: {sql_file}")
            return False
        
        try:
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            print(f"✓ SQL файл загружен: {sql_file}")
            
            # Выполняем SQL команды
            self.cursor.executescript(sql_script)
            self.conn.commit()
            
            # Подсчитываем загруженные данные
            self.stats['goods'] = self.cursor.execute("SELECT COUNT(*) FROM goods").fetchone()[0]
            self.stats['users'] = self.cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            self.stats['orders'] = self.cursor.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
            self.stats['services'] = self.cursor.execute("SELECT COUNT(*) FROM services").fetchone()[0]
            self.stats['cart'] = self.cursor.execute("SELECT COUNT(*) FROM cart").fetchone()[0]
            
            return True
            
        except sqlite3.Error as e:
            print(f"✗ Ошибка БД: {e}")
            self.conn.rollback()
            return False
    
    def _load_goods(self, goods_list):
        """Загрузить товары"""
        for item in goods_list:
            try:
                self.cursor.execute('''
                    INSERT INTO goods (name, price, image, description, category, 
                                     manufacturer, warranty, stock, compatibility)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item['name'],
                    item['price'],
                    item['image'],
                    item['description'],
                    item['category'],
                    item['manufacturer'],
                    item['warranty'],
                    item['stock'],
                    item['compatibility']
                ))
                self.stats['goods'] += 1
            except sqlite3.Error as e:
                print(f"  ⚠ Ошибка при вставке товара: {e}")
    
    def _load_users(self, users_list):
        """Загрузить пользователей"""
        for item in users_list:
            try:
                self.cursor.execute('''
                    INSERT INTO users (login, password, email, role, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    item['login'],
                    item['password'],
                    item['email'],
                    item['role'],
                    item['created_at']
                ))
                self.stats['users'] += 1
            except sqlite3.Error as e:
                print(f"  ⚠ Ошибка при вставке пользователя: {e}")
    
    def _load_services(self, services_list):
        """Загрузить услуги"""
        for item in services_list:
            try:
                self.cursor.execute('''
                    INSERT INTO services (name, description, price, image, category)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    item['name'],
                    item['description'],
                    item['price'],
                    item['image'],
                    item['category']
                ))
                self.stats['services'] += 1
            except sqlite3.Error as e:
                print(f"  ⚠ Ошибка при вставке услуги: {e}")
    
    def _load_orders(self, orders_list):
        """Загрузить заказы"""
        for item in orders_list:
            try:
                self.cursor.execute('''
                    INSERT INTO orders (fio, phone, email, comment, product_id, user_id, created_at, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item['fio'],
                    item['phone'],
                    item['email'],
                    item['comment'],
                    item['product_id'],
                    item['user_id'],
                    item['created_at'],
                    item['status']
                ))
                self.stats['orders'] += 1
            except sqlite3.Error as e:
                print(f"  ⚠ Ошибка при вставке заказа: {e}")
    
    def _load_cart(self, cart_list):
        """Загрузить корзину"""
        for item in cart_list:
            try:
                self.cursor.execute('''
                    INSERT INTO cart (user_id, product_id, quantity, added_at)
                    VALUES (?, ?, ?, ?)
                ''', (
                    item['user_id'],
                    item['product_id'],
                    item['quantity'],
                    item['added_at']
                ))
                self.stats['cart'] += 1
            except sqlite3.Error as e:
                print(f"  ⚠ Ошибка при вставке товара в корзину: {e}")
    
    def print_stats(self):
        """Вывести статистику загрузки"""
        print("\n" + "="*50)
        print("СТАТИСТИКА ЗАГРУЗКИ")
        print("="*50)
        print(f"Товары (goods):     {self.stats['goods']} записей")
        print(f"Пользователи (users): {self.stats['users']} записей")
        print(f"Заказы (orders):    {self.stats['orders']} записей")
        print(f"Услуги (services):  {self.stats['services']} записей")
        print(f"Корзина (cart):     {self.stats['cart']} записей")
        print(f"{'─'*50}")
        total = sum(self.stats.values())
        print(f"ВСЕГО:              {total} записей")
        print("="*50 + "\n")


def main():
    """Главная функция"""
    print("\n" + "="*50)
    print("ЗАГРУЗКА ТЕСТОВЫХ ДАННЫХ")
    print("autosalon-flask | Практическое занятие №5")
    print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50 + "\n")
    
    # Параметры по умолчанию
    db_path = 'data.db'
    json_file = 'test_data.json'
    sql_file = 'test_data.sql'
    use_json = True
    
    # Проверяем аргументы командной строки
    if len(sys.argv) > 1:
        if '--sql' in sys.argv:
            use_json = False
        if '--file' in sys.argv:
            idx = sys.argv.index('--file')
            if idx + 1 < len(sys.argv):
                json_file = sys.argv[idx + 1]
        if '--db' in sys.argv:
            idx = sys.argv.index('--db')
            if idx + 1 < len(sys.argv):
                db_path = sys.argv[idx + 1]
    
    # Создаем загрузчик
    loader = DataLoader(db_path)
    
    # Подключаемся к БД
    if not loader.connect():
        print("✗ Не удалось подключиться к БД")
        return False
    
    try:
        # Загружаем данные
        if use_json:
            success = loader.load_from_json(json_file)
        else:
            success = loader.load_from_sql(sql_file)
        
        if success:
            print("✓ Данные успешно загружены")
            loader.print_stats()
            return True
        else:
            print("✗ Ошибка при загрузке данных")
            return False
    
    finally:
        loader.disconnect()


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
