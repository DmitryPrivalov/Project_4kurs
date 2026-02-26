#!/usr/bin/env python3
"""
Export current `data.db` and trained recommendation engine into `prebuilt/` folder.

Usage:
  python scripts/export_prebuilt.py

This creates `prebuilt/data.db` (copy) and `prebuilt/engine.joblib` (serialized engine).
"""
import os
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))
PRE = os.path.join(ROOT, 'prebuilt')
DB_SRC = os.path.join(ROOT, 'data.db')
DB_DST = os.path.join(PRE, 'data.db')

def main():
    if not os.path.exists(DB_SRC):
        print('data.db not found; run setup scripts first')
        sys.exit(1)
    os.makedirs(PRE, exist_ok=True)
    print('Copying data.db to prebuilt/data.db')
    shutil.copy2(DB_SRC, DB_DST)

    # serialize recommendation engine
    try:
        sys.path.insert(0, ROOT)
        # Always build a fresh engine from current code + DB to ensure weights/config applied
        from recommendations import RecommendationEngine
        engine = RecommendationEngine(DB_SRC)
    except Exception as e:
        print('Failed to import/build engine:', e)
        engine = None

    if engine is not None:
        try:
            import joblib
            dst = os.path.join(PRE, 'engine.joblib')
            print('Serializing engine to', dst)
            joblib.dump(engine, dst)
            print('Engine serialized')
        except Exception as e:
            print('Failed to serialize engine:', e)
    else:
        print('Engine not present; skipped serialization')

if __name__ == '__main__':
    main()
