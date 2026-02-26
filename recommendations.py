import sqlite3
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import numpy as np


class RecommendationEngine:
    def __init__(self, db_path: str = 'data.db'):
        self.db_path = db_path
        self.ids = []
        self.products = []
        self.tfidf = None
        self.matrix = None
        self._build()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _fetch_products(self):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute('SELECT id, name, description, category, compatibility, manufacturer, price, image FROM goods')
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    def _build(self):
        rows = self._fetch_products()
        if not rows:
            self.ids = []
            self.products = []
            self.matrix = None
            return

        self.ids = [r['id'] for r in rows]
        self.products = rows

        corpus = []
        conn = self._connect()
        for r in rows:
            parts = [str(r.get('name', '')), str(r.get('description', '')),
                     str(r.get('category', '')), str(r.get('compatibility', '')),
                     str(r.get('manufacturer', ''))]

            # Enrich corpus with denormalized_data related to this product (user_login, order_status)
            try:
                cur = conn.cursor()
                cur.execute('SELECT GROUP_CONCAT(DISTINCT user_login, " ") as users, GROUP_CONCAT(DISTINCT order_status, " ") as statuses FROM denormalized_data WHERE product_id = ?', (r['id'],))
                extra = cur.fetchone()
                if extra:
                    users = extra['users'] or '' if isinstance(extra, dict) else (extra[0] or '')
                    statuses = extra['statuses'] or '' if isinstance(extra, dict) else (extra[1] or '')
                    parts.append(str(users))
                    parts.append(str(statuses))
            except Exception:
                # denormalized_data might not exist yet
                pass

            corpus.append(' '.join(parts))
        conn.close()

        # sklearn supports 'english' or custom list for stop_words; use default (None)
        self.tfidf = TfidfVectorizer(stop_words=None, max_features=5000)
        self.matrix = self.tfidf.fit_transform(corpus)
        # load popularity from denormalized table if exists
        try:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT product_id, COUNT(*) as cnt FROM orders GROUP BY product_id")
            counts = {r[0]: r[1] for r in cur.fetchall()}
            conn.close()
        except Exception:
            counts = {}

        # attach popularity to products
        for p in self.products:
            p['popularity'] = counts.get(p['id'], 0)

    def refresh(self):
        """Перестроить векторную модель (например, после обновления БД)."""
        self._build()

    def get_recommendations(self, product_id: int, top_k: int = 5) -> List[Dict]:
        """Вернуть список рекомендованных товаров (JSON-сериализуемый)."""
        if self.matrix is None or product_id not in self.ids:
            return []

        idx = self.ids.index(product_id)
        cosine_similarities = linear_kernel(self.matrix[idx:idx+1], self.matrix).flatten()
        # exclude itself
        cosine_similarities[idx] = -1
        top_indices = np.argsort(cosine_similarities)[::-1][:top_k]

        results = []
        # compute final score combining text similarity and popularity
        max_pop = max((p.get('popularity', 0) for p in self.products), default=1)
        alpha = 0.8  # weight for text similarity
        beta = 0.2   # weight for popularity
        for i in top_indices:
            cos = float(cosine_similarities[i])
            pop = float(self.products[i].get('popularity', 0))
            if cos <= 0 and pop == 0:
                continue
            pop_norm = pop / max_pop if max_pop > 0 else 0.0
            final_score = alpha * cos + beta * pop_norm
            p = self.products[i]
            results.append({
                'id': p['id'],
                'name': p['name'],
                'price': p.get('price', ''),
                'image': p.get('image', ''),
                'score': float(final_score)
            })

        return results


if __name__ == '__main__':
    # quick local test
    engine = RecommendationEngine()
    print(engine.get_recommendations(product_id=1, top_k=5))
