from datetime import datetime

from fastapi import FastAPI

app = FastAPI(title="Server Time API", version="1.0.0")


@app.get("/time")
def server_time() -> dict:
    now = datetime.now().astimezone()
    return {
        "server_time": now.isoformat(timespec="seconds"),
        "timezone": now.tzname(),
        "unix": int(now.timestamp()),
    }
