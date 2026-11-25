import csv
from contextlib import closing

from database.db_helper import DBHelper, DB_PATH


CSV_PATH = DB_PATH.with_name("tasks_export.csv")
CSV_COLUMNS = ("任务内容", "分类", "截止时间")


def export_tasks(filename=CSV_PATH):
    with closing(DBHelper()) as db:
        tasks = db.get_all_tasks()
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_COLUMNS)
        for _, task, category, due_date in tasks:
            writer.writerow([task, category, due_date])


def import_tasks(filename=CSV_PATH):
    with open(filename, mode="r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, strict=True)
        if not reader.fieldnames or "任务内容" not in reader.fieldnames:
            raise ValueError("CSV 缺少“任务内容”列。")
        tasks = [
            (row["任务内容"], row.get("分类", ""), row.get("截止时间", ""))
            for row in reader
            if row["任务内容"]
        ]
    if tasks:
        with closing(DBHelper()) as db:
            db.add_tasks(tasks)
    return len(tasks)
