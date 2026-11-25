# 智能待办事项系统

SmartTodoReminder 是一个 Python 桌面待办工具。使用 Tkinter 展示任务，使用 SQLite 在本地保存任务，支持到期弹窗、CSV 导入导出和天气预报展示。

## 安装与运行

准备带有 Tkinter 的 Python。本项目在 Windows 上使用 Python 3.12 验证。

```powershell
git clone https://github.com/Oumatsu/SmartTodoReminder.git
cd SmartTodoReminder
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

首次运行会在项目目录创建 `todo.db`。如果 Tkinter 无法导入，请检查 Python 安装中是否包含 Tcl/Tk。

## 使用方法

- 填写任务内容后点击 **添加任务**。分类和截止时间可选。截止时间使用本地时间，格式为 `YYYY-MM-DD HH:MM`，例如 `2026-12-01 18:30`。
- 在列表中选中一项或多项任务，点击 **删除选中任务**。
- 程序运行期间每隔约 30 秒检查截止时间。同一任务在一次运行中最多提醒一次，重启后仍会检查已到期的任务。
- 通过 **文件 → 导出任务** 将当前列表写入项目目录下的 `tasks_export.csv`。**导入任务**从同一文件追加任务，重复导入会产生重复记录。CSV 表头为 `任务内容,分类,截止时间`。
- 窗口顶部显示天气预报，启动后自动查询并每小时刷新。天气查询需要联网，通过 IP 地址估算所在城市。

备份任务数据时，可以退出程序后复制 `todo.db`。

## 代码结构

| 路径 | 用途 |
| --- | --- |
| `main.py` | 程序入口 |
| `gui/main_window.py` | 桌面界面与交互 |
| `database/db_helper.py` | SQLite 建表与任务读写 |
| `fileops/file_manager.py` | CSV 导入和导出 |
| `reminder/reminder_thread.py` | 后台到期检查 |
| `network/weather_manager.py` | 城市定位和天气查询 |
