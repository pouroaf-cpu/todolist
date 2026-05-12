import json
import threading

import requests

from logic.config import BASE_URL
from logic.task_utils import normalize_task, parse_tasks_from_response, safe_int


def load_tasks_async(app, silent=False):
    if app.loading:
        return

    app.loading = True
    app.refresh_btn.configure(state="disabled")

    if not silent:
        app.show_loading_overlay("Loading Tasks")

    def worker():
        try:
            response = requests.get(BASE_URL, params={"view": "today"}, timeout=20)
            raw = response.text.strip()

            try:
                data = response.json()
            except Exception:
                data = json.loads(raw)

            tasks = [normalize_task(item) for item in parse_tasks_from_response(data)]
            tasks = [task for task in tasks if task]
            metrics = data.get("metrics") if isinstance(data, dict) else None

            app.after(0, lambda tasks=tasks, metrics=metrics: app.on_tasks_loaded(tasks, metrics))

        except Exception as e:
            err = str(e)
            app.after(0, lambda err=err: app.on_tasks_error(err))

    threading.Thread(target=worker, daemon=True).start()


def complete_task_async(app, task_id):
    task = next((t for t in app.tasks if str(t.get("id", "")) == str(task_id)), None)
    if not task:
        return

    def worker():
        try:
            response = requests.post(
                BASE_URL,
                json={"action": "completeTask", "taskId": task_id},
                timeout=20,
            )
            response.raise_for_status()
            app.after(0, lambda task_id=task_id: app.on_task_completed_confirmed(task_id))
        except Exception as e:
            err = str(e)
            app.after(0, lambda task_id=task_id, err=err: app.on_task_completed_failed(task_id, err))

    threading.Thread(target=worker, daemon=True).start()


def add_task_async(app, payload):
    def worker():
        try:
            requests.post(BASE_URL, json={"action": "addTask", **payload}, timeout=20)
            app.after(0, app.on_task_added)
        except Exception as e:
            err = str(e)
            app.after(
                0,
                lambda err=err: app.add_status_label.configure(
                    text=f"Add failed: {err}",
                    text_color="#ff7a7a",
                ),
            )

    threading.Thread(target=worker, daemon=True).start()


def update_task_async(app, payload):
    def worker():
        try:
            requests.post(BASE_URL, json={"action": "updateTask", **payload}, timeout=20)
            app.after(0, lambda payload=payload: app.on_task_saved(payload))
        except Exception as e:
            err = str(e)
            app.after(
                0,
                lambda err=err: app.edit_info_label.configure(
                    text=f"Save failed: {err}",
                    text_color="#ff7a7a",
                ),
            )

    threading.Thread(target=worker, daemon=True).start()


def apply_remote_or_local_metrics(app, metrics=None):
    if isinstance(metrics, dict):
        app.metrics["completedToday"] = safe_int(metrics.get("completedToday"), 0)
        app.metrics["totalToday"] = safe_int(
            metrics.get("totalToday"),
            len(app.tasks) + len(app.completed_today_tasks),
        )
        app.metrics["remainingToday"] = safe_int(
            metrics.get("remainingToday"),
            len(app.tasks),
        )
        app.metrics["percent"] = safe_int(metrics.get("percent"), 0)
        return

    completed = len(app.completed_today_tasks)
    total = completed + len(app.tasks)
    remaining = len(app.tasks)

    app.metrics["completedToday"] = completed
    app.metrics["totalToday"] = total
    app.metrics["remainingToday"] = remaining
    app.metrics["percent"] = 0 if total == 0 else int(round((completed / total) * 100))