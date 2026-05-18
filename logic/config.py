import os
from pathlib import Path

BASE_URL = "https://script.google.com/macros/s/AKfycbzAkoPEaYa5Ys7GTZK8v-60i1x5jgsFLnkkVqfhdl1zGYjIq4SUGTxBUuv7d0LOpb-4pg/exec"
ICON_PATH = Path(__file__).resolve().parent.parent / "Assets" / "icons" / "app.ico"
DEFAULT_WEATHER_LOCATION = "Otorohanga, New Zealand"
DEFAULT_SETTINGS = {
    "task_height": 48,
    "font_size": 14,
    "auto_refresh_sec": 60,
    "completion_sound": True,
    "sorter_collapsed_on_start": True,
}

ICLOUD_USERNAME = "pouroaf@gmail.com"
ICLOUD_PASSWORD = os.environ.get("TODO_WIDGET_ICLOUD_PASSWORD", "")
ICLOUD_CALDAV_URL = "https://caldav.icloud.com"
SCHEDULE_TZ = "Pacific/Auckland"
