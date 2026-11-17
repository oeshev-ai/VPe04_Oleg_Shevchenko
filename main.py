from datetime import datetime

from fastapi import FastAPI

app = FastAPI(title="Server Time API", version="1.0.0")

WEEKDAYS = (
    "понедельник",
    "вторник",
    "среда",
    "четверг",
    "пятница",
    "суббота",
    "воскресенье",
)


def server_now() -> datetime:
    return datetime.now().astimezone()


@app.get("/time")
def server_time() -> dict:
    now = server_now()
    return {
        "server_time": now.isoformat(timespec="seconds"),
        "timezone": now.tzname(),
        "unix": int(now.timestamp()),
    }


@app.get("/date")
def server_date() -> dict:
    now = server_now()
    return {
        "date": now.date().isoformat(),
        "year": now.year,
        "month": now.month,
        "day": now.day,
        "weekday": WEEKDAYS[now.weekday()],
        "timezone": now.tzname(),
    }


@app.get("/datetime")
def server_datetime() -> dict:
    now = server_now()
    return {
        "datetime": now.isoformat(timespec="seconds"),
        "date": now.date().isoformat(),
        "time": now.strftime("%H:%M:%S"),
        "weekday": WEEKDAYS[now.weekday()],
        "timezone": now.tzname(),
        "unix": int(now.timestamp()),
    }
