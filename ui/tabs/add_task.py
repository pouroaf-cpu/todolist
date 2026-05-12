from datetime import datetime

import customtkinter as ctk

from logic.api import add_task_async
from logic.task_utils import safe_int
from ui.components.forms import make_entry, make_option_menu, make_textbox
from ui.styles import COLORS, font


def build_add_task_tab(app):
    app.add_task_tab = ctk.CTkFrame(app.tab_content, fg_color="transparent")
    app.add_task_tab.grid(row=0, column=0, sticky="nsew")
    app.add_task_tab.grid_columnconfigure(0, weight=1)
    app.add_task_tab.grid_rowconfigure(0, weight=1)

    wrap = ctk.CTkFrame(app.add_task_tab, fg_color=COLORS["header_bg"], corner_radius=14, border_width=1, border_color=COLORS["border_soft"])
    wrap.grid(row=0, column=0, sticky="nsew")
    wrap.grid_columnconfigure(0, weight=1)
    wrap.grid_rowconfigure(1, weight=1)

    header = ctk.CTkFrame(wrap, fg_color="transparent")
    header.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 10))
    header.grid_columnconfigure(0, weight=1)

    title_wrap = ctk.CTkFrame(header, fg_color="transparent")
    title_wrap.grid(row=0, column=0, sticky="w")
    ctk.CTkLabel(title_wrap, text="Add Task", font=font(24, "bold"), text_color=COLORS["text_primary"]).pack(anchor="w")
    ctk.CTkLabel(title_wrap, text="Everything fits on one screen", font=font(12), text_color=COLORS["text_muted"]).pack(anchor="w", pady=(4, 0))

    actions = ctk.CTkFrame(header, fg_color="transparent")
    actions.grid(row=0, column=1, sticky="e")
    app.add_submit_btn = ctk.CTkButton(actions, text="Add Task", width=104, height=36, corner_radius=10, fg_color="#1faa59", hover_color="#168648", command=app.submit_add_task)
    app.add_submit_btn.pack(side="left", padx=(0, 8))
    app.add_clear_btn = ctk.CTkButton(actions, text="Clear Form", width=104, height=36, corner_radius=10, fg_color=COLORS["button_bg"], hover_color=COLORS["button_hover"], command=app.clear_add_task_form)
    app.add_clear_btn.pack(side="left")

    form = ctk.CTkFrame(wrap, fg_color=COLORS["section_bg"], corner_radius=12, border_width=1, border_color=COLORS["border"])
    form.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 14))
    form.grid_columnconfigure((0, 1), weight=1)

    def form_label(parent, text, row, col):
        ctk.CTkLabel(parent, text=text, font=font(11, "bold"), text_color=COLORS["text_soft"]).grid(row=row, column=col, sticky="w", padx=14, pady=(12, 6))

    form_label(form, "Task Name", 0, 0)
    form_label(form, "Project", 0, 1)
    app.add_name_entry = make_entry(form)
    app.add_name_entry.grid(row=1, column=0, sticky="ew", padx=(14, 8))
    app.add_project_entry = make_entry(form)
    app.add_project_entry.grid(row=1, column=1, sticky="ew", padx=(8, 14))

    form_label(form, "Priority", 2, 0)
    form_label(form, "Due Date", 2, 1)
    app.add_priority_menu = make_option_menu(form, [str(i) for i in range(1, 11)])
    app.add_priority_menu.grid(row=3, column=0, sticky="ew", padx=(14, 8))
    app.add_priority_menu.set("5")
    app.add_due_entry = make_entry(form, "YYYY-MM-DD")
    app.add_due_entry.grid(row=3, column=1, sticky="ew", padx=(8, 14))
    app.add_due_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

    form_label(form, "Recurring", 4, 0)
    form_label(form, "Interval Days", 4, 1)
    app.add_recurring_menu = make_option_menu(form, ["No", "Yes"], app.on_recurring_change)
    app.add_recurring_menu.grid(row=5, column=0, sticky="ew", padx=(14, 8))
    app.add_recurring_menu.set("No")
    app.add_interval_entry = make_entry(form, "e.g. 7")
    app.add_interval_entry.grid(row=5, column=1, sticky="ew", padx=(8, 14))
    app.add_interval_entry.configure(state="disabled")

    form_label(form, "Notes", 6, 0)
    form_label(form, "URL", 6, 1)
    app.add_notes_entry = make_textbox(form, 120)
    app.add_notes_entry.grid(row=7, column=0, sticky="nsew", padx=(14, 8), pady=(0, 8))
    app.add_url_entry = make_entry(form, "Optional link")
    app.add_url_entry.grid(row=7, column=1, sticky="ew", padx=(8, 14), pady=(0, 8))

    app.add_status_label = ctk.CTkLabel(form, text="", font=font(10), text_color=COLORS["text_secondary"])
    app.add_status_label.grid(row=8, column=0, columnspan=2, sticky="w", padx=14, pady=(4, 12))


def submit_add_task(app):
    payload = {
        "name": app.add_name_entry.get().strip(),
        "project": app.add_project_entry.get().strip(),
        "priority": safe_int(app.add_priority_menu.get(), 5),
        "nextDue": app.add_due_entry.get().strip(),
        "recurring": app.add_recurring_menu.get() == "Yes",
        "intervalDays": safe_int(app.add_interval_entry.get(), 0),
        "notes": app.add_notes_entry.get("1.0", "end").strip(),
        "url": app.add_url_entry.get().strip(),
    }

    if not payload["name"]:
        app.add_status_label.configure(text="Task name is required", text_color=COLORS["danger"])
        return

    add_task_async(app, payload)


def clear_add_task_form(app):
    app.add_name_entry.delete(0, "end")
    app.add_project_entry.delete(0, "end")
    app.add_priority_menu.set("5")
    app.add_due_entry.delete(0, "end")
    app.add_due_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
    app.add_recurring_menu.set("No")
    app.add_interval_entry.configure(state="normal")
    app.add_interval_entry.delete(0, "end")
    app.add_interval_entry.configure(state="disabled")
    app.add_notes_entry.delete("1.0", "end")
    app.add_url_entry.delete(0, "end")
    app.add_status_label.configure(text="", text_color=COLORS["text_secondary"])


def on_recurring_change(app, value):
    if value == "Yes":
        app.add_interval_entry.configure(state="normal")
    else:
        app.add_interval_entry.delete(0, "end")
        app.add_interval_entry.configure(state="disabled")
