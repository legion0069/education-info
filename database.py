import os
import sqlite3
import hashlib
from typing import Optional
from config import DATABASE_URL

USE_POSTGRES = bool(DATABASE_URL and DATABASE_URL.startswith("postgres"))

if USE_POSTGRES:
    import psycopg2

def get_connection():
    if USE_POSTGRES:
        # Connect to Cloud PostgreSQL (Neon)
        return psycopg2.connect(DATABASE_URL)
    else:
        # Fallback to local SQLite
        return sqlite3.connect("alerts.db")

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    if USE_POSTGRES:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sent_alerts (
                id TEXT PRIMARY KEY,
                category TEXT,
                title TEXT,
                url TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    else:
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

def is_already_sent(alert_id: str) -> bool:
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if USE_POSTGRES:
            cursor.execute("SELECT 1 FROM sent_alerts WHERE id = %s", (alert_id,))
        else:
            cursor.execute("SELECT 1 FROM sent_alerts WHERE id = ?", (alert_id,))
        row = cursor.fetchone()
        conn.close()
        return row is not None
    except Exception as e:
        print(f"[DB Error in is_already_sent] {e}")
        return False

def mark_as_sent(alert_id: str, category: str, title: str, url: str):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        if USE_POSTGRES:
            cursor.execute("""
                INSERT INTO sent_alerts (id, category, title, url)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET category = EXCLUDED.category
            """, (alert_id, category, title, url))
        else:
            cursor.execute("""
                INSERT OR REPLACE INTO sent_alerts (id, category, title, url)
                VALUES (?, ?, ?, ?)
            """, (alert_id, category, title, url))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB Error in mark_as_sent] {e}")

def compute_alert_hash(*keys: str) -> str:
    combined = "|".join(k.strip().lower() for k in keys if k)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()[:16]

if __name__ == "__main__":
    init_db()
    print(f"Database initialized successfully! Using: {'Cloud PostgreSQL (Neon)' if USE_POSTGRES else 'Local SQLite'}")
    test_id = "test_persistence_123"
    mark_as_sent(test_id, "test", "Test Opening", "https://example.com")
    print(f"Is test alert marked? {is_already_sent(test_id)}")
