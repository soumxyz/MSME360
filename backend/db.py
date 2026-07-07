import sqlite3
import json
import os
import uuid
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "msme_workspace.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Decisions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS officer_decisions (
            business_id TEXT PRIMARY KEY,
            status TEXT NOT NULL,
            remarks TEXT,
            updated_at TEXT NOT NULL
        )
    """)
    # Audit events table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_events (
            id TEXT PRIMARY KEY,
            ts TEXT NOT NULL,
            type TEXT NOT NULL,
            business_id TEXT NOT NULL,
            business_name TEXT NOT NULL,
            actor TEXT NOT NULL,
            summary TEXT NOT NULL,
            payload TEXT
        )
    """)
    # Custom registered businesses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS custom_businesses (
            business_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            industry TEXT NOT NULL,
            score INTEGER NOT NULL,
            band TEXT NOT NULL,
            applied_at TEXT NOT NULL,
            data_json TEXT NOT NULL
        )
    """)
    # Optimize query performance with indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_events_ts ON audit_events (ts DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_events_business_id ON audit_events (business_id)")
    conn.commit()
    
    # Seed first default events if empty
    cursor.execute("SELECT COUNT(*) FROM audit_events")
    if cursor.fetchone()[0] == 0:
        seed_events = [
            ("evt-seed-1", datetime.now(timezone.utc).isoformat(), "intake", "MSME007", "Shree Industries", "Credit Officer (demo)", "Documents verified — bank statement (12 mo) + GST summary. Readiness: green.", "{}"),
            ("evt-seed-2", datetime.now(timezone.utc).isoformat(), "score", "MSME007", "Shree Industries", "Analyst Agent", "Financial health score computed from verified bank + GST data.", "{}")
        ]
        cursor.executemany("INSERT INTO audit_events VALUES (?, ?, ?, ?, ?, ?, ?, ?)", seed_events)
        conn.commit()
    conn.close()

def add_audit_event(event_type, business_id, business_name, summary, payload=None, actor="Credit Officer (demo)"):
    conn = get_db_connection()
    cursor = conn.cursor()
    evt_id = f"evt-{uuid.uuid4().hex}"
    ts = datetime.now(timezone.utc).isoformat()
    payload_str = json.dumps(payload) if payload else "{}"
    cursor.execute(
        "INSERT INTO audit_events VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (evt_id, ts, event_type, business_id, business_name, actor, summary, payload_str)
    )
    conn.commit()
    conn.close()

def get_audit_events():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_events ORDER BY ts DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_custom_business(business_id, name, industry, score, band, data_json):
    conn = get_db_connection()
    cursor = conn.cursor()
    applied_at = datetime.now(timezone.utc).isoformat()
    cursor.execute(
        "INSERT OR REPLACE INTO custom_businesses VALUES (?, ?, ?, ?, ?, ?, ?)",
        (business_id, name, industry, score, band, applied_at, data_json)
    )
    conn.commit()
    conn.close()

def get_custom_businesses():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM custom_businesses")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_custom_business_detail(business_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM custom_businesses WHERE business_id = ?", (business_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None
