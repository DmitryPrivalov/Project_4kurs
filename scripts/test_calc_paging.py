import sqlite3, json
import importlib.util, sys
spec = importlib.util.spec_from_file_location('appmod', r'c:\\Users\\Dima\\Project_4kurs\\app.py')
appmod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = appmod
spec.loader.exec_module(appmod)
app = getattr(appmod, 'app')

# get a product id
conn = sqlite3.connect('data.db')
cur = conn.cursor()
cur.execute('SELECT id FROM goods LIMIT 1')
row = cur.fetchone()
conn.close()
if not row:
    print('no goods')
    raise SystemExit(1)
pid = row[0]

with app.test_client() as client:
    with client.session_transaction() as sess:
        sess['user_id'] = 1
        sess['role'] = 'admin'
    resp = client.get(f'/api/admin/calculations/{pid}?page=1&per_page=10')
    print('status', resp.status_code)
    print(json.dumps(resp.get_json(), ensure_ascii=False, indent=2))
