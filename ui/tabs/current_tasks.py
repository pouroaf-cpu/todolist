import customtkinter as ctk

from logic.task_utils import filter_tasks_by_projects, group_tasks_by_project, summarize_project_filter_state, sort_tasks
from ui.components.project_group import add_project_group
from ui.styles import COLORS, font


def build_current_tasks_tab(app):
    app.current_tasks_tab = ctk.CTkFrame(app.tab_content, fg_color="transparent")
    app.current_tasks_tab.grid(row=0, column=0, sticky="nsew")
    app.current_tasks_tab.grid_columnconfigure(0, weight=1)
    app.current_tasks_tab.grid_rowconfigure(0, weight=1)

    body = ctk.CTkFrame(app.current_tasks_tab, fg_color="transparent")
    body.grid(row=0, column=0, sticky="nsew")
    body.grid_columnconfigure(0, weight=1)
    body.grid_rowconfigure(0, weight=1)

    app.scroll = ctk.CTkScrollableFrame(
        body,
        fg_color=COLORS["section_bg"],
        corner_radius=14,
        border_width=1,
        border_color=COLORS["border"],
        scrollbar_button_color=COLORS["scroll_btn"],
        scrollbar_button_hover_color=COLORS["scroll_btn_hover"],
    )
    app.scroll.grid(row=0, column=0, sticky="nsew")

    app.sort_card = ctk.CTkFrame(
        app.scroll,
        fg_color=COLORS["sort_bg"],
        corner_radius=14,
        border_width=1,
        border_color=COLORS["border_soft"],
    )
    app.sort_card.pack(fill="x", padx=4, pady=(4, 6))
    app.sort_card.grid_columnconfigure(0, weight=1)

    sort_header = ctk.CTkFrame(app.sort_card, fg_color="transparent")
    sort_header.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 6))
    sort_header.grid_columnconfigure(0, weight=1)

    app.sort_title = ctk.CTkLabel(sort_header, text="Sort & Filter", font=font(14, "bold"), text_color="#f3f8fe")
    app.sort_title.grid(row=0, column=0, sticky="w")

    toolbar = ctk.CTkFrame(sort_header, fg_color="transparent")
    toolbar.grid(row=0, column=1, sticky="e")

    app.default_sort_btn = ctk.CTkButton(
        toolbar,
        text="Default Sort",
        width=94,
        height=28,
        corner_radius=9,
        fg_color=COLORS["button_bg"],
        hover_color=COLORS["button_hover"],
        command=app.reset_default_sort,
    )
    app.default_sort_btn.pack(side="left", padx=(0, 6))

    app.clear_sort_btn = ctk.CTkButton(
        toolbar,
        text="Clear Sort",
        width=86,
        height=28,
        corner_radius=9,
        fg_color=COLORS["button_alt_bg"],
        hover_color=COLORS["button_alt_hover"],
        command=app.clear_all_sort,
    )
    app.clear_sort_btn.pack(side="left", padx=(0, 6))

    app.sort_toggle_btn = ctk.CTkButton(
        toolbar,
        text="Expand" if app.sort_collapsed else "Collapse",
        width=82,
        height=28,
        corner_radius=9,
        fg_color=COLORS["button_bg"],
        hover_color=COLORS["button_hover"],
        command=app.toggle_sorter,
    )
    app.sort_toggle_btn.pack(side="left")

    app.sort_rows_host = ctk.CTkFrame(app.sort_card, fg_color="transparent")
    app.sort_rows_host.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 8))
    app.sort_rows_host.grid_columnconfigure(0, weight=1)

    app.tasks_container = ctk.CTkFrame(app.scroll, fg_color="transparent")
    app.tasks_container.pack(fill="x", padx=4, pady=(0, 2))

    bottom = ctk.CTkFrame(app.current_tasks_tab, fg_color="transparent")
    bottom.grid(row=1, column=0, sticky="ew", pady=(6, 0))
    bottom.grid_columnconfigure(0, weight=1)

    app.status_label = ctk.CTkLabel(bottom, text="", font=font(10), text_color=COLORS["text_secondary"], anchor="w")
    app.status_label.grid(row=0, column=0, sticky="w")


def render_tasks(app):
    for widget in app.tasks_container.winfo_children():
        widget.destroy()

    app.card_widgets = {}
    app.project_widgets = {}
    app.ensure_project_filter_state()

    filtered_tasks = filter_tasks_by_projects(app.tasks, app.visible_projects)
    tasks = sort_tasks(filtered_tasks, app.sort_state) if app.sort_state else list(filtered_tasks)

    if not tasks:
        empty_text = "No projects selected" if not app.visible_projects else "No current tasks"
        empty = ctk.CTkLabel(
            app.tasks_container,
            text=empty_text,
            font=font(16, "bold"),
            text_color=COLORS["text_soft"],
        )
        empty.pack(anchor="center", pady=(20, 8))
        return

    grouped = group_tasks_by_project(tasks)
    for project, project_tasks in grouped.items():
        add_project_group(app, project, project_tasks)


