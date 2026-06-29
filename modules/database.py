import sqlite3
import os
from datetime import datetime

DB_PATH = "database/legalmind.db"


def init_db():
    os.makedirs("database", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            contract_type TEXT,
            risk_level TEXT,
            risk_score INTEGER,
            status TEXT DEFAULT 'Pending',
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def register_user(email, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        conn.close()
        return True
    except:
        return False


def login_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
    user = cur.fetchone()
    conn.close()
    return user is not None


def save_history(email, contract_type, risk_level, risk_score):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO history 
        (email, contract_type, risk_level, risk_score, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        email,
        contract_type,
        risk_level,
        risk_score,
        "Pending",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()


def get_history(email):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, contract_type, risk_level, risk_score, status, created_at
        FROM history
        WHERE email=?
        ORDER BY id DESC
    """, (email,))
    rows = cur.fetchall()
    conn.close()
    return rows


def get_all_history():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, email, contract_type, risk_level, risk_score, status, created_at
        FROM history
        ORDER BY id DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows


def update_status(record_id, status):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE history SET status=? WHERE id=?",
        (status, record_id)
    )
    conn.commit()
    conn.close()