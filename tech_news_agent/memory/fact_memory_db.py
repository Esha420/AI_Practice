# memory/fact_memory_db.py
import sqlite3
import os
import time


class FactMemoryDB:
    def __init__(self, db_path="memory/facts.db", max_facts=200):
        self.db_path = db_path
        self.max_facts = max_facts

        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fact TEXT NOT NULL,
                evidence TEXT,
                timestamp REAL
            )
        """)

        conn.commit()
        conn.close()

    def save_fact(self, fact, evidence=""):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO facts (fact, evidence, timestamp)
            VALUES (?, ?, ?)
        """, (fact, evidence, time.time()))
        conn.commit()

        # Sliding window — keep last N facts
        cur.execute("""
            DELETE FROM facts
            WHERE id NOT IN (
                SELECT id FROM facts ORDER BY timestamp DESC LIMIT ?
            )
        """, (self.max_facts,))
        conn.commit()

        conn.close()

    def get_recent_facts(self, limit=20):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            SELECT fact FROM facts
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))

        rows = cur.fetchall()
        conn.close()

        return [r[0] for r in rows]
