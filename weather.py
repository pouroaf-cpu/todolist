# weather.py

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Dict, Any, Optional
import requests


GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


@dataclass
class WeatherSlot:
    label: str
    temp: int
    rain: int
    icon: str


def weather_code_to_icon(code: Optional[int], is_day: bool = True) -> str:
    if code is None:
        return "•"

    code = int(code)

    if code == 0:
        return "☀" if is_day else "☾"
    if code in (1, 2):
        return "⛅" if is_day else "☁"
    if code == 3:
        return "☁"
    if code in (45, 48):
        return "🌫"
    if code in (51, 53, 55, 56, 57):
        return "🌦"
    if code in (61, 63, 65, 66, 67, 80, 81, 82):
        return "🌧"
    if code in (71, 73, 75, 77, 85, 86):
        return "❄"
    if code in (95, 96, 99):
        return "⛈"

    return "☁"


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(round(float(value)))
    except Exception:
        return default


def _hour_label(dt: datetime) -> str:
    hour = dt.strftime("%I").lstrip("0") or "12"
    suffix = dt.strftime("%p").lower()
    return f"{hour}{suffix}"


def _find_tomorrow_midday_index(times: List[str], tomorrow_date: str) -> int:
    candidates = []

    for i, time_str in enumerate(times):
        if not time_str.startswith(tomorrow_date):
            continue

        try:
            dt = datetime.fromisoformat(time_str)
            score = abs(dt.hour - 12)
            candidates.append((score, i))
        except Exception:
            continue

    if not candidates:
        raise ValueError("No hourly entries found for tomorrow")

    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]


def _geocode_location(location: str) -> Dict[str, Any]:
    response = requests.get(
        GEOCODE_URL,
        params={
            "name": location,
            "count": 1,
            "language": "en",
            "format": "json",
        },
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    results = data.get("results") or []
    if not results:
        raise ValueError(f"Location not found: {location}")

    return results[0]


def _fetch_forecast(latitude: float, longitude: float) -> Dict[str, Any]:
    response = requests.get(
        FORECAST_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "timezone": "auto",
            "forecast_days": 3,
            "current": "temperature_2m,precipitation_probability,weather_code,is_day",
            "hourly": "temperature_2m,precipitation_probability,weather_code,is_day",
        },
        timeout=15,
    )
    response.raise_for_status()
    return response.json()


def get_weather_slots(location: str = "Otorohanga, New Zealand") -> List[Dict[str, Any]]:
    """
    Returns 7 equal weather cards:
    1. Now
    2. +1 hour
    3. +2 hours
    4. +3 hours
    5. +4 hours
    6. +5 hours
    7. Tomorrow (closest to 12pm)
    """
    place = _geocode_location(location)
    latitude = place["latitude"]
    longitude = place["longitude"]

    forecast = _fetch_forecast(latitude, longitude)

    current = forecast.get("current", {})
    hourly = forecast.get("hourly", {})
    times = hourly.get("time", [])
    temps = hourly.get("temperature_2m", [])
    rains = hourly.get("precipitation_probability", [])
    codes = hourly.get("weather_code", [])
    is_days = hourly.get("is_day", [])

    if not times or len(times) < 6:
        raise ValueError("Not enough hourly weather data returned")

    now_dt = datetime.fromisoformat(current["time"])
    now_date = now_dt.date()
    tomorrow_date = now_date.fromordinal(now_date.toordinal() + 1).isoformat()

    current_slot = WeatherSlot(
        label="Now",
        temp=_safe_int(current.get("temperature_2m")),
        rain=_safe_int(current.get("precipitation_probability")),
        icon=weather_code_to_icon(
            current.get("weather_code"),
            bool(current.get("is_day", 1)),
        ),
    )

    upcoming_slots: List[WeatherSlot] = []
    future_indexes = []

    for i, time_str in enumerate(times):
        try:
            dt = datetime.fromisoformat(time_str)
        except Exception:
            continue

        if dt > now_dt:
            future_indexes.append(i)

        if len(future_indexes) >= 5:
            break

    if len(future_indexes) < 5:
        raise ValueError("Not enough future hourly slots returned")

    for idx in future_indexes[:5]:
        dt = datetime.fromisoformat(times[idx])
        upcoming_slots.append(
            WeatherSlot(
                label=_hour_label(dt),
                temp=_safe_int(temps[idx]),
                rain=_safe_int(rains[idx]),
                icon=weather_code_to_icon(codes[idx], bool(is_days[idx])),
            )
        )

    tomorrow_idx = _find_tomorrow_midday_index(times, tomorrow_date)
    tomorrow_slot = WeatherSlot(
        label="Tomorrow",
        temp=_safe_int(temps[tomorrow_idx]),
        rain=_safe_int(rains[tomorrow_idx]),
        icon=weather_code_to_icon(codes[tomorrow_idx], bool(is_days[tomorrow_idx])),
    )

    slots = [current_slot] + upcoming_slots + [tomorrow_slot]
    return [asdict(slot) for slot in slots]


if __name__ == "__main__":
    data = get_weather_slots("Otorohanga, New Zealand")
    for item in data:
        print(item)