#!/usr/bin/env python3
"""
Auto-populate project data and rebuild recommendation engine.

Run from repository root:
  python scripts/auto_populate.py

Actions (idempotent):
 - Ensure `goods` table has at least 1000 rows (clone existing rows if needed)
 - Ensure `orders` table has at least 1000 rows (insert synthetic orders)
 - Build `denormalized_data` table (uses create_denormalized_table.create_denormalized_table)
 - Duplicate denormalized table to `site_data.db` (handled by create_denormalized_table)
 - Rebuild in-memory recommendation engine (calls app.get_reco_engine().refresh())
"""
import sqlite3
import random
import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(__file__))
DB_PATH = os.path.join(ROOT, 'data.db')


def ensure_goods(n=1000):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM goods')
    count = cur.fetchone()[0]
    if count >= n:
        print(f'goods already >= {n} ({count})')
        conn.close()
        return count

    # fetch existing rows to clone
    cur.execute('SELECT name, price, image, description, category, compatibility, manufacturer, warranty, stock FROM goods')
    rows = cur.fetchall()
    if not rows:
        raise SystemExit('No existing goods to clone — please add at least one product first')

    needed = n - count
    print(f'Cloning {needed} goods to reach {n} (current {count})')
    to_insert = []
    for i in range(needed):
        base = rows[i % len(rows)]
        name = f"{base[0]} — sample {count + i + 1}"
        price = base[1]
        image = base[2]
        description = base[3]
        category = base[4]
        compatibility = base[5]
        manufacturer = base[6]
        warranty = base[7]
        stock = base[8] if base[8] is not None else 0
        to_insert.append((name, price, image, description, category, compatibility, manufacturer, warranty, stock))

    cur.executemany('INSERT INTO goods (name, price, image, description, category, compatibility, manufacturer, warranty, stock) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', to_insert)
    conn.commit()
    cur.execute('SELECT COUNT(*) FROM goods')
    new_count = cur.fetchone()[0]
    conn.close()
    print(f'goods now: {new_count}')
    return new_count


def ensure_orders(n=1000):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM orders')
    count = cur.fetchone()[0]
    if count >= n:
        print(f'orders already >= {n} ({count})')
        conn.close()
        return count

    # get existing product ids range
    cur.execute('SELECT id FROM goods')
    ids = [r[0] for r in cur.fetchall()]
    if not ids:
        raise SystemExit('No goods available to create orders')

    needed = n - count
    print(f'Inserting {needed} synthetic orders to reach {n} (current {count})')
    to_insert = []
    for i in range(needed):
        pid = random.choice(ids)
        name = f'Test User {random.randint(1000,9999)}'
        phone = f'+7{random.randint(9000000000,9999999999)}'
        email = f'user{random.randint(1000,9999)}@example.com'
        comment = 'auto-generated'
        created_at = datetime.utcnow().isoformat(' ')
        to_insert.append((name, phone, email, comment, pid, created_at))

    cur.executemany('INSERT INTO orders (fio, phone, email, comment, product_id, created_at) VALUES (?, ?, ?, ?, ?, ?)', to_insert)
    conn.commit()
    cur.execute('SELECT COUNT(*) FROM orders')
    new_count = cur.fetchone()[0]
    conn.close()
    print(f'orders now: {new_count}')
    return new_count


def build_denorm():
    print('Building denormalized_data (via create_denormalized_table) ...')
    try:
        sys.path.insert(0, ROOT)
        from create_denormalized_table import create_denormalized_table
    except Exception as e:
        print('Failed to import create_denormalized_table:', e)
        return False
    try:
        create_denormalized_table(duplicate_db='site_data.db')
        print('denormalized_data built and duplicated to site_data.db')
        return True
    except Exception as e:
        print('Error while building denormalized table:', e)
        return False


def rebuild_engine():
    print('Rebuilding in-memory recommendation engine...')
    try:
        sys.path.insert(0, ROOT)
        import app
        engine = app.get_reco_engine()
        if engine is None:
            print('Recommendation engine module missing or not available')
            return False
        try:
            engine.refresh()
            print('Engine refreshed: products=', len(engine.products), 'vocab=', len(engine.tfidf.vocabulary_))
            return True
        except Exception as e:
            print('Engine.refresh() failed:', e)
            return False
    except Exception as e:
        print('Failed to import app or rebuild engine:', e)
        return False


def main():
    print('Auto-populate start')
    ensure_goods(1000)
    ensure_orders(1000)
    build_denorm()
    rebuild_engine()
    print('Done')


if __name__ == '__main__':
    main()
