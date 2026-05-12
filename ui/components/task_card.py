# *** ui/components/task_card.py ***

import customtkinter as ctk

from logic.task_utils import format_due_date, normalize_project_name, project_colors, safe_int
from ui.styles import COLORS, font


def add_task_card(app, task, parent, show_project_toggle=False, project_collapsed=False):
    project = normalize_project_name(task.get("project", ""))
    accent, chip_bg, chip_text = project_colors(project)

    title_size = int(app.settings["font_size"]) + 1
    small_size = max(10, title_size - 3)
    task_height = int(app.settings["task_height"])
    task_id = str(task.get("id", ""))
    is_completed_visual = task_id in getattr(app, "completed_pending_visual", set())

    outer = ctk.CTkFrame(parent, fg_color="transparent")
    outer.pack(fill="x", padx=2, pady=4)

    card_fg = COLORS.get("completed_card_bg", "#4a4f57") if is_completed_visual else COLORS["card_bg"]
    card_border = COLORS.get("completed_border", "#6a717b") if is_completed_visual else COLORS["border"]
    accent_fg = COLORS.get("completed_accent", "#6a717b") if is_completed_visual else accent

    card = ctk.CTkFrame(
        outer,
        fg_color=card_fg,
        corner_radius=12,
        border_width=1,
        border_color=card_border,
        height=task_height + 16,
    )
    card.pack(fill="x")
    card.pack_propagate(False)

    accent_bar = ctk.CTkFrame(card, fg_color=accent_fg, width=6, corner_radius=999)
    accent_bar.pack(side="left", fill="y", padx=(0, 8), pady=8)

    row = ctk.CTkFrame(card, fg_color="transparent")
    row.pack(fill="both", expand=True, padx=(2, 10), pady=7)

    toggle_btn = None
    toggle_text_color = COLORS.get("completed_text", "#d3d7dc") if is_completed_visual else COLORS["text_primary"]

    if show_project_toggle:
        arrow = "▶" if project_collapsed else "▼"
        toggle_btn = ctk.CTkButton(
            row,
            text=arrow,
            width=34,
            height=34,
            corner_radius=10,
            fg_color=COLORS["toggle_task_bg"],
            hover_color=COLORS["toggle_task_hover"],
            text_color=toggle_text_color,
            font=font(12, "bold"),
            state="disabled" if is_completed_visual else "normal",
            command=lambda p=project: app.toggle_project(p),
        )
        toggle_btn.pack(side="left", padx=(0, 10))
    else:
        toggle_btn = ctk.CTkLabel(
            row,
            text="",
            width=34,
            text_color=toggle_text_color,
        )
        toggle_btn.pack(side="left", padx=(0, 10))

    due_label = ctk.CTkLabel(
        row,
        text=format_due_date(str(task.get("nextDue", ""))),
        font=font(small_size, "bold"),
        text_color=COLORS.get("completed_text", "#d3d7dc") if is_completed_visual else COLORS["text_primary"],
        width=74,
        anchor="w",
    )
    due_label.pack(side="left", padx=(0, 8))

    project_chip = ctk.CTkLabel(
        row,
        text=project,
        font=font(small_size, "bold"),
        text_color=COLORS.get("completed_text", "#d3d7dc") if is_completed_visual else chip_text,
        fg_color=COLORS.get("completed_chip_bg", "#5a616b") if is_completed_visual else chip_bg,
        corner_radius=999,
        padx=12,
        pady=4,
    )
    project_chip.pack(side="left", padx=(0, 8))

    priority_label = ctk.CTkLabel(
        row,
        text=f"P{safe_int(task.get('priority'), 5)}",
        font=font(small_size, "bold"),
        text_color=COLORS.get("completed_text", "#d3d7dc") if is_completed_visual else COLORS["priority_text"],
        fg_color=COLORS.get("completed_chip_bg", "#5a616b") if is_completed_visual else COLORS["priority_bg"],
        corner_radius=999,
        padx=10,
        pady=4,
    )
    priority_label.pack(side="left", padx=(0, 10))

    title_label = ctk.CTkLabel(
        row,
        text=str(task.get("name", "")),
        font=font(title_size, "bold"),
        text_color=COLORS.get("completed_text", "#d3d7dc") if is_completed_visual else COLORS["text_primary"],
        anchor="w",
    )
    title_label.pack(side="left", fill="x", expand=True)

    tick_btn = ctk.CTkButton(
        row,
        text="Done",
        width=74,
        height=32,
        corner_radius=10,
        fg_color=COLORS.get("completed_button_bg", "#5a616b") if is_completed_visual else COLORS["done_bg"],
        hover_color=COLORS.get("completed_button_bg", "#5a616b") if is_completed_visual else COLORS["done_hover"],
        text_color=COLORS.get("completed_text", "#d3d7dc") if is_completed_visual else "#ffffff",
        font=font(12, "bold"),
        state="disabled" if is_completed_visual else "normal",
        command=lambda i=task_id: app.complete_task(i),
    )
    tick_btn.pack(side="right", padx=(10, 0))

    app.card_widgets[task_id] = {
        "outer": outer,
        "card": card,
        "row": row,
        "accent_bar": accent_bar,
        "toggle_btn": toggle_btn,
        "due_label": due_label,
        "project_chip": project_chip,
        "priority_label": priority_label,
        "title_label": title_label,
        "tick_btn": tick_btn,
        "task": task,
        "project": project,
        "accent": accent,
        "chip_bg": chip_bg,
        "chip_text": chip_text,
    }