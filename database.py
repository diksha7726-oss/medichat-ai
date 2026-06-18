import sqlite3

conn = sqlite3.connect("chat_history.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    answer TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

def save_chat(q, a):
    cursor.execute("INSERT INTO history (question, answer) VALUES (?, ?)", (q, a))
    conn.commit()

def get_history():
    cursor.execute("SELECT question, answer FROM history ORDER BY id DESC")
    return cursor.fetchall()

def get_query_count():
    cursor.execute("SELECT COUNT(*) FROM history")
    return cursor.fetchone()[0]
