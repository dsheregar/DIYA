"""The read/serve path for stored facts.

Backed by SQLite. Stores facts with provenance (source, timestamp,
confidence, refresh_by) and serves them on request. Does not fetch new
information itself — that's data_gathering's job; it pushes results in
here via add_fact().
"""
import sqlite3
import time
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "memory.sqlite3"

SCHEMA = """
CREATE TABLE IF NOT EXISTS facts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fact TEXT NOT NULL,
    source TEXT NOT NULL CHECK(source IN ('web', 'user_stated', 'agent_inferred')),
    source_detail TEXT,
    timestamp REAL NOT NULL,
    confidence TEXT NOT NULL CHECK(confidence IN ('high', 'medium', 'low')),
    refresh_by REAL
);
"""


class Memory:
    def __init__(self, db_path: Path = DB_PATH):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute(SCHEMA)
        self.conn.commit()

    def add_fact(self, fact: str, source: str, source_detail: str = "",
                 confidence: str = "medium", refresh_by: float | None = None) -> int:
        cur = self.conn.execute(
            "INSERT INTO facts (fact, source, source_detail, timestamp, confidence, refresh_by) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (fact, source, source_detail, time.time(), confidence, refresh_by),
        )
        self.conn.commit()
        return cur.lastrowid

    def query(self, text: str, limit: int = 10) -> list[dict]:
        """Substring search over stored facts. No embeddings yet — see docs/ROADMAP.md."""
        rows = self.conn.execute(
            "SELECT id, fact, source, source_detail, timestamp, confidence, refresh_by "
            "FROM facts WHERE fact LIKE ? ORDER BY timestamp DESC LIMIT ?",
            (f"%{text}%", limit),
        ).fetchall()
        cols = ["id", "fact", "source", "source_detail", "timestamp", "confidence", "refresh_by"]
        return [dict(zip(cols, row)) for row in rows]

    def is_stale(self, fact_row: dict) -> bool:
        refresh_by = fact_row.get("refresh_by")
        return refresh_by is not None and time.time() > refresh_by
