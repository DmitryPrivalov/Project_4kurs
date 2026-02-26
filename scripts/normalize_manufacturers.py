import sqlite3
import re

DB = 'data.db'

def normalize(name: str) -> str:
    if not name:
        return ''
    s = name.lower()
    s = re.sub(r"\b(llc|ltd|inc|corp|corporation|gmbh|srl|oy|sa|limited)\b", "", s)
    s = re.sub(r"[^a-z0-9а-яё\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    # titlecase for DB readability
    return s.title()

if __name__ == '__main__':
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute('SELECT DISTINCT manufacturer FROM goods')
    rows = [r[0] for r in cur.fetchall() if r[0] is not None]
    changes = []
    for orig in rows:
        norm = normalize(orig)
        if norm != (orig or '').strip():
            cur.execute('UPDATE goods SET manufacturer = ? WHERE manufacturer = ?', (norm, orig))
            changes.append((orig, norm))
    conn.commit()
    conn.close()
    print(f'Normalized {len(changes)} manufacturer values')
    for o, n in changes[:50]:
        print(f'"{o}" -> "{n}"')
