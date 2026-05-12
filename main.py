import threading
from pathlib import Path

import customtkinter as ctk

from logic.api import apply_remote_or_local_metrics, complete_task_async, load_tasks_async
from logic.config import DEFAULT_SETTINGS, DEFAULT_WEATHER_LOCATION, ICON_PATH
from logic.task_utils import get_project_names, normalize_project_name, safe_int
from ui.header import build_header, render_weather_strip as _render_weather_strip
from ui.styles import COLORS, font
from ui.tabs.add_task import build_add_task_tab, clear_add_task_form, on_recurring_change, submit_add_task
from ui.tabs.completed_today import build_completed_today_tab, render_completed_today
from ui.tabs.current_tasks import build_current_tasks_tab, render_sort_rows, render_tasks
from ui.tabs.task_editor import build_task_editor_tab, clear_task_editor_form, render_task_editor_list, save_task_edit, select_task_for_edit
from ui.tabs.schedule import build_schedule_tab, render_schedule, scroll_to_now
from logic.schedule import fetch_and_schedule_async
from weather import get_weather_slots

try:
    import winsound
except ImportError:
    winsound = None


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class TodoWidget(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.setup_app_icon()
        self.title("Todo Widget")
        self.set_start_geometry()
        self.minsize(1120, 760)
        self.configure(fg_color=COLORS["app_bg"])

        self.settings = dict(DEFAULT_SETTINGS)
        self.tasks = []
        self.completed_today_tasks = []
        self.weather_slots = []
        self.weather_location = DEFAULT_WEATHER_LOCATION
        self.metrics = {"completedToday": 0, "totalToday": 0, "remainingToday": 0, "percent": 0}

        self.loading = False
        self.card_widgets = {}
        self.task_editor_card_widgets = {}
        self.project_widgets = {}
        self.selected_edit_task = None

        self.pending_complete_ids = set()
        self.completed_pending_visual = set()

        self.sort_state = self.get_default_sort_state()
        self.sort_collapsed = self.settings["sorter_collapsed_on_start"]
        self.weather_collapsed = False
        self.metrics_collapsed = False
        self.collapsed_projects = {}
        self.visible_projects = set()
        self._project_filter_initialized = False

        self.settings_open = False
        self._last_geometry = ""

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.build_ui()
        self.bind("<Configure>", self.on_window_configure)

        self.after(120, lambda: self.show_loading_overlay("Loading Tasks"))
        self.after(150, self.load_tasks)
        self.after(250, self.load_weather)
        self.after(self.settings["auto_refresh_sec"] * 1000, self.auto_refresh)
        self.after(3600 * 1000, self.auto_refresh_weather)

    def set_start_geometry(self):
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        width = int(sw * 0.68)
        height = int(sh * 0.84)
        x = int((sw - width) / 2)
        y = int((sh - height) / 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def setup_app_icon(self):
        try:
            if Path(ICON_PATH).exists():
                self.iconbitmap(str(ICON_PATH))
        except Exception:
            pass

    def get_default_sort_state(self):
        return [
            {"type": "Project", "settings": {"order": "A-Z"}},
            {"type": "Due Date", "settings": {"order": "Oldest to newest"}},
            {"type": "Priority", "settings": {"order": "Highest to lowest"}},
        ]

    def build_ui(self):
        self.main_shell = ctk.CTkFrame(self, fg_color="transparent")
        self.main_shell.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.main_shell.grid_columnconfigure(0, weight=1)
        self.main_shell.grid_rowconfigure(1, weight=1)

        build_header(self)
        self.build_tabs()
        self.build_settings_overlay()
        self.build_loading_overlay()

        self.show_current_tasks_tab()
        self.render_sort_rows()
        self.update_sort_panel_visibility()
        self.render_weather_strip()
        self.update_weather_panel_visibility()
        self.update_metrics_panel_visibility()
        self.render_completed_today()
        self.render_task_editor_list()

    def build_tabs(self):
        self.tab_content = ctk.CTkFrame(self.main_shell, fg_color="transparent")
        self.tab_content.grid(row=1, column=0, sticky="nsew")
        self.tab_content.grid_columnconfigure(0, weight=1)
        self.tab_content.grid_rowconfigure(0, weight=1)

        build_current_tasks_tab(self)
        build_add_task_tab(self)
        build_completed_today_tab(self)
        build_task_editor_tab(self)
        build_schedule_tab(self)

    def build_settings_overlay(self):
        self.settings_overlay = ctk.CTkFrame(self, fg_color=COLORS["overlay_bg"], corner_radius=0)
        self.settings_overlay.bind("<Button-1>", lambda _e: self.hide_settings_panel())

        self.settings_panel = ctk.CTkFrame(
            self.settings_overlay,
            fg_color=COLORS["settings_bg"],
            corner_radius=18,
            border_width=1,
            border_color=COLORS["border"],
            width=320,
        )
        self.settings_panel.place(x=5000, y=16)
        self.settings_panel.bind("<Button-1>", lambda e: "break")

        wrap = ctk.CTkScrollableFrame(self.settings_panel, fg_color="transparent")
        wrap.pack(fill="both", expand=True, padx=14, pady=14)

        ctk.CTkLabel(wrap, text="Settings", font=font(22, "bold"), text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 10))
        self.settings_preview = ctk.CTkFrame(
            wrap,
            height=max(56, self.settings["task_height"] + 16),
            fg_color=COLORS["preview_bg"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
        )
        self.settings_preview.pack(fill="x", pady=(0, 12))
        self.settings_preview.pack_propagate(False)
        self.preview_label = ctk.CTkLabel(
            self.settings_preview,
            text="Preview task row",
            font=font(self.settings["font_size"], "bold"),
            text_color=COLORS["text_primary"],
        )
        self.preview_label.pack(anchor="w", padx=12, pady=10)

        self._build_settings_controls(wrap)

    def _build_settings_controls(self, wrap):
        self.build_settings_section_label(wrap, "Appearance")
        ctk.CTkLabel(wrap, text="Task height", text_color="#d2ddea").pack(anchor="w")
        self.task_height_slider = ctk.CTkSlider(wrap, from_=40, to=72, number_of_steps=8, command=self.on_task_height_change)
        self.task_height_slider.pack(fill="x", pady=(6, 4))
        self.task_height_slider.set(self.settings["task_height"])
        self.task_height_value = ctk.CTkLabel(wrap, text=str(self.settings["task_height"]), text_color=COLORS["text_secondary"])
        self.task_height_value.pack(anchor="e", pady=(0, 10))

        ctk.CTkLabel(wrap, text="Font size", text_color="#d2ddea").pack(anchor="w")
        self.font_size_slider = ctk.CTkSlider(wrap, from_=12, to=18, number_of_steps=6, command=self.on_font_size_change)
        self.font_size_slider.pack(fill="x", pady=(6, 4))
        self.font_size_slider.set(self.settings["font_size"])
        self.font_size_value = ctk.CTkLabel(wrap, text=str(self.settings["font_size"]), text_color=COLORS["text_secondary"])
        self.font_size_value.pack(anchor="e", pady=(0, 10))

        self.build_settings_section_label(wrap, "Behaviour")
        ctk.CTkLabel(wrap, text="Auto refresh", text_color="#d2ddea").pack(anchor="w")
        self.refresh_menu = ctk.CTkOptionMenu(
            wrap,
            values=["15s", "30s", "60s", "120s", "300s"],
            command=self.on_auto_refresh_change,
            height=36,
            corner_radius=10,
            fg_color="#192739",
            button_color=COLORS["border"],
            button_hover_color="#36516f",
            text_color=COLORS["text_primary"],
        )
        self.refresh_menu.pack(fill="x", pady=(6, 12))
        self.refresh_menu.set(f'{self.settings["auto_refresh_sec"]}s')

        self.sorter_toggle = ctk.CTkSwitch(wrap, text="Start with sorter collapsed", command=self.on_sorter_collapsed_setting_change)
        self.sorter_toggle.pack(anchor="w", pady=(0, 12))
        if self.settings["sorter_collapsed_on_start"]:
            self.sorter_toggle.select()

        self.build_settings_section_label(wrap, "Feedback")
        self.sound_toggle = ctk.CTkSwitch(wrap, text="Completion sound", command=self.on_completion_sound_toggle)
        self.sound_toggle.pack(anchor="w", pady=(0, 12))
        if self.settings["completion_sound"]:
            self.sound_toggle.select()

    def build_loading_overlay(self):
        self.loading_overlay = ctk.CTkFrame(self, fg_color=COLORS["app_bg"], corner_radius=0)
        self.loading_title = ctk.CTkLabel(self.loading_overlay, text="Loading Tasks", font=font(24, "bold"), text_color=COLORS["text_primary"])
        self.loading_title.place(relx=0.5, rely=0.47, anchor="center")
        self.loading_bar = ctk.CTkProgressBar(self.loading_overlay, width=260, height=12, corner_radius=999, mode="indeterminate")
        self.loading_bar.place(relx=0.5, rely=0.53, anchor="center")

    def build_settings_section_label(self, parent, text):
        ctk.CTkLabel(parent, text=text, font=font(13, "bold"), text_color=COLORS["text_primary"]).pack(anchor="w", pady=(8, 8))

    def on_window_configure(self, _event=None):
        geometry = self.geometry()
        if geometry == self._last_geometry:
            return
        self._last_geometry = geometry
        if self.settings_open:
            self.position_settings_panel()

    def position_settings_panel(self):
        self.settings_overlay.place(x=0, y=0, relwidth=1, relheight=1)
        self.settings_overlay.lift()
        self.settings_panel.update_idletasks()
        panel_w = self.settings_panel.winfo_width() or 320
        self.settings_panel.place(x=max(16, self.winfo_width() - panel_w - 18), y=16)

    def toggle_settings_panel(self):
        if self.settings_open:
            self.hide_settings_panel()
        else:
            self.show_settings_panel()

    def show_settings_panel(self):
        self.settings_open = True
        self.position_settings_panel()

    def hide_settings_panel(self):
        self.settings_open = False
        self.settings_overlay.place_forget()

    def show_loading_overlay(self, title="Loading Tasks"):
        self.loading_title.configure(text=title)
        self.loading_overlay.place(x=0, y=0, relwidth=1, relheight=1)
        self.loading_overlay.lift()
        self.loading_bar.start()

    def hide_loading_overlay(self):
        self.loading_bar.stop()
        self.loading_overlay.place_forget()

    def switch_tab(self, value):
        {
            "Current Tasks": self.show_current_tasks_tab,
            "Add Task": self.show_add_task_tab,
            "Completed Today": self.show_completed_today_tab,
            "Task Editor": self.show_task_editor_tab,
            "Schedule": self.show_schedule_tab,
        }[value]()

    def show_current_tasks_tab(self):
        self.current_tasks_tab.tkraise()

    def show_add_task_tab(self):
        self.add_task_tab.tkraise()

    def show_completed_today_tab(self):
        self.completed_today_tab.tkraise()

    def show_task_editor_tab(self):
        self.task_editor_tab.tkraise()

    def show_schedule_tab(self):
        self.schedule_tab.tkraise()
        if self._schedule_result is None:
            self.load_schedule()
        else:
            scroll_to_now(self)

    def load_schedule(self):
        self.schedule_status_label.configure(text="Loading…", text_color=COLORS["text_secondary"])
        self.schedule_refresh_btn.configure(state="disabled")
        fetch_and_schedule_async(self, self.on_schedule_loaded)

    def on_schedule_loaded(self, result, error):
        self.schedule_refresh_btn.configure(state="normal")
        if error:
            self.schedule_status_label.configure(
                text=f"Error: {error[:80]}", text_color=COLORS["danger"]
            )
            return
        n_events = sum(1 for x in result.get("timeline", []) if x["type"] == "event")
        n_tasks = sum(1 for x in result.get("timeline", []) if x["type"] == "task")
        n_overflow = len(result.get("overflow", []))
        cal_error = result.get("cal_error")

        if cal_error:
            status = f"⚠ Calendar unavailable · {n_tasks} tasks scheduled"
            self.schedule_status_label.configure(text=status, text_color=COLORS["priority_bg"])
        else:
            status = f"{n_events} events · {n_tasks} tasks scheduled"
            if n_overflow:
                status += f" · {n_overflow} overflow"
            self.schedule_status_label.configure(text=status, text_color=COLORS["text_secondary"])

        render_schedule(self, result)
        self.after(100, lambda: scroll_to_now(self))

    def on_task_height_change(self, value):
        self.settings["task_height"] = int(round(float(value)))
        self.task_height_value.configure(text=str(self.settings["task_height"]))
        self.settings_preview.configure(height=max(56, self.settings["task_height"] + 16))
        self.render_tasks()

    def on_font_size_change(self, value):
        self.settings["font_size"] = int(round(float(value)))
        self.font_size_value.configure(text=str(self.settings["font_size"]))
        self.preview_label.configure(font=font(self.settings["font_size"], "bold"))
        self.render_tasks()

    def on_auto_refresh_change(self, value):
        self.settings["auto_refresh_sec"] = safe_int(str(value).replace("s", ""), 60)

    def on_sorter_collapsed_setting_change(self):
        self.settings["sorter_collapsed_on_start"] = bool(self.sorter_toggle.get())

    def on_completion_sound_toggle(self):
        self.settings["completion_sound"] = bool(self.sound_toggle.get())

    def toggle_metrics(self):
        self.metrics_collapsed = not self.metrics_collapsed
        self.update_metrics_panel_visibility()

    def update_metrics_panel_visibility(self):
        if self.metrics_collapsed:
            self.metrics_content.grid_remove()
            self.metrics_toggle_btn.configure(text="▶")
        else:
            self.metrics_content.grid()
            self.metrics_toggle_btn.configure(text="▼")

    def toggle_weather(self):
        self.weather_collapsed = not self.weather_collapsed
        self.update_weather_panel_visibility()

    def update_weather_panel_visibility(self):
        if self.weather_collapsed:
            self.weather_slots_wrap.grid_remove()
            self.weather_toggle_btn.configure(text="▶")
        else:
            self.weather_slots_wrap.grid()
            self.weather_toggle_btn.configure(text="▼")

    def toggle_sorter(self):
        self.sort_collapsed = not self.sort_collapsed
        self.update_sort_panel_visibility()

    def update_sort_panel_visibility(self):
        if self.sort_collapsed:
            self.sort_rows_host.grid_remove()
            self.sort_toggle_btn.configure(text="Expand")
        else:
            self.sort_rows_host.grid()
            self.sort_toggle_btn.configure(text="Collapse")

    def reset_default_sort(self):
        self.sort_state = self.get_default_sort_state()
        self.render_sort_rows()
        self.render_tasks()

    def clear_all_sort(self):
        self.sort_state = []
        self.render_sort_rows()
        self.render_tasks()

    def get_available_projects(self):
        return get_project_names(self.tasks)

    def ensure_project_filter_state(self):
        available = set(self.get_available_projects())

        if not self._project_filter_initialized:
            self.visible_projects = set(available)
            self._project_filter_initialized = True
            return

        self.visible_projects = {
            normalize_project_name(p)
            for p in self.visible_projects
            if normalize_project_name(p) in available
        }

        missing = available - self.visible_projects
        if missing and not self.visible_projects:
            self.visible_projects = set(available)

    def show_all_projects(self):
        self.visible_projects = set(self.get_available_projects())
        self._project_filter_initialized = True
        self.render_sort_rows()
        self.render_tasks()

    def hide_all_projects(self):
        self.visible_projects = set()
        self._project_filter_initialized = True
        self.render_sort_rows()
        self.render_tasks()

    def toggle_project_visibility(self, project):
        project = normalize_project_name(project)
        self._project_filter_initialized = True

        if project in self.visible_projects:
            self.visible_projects.remove(project)
        else:
            self.visible_projects.add(project)

        self.render_sort_rows()
        self.render_tasks()

    def is_project_visible(self, project):
        project = normalize_project_name(project)
        self.ensure_project_filter_state()
        return project in self.visible_projects

    def auto_refresh_weather(self):
        self.load_weather()
        self.after(3600 * 1000, self.auto_refresh_weather)

    def load_weather(self):
        def worker():
            try:
                slots = get_weather_slots(self.weather_location)
                self.after(0, lambda: self.on_weather_loaded(slots))
            except Exception:
                self.after(0, lambda: self.on_weather_loaded([]))

        threading.Thread(target=worker, daemon=True).start()

    def on_weather_loaded(self, slots):
        self.weather_slots = slots or []
        self.render_weather_strip()

    def render_weather_strip(self):
        _render_weather_strip(self)

    def auto_refresh(self):
        self.load_tasks(silent=True)
        self.after(self.settings["auto_refresh_sec"] * 1000, self.auto_refresh)

    def load_tasks(self, silent=False):
        load_tasks_async(self, silent)

    def on_tasks_loaded(self, tasks, metrics=None):
        self.loading = False
        self.refresh_btn.configure(state="normal")
        self.hide_loading_overlay()

        completed_ids = set(self.completed_pending_visual)
        self.tasks = [task for task in tasks if str(task.get("id", "")) not in completed_ids]

        self.ensure_project_filter_state()
        apply_remote_or_local_metrics(self, metrics)
        self.render_metrics()
        self.render_sort_rows()
        self.render_tasks()
        self.render_task_editor_list()
        self.set_status(f"Loaded {len(self.tasks)} tasks", COLORS["success"])

    def on_tasks_error(self, error):
        self.loading = False
        self.refresh_btn.configure(state="normal")
        self.hide_loading_overlay()
        self.set_status(f"Load failed: {error}", COLORS["danger"])

    def render_tasks(self):
        render_tasks(self)

    def render_sort_rows(self):
        render_sort_rows(self)

    def render_completed_today(self):
        render_completed_today(self)

    def render_task_editor_list(self):
        render_task_editor_list(self)

    def render_metrics(self):
        completed = safe_int(self.metrics.get("completedToday"), 0)
        total = safe_int(self.metrics.get("totalToday"), 0)
        remaining = safe_int(self.metrics.get("remainingToday"), 0)
        percent = 0 if total <= 0 else int(round((completed / total) * 100))
        self.metrics["percent"] = percent
        self.metrics_title.configure(text=f"{completed}/{total} tasks completed today")
        subtitle = "Let's get started" if completed == 0 else ("Everything scheduled for today is done" if remaining == 0 and total > 0 else "Keep going")
        self.metrics_subtitle.configure(text=subtitle)
        self.metrics_progress.set(max(0, min(1, percent / 100)))
        self.metrics_footer.configure(text=f"{percent}% complete • {remaining} remaining")

    def _apply_completed_visual_state(self, task_id):
        task_id = str(task_id)
        widget = self.card_widgets.get(task_id)
        if not widget:
            return

        try:
            widget["card"].configure(
                fg_color=COLORS.get("completed_card_bg", "#4a4f57"),
                border_color=COLORS.get("completed_border", "#6a717b"),
            )
        except Exception:
            pass

        try:
            widget["accent_bar"].configure(fg_color=COLORS.get("completed_accent", "#6a717b"))
        except Exception:
            pass

        for key in ("due_label", "project_chip", "priority_label", "title_label", "toggle_btn"):
            control = widget.get(key)
            if not control:
                continue
            try:
                if key == "project_chip":
                    control.configure(
                        fg_color=COLORS.get("completed_chip_bg", "#5a616b"),
                        text_color=COLORS.get("completed_text", "#d3d7dc"),
                    )
                elif key == "priority_label":
                    control.configure(
                        fg_color=COLORS.get("completed_chip_bg", "#5a616b"),
                        text_color=COLORS.get("completed_text", "#d3d7dc"),
                    )
                else:
                    control.configure(text_color=COLORS.get("completed_text", "#d3d7dc"))
            except Exception:
                pass

        tick_btn = widget.get("tick_btn")
        if tick_btn:
            try:
                tick_btn.configure(
                    state="disabled",
                    text="Done",
                    fg_color=COLORS.get("completed_button_bg", "#5a616b"),
                    hover_color=COLORS.get("completed_button_bg", "#5a616b"),
                    text_color=COLORS.get("completed_text", "#d3d7dc"),
                )
            except Exception:
                pass

    def complete_task(self, task_id):
        task_id = str(task_id)

        if task_id in self.completed_pending_visual:
            return

        task = next((t for t in self.tasks if str(t.get("id", "")) == task_id), None)
        if not task:
            return

        self.completed_pending_visual.add(task_id)
        self.pending_complete_ids.add(task_id)

        self._apply_completed_visual_state(task_id)
        self.play_completion_sound()
        self.set_status("Completing task...", COLORS["text_secondary"])

        complete_task_async(self, task_id)

    def on_task_completed_confirmed(self, task_id):
        task_id = str(task_id)
        self.pending_complete_ids.discard(task_id)

    def on_task_completed_failed(self, task_id, error):
        task_id = str(task_id)
        self.pending_complete_ids.discard(task_id)
        self.completed_pending_visual.discard(task_id)
        self.render_tasks()
        self.set_status(f"Complete failed: {error}", COLORS["danger"])

    def on_task_completed_local(self, task_id):
        pass

    def submit_add_task(self):
        submit_add_task(self)

    def on_task_added(self):
        self.add_status_label.configure(text="Task added", text_color=COLORS["success"])
        self.clear_add_task_form()
        self.load_tasks(silent=True)

    def clear_add_task_form(self):
        clear_add_task_form(self)

    def on_recurring_change(self, value):
        on_recurring_change(self, value)

    def select_task_for_edit(self, task):
        select_task_for_edit(self, task)

    def clear_task_editor_form(self):
        clear_task_editor_form(self)

    def save_task_edit(self):
        save_task_edit(self)

    def on_task_saved(self, payload):
        task_id = str(payload.get("taskId", ""))
        for task in self.tasks:
            if str(task.get("id", "")) == task_id:
                task["name"] = payload["name"]
                task["project"] = payload["project"]
                task["priority"] = payload["priority"]
                task["nextDue"] = payload["nextDue"]
                task["notes"] = payload["notes"]
                task["url"] = payload["url"]
                self.selected_edit_task = task
                break
        self.ensure_project_filter_state()
        self.edit_info_label.configure(text="Changes saved", text_color=COLORS["success"])
        self.render_sort_rows()
        self.render_tasks()
        self.render_task_editor_list()

    def toggle_project(self, project):
        self.collapsed_projects[project] = not self.collapsed_projects.get(project, False)
        self.render_tasks()

    def set_status(self, text, color=None):
        self.status_label.configure(text=text, text_color=color or COLORS["text_secondary"])

    def play_completion_sound(self):
        if not self.settings.get("completion_sound") or winsound is None:
            return
        try:
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            pass


def main():
    app = TodoWidget()
    app.mainloop()


if __name__ == "__main__":
    main()