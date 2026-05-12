# *** ui/header.py ***
# *** Builds the header area, including title, tabs, metrics, and weather strip. ***

import customtkinter as ctk

from ui.styles import COLORS, FONT_SIZES, font


def build_header(app):
    app.header = ctk.CTkFrame(
        app.main_shell,
        fg_color=COLORS["header_bg"],
        corner_radius=16,
        border_width=1,
        border_color=COLORS["border_soft"],
    )
    app.header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
    app.header.grid_columnconfigure(0, weight=1)

    header_top = ctk.CTkFrame(app.header, fg_color="transparent")
    header_top.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 6))
    header_top.grid_columnconfigure(0, weight=1)

    title_wrap = ctk.CTkFrame(header_top, fg_color="transparent")
    title_wrap.grid(row=0, column=0, sticky="w")

    app.title_label = ctk.CTkLabel(
        title_wrap,
        text="Task Focus",
        font=font(FONT_SIZES["title"], "bold"),
        text_color=COLORS["text_primary"],
    )
    app.title_label.pack(anchor="w")

    app.sub_label = ctk.CTkLabel(
        title_wrap,
        text="Today + overdue non-recurring + next 7 days one-offs",
        font=font(FONT_SIZES["subtitle"]),
        text_color="#a5b3c2",
    )
    app.sub_label.pack(anchor="w")

    header_actions = ctk.CTkFrame(header_top, fg_color="transparent")
    header_actions.grid(row=0, column=1, sticky="e")

    app.tab_selector = ctk.CTkSegmentedButton(
        header_actions,
        values=["Current Tasks", "Add Task", "Completed Today", "Task Editor", "Schedule"],
        command=app.switch_tab,
        height=34,
        corner_radius=10,
        fg_color=COLORS["tab_bg"],
        selected_color=COLORS["tab_selected"],
        selected_hover_color=COLORS["tab_selected_hover"],
        unselected_color=COLORS["tab_bg"],
        unselected_hover_color=COLORS["tab_hover"],
        text_color="#edf3fa",
    )
    app.tab_selector.pack(side="left", padx=(0, 8))
    app.tab_selector.set("Current Tasks")

    app.refresh_btn = ctk.CTkButton(
        header_actions,
        text="Refresh",
        width=84,
        height=34,
        corner_radius=10,
        fg_color=COLORS["button_bg"],
        hover_color=COLORS["button_hover"],
        text_color="#edf3fa",
        command=app.load_tasks,
    )
    app.refresh_btn.pack(side="left", padx=(0, 8))

    app.settings_btn = ctk.CTkButton(
        header_actions,
        text="⋮",
        width=36,
        height=34,
        corner_radius=10,
        fg_color=COLORS["button_bg"],
        hover_color=COLORS["button_hover"],
        text_color="#edf3fa",
        font=font(18, "bold"),
        command=app.toggle_settings_panel,
    )
    app.settings_btn.pack(side="left")

    build_metrics(app)
    build_weather_strip(app)


def build_metrics(app):
    app.metrics_card = ctk.CTkFrame(
        app.header,
        fg_color=COLORS["section_bg"],
        corner_radius=14,
        border_width=1,
        border_color=COLORS["border"],
    )
    app.metrics_card.grid(row=1, column=0, sticky="ew", padx=12, pady=(4, 8))
    app.metrics_card.grid_columnconfigure(0, weight=1)

    metrics_top = ctk.CTkFrame(app.metrics_card, fg_color="transparent")
    metrics_top.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 4))
    metrics_top.grid_columnconfigure(1, weight=1)

    app.metrics_toggle_btn = ctk.CTkButton(
        metrics_top,
        text="▼",
        width=28,
        height=28,
        corner_radius=8,
        fg_color=COLORS["toggle_bg"],
        hover_color=COLORS["toggle_hover"],
        text_color="#eef5fb",
        font=font(12, "bold"),
        command=app.toggle_metrics,
    )
    app.metrics_toggle_btn.grid(row=0, column=0, sticky="w", padx=(0, 8))

    app.metrics_title = ctk.CTkLabel(
        metrics_top,
        text="0/0 tasks completed today",
        font=font(14, "bold"),
        text_color=COLORS["text_primary"],
    )
    app.metrics_title.grid(row=0, column=1, sticky="w")

    app.metrics_content = ctk.CTkFrame(app.metrics_card, fg_color="transparent")
    app.metrics_content.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))
    app.metrics_content.grid_columnconfigure(0, weight=1)

    app.metrics_subtitle = ctk.CTkLabel(
        app.metrics_content,
        text="Let's get started",
        font=font(11),
        text_color="#b4c0cc",
    )
    app.metrics_subtitle.grid(row=0, column=0, sticky="w", pady=(0, 5))

    app.metrics_progress = ctk.CTkProgressBar(
        app.metrics_content,
        height=10,
        corner_radius=999,
        fg_color=COLORS["progress_bg"],
        progress_color=COLORS["progress_fg"],
    )
    app.metrics_progress.grid(row=1, column=0, sticky="ew", pady=(0, 5))
    app.metrics_progress.set(0)

    app.metrics_footer = ctk.CTkLabel(
        app.metrics_content,
        text="0% complete • 0 remaining",
        font=font(11),
        text_color="#8ea3b8",
    )
    app.metrics_footer.grid(row=2, column=0, sticky="w")


