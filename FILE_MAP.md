# todo_widget — File Map

## Entry Points
- `main.py` — App entry point; initialises Tkinter main window and launches the widget.
- `weather.py` — Weather data integration module used in the widget header.
- `main.spec` / `todo_widget.spec` — PyInstaller build specs for compiling to Windows .exe.

## Logic Layer (`logic/`)
- `logic/api.py` — External API calls and data access (task storage backend).
- `logic/config.py` — App configuration constants and settings.
- `logic/schedule.py` — Task scheduling and recurrence logic.
- `logic/task_utils.py` — Utility functions for task manipulation and filtering.

## UI Layer (`ui/`)
- `ui/header.py` — Top header widget (date, weather, summary stats).
- `ui/styles.py` — UI style constants (colours, fonts, padding).
- `ui/components/forms.py` — Form input components.
- `ui/components/project_group.py` — Project grouping container widget.
- `ui/components/task_card.py` — Individual task card widget.
- `ui/tabs/add_task.py` — Add task tab UI.
- `ui/tabs/completed_today.py` — Completed tasks tab UI.
- `ui/tabs/current_tasks.py` — Current tasks tab UI.
- `ui/tabs/schedule.py` — Schedule view tab UI.
- `ui/tabs/task_editor.py` — Task detail editor panel.

## Web Interface (`web/`)
- `web/app.jsx` — React web interface for the widget (browser-based version).
- `web/data.js` — Data layer for the web interface.

## Assets & Build
- `Assets/icons/app.ico` — Application icon for taskbar.
- `taskfocus_icon.ico` — System tray icon.
- `complete.wav` — Audio cue played on task completion.
- `dist/todo_widget.exe` — Built Windows executable (output of PyInstaller).
- `build/` — PyInstaller intermediate build artefacts.

## Docs
- `HANDOFF.md` — Agent handoff notes.
- `CLAUDE.md` — Claude Code session instructions.
- `AGENTS.md` — Codex agent instructions.
