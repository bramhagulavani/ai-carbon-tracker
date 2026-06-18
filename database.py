import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "carbon_tracker.db")

def init_db():
    """Create the queries table if it doesn't exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp       TEXT NOT NULL,
            model           TEXT NOT NULL,
            prompt          TEXT NOT NULL,
            tokens_generated INTEGER,
            tokens_prompt   INTEGER,
            wall_time_s     REAL,
            tokens_per_sec  REAL,
            avg_watts       REAL,
            peak_watts      REAL,
            watt_hours      REAL,
            co2_local_g     REAL,
            co2_gpt4o_g     REAL,
            co2_claude_g    REAL,
            co2_gemini_g    REAL,
            co2_saved_g     REAL,
            response_preview TEXT
        )
    """)
    conn.commit()
    conn.close()
    print(f"✅ Database ready at: {DB_PATH}")


def log_query(data: dict):
    """Save a completed query result to the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO queries (
            timestamp, model, prompt,
            tokens_generated, tokens_prompt,
            wall_time_s, tokens_per_sec,
            avg_watts, peak_watts, watt_hours,
            co2_local_g, co2_gpt4o_g, co2_claude_g, co2_gemini_g,
            co2_saved_g, response_preview
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        data.get("model"),
        data.get("prompt"),
        data.get("tokens"),
        data.get("tokens_prompt", 0),
        data.get("wall_time_s"),
        data.get("tokens_per_sec", 0),
        data.get("avg_watts"),
        data.get("peak_watts"),
        data.get("watt_hours"),
        data.get("co2_local_g"),
        data.get("co2_gpt4o_g"),
        data.get("co2_claude_g", 0),
        data.get("co2_gemini_g", 0),
        data.get("co2_saved_g"),
        data.get("response", "")[:300]
    ))
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def get_all_queries():
    """Fetch every logged query — used by the dashboard later"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM queries ORDER BY timestamp DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def get_session_stats():
    """Lifetime totals — for the dashboard summary cards"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(*)            AS total_queries,
            SUM(tokens_generated) AS total_tokens,
            ROUND(SUM(co2_local_g), 4)  AS total_co2_local,
            ROUND(SUM(co2_saved_g), 4)  AS total_co2_saved,
            ROUND(AVG(avg_watts), 2)     AS avg_watts,
            ROUND(AVG(tokens_per_sec),1) AS avg_tokens_per_sec
        FROM queries
    """)
    row = cursor.fetchone()
    conn.close()
    return {
        "total_queries":     row[0] or 0,
        "total_tokens":      row[1] or 0,
        "total_co2_local":   row[2] or 0,
        "total_co2_saved":   row[3] or 0,
        "avg_watts":         row[4] or 0,
        "avg_tokens_per_sec": row[5] or 0
    }


# ── TEST IT ──────────────────────────────────────────
if __name__ == "__main__":
    init_db()

    # Insert a sample row to verify it works
    test_data = {
        "model": "deepseek-r1:1.5b",
        "prompt": "What is AI?",
        "tokens": 361,
        "tokens_prompt": 14,
        "wall_time_s": 5.69,
        "tokens_per_sec": 63.4,
        "avg_watts": 23.06,
        "peak_watts": 64.11,
        "watt_hours": 0.032029,
        "co2_local_g": 0.0263,
        "co2_gpt4o_g": 1.7689,
        "co2_claude_g": 1.4801,
        "co2_gemini_g": 1.3718,
        "co2_saved_g": 1.3455,
        "response": "Artificial intelligence is a branch of technology..."
    }

    row_id = log_query(test_data)
    print(f"✅ Test query saved with ID: {row_id}")

    stats = get_session_stats()
    print(f"\n📊 Lifetime stats:")
    for key, val in stats.items():
        print(f"  {key:<22}: {val}")