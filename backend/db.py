"""
SQLite access for MSME360.

Every function opens a short-lived connection and closes it under try/finally
so an exception between execute() and close() cannot leak the handle. WAL mode
is enabled once at init so concurrent readers don't block writers under
uvicorn's threadpool.

Foreign keys are declared but not enforced at the schema level yet because
`custom_businesses` is populated *after* an `officer_decisions` row can already
exist for the same id via IDOR — we handle that at the API layer instead.
"""

import contextlib
import sqlite3
import json
import os
import uuid
from datetime import datetime, timezone

DB_PATH = os.environ.get("MSME_DB_PATH") or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "msme_workspace.db"
)


@contextlib.contextmanager
def _cursor():
    """Yield a cursor, commit on clean exit, rollback + re-raise otherwise."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        # PRAGMAs must be issued per connection.
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        cur = conn.cursor()
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_db_connection():
    """Legacy accessor used by main.py routes. Prefer `_cursor()` in new code.

    Callers MUST close the connection in a finally block; earlier code relied
    on GC to eventually close, which under FastAPI's threadpool caused
    `database is locked` errors.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    with _cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS officer_decisions (
                business_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                remarks TEXT,
                updated_at TEXT NOT NULL
            )
            """
        )
        cur.execute(
            """
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
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS custom_businesses (
                business_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                industry TEXT NOT NULL,
                score INTEGER NOT NULL,
                band TEXT NOT NULL,
                applied_at TEXT NOT NULL,
                data_json TEXT NOT NULL
            )
            """
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_audit_events_ts ON audit_events (ts DESC)"
        )
        cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_audit_events_business_id ON audit_events (business_id)"
        )

        cur.execute("SELECT COUNT(*) FROM audit_events")
        if cur.fetchone()[0] == 0:
            now = datetime.now(timezone.utc).isoformat()
            seed_events = [
                (
                    "evt-seed-1", now, "intake", "MSME007", "Shree Industries",
                    "Credit Officer (demo)",
                    "Documents verified — bank statement (12 mo) + GST summary. Readiness: green.",
                    "{}",
                ),
                (
                    "evt-seed-2", now, "score", "MSME007", "Shree Industries",
                    "Analyst Agent",
                    "Financial health score computed from verified bank + GST data.",
                    "{}",
                ),
            ]
            cur.executemany(
                "INSERT INTO audit_events VALUES (?, ?, ?, ?, ?, ?, ?, ?)", seed_events
            )


def add_audit_event(event_type, business_id, business_name, summary, payload=None, actor="Credit Officer (demo)"):
    evt_id = f"evt-{uuid.uuid4().hex}"
    ts = datetime.now(timezone.utc).isoformat()
    payload_str = json.dumps(payload) if payload else "{}"
    with _cursor() as cur:
        cur.execute(
            "INSERT INTO audit_events VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (evt_id, ts, event_type, business_id, business_name, actor, summary, payload_str),
        )


def get_audit_events():
    with _cursor() as cur:
        cur.execute("SELECT * FROM audit_events ORDER BY ts DESC")
        rows = cur.fetchall()
    return [dict(row) for row in rows]


def add_custom_business(business_id, name, industry, score, band, data_json):
    applied_at = datetime.now(timezone.utc).isoformat()
    with _cursor() as cur:
        cur.execute(
            "INSERT OR REPLACE INTO custom_businesses VALUES (?, ?, ?, ?, ?, ?, ?)",
            (business_id, name, industry, score, band, applied_at, data_json),
        )


def get_custom_businesses():
    with _cursor() as cur:
        cur.execute("SELECT * FROM custom_businesses")
        rows = cur.fetchall()
    return [dict(row) for row in rows]


def get_custom_business_detail(business_id):
    with _cursor() as cur:
        cur.execute("SELECT * FROM custom_businesses WHERE business_id = ?", (business_id,))
        row = cur.fetchone()
    return dict(row) if row else None
