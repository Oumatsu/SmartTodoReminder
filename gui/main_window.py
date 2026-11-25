import tkinter as tk
from csv import Error as CSVError
from datetime import datetime
from queue import Empty, SimpleQueue
from sqlite3 import Error as DatabaseError
from threading import Thread
from tkinter import messagebox, ttk

from database.db_helper import DBHelper
from fileops import file_manager as fm
from network.weather_manager import get_user_city, get_weather
from reminder.reminder_thread import DUE_DATE_FORMAT, ReminderThread


class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("智能待办事项系统")
        self.root.geometry("700x500")
        self.weather_label = tk.Label(self.root, text="正在获取天气…", font=("宋体", 12))
        self.weather_label.pack(pady=5)
        self.db = DBHelper()
        self.create_menu()
        self.create_widgets()

        self.closing = False
        self.weather_results = SimpleQueue()
        self.reminders = SimpleQueue()
        self.reminder = ReminderThread(self.reminders)
        self.reminder.start()
        self.weather_job = self.root.after_idle(self.auto_refresh_weather)
        self.background_job = self.root.after(100, self.process_background_updates)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="导出任务", command=self.export_tasks)
        file_menu.add_command(label="导入任务", command=self.import_tasks)
        menubar.add_cascade(label="文件", menu=file_menu)
        self.root.config(menu=menubar)

    def create_widgets(self):
        # ----- 上方输入区域 -----
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)

        # 任务内容输入框
        tk.Label(input_frame, text="任务内容：").grid(row=0, column=0)
        self.task_entry = tk.Entry(input_frame, width=30)
        self.task_entry.grid(row=0, column=1, padx=5)

        # 分类输入（后续可以改成下拉框）
        tk.Label(input_frame, text="分类：").grid(row=0, column=2)
        self.category_entry = tk.Entry(input_frame, width=15)
        self.category_entry.grid(row=0, column=3, padx=5)

        # 任务截止时间输入框
        tk.Label(input_frame, text="截止时间：").grid(row=0, column=4)
        self.due_entry = tk.Entry(input_frame, width=15)
        self.due_entry.grid(row=0, column=5, padx=5)

        # 添加按钮
        add_button = tk.Button(input_frame, text="添加任务", command=self.add_task)
        add_button.grid(row=0, column=6, padx=10)

        # ----- 中部 Treeview 表格 -----
        columns = ("任务内容", "分类", "截止时间")  # 新增列
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=15)
        self.tree.heading("任务内容", text="任务内容")
        self.tree.heading("分类", text="分类")
        self.tree.heading("截止时间", text="截止时间")  # 新增列
        self.tree.pack(fill="both", expand=True, pady=10)

        # 删除按钮
        delete_button = tk.Button(self.root, text="删除选中任务", command=self.delete_task)
        delete_button.pack(pady=5)

        self.load_tasks_from_db()

    # ---------------- 功能函数 ----------------
    def add_task(self):
        task = self.task_entry.get().strip()
        category = self.category_entry.get().strip()
        due_date = self.due_entry.get().strip()
        if not task:
            return
        if due_date:
            try:
                datetime.strptime(due_date, DUE_DATE_FORMAT)
            except ValueError:
                messagebox.showwarning("截止时间无效", "请输入 YYYY-MM-DD HH:MM，例如 2026-12-01 18:30。")
                self.due_entry.focus_set()
                return

        task_id = self.db.add_task(task, category, due_date)
        self.tree.insert("", "end", iid=str(task_id), values=(task, category, due_date))
        self.task_entry.delete(0, "end")
        self.category_entry.delete(0, "end")
        self.due_entry.delete(0, "end")

    def load_tasks_from_db(self):
        for task_id, task, category, due_date in self.db.get_all_tasks():
            self.tree.insert("", "end", iid=str(task_id), values=(task, category, due_date))

    def delete_task(self):
        selected = self.tree.selection()
        for item in selected:
            task_id = int(item)

            # 删除数据库记录
            self.db.delete_task(task_id)

            # 删除 GUI 显示行
            self.tree.delete(item)

    # 导出任务
    def export_tasks(self):
        try:
            fm.export_tasks()
        except (OSError, CSVError, DatabaseError) as error:
            messagebox.showerror("导出失败", str(error))
            return
        messagebox.showinfo("导出成功", "任务列表已导出到 tasks_export.csv")

    # 导入任务
    def import_tasks(self):
        try:
            imported = fm.import_tasks()
        except (OSError, CSVError, DatabaseError, ValueError) as error:
            messagebox.showerror("导入失败", str(error))
            return
        self.tree.delete(*self.tree.get_children())
        self.load_tasks_from_db()
        messagebox.showinfo("导入完成", f"已从 tasks_export.csv 导入 {imported} 条任务。")

    def on_closing(self):
        self.closing = True
        self.root.after_cancel(self.weather_job)
        self.root.after_cancel(self.background_job)
        self.reminder.stop()
        self.db.close()
        self.root.destroy()

    @staticmethod
    def load_weather(results):
        results.put(get_weather(get_user_city()))

    def auto_refresh_weather(self):
        Thread(target=self.load_weather, args=(self.weather_results,), daemon=True).start()
        self.weather_job = self.root.after(3600 * 1000, self.auto_refresh_weather)

    def process_background_updates(self):
        try:
            weather = self.weather_results.get_nowait()
        except Empty:
            pass
        else:
            self.weather_label.config(text=weather)

        try:
            task, category, due_date = self.reminders.get_nowait()
        except Empty:
            pass
        else:
            messagebox.showinfo(
                "任务提醒",
                f"任务：{task}\n分类：{category}\n截止时间已到：{due_date}",
            )

        if not self.closing:
            self.background_job = self.root.after(100, self.process_background_updates)

    def run(self):
        self.root.mainloop()
