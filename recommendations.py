import sqlite3
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from scipy.sparse import hstack
import numpy as np
import json
import os
import re


class RecommendationEngine:
    def __init__(self, db_path: str = 'data.db'):
        self.db_path = db_path
        self.ids = []
        self.products = []
        # vectorizers / matrices
        self.tfidf_text = None
        self.tfidf_category = None
        self.tfidf_manufacturer = None
        self.matrix_text = None
        self.matrix_category = None
        self.matrix_manufacturer = None
        # default weights (four components: text, category, manufacturer, popularity)
        self.w_text = 0.6
        self.w_category = 0.2
        self.w_manufacturer = 0.1
        self.w_popularity = 0.1
        # scaling for categorical sparse matrices
        self.cat_scale = 1.0
        self._load_weights()
        self._build()

    def _load_weights(self):
        try:
            cfg_path = os.path.join(os.path.dirname(__file__), 'reco_config.json')
            if os.path.exists(cfg_path):
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                    # new explicit weights
                    self.w_text = float(cfg.get('w_text', cfg.get('alpha', self.w_text)))
                    self.w_popularity = float(cfg.get('w_popularity', cfg.get('beta', self.w_popularity)))
                    self.w_category = float(cfg.get('w_category', self.w_category))
                    self.w_manufacturer = float(cfg.get('w_manufacturer', self.w_manufacturer))
                    # scaling factor for category/manufacturer vectors
                    self.cat_scale = float(cfg.get('cat_scale', cfg.get('cat_weight', 1.0)))
        except Exception:
            pass

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
        # separate categorical text for category/manufacturer/compatibility
        cat_corpus = []
        manuf_corpus = []
        conn = self._connect()
        def _normalize_manufacturer(name: str) -> str:
            if not name:
                return ''
            s = str(name).lower()
            # remove common company suffixes and punctuation
            s = re.sub(r"\b(llc|ltd|inc|corp|corporation|gmbh|srl|oy|sa|limited)\b", "", s)
            s = re.sub(r"[^a-z0-9а-яё\s]", " ", s)
            s = re.sub(r"\s+", " ", s).strip()
            return s

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
            # build small categorical text blob (short, repeated)
            # category + compatibility as word-level tokens
            cat_parts = [str(r.get('category', '')), str(r.get('compatibility', ''))]
            cat_corpus.append(' '.join(cat_parts).lower())
            # normalize manufacturer for fuzzy matching (use char n-grams later)
            mnorm = _normalize_manufacturer(r.get('manufacturer', ''))
            # avoid treating empty manufacturer as identical across many products
            if not mnorm:
                mnorm = f'__no_manufacturer_{r.get("id")}'
            manuf_corpus.append(mnorm)
        conn.close()

        # Vectorize main textual corpus
        self.tfidf_text = TfidfVectorizer(stop_words=None, max_features=5000)
        matrix_text = self.tfidf_text.fit_transform(corpus)
        self.matrix_text = matrix_text

        # Vectorize category (category + compatibility) and manufacturer separately
        self.tfidf_category = TfidfVectorizer(stop_words=None, max_features=300)
        matrix_category = self.tfidf_category.fit_transform(cat_corpus)
        # manufacturer: use character n-grams to allow partial/fuzzy matches between similar names
        self.tfidf_manufacturer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3,6), lowercase=True, max_features=200)
        matrix_manufacturer = self.tfidf_manufacturer.fit_transform(manuf_corpus)

        # scale categorical matrices by configured factor
        try:
            matrix_category = matrix_category.multiply(self.cat_scale)
            matrix_manufacturer = matrix_manufacturer.multiply(self.cat_scale)
        except Exception:
            pass

        self.matrix_category = matrix_category
        self.matrix_manufacturer = matrix_manufacturer
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
        if product_id not in self.ids:
            return []

        idx = self.ids.index(product_id)

        # compute per-component cosine similarities (text / category / manufacturer)
        sims_text = np.zeros(len(self.ids))
        sims_category = np.zeros(len(self.ids))
        sims_manufacturer = np.zeros(len(self.ids))
        try:
            if self.matrix_text is not None:
                sims_text = linear_kernel(self.matrix_text[idx:idx+1], self.matrix_text).flatten()
        except Exception:
            sims_text = np.zeros(len(self.ids))

        try:
            if self.matrix_category is not None:
                sims_category = linear_kernel(self.matrix_category[idx:idx+1], self.matrix_category).flatten()
        except Exception:
            sims_category = np.zeros(len(self.ids))

        try:
            if self.matrix_manufacturer is not None:
                sims_manufacturer = linear_kernel(self.matrix_manufacturer[idx:idx+1], self.matrix_manufacturer).flatten()
        except Exception:
            sims_manufacturer = np.zeros(len(self.ids))

        # exclude itself
        sims_text[idx] = -1
        sims_category[idx] = -1
        sims_manufacturer[idx] = -1

        # popularity normalization
        max_pop = max((p.get('popularity', 0) for p in self.products), default=1)

        # compute final score as weighted sum of four components
        results = []
        scores = []
        for i in range(len(self.ids)):
            cos_t = float(sims_text[i]) if sims_text is not None else 0.0
            cos_c = float(sims_category[i]) if sims_category is not None else 0.0
            cos_m = float(sims_manufacturer[i]) if sims_manufacturer is not None else 0.0
            pop = float(self.products[i].get('popularity', 0))
            pop_norm = pop / max_pop if max_pop > 0 else 0.0

            score = (self.w_text * cos_t) + (self.w_category * cos_c) + (self.w_manufacturer * cos_m) + (self.w_popularity * pop_norm)
            scores.append((i, score))

        # sort by score desc and take top_k (exclude negative/zero)
        top = sorted(scores, key=lambda x: x[1], reverse=True)
        taken = 0
        for i, sc in top:
            if taken >= top_k:
                break
            if sc <= 0:
                continue
            p = self.products[i]
            results.append({
                'id': p['id'],
                'name': p['name'],
                'price': p.get('price', ''),
                'image': p.get('image', ''),
                'score': float(sc)
            })
            taken += 1

        return results


if __name__ == '__main__':
    # quick local test
    engine = RecommendationEngine()
    print(engine.get_recommendations(product_id=1, top_k=5))
