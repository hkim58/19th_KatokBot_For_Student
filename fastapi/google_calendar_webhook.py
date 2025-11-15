"""
FastAPI + Google Calendar MCP 예제 서버
---------------------------------------
이 서버는 메신저봇에서 전달한 자연어 명령을 받아 Google Calendar API를 호출합니다.

필수 환경 변수 (.env):
  GOOGLE_SERVICE_ACCOUNT_JSON=/path/to/service-account.json
  GOOGLE_CALENDAR_ID=primary
  CALENDAR_TIMEZONE=Asia/Seoul

실행:
  uvicorn google_calendar_webhook:app --host 0.0.0.0 --port 9000 --reload
"""

import os
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo
from typing import List, Tuple

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "service-account.json")
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")
TIMEZONE = os.getenv("CALENDAR_TIMEZONE", "Asia/Seoul")


def get_calendar_service():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build("calendar", "v3", credentials=creds, cache_discovery=False)


class CalendarRequest(BaseModel):
    room: str
    sender: str
    message: str


app = FastAPI(title="Google Calendar MCP Webhook")


def parse_relative_date(token: str) -> date:
    base = datetime.now().date()
    if token == "오늘":
        return base
    if token == "내일":
        return base + timedelta(days=1)
    if token == "모레":
        return base + timedelta(days=2)
    return datetime.strptime(token, "%Y-%m-%d").date()


def parse_show_command(msg: str) -> date:
    parts = msg.split()
    if len(parts) >= 3:
        try:
            return parse_relative_date(parts[2])
        except ValueError:
            pass
    return datetime.now().date()


def parse_add_command(msg: str) -> Tuple[date, time, str]:
    parts = msg.split()
    if len(parts) < 5:
        raise ValueError("사용법: 캘린더 추가 YYYY-MM-DD HH:MM 제목")
    try:
        target_date = parse_relative_date(parts[2])
    except ValueError:
        target_date = datetime.strptime(parts[2], "%Y-%m-%d").date()
    target_time = datetime.strptime(parts[3], "%H:%M").time()
    title = " ".join(parts[4:])
    return target_date, target_time, title


def parse_delete_command(msg: str) -> str:
    parts = msg.split()
    if len(parts) < 3:
        raise ValueError("사용법: 캘린더 삭제 <EVENT_ID>")
    return parts[2]


def format_events(events: List[dict]) -> str:
    if not events:
        return "📭 해당 날짜에는 일정이 없습니다."

    lines = ["🗓 일정 목록"]
    for ev in events:
        start = ev["start"].get("dateTime") or ev["start"].get("date")
        summary = ev.get("summary", "제목 없음")
        event_id = ev.get("id", "")
        lines.append("- {} ({}) [{}]".format(summary, start, event_id))
    return "\n".join(lines)


def list_day_events(target_date: date) -> str:
    tz = ZoneInfo(TIMEZONE)
    start_dt = datetime.combine(target_date, time.min).replace(tzinfo=tz)
    end_dt = start_dt + timedelta(days=1)
    service = get_calendar_service()
    events = (
        service.events()
        .list(
            calendarId=CALENDAR_ID,
            timeMin=start_dt.isoformat(),
            timeMax=end_dt.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
        .get("items", [])
    )
    return format_events(events)


def list_free_slots(target_date: date) -> str:
    tz = ZoneInfo(TIMEZONE)
    start_dt = datetime.combine(target_date, time(hour=9), tzinfo=tz)
    end_dt = datetime.combine(target_date, time(hour=19), tzinfo=tz)
    service = get_calendar_service()
    busy = (
        service.freebusy()
        .query(
            body={
                "timeMin": start_dt.isoformat(),
                "timeMax": end_dt.isoformat(),
                "items": [{"id": CALENDAR_ID}],
            }
        )
        .execute()
        .get("calendars", {})
        .get(CALENDAR_ID, {})
        .get("busy", [])
    )
    cursor = start_dt
    slots = []
    for block in busy:
        busy_start = datetime.fromisoformat(block["start"])
        busy_end = datetime.fromisoformat(block["end"])
        if cursor < busy_start:
            slots.append("{}~{}".format(cursor.time().strftime("%H:%M"), busy_start.time().strftime("%H:%M")))
        cursor = max(cursor, busy_end)
    if cursor < end_dt:
        slots.append("{}~{}".format(cursor.time().strftime("%H:%M"), end_dt.time().strftime("%H:%M")))
    if not slots:
        return "📅 해당 날짜에 빈 시간이 없습니다."
    return "🕒 빈 시간대:\n" + "\n".join(["- " + s for s in slots])


def create_event(target_date: date, target_time: time, title: str) -> str:
    tz = ZoneInfo(TIMEZONE)
    start_dt = datetime.combine(target_date, target_time, tzinfo=tz)
    end_dt = start_dt + timedelta(hours=1)
    service = get_calendar_service()

    conflicts = (
        service.events()
        .list(
            calendarId=CALENDAR_ID,
            timeMin=start_dt.isoformat(),
            timeMax=end_dt.isoformat(),
            singleEvents=True,
        )
        .execute()
        .get("items", [])
    )
    if conflicts:
        return "⚠️ 해당 시간에 이미 다른 일정이 있습니다:\n{}".format(
            "\n".join(["- " + c.get("summary", "제목 없음") for c in conflicts])
        )

    body = {
        "summary": title,
        "start": {"dateTime": start_dt.isoformat(), "timeZone": TIMEZONE},
        "end": {"dateTime": end_dt.isoformat(), "timeZone": TIMEZONE},
    }
    event = service.events().insert(calendarId=CALENDAR_ID, body=body).execute()
    return "✅ 일정이 등록되었습니다!\n제목: {}\nID: {}".format(event.get("summary"), event.get("id"))


def delete_event(event_id: str) -> str:
    service = get_calendar_service()
    service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
    return "🗑 일정이 삭제되었습니다. (ID: {})".format(event_id)


@app.post("/calendar/webhook")
async def calendar_webhook(req: CalendarRequest):
    message = req.message.strip()
    try:
        if message.startswith("캘린더 조회"):
            target_date = parse_show_command(message)
            return list_day_events(target_date)
        if message.startswith("캘린더 빈시간"):
            target_date = parse_show_command(message.replace("빈시간", "조회", 1))
            return list_free_slots(target_date)
        if message.startswith("캘린더 추가"):
            target_date, target_time, title = parse_add_command(message)
            return create_event(target_date, target_time, title)
        if message.startswith("캘린더 삭제"):
            event_id = parse_delete_command(message)
            return delete_event(event_id)
        return "지원하지 않는 명령입니다. 예) 캘린더 조회, 캘린더 추가, 캘린더 삭제"
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
