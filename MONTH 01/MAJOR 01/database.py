"""
SQLite database layer for products and reviews.
Swap this out for MongoDB/PostgreSQL later if you want — the interface
(add_product, add_reviews, get_products, get_reviews) stays the same.
"""
import sqlite3
import os
import sys
from datetime import datetime


def _get_db_path():
    """
    Persistent location for the SQLite file.
    - Normal script run: next to database.py.
    - Packaged .exe (PyInstaller): next to the .exe itself, NOT the temp
      extraction folder (sys._MEIPASS), which is deleted after each run.
    """
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, 'sentiment_data.db')


DB_PATH = _get_db_path()


class Database:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                source TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                rating REAL,
                date TEXT,
                sentiment TEXT,
                score REAL,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        conn.commit()
        conn.close()

    def add_product(self, name, source):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute(
            'SELECT id FROM products WHERE name = ? AND source = ?',
            (name, source)
        )
        row = cur.fetchone()
        if row:
            conn.close()
            return row['id']

        cur.execute(
            'INSERT INTO products (name, source, created_at) VALUES (?, ?, ?)',
            (name, source, datetime.now().isoformat())
        )
        conn.commit()
        product_id = cur.lastrowid
        conn.close()
        return product_id

    def add_reviews(self, product_id, reviews):
        conn = self._connect()
        cur = conn.cursor()
        for r in reviews:
            cur.execute(
                '''INSERT INTO reviews (product_id, text, rating, date, sentiment, score)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (product_id, r['text'], r.get('rating'), r.get('date'),
                 r['sentiment'], r['score'])
            )
        conn.commit()
        conn.close()

    def get_products(self):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute('SELECT * FROM products ORDER BY created_at DESC')
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows

    def get_reviews(self, product_id):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute('SELECT * FROM reviews WHERE product_id = ?', (product_id,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows
