import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parents[1] / "todo.db"
INSERT_TASK = "INSERT INTO tasks (task, category, due_date) VALUES (?, ?, ?)"


class DBHelper:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        try:
            self.create_table()
        except sqlite3.Error:
            self.close()
            raise

    def create_table(self):
        with self.conn:
            # 在同一事务中检查和升级旧表。
            self.conn.execute("BEGIN IMMEDIATE")
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task TEXT NOT NULL,
                    category TEXT,
                    due_date TEXT
                )
            """)
            columns = {row[1] for row in self.conn.execute("PRAGMA table_info(tasks)")}
            if "due_date" not in columns:
                self.conn.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT")

    def add_task(self, task, category, due_date):
        with self.conn:
            cursor = self.conn.execute(INSERT_TASK, (task, category, due_date))
        return cursor.lastrowid

    def add_tasks(self, tasks):
        with self.conn:
            self.conn.executemany(INSERT_TASK, tasks)

    def get_all_tasks(self):
        sql = "SELECT id, task, category, due_date FROM tasks"
        return self.conn.execute(sql).fetchall()

    def delete_task(self, task_id):
        with self.conn:
            self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    def close(self):
        self.conn.close()
