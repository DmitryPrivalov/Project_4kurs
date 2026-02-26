import sqlite3
import os
from datetime import datetime

DB = 'data.db'


def create_denormalized_table(duplicate_db: str = 'site_data.db'):
    """Create `denormalized_data` in `data.db` and optionally duplicate into another DB file.

    If `duplicate_db` is provided (filename), the same table will be created/overwritten
    in that database with the same rows, so both DBs contain identical denormalized data.
    """
    if not os.path.exists(DB):
        print('❌ data.db не найден')
        return

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # Drop old table if exists
    cursor.execute('DROP TABLE IF EXISTS denormalized_data')

    # Create denormalized table
    cursor.execute('''
        CREATE TABLE denormalized_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            user_id INTEGER,
            user_login TEXT,
            product_id INTEGER,
            product_name TEXT,
            order_quantity INTEGER,
            total_price REAL,
            order_status TEXT,
            product_category TEXT,
            product_manufacturer TEXT,
            days_since_order INTEGER,
            product_popularity INTEGER,
            product_price REAL,
            product_stock INTEGER,
            created_at TIMESTAMP
        )
    ''')

    # Build base rows joining orders and goods; for user try to match by user_id or email
    # Orders schema may be minimal (product_id, fio, email, created_at)
    cursor.execute("PRAGMA table_info('orders')")
    orders_cols = [r[1] for r in cursor.fetchall()]

    # Query orders
    if 'user_id' in orders_cols:
        cursor.execute('SELECT id, user_id, fio, email, product_id, created_at FROM orders')
        orders = cursor.fetchall()
    else:
        cursor.execute('SELECT id, NULL as user_id, fio, email, product_id, created_at FROM orders')
        orders = cursor.fetchall()

    # Get popularity counts per product
    cursor.execute('SELECT product_id, COUNT(*) as cnt FROM orders GROUP BY product_id')
    pop = {r[0]: r[1] for r in cursor.fetchall()}
    max_pop = max(pop.values()) if pop else 1

    now = datetime.now()

    for row in orders:
        order_id, user_id, fio, email, product_id, created_at = row
        # product info
        cursor.execute('SELECT name, price, category, manufacturer, stock FROM goods WHERE id = ?', (product_id,))
        g = cursor.fetchone()
        if not g:
            continue
        name, price, category, manufacturer, stock = g

        # find user login
        user_login = None
        if user_id:
            cursor.execute('SELECT login FROM users WHERE id = ?', (user_id,))
            u = cursor.fetchone()
            if u:
                user_login = u[0]
        if not user_login and email:
            cursor.execute('SELECT login FROM users WHERE email = ?', (email,))
            u = cursor.fetchone()
            if u:
                user_login = u[0]

        qty = 1
        try:
            created = datetime.fromisoformat(created_at) if isinstance(created_at, str) else datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
        except Exception:
            try:
                created = datetime.strptime(created_at, '%Y-%m-%d')
            except Exception:
                created = now

        days = (now - created).days
        popularity = pop.get(product_id, 0)
        total_price = float(price) * qty if price is not None else 0.0

        cursor.execute('''
            INSERT INTO denormalized_data (
                order_id, user_id, user_login, product_id, product_name,
                order_quantity, total_price, order_status, product_category,
                product_manufacturer, days_since_order, product_popularity,
                product_price, product_stock, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_id, user_id, user_login, product_id, name,
            qty, total_price, 'completed', category, manufacturer,
            days, popularity, float(price or 0), stock or 0, created
        ))

    conn.commit()
    # Read back rows for optional duplication
    cursor.execute('SELECT * FROM denormalized_data')
    rows = cursor.fetchall()
    cols = [d[0] for d in cursor.description]
    conn.close()

    print('✅ Таблица denormalized_data создана и заполнена в', DB)

    # duplicate into another DB file if requested
    if duplicate_db and duplicate_db != DB:
        try:
            dconn = sqlite3.connect(duplicate_db)
            dcur = dconn.cursor()
            # drop/create schema
            dcur.execute('DROP TABLE IF EXISTS denormalized_data')
            dcur.execute('''
                CREATE TABLE denormalized_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER,
                    user_id INTEGER,
                    user_login TEXT,
                    product_id INTEGER,
                    product_name TEXT,
                    order_quantity INTEGER,
                    total_price REAL,
                    order_status TEXT,
                    product_category TEXT,
                    product_manufacturer TEXT,
                    days_since_order INTEGER,
                    product_popularity INTEGER,
                    product_price REAL,
                    product_stock INTEGER,
                    created_at TIMESTAMP
                )
            ''')

            if rows:
                placeholders = ','.join('?' for _ in cols)
                dcur.executemany(f'INSERT INTO denormalized_data ({",".join(cols)}) VALUES ({placeholders})', rows)
            dconn.commit()
            dconn.close()
            print(f'✅ Данные denormalized_data продублированы в {duplicate_db}')
        except Exception as e:
            print('❌ Ошибка при дублировании в', duplicate_db, e)


if __name__ == '__main__':
    create_denormalized_table()
