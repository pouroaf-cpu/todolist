import threading
from datetime import datetime, date, timedelta, time as dtime

import pytz

from logic.config import ICLOUD_USERNAME, ICLOUD_PASSWORD, ICLOUD_CALDAV_URL, SCHEDULE_TZ

TZ = pytz.timezone(SCHEDULE_TZ)
DAY_START_HOUR = 7
DAY_END_HOUR = 22
BUFFER_MINUTES = 15


def fetch_and_schedule_async(app, callback):
    def worker():
        try:
            today = date.today()

            cal_error = None
            try:
                events = _fetch_calendar_events(today)
            except Exception as e:
                events = []
                cal_error = str(e)

            # Use app.tasks if populated, otherwise fetch fresh from API
            tasks = list(app.tasks or [])
            if not tasks:
                try:
                    tasks = _fetch_tasks_sync()
                except Exception:
                    tasks = []

            result = _build_schedule(events, tasks, today)
            result["cal_error"] = cal_error
            app.after(0, lambda r=result: callback(r, None))
        except Exception as e:
            app.after(0, lambda err=str(e): callback(None, err))
    threading.Thread(target=worker, daemon=True).start()


def _fetch_tasks_sync():
    import requests
    from logic.config import BASE_URL
    from logic.task_utils import normalize_task, parse_tasks_from_response
    response = requests.get(BASE_URL, params={"view": "today"}, timeout=20)
    data = response.json()
    tasks = [normalize_task(item) for item in parse_tasks_from_response(data)]
    return [t for t in tasks if t]


# ── CalDAV fetch ─────────────────────────────────────────────────────────────

def _fetch_calendar_events(today):
    import caldav
    from icalendar import vDatetime

    start = TZ.localize(datetime.combine(today, dtime(0, 0, 0)))
    end = TZ.localize(datetime.combine(today, dtime(23, 59, 59)))

    client = caldav.DAVClient(
        url=ICLOUD_CALDAV_URL,
        username=ICLOUD_USERNAME,
        password=ICLOUD_PASSWORD,
    )
    principal = client.principal()
    calendars = principal.calendars()

    events = []
    for cal in calendars:
        try:
            for event in cal.date_search(start=start, end=end, expand=True):
                parsed = _parse_event(event)
                if parsed:
                    events.append(parsed)
        except Exception:
            continue

    events.sort(key=lambda e: e["start"])
    return events


def _parse_event(event):
    try:
        comp = event.icalendar_component
        summary = str(comp.get("SUMMARY", "Event"))

        dtstart = comp.decoded("DTSTART")
        if isinstance(dtstart, date) and not isinstance(dtstart, datetime):
            return None  # skip all-day events

        dtend = comp.decoded("DTEND") if "DTEND" in comp else dtstart + timedelta(hours=1)
        if isinstance(dtend, date) and not isinstance(dtend, datetime):
            return None

        # Normalise to NZ tz
        if dtstart.tzinfo is None:
            dtstart = pytz.utc.localize(dtstart)
        dtstart = dtstart.astimezone(TZ)

        if dtend.tzinfo is None:
            dtend = pytz.utc.localize(dtend)
        dtend = dtend.astimezone(TZ)

        return {"title": summary, "start": dtstart, "end": dtend, "type": "event"}
    except Exception:
        return None


# ── Scheduler ────────────────────────────────────────────────────────────────

def _build_schedule(events, tasks, today):
    day_start = TZ.localize(datetime.combine(today, dtime(DAY_START_HOUR, 0)))
    day_end = TZ.localize(datetime.combine(today, dtime(DAY_END_HOUR, 0)))

    free_slots = _build_free_slots(events, day_start, day_end)

    # Sort: priority desc, then cluster by project
    sorted_tasks = sorted(tasks, key=lambda t: (-int(t.get("priority", 0)), t.get("project", "")))

    scheduled = []
    overflow = []

    for task in sorted_tasks:
        duration_min = max(15, int(task.get("duration", 30)))
        preferred_window = str(task.get("preferredWindow", "")).strip()

        slot = None

        if preferred_window:
            pref_start, pref_end = _parse_window(preferred_window, today)
            if pref_start and pref_end:
                slot = _find_slot_in_range(free_slots, pref_start, pref_end, duration_min)

        if not slot:
            slot = _find_next_slot(free_slots, duration_min)

        if slot:
            task_start, task_end = slot
            _consume_slot(free_slots, task_start, task_end)
            scheduled.append({
                "type": "task",
                "task": task,
                "start": task_start,
                "end": task_end,
                "completed": False,
            })
        else:
            overflow.append(task)

    timeline = [{"type": "event", "title": e["title"], "start": e["start"], "end": e["end"]} for e in events]
    timeline.extend(scheduled)
    timeline.sort(key=lambda x: x["start"])

    return {
        "timeline": timeline,
        "overflow": overflow,
        "day_start": day_start,
        "day_end": day_end,
        "date": today,
    }


def _build_free_slots(events, day_start, day_end):
    blocked = []
    for e in events:
        b_start = max(e["start"] - timedelta(minutes=BUFFER_MINUTES), day_start)
        b_end = min(e["end"] + timedelta(minutes=BUFFER_MINUTES), day_end)
        if b_start < b_end:
            blocked.append([b_start, b_end])

    blocked.sort(key=lambda x: x[0])
    merged = []
    for b in blocked:
        if merged and b[0] <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], b[1])
        else:
            merged.append(list(b))

    free = []
    cursor = day_start
    for b_start, b_end in merged:
        if cursor < b_start:
            free.append([cursor, b_start])
        cursor = max(cursor, b_end)
    if cursor < day_end:
        free.append([cursor, day_end])

    return free


def _find_slot_in_range(free_slots, range_start, range_end, duration_min):
    duration = timedelta(minutes=duration_min)
    for slot in free_slots:
        s = max(slot[0], range_start)
        e = min(slot[1], range_end)
        if e - s >= duration:
            return (s, s + duration)
    return None


def _find_next_slot(free_slots, duration_min):
    duration = timedelta(minutes=duration_min)
    for slot in free_slots:
        if slot[1] - slot[0] >= duration:
            return (slot[0], slot[0] + duration)
    return None


def _consume_slot(free_slots, task_start, task_end):
    for i, slot in enumerate(free_slots):
        if slot[0] <= task_start and task_end <= slot[1]:
            left = [slot[0], task_start]
            right = [task_end, slot[1]]
            free_slots[i:i + 1] = [s for s in [left, right] if s[0] < s[1]]
            return


def _parse_window(window_str, today):
    try:
        parts = window_str.strip().split("-")
        if len(parts) != 2:
            return None, None
        sh, sm = map(int, parts[0].strip().split(":"))
        eh, em = map(int, parts[1].strip().split(":"))
        start = TZ.localize(datetime.combine(today, dtime(sh, sm)))
        end = TZ.localize(datetime.combine(today, dtime(eh, em)))
        return start, end
    except Exception:
        return None, None
