import sqlite3
import random
from itertools import cycle

DB = 'data.db'
SEED = 42
NUM = 100  # number of distinct manufacturers and compatibilities to generate

random.seed(SEED)

manufacturers = [f"Manufacturer {i:03d}" for i in range(1, NUM+1)]
compatibilities = [f"Compatibility {i:03d}" for i in range(1, NUM+1)]

# For more realistic compatibility values, create some comma-separated groups
compat_groups = []
for i, c in enumerate(compatibilities, start=1):
    # each compatibility entry will list 1-3 compat names to vary
    k = random.randint(1, 3)
    picks = random.sample(compatibilities, k)
    compat_groups.append(", ".join(picks))

if __name__ == '__main__':
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('SELECT id FROM goods ORDER BY id')
    rows = [r[0] for r in cur.fetchall()]
    if not rows:
        print('No goods found in DB')
    else:
        print(f'Found {len(rows)} goods, assigning {NUM} manufacturers and compatibilities...')
        # cycle through manufacturers and compat_groups deterministically
        manu_cycle = cycle(manufacturers)
        compat_cycle = cycle(compat_groups)
        updates = 0
        for gid in rows:
            manu = next(manu_cycle)
            comp = next(compat_cycle)
            cur.execute('UPDATE goods SET manufacturer = ?, compatibility = ? WHERE id = ?', (manu, comp, gid))
            updates += 1
        conn.commit()
        conn.close()
        print(f'Applied updates to {updates} goods. Sample manufacturer: {manufacturers[0]}, sample compatibility: {compat_groups[0]}')
