import customtkinter as ctk

from logic.task_utils import format_due_date, normalize_project_name
from ui.styles import COLORS, font


def build_completed_today_tab(app):
    app.completed_today_tab = ctk.CTkFrame(app.tab_content, fg_color="transparent")
    app.completed_today_tab.grid(row=0, column=0, sticky="nsew")
    app.completed_today_tab.grid_columnconfigure(0, weight=1)
    app.completed_today_tab.grid_rowconfigure(0, weight=1)

    wrap = ctk.CTkFrame(app.completed_today_tab, fg_color=COLORS["header_bg"], corner_radius=14, border_width=1, border_color=COLORS["border_soft"])
    wrap.grid(row=0, column=0, sticky="nsew")
    wrap.grid_columnconfigure(0, weight=1)
    wrap.grid_rowconfigure(1, weight=1)

    header = ctk.CTkFrame(wrap, fg_color="transparent")
    header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
    header.grid_columnconfigure(0, weight=1)
    ctk.CTkLabel(header, text="Completed Tasks Today", font=font(24, "bold"), text_color=COLORS["text_primary"]).grid(row=0, column=0, sticky="w")
    ctk.CTkLabel(header, text="Completed tasks you tick off in this session", font=font(12), text_color=COLORS["text_muted"]).grid(row=1, column=0, sticky="w", pady=(6, 0))

    app.completed_today_container = ctk.CTkScrollableFrame(wrap, fg_color="transparent", corner_radius=0, border_width=0, scrollbar_button_color=COLORS["scroll_btn"], scrollbar_button_hover_color=COLORS["scroll_btn_hover"])
    app.completed_today_container.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))


def render_completed_today(app):
    for child in app.completed_today_container.winfo_children():
        child.destroy()

    if not app.completed_today_tasks:
        ctk.CTkLabel(app.completed_today_container, text="No completed tasks yet", text_color=COLORS["text_secondary"]).pack(anchor="w", pady=10)
        return

    for task in app.completed_today_tasks:
        card = ctk.CTkFrame(app.completed_today_container, fg_color="#162536", corner_radius=12, border_width=1, border_color=COLORS["border"])
        card.pack(fill="x", pady=4)
        ctk.CTkLabel(card, text=str(task.get("name", "")), font=font(14, "bold"), text_color=COLORS["text_primary"]).pack(anchor="w", padx=12, pady=(10, 2))
        meta = f"{format_due_date(str(task.get('nextDue', '')))}  •  {normalize_project_name(task.get('project', ''))}"
        ctk.CTkLabel(card, text=meta, text_color=COLORS["text_secondary"]).pack(anchor="w", padx=12, pady=(0, 10))
