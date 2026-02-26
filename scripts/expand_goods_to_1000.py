import sqlite3
import random
import os

DB = 'data.db'
TARGET = 1000


def expand_goods(target=TARGET):
    if not os.path.exists(DB):
        print('data.db not found')
        return
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('SELECT COUNT(*) FROM goods')
    cur_count = cur.fetchone()[0]
    if cur_count >= target:
        print(f'Goods already >= {target} ({cur_count})')
        conn.close()
        return cur_count

    cur.execute('SELECT id, name, price, image, description, category, compatibility, manufacturer, warranty, stock FROM goods')
    bases = cur.fetchall()
    if not bases:
        print('No base goods to clone')
        conn.close()
        return cur_count

    need = target - cur_count
    print(f'Cloning {need} goods to reach {target}...')
    idx = 0
    while need > 0:
        b = bases[idx % len(bases)]
        base_name = b[1]
        price = b[2]
        image = b[3]
        description = b[4]
        category = b[5]
        compatibility = b[6]
        manufacturer = b[7]
        warranty = b[8]
        stock = b[9] if b[9] is not None else 10
        # create unique name
        new_name = f"{base_name} — sample {cur_count + (TARGET - need) + 1}"
        # random small price variation
        try:
            p = float(price)
            p = round(p * random.uniform(0.8, 1.2), 2)
            p_str = str(int(p)) if p.is_integer() else str(p)
        except Exception:
            p_str = price
        try:
            cur.execute('INSERT INTO goods (name, price, image, description, category, compatibility, manufacturer, warranty, stock) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (new_name, p_str, image, description, category, compatibility, manufacturer, warranty, stock))
            need -= 1
            cur_count += 1
        except Exception as e:
            print('Insert error', e)
            break
        idx += 1
    conn.commit()
    conn.close()
    print('Done. Goods now:', cur_count)
    return cur_count

if __name__ == '__main__':
    expand_goods()
