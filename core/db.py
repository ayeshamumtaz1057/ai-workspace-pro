"""SQLite persistence: chat history, activity stats, settings, planner tasks."""
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module TEXT NOT NULL,
    title  TEXT NOT NULL,
    role   TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS stats (
    key TEXT PRIMARY KEY,
    value INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    subject TEXT,
    due TEXT,
    minutes INTEGER DEFAULT 30,
    done INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);
"""

DEFAULT_STATS = ["chats", "files_analyzed", "pdfs_processed", "reports_exported"]


@contextmanager
def conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    finally:
        c.close()


def init_db() -> None:
    with conn() as c:
        c.executescript(SCHEMA)
        for k in DEFAULT_STATS:
            c.execute("INSERT OR IGNORE INTO stats(key,value) VALUES(?,0)", (k,))


# ---- stats ---------------------------------------------------------------
def bump(key: str, amount: int = 1) -> None:
    with conn() as c:
        c.execute("INSERT OR IGNORE INTO stats(key,value) VALUES(?,0)", (key,))
        c.execute("UPDATE stats SET value = value + ? WHERE key = ?", (amount, key))


def get_stats() -> dict:
    with conn() as c:
        return {r["key"]: r["value"] for r in c.execute("SELECT * FROM stats")}


# ---- chat log ------------------------------------------------------------
def log_message(module: str, title: str, role: str, content: str) -> None:
    with conn() as c:
        c.execute(
            "INSERT INTO chats(module,title,role,content,created_at) VALUES(?,?,?,?,?)",
            (module, title[:80], role, content, datetime.utcnow().isoformat(timespec="seconds")),
        )


def recent_chats(limit: int = 6) -> list:
    with conn() as c:
        rows = c.execute(
            """SELECT module, title, MAX(created_at) AS ts FROM chats
               WHERE role='user' GROUP BY module, title
               ORDER BY ts DESC LIMIT ?""", (limit,)).fetchall()
    return [dict(r) for r in rows]


def clear_history() -> None:
    with conn() as c:
        c.execute("DELETE FROM chats")


# ---- settings ------------------------------------------------------------
def set_setting(key: str, value: str) -> None:
    with conn() as c:
        c.execute("INSERT INTO settings(key,value) VALUES(?,?) "
                  "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, str(value)))


def get_setting(key: str, default=None):
    with conn() as c:
        r = c.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return r["value"] if r else default


# ---- planner -------------------------------------------------------------
def add_task(title: str, subject: str, due: str, minutes: int) -> None:
    with conn() as c:
        c.execute("INSERT INTO tasks(title,subject,due,minutes,done,created_at) "
                  "VALUES(?,?,?,?,0,?)",
                  (title, subject, due, minutes, datetime.utcnow().isoformat(timespec="seconds")))


def list_tasks() -> list:
    with conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT * FROM tasks ORDER BY done, due")]


def toggle_task(task_id: int, done: bool) -> None:
    with conn() as c:
        c.execute("UPDATE tasks SET done=? WHERE id=?", (int(done), task_id))


def delete_task(task_id: int) -> None:
    with conn() as c:
        c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