def render_sort_rows(app):
    for child in app.sort_rows_host.winfo_children():
        child.destroy()

    row_index = 0

    sort_section = ctk.CTkFrame(app.sort_rows_host, fg_color="transparent")
    sort_section.grid(row=row_index, column=0, sticky="ew")
    sort_section.grid_columnconfigure(0, weight=1)
    row_index += 1

    ctk.CTkLabel(sort_section, text="Sort Rules", font=font(12, "bold"), text_color=COLORS["text_soft"]).grid(row=0, column=0, sticky="w", pady=(0, 6))

    if not app.sort_state:
        ctk.CTkLabel(sort_section, text="No active sort rules", text_color=COLORS["text_secondary"]).grid(row=1, column=0, sticky="w")
    else:
        for idx, rule in enumerate(app.sort_state, start=1):
            row = ctk.CTkFrame(
                sort_section,
                fg_color="#152233",
                corner_radius=10,
                border_width=1,
                border_color=COLORS["border"],
            )
            row.grid(row=idx, column=0, sticky="ew", pady=(0, 6))
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(row, text=str(idx), width=30, text_color=COLORS["text_primary"]).grid(row=0, column=0, padx=(10, 6), pady=8)
            ctk.CTkLabel(row, text=rule.get("type", "Sort"), font=font(12, "bold"), text_color=COLORS["text_primary"]).grid(row=0, column=1, sticky="w")
            setting_text = ", ".join(f"{k}: {v}" for k, v in rule.get("settings", {}).items())
            ctk.CTkLabel(row, text=setting_text, text_color=COLORS["text_secondary"]).grid(row=0, column=2, sticky="e", padx=(8, 12))

    divider = ctk.CTkFrame(app.sort_rows_host, fg_color=COLORS["border_soft"], height=1)
    divider.grid(row=row_index, column=0, sticky="ew", pady=(8, 10))
    row_index += 1

    filter_section = ctk.CTkFrame(app.sort_rows_host, fg_color="transparent")
    filter_section.grid(row=row_index, column=0, sticky="ew")
    filter_section.grid_columnconfigure(0, weight=1)

    header = ctk.CTkFrame(filter_section, fg_color="transparent")
    header.grid(row=0, column=0, sticky="ew", pady=(0, 8))
    header.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(header, text="Projects", font=font(12, "bold"), text_color=COLORS["text_soft"]).grid(row=0, column=0, sticky="w")

    count_text = summarize_project_filter_state(app.get_available_projects(), app.visible_projects)
    ctk.CTkLabel(header, text=count_text, font=font(10), text_color=COLORS["text_secondary"]).grid(row=0, column=1, sticky="e")

    controls = ctk.CTkFrame(filter_section, fg_color="transparent")
    controls.grid(row=1, column=0, sticky="w", pady=(0, 8))

    ctk.CTkButton(
        controls,
        text="All",
        width=58,
        height=28,
        corner_radius=999,
        fg_color=COLORS["filter_button_bg"],
        hover_color=COLORS["filter_button_hover"],
        command=app.show_all_projects,
    ).pack(side="left", padx=(0, 6))

    ctk.CTkButton(
        controls,
        text="None",
        width=58,
        height=28,
        corner_radius=999,
        fg_color=COLORS["button_alt_bg"],
        hover_color=COLORS["button_alt_hover"],
        command=app.hide_all_projects,
    ).pack(side="left")

    chip_wrap = ctk.CTkFrame(filter_section, fg_color="transparent")
    chip_wrap.grid(row=2, column=0, sticky="ew")
    chip_wrap.grid_columnconfigure((0, 1, 2, 3), weight=1)

    projects = app.get_available_projects()
    if not projects:
        ctk.CTkLabel(chip_wrap, text="No projects found", text_color=COLORS["text_secondary"]).grid(row=0, column=0, sticky="w")
        return

    for idx, project in enumerate(projects):
        selected = app.is_project_visible(project)
        fg = COLORS["filter_button_selected_bg"] if selected else COLORS["filter_button_bg"]
        hover = COLORS["filter_button_selected_hover"] if selected else COLORS["filter_button_hover"]
        text_color = COLORS["text_primary"] if selected else COLORS["text_soft"]

        button = ctk.CTkButton(
            chip_wrap,
            text=project,
            height=30,
            corner_radius=999,
            fg_color=fg,
            hover_color=hover,
            text_color=text_color,
            command=lambda p=project: app.toggle_project_visibility(p),
        )
        button.grid(row=idx // 4, column=idx % 4, sticky="ew", padx=4, pady=4)