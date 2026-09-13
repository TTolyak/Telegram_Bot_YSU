from html import escape
from pathlib import Path
from datetime import date
import yaml


BASE_DIR = Path(__file__).resolve().parent
SCHEDULE_PATH = BASE_DIR / "schedule.yaml"

SEMESTER_START = date(2026, 9, 7) # меняем эту и следующую строку при новом семестре
START_PARITY = "denominator" # denominator - знаменатель; numerator - числитель


DAYS = {
    0: "monday", 1: "tuesday", 2: "wednesday", 3: "thursday",
    4: "friday", 5: "saturday", 6: "sunday",
    }

DAY_NAMES_RU = {
    "monday": "ПОНЕДЕЛЬНИК",
    "tuesday": "ВТОРНИК",
    "wednesday": "СРЕДА",
    "thursday": "ЧЕТВЕРГ",
    "friday": "ПЯТНИЦА",
    "saturday": "СУББОТА",
    "sunday": "Воскресенье",
}

PARITY_RU = {
    "numerator": "Неделя числителя",
    "denominator": "Неделя знаменателя",
}

WEEK_ORDER = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]


def load_schedule() -> dict:
    with open(SCHEDULE_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def current_day_key(today: date | None = None) -> str:
    today = today or date.today()
    return DAYS[today.weekday()]


def current_parity(today: date | None = None) -> str:
    today = today or date.today()
    if today < SEMESTER_START:
        raise ValueError("Семестр ещё не начался")
    n = (today - SEMESTER_START).days // 7
    if n % 2 == 0:
        return START_PARITY
    return "numerator" if START_PARITY == "denominator" else "denominator"


def render_schedule(schedule: dict, parity: str, days: list[str]) -> str:
    header = f"📅 <b>{PARITY_RU[parity]}</b>\n\n"
    blocks = []

    for day_key in days:
        pairs = schedule.get(parity, {}).get(day_key, []) or []
        if not pairs:
            continue

        day_header = f"<b>{DAY_NAMES_RU[day_key]}</b>"
        lines = []
        for p in pairs:
            lines.append(
                f"🕐 <b>{escape(p['time'])}</b>\n"
                f"📚 {escape(p['subject'])}\n"
                f"🚪 ауд. {escape(p['room'])}   👤 {escape(p['teacher'])}"
            )
        blocks.append(day_header + "\n" + "\n\n".join(lines))

    if not blocks:
        return f"На {PARITY_RU[parity]} неделе пар нет 🎉"

    return header + "\n\n\n".join(blocks)