import customtkinter as ctk

from logic.api import update_task_async
from logic.task_utils import format_due_date, normalize_project_name, safe_int, sort_tasks
from ui.components.forms import make_entry, make_option_menu, make_textbox
from ui.styles import COLORS, font


def build_task_editor_tab(app):
    app.task_editor_tab = ctk.CTkFrame(app.tab_content, fg_color="transparent")
    app.task_editor_tab.grid(row=0, column=0, sticky="nsew")
    app.task_editor_tab.grid_columnconfigure(0, weight=1)
    app.task_editor_tab.grid_columnconfigure(1, weight=0)
    app.task_editor_tab.grid_rowconfigure(0, weight=1)

    editor_left = ctk.CTkFrame(app.task_editor_tab, fg_color=COLORS["header_bg"], corner_radius=14, border_width=1, border_color=COLORS["border_soft"])
    editor_left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
    editor_left.grid_columnconfigure(0, weight=1)
    editor_left.grid_rowconfigure(1, weight=1)

    editor_header = ctk.CTkFrame(editor_left, fg_color="transparent")
    editor_header.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 10))
    editor_header.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(editor_header, text="Task Editor", font=font(24, "bold"), text_color=COLORS["text_primary"]).grid(row=0, column=0, sticky="w")
    ctk.CTkLabel(editor_header, text="Edit tasks from the current loaded list", font=font(12), text_color=COLORS["text_muted"]).grid(row=1, column=0, sticky="w", pady=(4, 0))

    app.task_editor_list = ctk.CTkScrollableFrame(editor_left, fg_color=COLORS["section_bg"], corner_radius=12, border_width=1, border_color=COLORS["border"], scrollbar_button_color=COLORS["scroll_btn"], scrollbar_button_hover_color=COLORS["scroll_btn_hover"])
    app.task_editor_list.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 14))

    editor_right = ctk.CTkFrame(app.task_editor_tab, fg_color=COLORS["header_bg"], corner_radius=14, border_width=1, border_color=COLORS["border_soft"], width=360)
    editor_right.grid(row=0, column=1, sticky="ns")
    editor_right.grid_propagate(False)
    editor_right.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(editor_right, text="Edit Task", font=font(20, "bold"), text_color=COLORS["text_primary"]).grid(row=0, column=0, sticky="w", padx=16, pady=(16, 6))

    def edit_label(text, row):
        ctk.CTkLabel(editor_right, text=text, font=font(11, "bold"), text_color=COLORS["text_soft"]).grid(row=row, column=0, sticky="w", padx=16, pady=(12, 6))

    edit_label("Task Name", 1)
    app.edit_name_entry = make_entry(editor_right)
    app.edit_name_entry.grid(row=2, column=0, sticky="ew", padx=16)

    edit_label("Project", 3)
    app.edit_project_entry = make_entry(editor_right)
    app.edit_project_entry.grid(row=4, column=0, sticky="ew", padx=16)

    edit_label("Priority", 5)
    app.edit_priority_menu = make_option_menu(editor_right, [str(i) for i in range(1, 11)])
    app.edit_priority_menu.grid(row=6, column=0, sticky="ew", padx=16)
    app.edit_priority_menu.set("5")

    edit_label("Due Date", 7)
    app.edit_due_entry = make_entry(editor_right, "YYYY-MM-DD")
    app.edit_due_entry.grid(row=8, column=0, sticky="ew", padx=16)

    edit_label("Notes", 9)
    app.edit_notes_entry = make_textbox(editor_right, 110)
    app.edit_notes_entry.grid(row=10, column=0, sticky="ew", padx=16)

    edit_label("URL", 11)
    app.edit_url_entry = make_entry(editor_right)
    app.edit_url_entry.grid(row=12, column=0, sticky="ew", padx=16)

    app.edit_info_label = ctk.CTkLabel(editor_right, text="No task selected", font=font(10), text_color=COLORS["text_secondary"])
    app.edit_info_label.grid(row=13, column=0, sticky="w", padx=16, pady=(12, 6))

    actions = ctk.CTkFrame(editor_right, fg_color="transparent")
    actions.grid(row=14, column=0, sticky="ew", padx=16, pady=(6, 16))
    actions.grid_columnconfigure((0, 1), weight=1)

    app.edit_save_btn = ctk.CTkButton(actions, text="Save Changes", height=36, corner_radius=10, fg_color="#1faa59", hover_color="#168648", command=app.save_task_edit)
    app.edit_save_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))
    app.edit_reset_btn = ctk.CTkButton(actions, text="Clear", height=36, corner_radius=10, fg_color=COLORS["button_bg"], hover_color=COLORS["button_hover"], command=app.clear_task_editor_form)
    app.edit_reset_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0))