def build_weather_strip(app):
    app.weather_card = ctk.CTkFrame(
        app.header,
        fg_color=COLORS["section_bg"],
        corner_radius=14,
        border_width=1,
        border_color=COLORS["border"],
    )
    app.weather_card.grid(row=2, column=0, sticky="ew", padx=12, pady=(0, 8))
    app.weather_card.grid_columnconfigure(0, weight=1)

    weather_top = ctk.CTkFrame(app.weather_card, fg_color="transparent")
    weather_top.grid(row=0, column=0, sticky="ew", padx=10, pady=(8, 4))
    weather_top.grid_columnconfigure(1, weight=1)

    app.weather_toggle_btn = ctk.CTkButton(
        weather_top,
        text="▼",
        width=28,
        height=28,
        corner_radius=8,
        fg_color=COLORS["toggle_bg"],
        hover_color=COLORS["toggle_hover"],
        text_color="#eef5fb",
        font=font(12, "bold"),
        command=app.toggle_weather,
    )
    app.weather_toggle_btn.grid(row=0, column=0, sticky="w", padx=(0, 8))

    app.weather_title = ctk.CTkLabel(
        weather_top,
        text="Weather",
        font=font(12, "bold"),
        text_color="#f3f8fe",
    )
    app.weather_title.grid(row=0, column=1, sticky="w")

    app.weather_status = ctk.CTkLabel(
        weather_top,
        text=app.weather_location,
        font=font(10),
        text_color="#94a7bb",
    )
    app.weather_status.grid(row=0, column=2, sticky="e")

    app.weather_slots_wrap = ctk.CTkFrame(app.weather_card, fg_color="transparent")
    app.weather_slots_wrap.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

    for col in range(7):
        app.weather_slots_wrap.grid_columnconfigure(col, weight=1, uniform="weather")


def render_weather_strip(app):
    for child in app.weather_slots_wrap.winfo_children():
        child.destroy()

    if not app.weather_slots:
        ctk.CTkLabel(
            app.weather_slots_wrap,
            text="Weather unavailable",
            font=font(10),
            text_color=COLORS["text_secondary"],
        ).grid(row=0, column=0, sticky="w")
        return

    for idx, slot in enumerate(app.weather_slots[:7]):
        icon = str(slot.get("icon", "•"))
        temp = slot.get("temp", "")
        rain = slot.get("rain", 0)

        card = ctk.CTkFrame(
            app.weather_slots_wrap,
            fg_color=COLORS["card_bg"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        card.grid(row=0, column=idx, sticky="nsew", padx=4)

        ctk.CTkLabel(
            card,
            text=str(slot.get("label", "")),
            font=font(11, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", padx=12, pady=(10, 2))

        ctk.CTkLabel(
            card,
            text=icon,
            font=font(22, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", padx=12, pady=(0, 2))

        ctk.CTkLabel(
            card,
            text=f"{temp}°",
            font=font(16, "bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w", padx=12)

        ctk.CTkLabel(
            card,
            text=f"{rain}% rain",
            font=font(10),
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w", padx=12, pady=(2, 10))