# database.py
import os
import sqlite3
from pathlib import Path

# optional postgres driver
try:
    import psycopg2
    import psycopg2.extras
except Exception:
    psycopg2 = None

DB_PATH = Path("students.db")

def get_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL and psycopg2:
        # connect to Postgres; override .cursor to return RealDictCursor by default
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        def cursor(*args, **kwargs):
            return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        conn.cursor = cursor
        return conn
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    DATABASE_URL = os.getenv("DATABASE_URL")
    if DATABASE_URL and psycopg2:
        # Postgres syntax
        cur.execute("""
            CREATE TABLE IF NOT EXISTS students (
                roll_number TEXT PRIMARY KEY,
                name TEXT NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS grades (
                id SERIAL PRIMARY KEY,
                roll_number TEXT NOT NULL,
                subject TEXT NOT NULL,
                grade INTEGER NOT NULL CHECK (grade BETWEEN 0 AND 100),
                UNIQUE (roll_number, subject),
                FOREIGN KEY (roll_number) REFERENCES students(roll_number) ON DELETE CASCADE
            );
        """)
    else:
        # SQLite syntax
        cur.execute("""
            CREATE TABLE IF NOT EXISTS students (
                roll_number TEXT PRIMARY KEY,
                name TEXT NOT NULL
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_number TEXT NOT NULL,
                subject TEXT NOT NULL,
                grade INTEGER NOT NULL CHECK(grade BETWEEN 0 AND 100),
                UNIQUE (roll_number, subject),
                FOREIGN KEY (roll_number) REFERENCES students(roll_number) ON DELETE CASCADE
            );
        """)
    conn.commit()
    conn.close()