#!/usr/bin/env python3
"""
Orchestrator to fully prepare the project after clone.

This script performs idempotent steps:
 - run `init_db.py` (if present)
 - run `generate_realistic_data.py` with defaults (if present)
 - run `scripts/auto_populate.py` (fills goods/orders, builds denorm, refreshes engine)

It tolerates missing optional scripts and logs actions.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(__file__))


def run_py(script, args=None, check=True):
    path = os.path.join(ROOT, script)
    if not os.path.exists(path):
        print(f' - skip (not found): {script}')
        return False
    cmd = [sys.executable, path]
    if args:
        cmd += args
    print('> Running:', ' '.join(cmd))
    try:
        subprocess.run(cmd, check=check)
        return True
    except subprocess.CalledProcessError as e:
        print('Command failed:', e)
        return False


def main():
    print('\n=== Full setup start ===')
    # If prebuilt archive exists, restore DB and skip heavy generation
    prebuilt_db_gz = os.path.join(ROOT, 'prebuilt', 'data.db.gz')
    if os.path.exists(prebuilt_db_gz):
        print('Found prebuilt data archive. Restoring data.db from prebuilt/data.db.gz')
        try:
            import gzip, shutil
            with gzip.open(prebuilt_db_gz, 'rb') as f_in:
                with open(os.path.join(ROOT, 'data.db'), 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            print('Restored data.db — skipping generation and population')
            return True
        except Exception as e:
            print('Failed to restore prebuilt DB:', e)
            # continue with normal flow
    # 1. init_db
    run_py('init_db.py')

    # 2. generate realistic data (optional)
    run_py('generate_realistic_data.py', args=['200', '1000', '300'])

    # 3. auto-populate (goods/orders/denorm/rebuild)
    run_py('scripts/auto_populate.py')

    print('=== Full setup finished ===\n')


if __name__ == '__main__':
    main()
