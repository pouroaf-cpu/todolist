import json
from datetime import datetime


def safe_int(value, default=0):
    try:
        return int(float(value))
    except Exception:
        return default


def safe_date_sort_value(value):
    value = str(value or "").strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt)
        except Exception:
            continue
    return datetime.max


def format_due_date(value):
    value = str(value or "").strip()
    if not value:
        return "No date"
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            dt = datetime.strptime(value, fmt)
            try:
                return dt.strftime("%-d %b")
            except Exception:
                return dt.strftime("%d %b")
        except Exception:
            continue
    return value


def normalize_project_name(project):
    value = str(project or "").strip()
    return value if value else "General"


def get_project_names(tasks):
    names = {normalize_project_name(task.get("project", "")) for task in tasks or []}
    return sorted(names, key=lambda p: p.lower())


def filter_tasks_by_projects(tasks, visible_projects):
    visible = {normalize_project_name(p) for p in visible_projects or set()}
    return [task for task in tasks if normalize_project_name(task.get("project", "")) in visible]


def summarize_project_filter_state(all_projects, visible_projects):
    total = len(all_projects or [])
    visible = len(visible_projects or set())
    return f"{visible}/{total} visible"


def group_tasks_by_project(tasks):
    grouped = {}
    for task in tasks:
        project = normalize_project_name(task.get("project", ""))
        grouped.setdefault(project, []).append(task)
    return grouped


def project_colors(project):
    project = normalize_project_name(project).lower()

    palette = [
        ("#0ea5e9", "#0ea5e9", "#ffffff"),
        ("#84cc16", "#a3e635", "#1a1a1a"),
        ("#f472b6", "#f9a8d4", "#3a1028"),
        ("#22c55e", "#4ade80", "#062b14"),
        ("#a78bfa", "#c4b5fd", "#231942"),
        ("#f59e0b", "#fbbf24", "#3b2500"),
        ("#14b8a6", "#2dd4bf", "#042f2e"),
        ("#ef4444", "#fca5a5", "#3f1010"),
        ("#3b82f6", "#60a5fa", "#0b1f3a"),
        ("#f97316", "#fdba74", "#40210a"),
    ]

    idx = sum(ord(c) for c in project) % len(palette)
    return palette[idx]


def parse_tasks_from_response(data):
    if isinstance(data, list):
        return data
    if not isinstance(data, dict):
        return []
    for key in ("tasks", "items", "today", "data"):
        if isinstance(data.get(key), list):
            return data.get(key)
    return []


def normalize_task(item):
    if not isinstance(item, dict):
        return None

    task_id = item.get("id") or item.get("taskId") or item.get("ID") or f"tmp-{hash(json.dumps(item, sort_keys=True, default=str))}"
    name = item.get("name") or item.get("task") or item.get("title") or "Untitled Task"
    project = item.get("project") or item.get("category") or "General"
    priority = safe_int(item.get("priority"), 5)
    next_due = item.get("nextDue") or item.get("dueDate") or item.get("date") or ""
    notes = item.get("notes") or item.get("description") or ""
    url = item.get("url") or item.get("link") or ""
    duration = safe_int(item.get("duration"), 30) or 30
    preferred_window = str(item.get("preferredWindow") or "").strip()

    return {
        "id": str(task_id),
        "name": str(name),
        "project": str(project),
        "priority": priority,
        "nextDue": str(next_due),
        "notes": str(notes),
        "url": str(url),
        "duration": duration,
        "preferredWindow": preferred_window,
        "raw": item,
    }


def sort_tasks(tasks, sort_state):
    items = list(tasks)
    for rule in reversed(sort_state or []):
        kind = rule.get("type", "")
        settings = rule.get("settings", {})

        if kind == "Project":
            reverse = settings.get("order") == "Z-A"
            items.sort(key=lambda t: normalize_project_name(t.get("project", "")).lower(), reverse=reverse)
        elif kind == "Due Date":
            reverse = settings.get("order") == "Newest to oldest"
            items.sort(key=lambda t: safe_date_sort_value(t.get("nextDue")), reverse=reverse)
        elif kind == "Priority":
            highest_first = settings.get("order", "Highest to lowest") == "Highest to lowest"
            items.sort(key=lambda t: safe_int(t.get("priority"), 5), reverse=highest_first)

    return items