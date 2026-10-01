import sqlite3

with sqlite3.connect("database.db") as conn:
    cursor = conn.cursor() 

cursor.execute('''
    CREATE TABLE IF NOT EXISTS prompts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        version TEXT NOT NULL,
        template_text TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

cursor.execute('''
          CREATE TABLE IF NOT EXISTS api_logs (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
              requested_model TEXT NOT NULL,
              actual_model_used TEXT NOT NULL,
              prompt_tokens INTEGER NOT NULL,
              completion_tokens INTEGER NOT NULL,
              latency_ms REAL NOT NULL,
              status_code INTEGER NOT NULL
          );
''')

conn.commit()

print("Database initialized: prompts, api_logs tables ready.")