import tkinter as tk
from datetime import datetime, timedelta

import pytz
import customtkinter as ctk

from logic.config import SCHEDULE_TZ
from logic.task_utils import project_colors
from ui.styles import COLORS, font

TZ = pytz.timezone(SCHEDULE_TZ)

PX_PER_MIN  = 2.0
DAY_START_H = 7
DAY_END_H   = 22
TIME_COL_W  = 60
TOP_PAD     = 16
PAD_R       = 10
SNAP_MINS   = 15
BUFFER_MINS = 15


# ── build ─────────────────────────────────────────────────────────────────────

def build_schedule_tab(app):
    app.schedule_tab = ctk.CTkFrame(app.tab_content, fg_color="transparent")
    app.schedule_tab.grid(row=0, column=0, sticky="nsew")
    app.schedule_tab.grid_columnconfigure(0, weight=1)
    app.schedule_tab.grid_rowconfigure(2, weight=1)

    # Header
    hdr = ctk.CTkFrame(app.schedule_tab, fg_color=COLORS["sort_bg"],
                        corner_radius=14, border_width=1, border_color=COLORS["border_soft"])
    hdr.grid(row=0, column=0, sticky="ew", pady=(0, 4))
    hdr.grid_columnconfigure(1, weight=1)

    app.schedule_date_label = ctk.CTkLabel(hdr, text="Today's Schedule",
        font=font(14, "bold"), text_color=COLORS["text_primary"])
    app.schedule_date_label.grid(row=0, column=0, sticky="w", padx=(14, 10), pady=10)

    app.schedule_status_label = ctk.CTkLabel(hdr, text="",
        font=font(11), text_color=COLORS["text_secondary"])
    app.schedule_status_label.grid(row=0, column=1, sticky="w")

    legend = ctk.CTkFrame(hdr, fg_color="transparent")
    legend.grid(row=0, column=2, sticky="e", padx=(0, 10))
    for color, lbl in [("#2e5a9c", "Calendar"), ("#1a6a3a", "Task"), ("#e53e3e", "Now")]:
        ctk.CTkFrame(legend, width=10, height=10, corner_radius=5, fg_color=color).pack(side="left", padx=(6, 2))
        ctk.CTkLabel(legend, text=lbl, font=font(10), text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 4))

    app.schedule_refresh_btn = ctk.CTkButton(hdr, text="Refresh", width=84, height=30,
        corner_radius=9, fg_color=COLORS["button_bg"], hover_color=COLORS["button_hover"],
        command=app.load_schedule)
    app.schedule_refresh_btn.grid(row=0, column=3, sticky="e", padx=(0, 12), pady=8)

    # Overflow / unscheduled task queue
    app.schedule_queue_frame = ctk.CTkFrame(app.schedule_tab, fg_color=COLORS["section_bg"],
        corner_radius=10, border_width=1, border_color=COLORS["border"])
    app.schedule_queue_frame.grid(row=1, column=0, sticky="ew", pady=(0, 4))

    app.schedule_queue_label = ctk.CTkLabel(app.schedule_queue_frame,
        text="Unscheduled — drag onto timeline:", font=font(11), text_color=COLORS["text_secondary"])
    app.schedule_queue_label.pack(anchor="w", padx=12, pady=(6, 2))

    app.schedule_queue_chips = ctk.CTkFrame(app.schedule_queue_frame, fg_color="transparent")
    app.schedule_queue_chips.pack(fill="x", padx=10, pady=(0, 8))

    # Timeline canvas
    host = ctk.CTkFrame(app.schedule_tab, fg_color=COLORS["section_bg"],
                         corner_radius=14, border_width=1, border_color=COLORS["border"])
    host.grid(row=2, column=0, sticky="nsew")
    host.grid_columnconfigure(0, weight=1)
    host.grid_rowconfigure(0, weight=1)

    wrap = tk.Frame(host, bg=COLORS["section_bg"])
    wrap.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
    wrap.grid_columnconfigure(0, weight=1)
    wrap.grid_rowconfigure(0, weight=1)

    app.schedule_canvas = tk.Canvas(wrap, bg="#0d1622", highlightthickness=0, bd=0)
    app.schedule_canvas.grid(row=0, column=0, sticky="nsew")

    sb = tk.Scrollbar(wrap, orient="vertical", command=app.schedule_canvas.yview)
    sb.grid(row=0, column=1, sticky="ns")
    app.schedule_canvas.configure(yscrollcommand=sb.set)

    app.schedule_canvas.bind("<Configure>",   lambda _e: _redraw_if_ready(app))
    app.schedule_canvas.bind("<MouseWheel>",  lambda e: app.schedule_canvas.yview_scroll(-1 * (e.delta // 120), "units"))
    app.schedule_canvas.bind("<ButtonPress-1>",   lambda e: _drag_press(app, e))
    app.schedule_canvas.bind("<B1-Motion>",        lambda e: _drag_motion(app, e))
    app.schedule_canvas.bind("<ButtonRelease-1>",  lambda e: _drag_release(app, e))

    app._schedule_result   = None
    app._schedule_completed_ids = set()
    app._sched_drag        = None


# ── render ────────────────────────────────────────────────────────────────────

def _redraw_if_ready(app):
    if app._schedule_result:
        render_schedule(app, app._schedule_result)


def render_schedule(app, result):
    app._schedule_result = result
    c = app.schedule_canvas
    c.delete("all")
    c.update_idletasks()

    cw      = c.winfo_width() or 640
    bx1     = TIME_COL_W + 4
    bx2     = cw - PAD_R
    total_h = int((DAY_END_H - DAY_START_H) * 60 * PX_PER_MIN) + TOP_PAD + 20

    # Grid lines + time labels
    for hour in range(DAY_START_H, DAY_END_H + 1):
        y = _ty((hour - DAY_START_H) * 60)
        c.create_line(TIME_COL_W, y, bx2, y, fill="#1a2d40", width=1)
        c.create_text(TIME_COL_W - 6, y, text=f"{hour:02d}:00",
                      fill="#3d5a70", font=("Courier", 9), anchor="e")
        if hour < DAY_END_H:
            yh = _ty((hour - DAY_START_H) * 60 + 30)
            c.create_line(TIME_COL_W, yh, bx2, yh, fill="#131e2b", width=1)
            c.create_text(TIME_COL_W - 6, yh, text=f"{hour:02d}:30",
                          fill="#253545", font=("Courier", 8), anchor="e")

    # Calendar events (no tag — not draggable)
    for item in result.get("timeline", []):
        if item["type"] != "event":
            continue
        y1 = _dt_y(item["start"])
        y2 = max(_dt_y(item["end"]), y1 + 22)
        _draw_block(c, bx1, y1, bx2, y2,
                    bg="#132840", border="#2e5a9c", accent="#4a8fd4",
                    title=item["title"],
                    subtitle=_tr(item["start"], item["end"]),
                    text_color="#a0c4f0")

    # Scheduled tasks (tagged — draggable)
    for item in result.get("timeline", []):
        if item["type"] != "task":
            continue
        task   = item["task"]
        tid    = str(task.get("id", ""))
        done   = tid in app._schedule_completed_ids
        accent, _, tcol = project_colors(task.get("project", ""))
        if done:
            accent, tcol = "#4a5568", "#6a7a8a"
        tag = f"sched_task_{tid}"
        _draw_block(c, bx1, _dt_y(item["start"]), bx2, max(_dt_y(item["end"]), _dt_y(item["start"]) + 22),
                    bg="#0e2218" if not done else "#1c1c2a",
                    border=accent + "90", accent=accent,
                    title=task.get("name", "Task"),
                    subtitle=f"{task.get('project','')}  ·  p{task.get('priority',0)}  ·  {_tr(item['start'],item['end'])}",
                    text_color=tcol, done=done, tag=tag)

    # Current time line
    now = datetime.now(tz=TZ)
    if DAY_START_H <= now.hour < DAY_END_H:
        ny = _dt_y(now)
        c.create_line(TIME_COL_W, ny, bx2, ny, fill="#e53e3e", width=2)
        c.create_oval(TIME_COL_W - 5, ny - 5, TIME_COL_W + 5, ny + 5, fill="#e53e3e", outline="")

    c.configure(scrollregion=(0, 0, cw, total_h))

    # Overflow chips
    _render_queue(app, result.get("overflow", []))

    # Date label
    d = result.get("date")
    if d:
        try:
            app.schedule_date_label.configure(text=d.strftime("Schedule — %A %-d %B %Y"))
        except Exception:
            app.schedule_date_label.configure(text=d.strftime("Schedule — %A %d %B %Y"))


def _render_queue(app, overflow_tasks):
    for w in app.schedule_queue_chips.winfo_children():
        w.destroy()

    if not overflow_tasks:
        app.schedule_queue_label.configure(text="All tasks scheduled ✓")
        return

    app.schedule_queue_label.configure(
        text=f"Unscheduled ({len(overflow_tasks)}) — drag onto timeline:")

    for task in overflow_tasks:
        accent, _, _ = project_colors(task.get("project", ""))
        chip = ctk.CTkFrame(app.schedule_queue_chips, fg_color=COLORS["card_bg"],
                             corner_radius=8, border_width=1, border_color=accent + "80")
        chip.pack(side="left", padx=(0, 6), pady=2)

        ctk.CTkLabel(chip, text=task.get("name", "Task")[:22],
                     font=font(11, "bold"), text_color="#d0e8ff").pack(
            anchor="w", padx=8, pady=(4, 0))
        ctk.CTkLabel(chip,
                     text=f"{task.get('project','')}  ·  {task.get('duration',30)}min",
                     font=font(10), text_color=COLORS["text_secondary"]).pack(
            anchor="w", padx=8, pady=(0, 4))

        # Bind drag from chip onto canvas
        for widget in (chip, *chip.winfo_children()):
            widget.bind("<ButtonPress-1>",  lambda e, t=task: _chip_press(app, e, t))
            widget.bind("<B1-Motion>",       lambda e: _chip_motion(app, e))
            widget.bind("<ButtonRelease-1>", lambda e: _chip_release(app, e))


# ── canvas drag (scheduled tasks) ─────────────────────────────────────────────

def _drag_press(app, event):
    cy  = app.schedule_canvas.canvasy(event.y)
    items = app.schedule_canvas.find_overlapping(event.x - 2, cy - 2, event.x + 2, cy + 2)
    for item in reversed(list(items)):
        for tag in app.schedule_canvas.gettags(item):
            if tag.startswith("sched_task_"):
                tid  = tag[len("sched_task_"):]
                bbox = app.schedule_canvas.bbox(f"sched_task_{tid}")
                if bbox:
                    app._sched_drag = {
                        "tid": tid, "press_cy": cy,
                        "last_cy": cy, "moved": False,
                        "y1": bbox[1], "y2": bbox[3],
                    }
                    app.schedule_canvas.config(cursor="fleur")
                return


def _drag_motion(app, event):
    if not app._sched_drag:
        return
    cy    = app.schedule_canvas.canvasy(event.y)
    delta = cy - app._sched_drag["last_cy"]
    app._sched_drag["last_cy"] = cy
    if abs(cy - app._sched_drag["press_cy"]) > 4:
        app._sched_drag["moved"] = True
    app.schedule_canvas.move(f"sched_task_{app._sched_drag['tid']}", 0, delta)


def _drag_release(app, event):
    if not app._sched_drag:
        return
    drag = app._sched_drag
    app._sched_drag = None
    app.schedule_canvas.config(cursor="")

    if not drag["moved"]:
        _toggle_done(app, drag["tid"])
        return

    cy       = app.schedule_canvas.canvasy(event.y)
    dy       = cy - drag["press_cy"]
    new_y1   = drag["y1"] + dy
    _apply_drag(app, drag["tid"], new_y1)


def _apply_drag(app, tid, new_y1):
    result = app._schedule_result
    today  = result["date"]
    events = [i for i in result["timeline"] if i["type"] == "event"]

    # Snap y → time
    mins_raw      = (new_y1 - TOP_PAD) / PX_PER_MIN
    snapped_mins  = round(mins_raw / SNAP_MINS) * SNAP_MINS
    snapped_mins  = max(0, min((DAY_END_H - DAY_START_H) * 60 - SNAP_MINS, snapped_mins))
    start_h = DAY_START_H + int(snapped_mins // 60)
    start_m = int(snapped_mins % 60)

    for item in result["timeline"]:
        if item["type"] != "task":
            continue
        if str(item["task"].get("id", "")) != tid:
            continue

        duration    = item["end"] - item["start"]
        new_start   = TZ.localize(datetime(today.year, today.month, today.day, start_h, start_m))
        new_end     = new_start + duration
        day_end     = TZ.localize(datetime(today.year, today.month, today.day, DAY_END_H, 0))
        buf         = timedelta(minutes=BUFFER_MINS)

        conflict = (new_end > day_end) or any(
            new_start < e["end"] + buf and new_end > e["start"] - buf
            for e in events
        )

        if not conflict:
            item["start"] = new_start
            item["end"]   = new_end
        break

    render_schedule(app, result)


# ── chip drag (overflow tasks → canvas) ───────────────────────────────────────

def _chip_press(app, event, task):
    ghost = tk.Label(app, text=f"  {task.get('name','')[:20]}  ",
                     bg="#1e3a5a", fg="#c0deff", font=("Helvetica", 10),
                     relief="solid", bd=1, cursor="fleur")
    ghost.place(x=event.x_root - app.winfo_rootx(),
                y=event.y_root - app.winfo_rooty())
    app._chip_drag = {"task": task, "ghost": ghost}


def _chip_motion(app, event):
    if not getattr(app, "_chip_drag", None):
        return
    x = event.x_root - app.winfo_rootx() - 40
    y = event.y_root - app.winfo_rooty() - 10
    app._chip_drag["ghost"].place(x=x, y=y)


def _chip_release(app, event):
    if not getattr(app, "_chip_drag", None):
        return
    drag = app._chip_drag
    app._chip_drag = None
    drag["ghost"].destroy()

    c   = app.schedule_canvas
    cx1 = c.winfo_rootx()
    cy1 = c.winfo_rooty()
    cw  = c.winfo_width()
    ch  = c.winfo_height()

    # Only place if dropped over the canvas
    if not (cx1 <= event.x_root <= cx1 + cw and cy1 <= event.y_root <= cy1 + ch):
        return

    canvas_y  = (event.y_root - cy1) + c.canvasy(0)
    mins_raw  = (canvas_y - TOP_PAD) / PX_PER_MIN
    snapped   = round(mins_raw / SNAP_MINS) * SNAP_MINS
    snapped   = max(0, min((DAY_END_H - DAY_START_H) * 60 - SNAP_MINS, snapped))
    start_h   = DAY_START_H + int(snapped // 60)
    start_m   = int(snapped % 60)

    result  = app._schedule_result
    today   = result["date"]
    task    = drag["task"]
    dur_min = max(15, int(task.get("duration", 30)))
    events  = [i for i in result["timeline"] if i["type"] == "event"]

    new_start = TZ.localize(datetime(today.year, today.month, today.day, start_h, start_m))
    new_end   = new_start + timedelta(minutes=dur_min)
    day_end   = TZ.localize(datetime(today.year, today.month, today.day, DAY_END_H, 0))
    buf       = timedelta(minutes=BUFFER_MINS)

    conflict = (new_end > day_end) or any(
        new_start < e["end"] + buf and new_end > e["start"] - buf
        for e in events
    )

    if conflict:
        return  # silently reject — keep in overflow

    # Move from overflow → timeline
    result["overflow"] = [t for t in result.get("overflow", []) if str(t.get("id")) != str(task.get("id"))]
    result["timeline"].append({
        "type": "task",
        "task": task,
        "start": new_start,
        "end": new_end,
        "completed": False,
    })
    result["timeline"].sort(key=lambda x: x["start"])
    render_schedule(app, result)


# ── helpers ───────────────────────────────────────────────────────────────────

def _toggle_done(app, tid):
    if tid in app._schedule_completed_ids:
        app._schedule_completed_ids.discard(tid)
    else:
        app._schedule_completed_ids.add(tid)
    if app._schedule_result:
        render_schedule(app, app._schedule_result)


def _draw_block(c, x1, y1, x2, y2, bg, border, accent,
                title, subtitle="", text_color="#f0f0f2", done=False, tag=None):
    kw = {"tags": tag} if tag else {}
    c.create_rectangle(x1, y1, x2, y2, fill=bg, outline=border, width=1, **kw)
    c.create_rectangle(x1, y1, x1 + 3, y2, fill=accent, outline="", **kw)
    tx = x1 + 10
    tall = (y2 - y1) > 30
    if tall:
        c.create_text(tx, y1 + 7,  text=title,    fill=text_color, anchor="nw",
                      font=("Helvetica", 11, "bold"), **kw)
        if subtitle:
            c.create_text(tx, y1 + 22, text=subtitle, fill="#4a6070", anchor="nw",
                          font=("Courier", 9), **kw)
    else:
        c.create_text(tx, (y1 + y2) // 2, text=title, fill=text_color, anchor="w",
                      font=("Helvetica", 10), **kw)
    if done:
        mid = (y1 + y2) // 2
        c.create_line(x1 + 6, mid, x2 - 6, mid, fill="#4a5568", width=1, **kw)


def _ty(mins_from_start):
    return int(mins_from_start * PX_PER_MIN) + TOP_PAD


def _dt_y(dt):
    return _ty(dt.hour * 60 + dt.minute - DAY_START_H * 60)


def _tr(start, end):
    return start.strftime("%H:%M") + "–" + end.strftime("%H:%M")


def scroll_to_now(app):
    now          = datetime.now(tz=TZ)
    total_min    = (DAY_END_H - DAY_START_H) * 60
    total_h      = total_min * PX_PER_MIN + TOP_PAD
    mins_elapsed = now.hour * 60 + now.minute - DAY_START_H * 60
    frac = max(0.0, min(1.0, (mins_elapsed * PX_PER_MIN - 120) / total_h))
    app.schedule_canvas.yview_moveto(frac)