def render_task_editor_list(app):
    if not hasattr(app, "task_editor_list"):
        return

    for child in app.task_editor_list.winfo_children():
        child.destroy()
    app.task_editor_card_widgets = {}

    for task in sort_tasks(app.tasks, app.sort_state):
        card = ctk.CTkFrame(app.task_editor_list, fg_color="#162536", corner_radius=12, border_width=1, border_color=COLORS["border"])
        card.pack(fill="x", pady=4)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=10, pady=(8, 4))
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(top, text=str(task.get("name", "")), font=font(13, "bold"), text_color=COLORS["text_primary"]).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(top, text="Edit", width=64, height=28, corner_radius=8, fg_color=COLORS["button_bg"], hover_color=COLORS["button_hover"], command=lambda t=task: app.select_task_for_edit(t)).grid(row=0, column=1, sticky="e")

        meta = f"{normalize_project_name(task.get('project', ''))} • {format_due_date(str(task.get('nextDue', '')))} • P{safe_int(task.get('priority'), 5)}"
        ctk.CTkLabel(card, text=meta, text_color=COLORS["text_secondary"]).pack(anchor="w", padx=10, pady=(0, 8))


def select_task_for_edit(app, task):
    app.selected_edit_task = task
    app.edit_name_entry.delete(0, "end")
    app.edit_name_entry.insert(0, str(task.get("name", "")))
    app.edit_project_entry.delete(0, "end")
    app.edit_project_entry.insert(0, str(task.get("project", "")))
    app.edit_priority_menu.set(str(safe_int(task.get("priority"), 5)))
    app.edit_due_entry.delete(0, "end")
    app.edit_due_entry.insert(0, str(task.get("nextDue", "")))
    app.edit_notes_entry.delete("1.0", "end")
    app.edit_notes_entry.insert("1.0", str(task.get("notes", "")))
    app.edit_url_entry.delete(0, "end")
    app.edit_url_entry.insert(0, str(task.get("url", "")))
    app.edit_info_label.configure(text=f"Editing: {task.get('name', '')}", text_color=COLORS["success"])


def clear_task_editor_form(app):
    app.selected_edit_task = None
    app.edit_name_entry.delete(0, "end")
    app.edit_project_entry.delete(0, "end")
    app.edit_priority_menu.set("5")
    app.edit_due_entry.delete(0, "end")
    app.edit_notes_entry.delete("1.0", "end")
    app.edit_url_entry.delete(0, "end")
    app.edit_info_label.configure(text="No task selected", text_color=COLORS["text_secondary"])


def save_task_edit(app):
    if not app.selected_edit_task:
        app.edit_info_label.configure(text="Select a task first", text_color=COLORS["danger"])
        return

    payload = {
        "taskId": app.selected_edit_task.get("id"),
        "name": app.edit_name_entry.get().strip(),
        "project": app.edit_project_entry.get().strip(),
        "priority": safe_int(app.edit_priority_menu.get(), 5),
        "nextDue": app.edit_due_entry.get().strip(),
        "notes": app.edit_notes_entry.get("1.0", "end").strip(),
        "url": app.edit_url_entry.get().strip(),
    }
    update_task_async(app, payload)
