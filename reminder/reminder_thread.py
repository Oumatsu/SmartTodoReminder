import threading
from contextlib import closing
from datetime import datetime

from database.db_helper import DBHelper


DUE_DATE_FORMAT = "%Y-%m-%d %H:%M"


class ReminderThread(threading.Thread):
    def __init__(self, reminders):
        super().__init__(daemon=True)
        self.reminders = reminders
        self.stop_event = threading.Event()

    def run(self):
        checked = set()
        # SQLite 连接由使用它的线程创建和关闭。
        with closing(DBHelper()) as db:
            while not self.stop_event.is_set():
                for task_id, task, category, due_date in db.get_all_tasks():
                    if not due_date or task_id in checked:
                        continue
                    try:
                        target_time = datetime.strptime(due_date, DUE_DATE_FORMAT)
                    except (TypeError, ValueError):
                        continue
                    if datetime.now() >= target_time:
                        checked.add(task_id)
                        self.reminders.put((task, category, due_date))
                self.stop_event.wait(30)

    def stop(self):
        self.stop_event.set()
