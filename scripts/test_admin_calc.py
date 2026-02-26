import sqlite3
import json
import importlib.util
import sys

# load recommendations.py module directly
spec = importlib.util.spec_from_file_location("recom_mod", r"c:\\Users\\Dima\\Project_4kurs\\recommendations.py")
recom_mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = recom_mod
spec.loader.exec_module(recom_mod)
RecommendationEngine = getattr(recom_mod, 'RecommendationEngine')
from sklearn.metrics.pairwise import linear_kernel


def get_first_product_id():
    try:
        conn = sqlite3.connect('data.db')
        cur = conn.cursor()
        cur.execute('SELECT id FROM goods LIMIT 1')
        r = cur.fetchone()
        conn.close()
        return r[0] if r else None
    except Exception as e:
        print('DB error:', e)
        return None


if __name__ == '__main__':
    pid = get_first_product_id()
    if pid is None:
        print('No products found in data.db')
    else:
        engine = RecommendationEngine('data.db')
        # find index
        if pid not in engine.ids:
            print('Product id not found in engine ids')
        else:
            idx = engine.ids.index(pid)
            mat = engine.matrix
            cosine_similarities = linear_kernel(mat[idx:idx+1], mat).flatten()
            cosine_similarities[idx] = -1

            items = []
            max_pop = max((p.get('popularity', 0) for p in engine.products), default=1)
            alpha = 0.8
            beta = 0.2
            for i, cos in enumerate(cosine_similarities):
                if i == idx:
                    continue
                p = engine.products[i]
                pop = float(p.get('popularity', 0))
                pop_norm = pop / max_pop if max_pop > 0 else 0.0
                final_score = alpha * float(cos) + beta * pop_norm
                items.append({
                    'id': p['id'],
                    'name': p['name'],
                    'cosine': float(cos),
                    'popularity': pop,
                    'pop_norm': pop_norm,
                    'final_score': float(final_score)
                })

            items = sorted(items, key=lambda x: x['final_score'], reverse=True)[:12]
            print(json.dumps({'product_id': pid, 'items': items}, ensure_ascii=False, indent=2))
