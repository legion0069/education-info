import sqlite3
import hashlib
from typing import Optional

DB_FILE = "alerts.db"

def init_db(db_path: str = DB_FILE):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sent_alerts (
            id TEXT PRIMARY KEY,
            category TEXT,
            title TEXT,
            url TEXT,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def is_already_sent(alert_id: str, db_path: str = DB_FILE) -> bool:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM sent_alerts WHERE id = ?", (alert_id,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def mark_as_sent(alert_id: str, category: str, title: str, url: str, db_path: str = DB_FILE):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO sent_alerts (id, category, title, url)
        VALUES (?, ?, ?, ?)
    """, (alert_id, category, title, url))
    conn.commit()
    conn.close()

def compute_alert_hash(*keys: str) -> str:
    combined = "|".join(k.strip().lower() for k in keys if k)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()[:16]
