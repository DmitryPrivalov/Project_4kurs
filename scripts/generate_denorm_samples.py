import sqlite3
import random
from datetime import datetime, timedelta
import os
import importlib.util, sys
# load create_denormalized_table from workspace path
spec = importlib.util.spec_from_file_location('denorm_mod', r'c:\\Users\\Dima\\Project_4kurs\\create_denormalized_table.py')
denorm_mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = denorm_mod
spec.loader.exec_module(denorm_mod)
create_denormalized_table = getattr(denorm_mod, 'create_denormalized_table')

DB = 'data.db'
TARGET = 1000

def random_name(i):
    return f"User{i:04d}"

def random_email(i):
    return f"user{i:04d}@example.com"

def ensure_min_orders(target=TARGET):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM orders')
    cur_count = cur.fetchone()[0]
    if cur_count >= target:
        print(f"Orders already >= {target} ({cur_count}) — no insertion needed")
        conn.close()
        return cur_count

    # gather goods ids
    cur.execute('SELECT id, price FROM goods')
    goods = cur.fetchall()
    if not goods:
        print('No goods found in DB — cannot generate orders')
        conn.close()
        return cur_count

    # ensure at least one user exists; otherwise create test users
    cur.execute('SELECT id FROM users LIMIT 1')
    u = cur.fetchone()
    if not u:
        # create 10 users
        for i in range(1, 11):
            try:
                cur.execute('INSERT INTO users (login, password, email, role) VALUES (?, ?, ?, ?)',
                            (random_name(i), 'pass', random_email(i), 'user'))
            except Exception:
                pass
        conn.commit()

    # re-fetch some user ids
    cur.execute('SELECT id FROM users')
    user_ids = [r[0] for r in cur.fetchall()]
    if not user_ids:
        print('No users available even after creation — abort')
        conn.close()
        return cur_count

    need = target - cur_count
    print(f'Inserting {need} synthetic orders...')
    now = datetime.now()
    for i in range(need):
        prod = random.choice(goods)
        product_id = prod[0]
        price = prod[1] if prod[1] is not None else 0
        user_id = random.choice(user_ids)
        fio = f"AutoBuyer {random.randint(1000,9999)}"
        email = f"buyer{random.randint(1000,9999)}@example.com"
        created_at = (now - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d %H:%M:%S')
        try:
            cur.execute('INSERT INTO orders (fio, phone, email, comment, product_id, created_at, user_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (fio, '', email, 'auto-generated', product_id, created_at, user_id))
        except Exception:
            # fallback if schema different
            try:
                cur.execute('INSERT INTO orders (fio, phone, email, comment, product_id, created_at) VALUES (?, ?, ?, ?, ?, ?)',
                            (fio, '', email, 'auto-generated', product_id, created_at))
            except Exception:
                # last resort insert minimal
                try:
                    cur.execute('INSERT INTO orders (product_id) VALUES (?)', (product_id,))
                except Exception:
                    pass
    conn.commit()
    cur.execute('SELECT COUNT(*) FROM orders')
    total = cur.fetchone()[0]
    conn.close()
    print('Orders after insertion:', total)
    return total

if __name__ == '__main__':
    if not os.path.exists(DB):
        print('data.db not found in current folder')
        raise SystemExit(1)

    total = ensure_min_orders(TARGET)
    # build denormalized table and duplicate into site_data.db
    create_denormalized_table(duplicate_db='site_data.db')

    # report denormalized_data count
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    try:
        cur.execute('SELECT COUNT(*) FROM denormalized_data')
        den_count = cur.fetchone()[0]
    except Exception:
        den_count = 0
    conn.close()
    print('Denormalized rows in data.db:', den_count)
    # also check duplicate
    if os.path.exists('site_data.db'):
        dconn = sqlite3.connect('site_data.db')
        dcur = dconn.cursor()
        try:
            dcur.execute('SELECT COUNT(*) FROM denormalized_data')
            dcount = dcur.fetchone()[0]
        except Exception:
            dcount = 0
        dconn.close()
        print('Denormalized rows in site_data.db:', dcount)
    else:
        print('site_data.db not present')
