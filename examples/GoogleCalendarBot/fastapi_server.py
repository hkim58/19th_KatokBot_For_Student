#!/usr/bin/env python3
"""
Google Calendar MCP 연동 FastAPI 서버 (완전 실용 버전)

기능:
- 메신저봇에서 오는 캘린더 요청 처리
- Google Calendar API를 통한 일정 CRUD
- 충돌 검사 및 빈 시간 조회
- OAuth 2.0 인증 관리

설치 필요 패키지:
pip install fastapi uvicorn google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv

사용법:
1. Google Cloud Console에서 Calendar API 활성화
2. OAuth 2.0 클라이언트 ID 생성 후 credentials.json 저장
3. .env 파일에 설정값 입력
4. python fastapi_server.py 실행
"""

import os
import json
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from pathlib import Path

# Google Calendar API
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# 환경 변수 로드
from dotenv import load_dotenv
load_dotenv()

# ====== 설정 ======
SCOPES = ['https://www.googleapis.com/auth/calendar']
CREDENTIALS_FILE = 'credentials.json'  # Google Cloud Console에서 다운로드한 파일
TOKEN_FILE = 'token.pickle'  # OAuth 토큰 저장 파일

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('calendar_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="Google Calendar MCP Server",
    description="메신저봇과 연동되는 Google Calendar API 서버",
    version="1.0.0"
)

# CORS 설정 (메신저봇에서 호출할 수 있도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====== 데이터 모델 ======

class EventRequest(BaseModel):
    action: str  # get_events, add_event, delete_event, check_free_time
    title: Optional[str] = None
    datetime: Optional[str] = None
    description: Optional[str] = None
    period: Optional[str] = "today"  # today, tomorrow, week
    event_id: Optional[str] = None
    date: Optional[str] = None

class CalendarEvent(BaseModel):
    id: str
    title: str
    start_time: str
    end_time: Optional[str] = None
    description: Optional[str] = None
    location: Optional[str] = None

# ====== Google Calendar 인증 ======

def get_calendar_service():
    """Google Calendar API 서비스 객체 반환"""
    creds = None
    
    # 기존 토큰 파일 확인
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    # 토큰이 없거나 유효하지 않은 경우 새로 인증
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(GoogleRequest())
                logger.info("Google OAuth 토큰 갱신 완료")
            except Exception as e:
                logger.error(f"토큰 갱신 실패: {e}")
                creds = None
        
        if not creds:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"{CREDENTIALS_FILE} 파일이 없습니다. "
                    "Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 다운로드하세요."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            logger.info("Google OAuth 새 인증 완료")
        
        # 토큰 저장
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    service = build('calendar', 'v3', credentials=creds)
    return service

# ====== 유틸리티 함수 ======

def parse_korean_date(date_str: str) -> datetime:
    """한글 날짜를 datetime 객체로 변환"""
    today = datetime.now()
    
    if date_str in ["오늘", "today"]:
        return today
    elif date_str in ["내일", "tomorrow"]:
        return today + timedelta(days=1)
    elif date_str in ["모레"]:
        return today + timedelta(days=2)
    else:
        try:
            # YYYY-MM-DD 형식 파싱
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            # 다른 형식 시도
            try:
                return datetime.strptime(date_str, "%m/%d")
            except ValueError:
                return today

def parse_relative_date(date_str: str) -> datetime:
    """상대적 날짜 문자열을 datetime 객체로 변환 (코덱스 피드백 반영)"""
    today = datetime.now()
    
    # 자연어 날짜 처리 강화
    if date_str in ["오늘", "today"]:
        return today
    elif date_str in ["내일", "tomorrow"]:
        return today + timedelta(days=1)
    elif date_str in ["모레", "day_after_tomorrow"]:
        return today + timedelta(days=2)
    elif date_str in ["이번주", "this_week"]:
        return today  # 주간 조회의 시작점
    elif date_str in ["다음주", "next_week"]:
        return today + timedelta(weeks=1)
    else:
        try:
            # YYYY-MM-DD 형식 파싱
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            # MM-DD 형식 시도
            try:
                this_year = today.year
                parsed = datetime.strptime(f"{this_year}-{date_str}", "%Y-%m-%d")
                return parsed
            except ValueError:
                # M/D 형식 시도
                try:
                    return datetime.strptime(f"{today.year}/{date_str}", "%Y/%m/%d")
                except ValueError:
                    logger.warning(f"날짜 파싱 실패, 기본값 사용: {date_str}")
                    return today

def parse_datetime_string(datetime_str: str) -> datetime:
    """날짜/시간 문자열을 datetime 객체로 변환 (자연어 처리 강화)"""
    today = datetime.now()
    
    # "내일 3시" / "내일 오후 3시" 형식 처리
    if "내일" in datetime_str:
        tomorrow = today + timedelta(days=1)
        if "시" in datetime_str:
            # 시간 추출 (숫자만)
            hour_match = re.search(r'(\d{1,2})', datetime_str)
            if hour_match:
                hour = int(hour_match.group(1))
                # 오후 처리
                if "오후" in datetime_str and hour != 12:
                    hour += 12
                elif "오전" in datetime_str and hour == 12:
                    hour = 0
                return tomorrow.replace(hour=hour, minute=0, second=0, microsecond=0)
        return tomorrow
    
    # "오늘 3시" / "오늘 오후 3시" 형식 처리
    elif "오늘" in datetime_str:
        if "시" in datetime_str:
            hour_match = re.search(r'(\d{1,2})', datetime_str)
            if hour_match:
                hour = int(hour_match.group(1))
                # 오후 처리
                if "오후" in datetime_str and hour != 12:
                    hour += 12
                elif "오전" in datetime_str and hour == 12:
                    hour = 0
                return today.replace(hour=hour, minute=0, second=0, microsecond=0)
        return today
    
    # "YYYY-MM-DD HH:MM" 형식 처리
    try:
        return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
    except ValueError:
        pass
    
    # "HH:MM" 형식 처리 (오늘 날짜에)
    try:
        time_only = datetime.strptime(datetime_str, "%H:%M").time()
        return datetime.combine(today.date(), time_only)
    except ValueError:
        pass
    
    # 기본값: 1시간 후
    logger.warning(f"시간 파싱 실패, 기본값 사용: {datetime_str}")
    return today + timedelta(hours=1)

def format_event_time(dt_str: str) -> str:
    """ISO 형식 시간을 한글 형식으로 변환"""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime("%m/%d %H:%M")
    except:
        return dt_str

def list_free_slots(target_date: datetime, working_hours_start: int = 9, working_hours_end: int = 19) -> List[str]:
    """특정 날짜의 빈 시간대 계산 (코덱스 피드백 반영 - FreeBusy API 활용)"""
    try:
        service = get_calendar_service()
        
        # 해당 날짜의 시작과 끝 시간 설정
        day_start = target_date.replace(hour=working_hours_start, minute=0, second=0, microsecond=0)
        day_end = target_date.replace(hour=working_hours_end, minute=0, second=0, microsecond=0)
        
        # Google Calendar FreeBusy API 호출
        freebusy_request = {
            "timeMin": day_start.isoformat() + 'Z',
            "timeMax": day_end.isoformat() + 'Z',
            "items": [{"id": "primary"}],
            "timeZone": "Asia/Seoul"
        }
        
        freebusy_result = service.freebusy().query(body=freebusy_request).execute()
        busy_times = freebusy_result.get('calendars', {}).get('primary', {}).get('busy', [])
        
        # 바쁜 시간대를 datetime 객체로 변환
        busy_intervals = []
        for busy in busy_times:
            start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
            end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
            busy_intervals.append((start, end))
        
        # 바쁜 시간대 정렬
        busy_intervals.sort(key=lambda x: x[0])
        
        # 빈 시간대 계산
        free_slots = []
        current_time = day_start
        
        for busy_start, busy_end in busy_intervals:
            # 현재 시간과 다음 바쁜 시간 사이에 여유가 있으면 추가
            if current_time < busy_start:
                free_slots.append(f"{current_time.strftime('%H:%M')} - {busy_start.strftime('%H:%M')}")
            current_time = max(current_time, busy_end)
        
        # 마지막 바쁜 시간 이후에 여유가 있으면 추가
        if current_time < day_end:
            free_slots.append(f"{current_time.strftime('%H:%M')} - {day_end.strftime('%H:%M')}")
        
        # 빈 시간이 없으면 안내 메시지
        if not free_slots:
            return [f"{working_hours_start}:00 - {working_hours_end}:00 시간대가 모두 사용 중입니다."]
        
        logger.info(f"빈 시간 조회 완료: {target_date.strftime('%Y-%m-%d')} ({len(free_slots)}개 구간)")
        return free_slots
        
    except Exception as e:
        logger.error(f"빈 시간 조회 실패: {e}")
        return [f"빈 시간 조회 중 오류 발생: {str(e)}"]

# ====== Calendar API 함수들 ======

def get_events_from_calendar(period: str = "today") -> List[CalendarEvent]:
    """Google Calendar에서 일정 조회"""
    try:
        service = get_calendar_service()
        
        # 시간 범위 설정
        now = datetime.now()
        if period == "today":
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=1)
        elif period == "tomorrow":
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            end_time = start_time + timedelta(days=1)
        elif period == "week":
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=7)
        else:
            start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(days=1)
        
        # Google Calendar API 호출
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_time.isoformat() + 'Z',
            timeMax=end_time.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        # CalendarEvent 객체로 변환
        calendar_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            calendar_event = CalendarEvent(
                id=event['id'],
                title=event.get('summary', '제목 없음'),
                start_time=format_event_time(start),
                end_time=format_event_time(end) if end else None,
                description=event.get('description', ''),
                location=event.get('location', '')
            )
            calendar_events.append(calendar_event)
        
        logger.info(f"일정 조회 완료: {len(calendar_events)}개")
        return calendar_events
        
    except Exception as e:
        logger.error(f"일정 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"일정 조회 실패: {str(e)}")

def add_event_to_calendar(title: str, datetime_str: str, description: str = "") -> Dict[str, Any]:
    """Google Calendar에 새 일정 추가"""
    try:
        service = get_calendar_service()
        
        # 날짜/시간 파싱
        start_datetime = parse_datetime_string(datetime_str)
        end_datetime = start_datetime + timedelta(hours=1)  # 기본 1시간 이벤트
        
        # 충돌 검사
        existing_events = service.events().list(
            calendarId='primary',
            timeMin=start_datetime.isoformat() + 'Z',
            timeMax=end_datetime.isoformat() + 'Z',
            singleEvents=True
        ).execute().get('items', [])
        
        warning_message = None
        if existing_events:
            conflict_titles = [event.get('summary', '제목없음') for event in existing_events]
            warning_message = f"충돌하는 일정이 있습니다: {', '.join(conflict_titles)}"
        
        # 이벤트 생성
        event = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'Asia/Seoul',
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'Asia/Seoul',
            },
        }
        
        # Calendar에 이벤트 추가
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        
        logger.info(f"일정 추가 완료: {title}")
        
        result = {
            "success": True,
            "event_id": created_event['id'],
            "message": "일정이 성공적으로 추가되었습니다."
        }
        
        if warning_message:
            result["warning"] = warning_message
            
        return result
        
    except Exception as e:
        logger.error(f"일정 추가 실패: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "일정 추가에 실패했습니다."
        }

def delete_event_from_calendar(event_number: str) -> Dict[str, Any]:
    """일정 삭제 (번호로)"""
    try:
        # 먼저 오늘 일정 조회해서 번호에 해당하는 이벤트 찾기
        events = get_events_from_calendar("today")
        
        try:
            index = int(event_number) - 1  # 1부터 시작하는 번호를 0부터 시작하는 인덱스로 변환
            if index < 0 or index >= len(events):
                return {
                    "success": False,
                    "message": "해당 번호의 일정을 찾을 수 없습니다."
                }
            
            event_to_delete = events[index]
            service = get_calendar_service()
            
            # Google Calendar에서 삭제
            service.events().delete(calendarId='primary', eventId=event_to_delete.id).execute()
            
            logger.info(f"일정 삭제 완료: {event_to_delete.title}")
            
            return {
                "success": True,
                "message": f"'{event_to_delete.title}' 일정이 삭제되었습니다."
            }
            
        except ValueError:
            return {
                "success": False,
                "message": "올바른 번호를 입력해주세요."
            }
            
    except Exception as e:
        logger.error(f"일정 삭제 실패: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "일정 삭제에 실패했습니다."
        }

def check_free_time(date_str: str) -> Dict[str, Any]:
    """특정 날짜의 빈 시간 조회 (코덱스 피드백 반영 - FreeBusy API 활용)"""
    try:
        target_date = parse_relative_date(date_str)
        
        # 빈 시간대 계산
        free_slots = list_free_slots(target_date)
        
        # 날짜 포맷팅
        date_formatted = target_date.strftime("%Y-%m-%d (%A)")
        korean_weekdays = {
            'Monday': '월요일', 'Tuesday': '화요일', 'Wednesday': '수요일', 
            'Thursday': '목요일', 'Friday': '금요일', 'Saturday': '토요일', 'Sunday': '일요일'
        }
        for eng, kor in korean_weekdays.items():
            date_formatted = date_formatted.replace(eng, kor)
        
        response = {
            "success": True,
            "date": date_formatted,
            "free_slots": free_slots,
            "message": f"🕐 {date_formatted} 빈 시간:\n\n" + 
                      "\n".join([f"⭕ {slot}" for slot in free_slots])
        }
        
        logger.info(f"빈 시간 조회 성공: {date_str} → {len(free_slots)}개 구간")
        return response
        
    except Exception as e:
        logger.error(f"빈 시간 조회 실패: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"빈 시간 조회 중 오류가 발생했습니다: {str(e)}"
        }

# ====== FastAPI 엔드포인트들 ======

@app.get("/")
async def root():
    """서버 상태 확인"""
    return {
        "message": "Google Calendar MCP 서버가 정상 작동 중입니다.",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/health")
async def health_check():
    """헬스체크 엔드포인트"""
    try:
        # Google Calendar API 연결 테스트
        service = get_calendar_service()
        calendar = service.calendars().get(calendarId='primary').execute()
        
        return {
            "success": True,
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "calendar_connected": True,
            "calendar_name": calendar.get('summary', 'Primary Calendar')
        }
    except Exception as e:
        logger.error(f"헬스체크 실패: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "status": "error",
                "error": str(e),
                "calendar_connected": False
            }
        )

@app.post("/api/calendar/events")
async def handle_calendar_events(request: EventRequest):
    """캘린더 이벤트 처리 (조회, 추가, 삭제)"""
    try:
        action = request.action.lower()
        
        if action == "get_events":
            events = get_events_from_calendar(request.period or "today")
            return {
                "success": True,
                "events": [event.dict() for event in events],
                "count": len(events)
            }
        
        elif action == "add_event":
            if not request.title or not request.datetime:
                raise HTTPException(status_code=400, detail="제목과 시간이 필요합니다.")
            
            result = add_event_to_calendar(
                request.title, 
                request.datetime, 
                request.description or ""
            )
            return result
        
        elif action == "delete_event":
            if not request.event_id:
                raise HTTPException(status_code=400, detail="삭제할 일정 번호가 필요합니다.")
            
            result = delete_event_from_calendar(request.event_id)
            return result
        
        else:
            raise HTTPException(status_code=400, detail="지원하지 않는 액션입니다.")
            
    except Exception as e:
        logger.error(f"이벤트 처리 실패: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "message": "요청 처리에 실패했습니다."
            }
        )

@app.post("/api/calendar/free-busy")
async def handle_free_busy(request: EventRequest):
    """빈 시간 조회"""
    try:
        if not request.date:
            request.date = "오늘"
        
        result = check_free_time(request.date)
        return result
        
    except Exception as e:
        logger.error(f"빈시간 조회 실패: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e),
                "message": "빈시간 조회에 실패했습니다."
            }
        )

@app.post("/webhook")
async def webhook_handler(request: Request):
    """메신저봇 웹훅 엔드포인트 (레거시 지원)"""
    try:
        data = await request.json()
        msg = data.get("msg", "")
        sender = data.get("sender", "")
        room = data.get("room", "")
        
        logger.info(f"웹훅 수신 - 방: {room}, 발신자: {sender}, 메시지: {msg}")
        
        # 자연어 명령어 처리 (코덱스 피드백 반영)
        if "일정" in msg and "보여줘" in msg:
            events = get_events_from_calendar("today")
            if events:
                response = "📅 오늘 일정:\n\n"
                for i, event in enumerate(events, 1):
                    response += f"{i}. {event.title} ({event.start_time})\n"
                return response
            else:
                return "📅 오늘 일정이 없습니다."
        
        # 빈시간 조회 명령어 처리
        elif "빈시간" in msg:
            date_str = "오늘"  # 기본값
            if "내일" in msg:
                date_str = "내일"
            elif "모레" in msg:
                date_str = "모레"
            # YYYY-MM-DD 형식 날짜 추출
            import re
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', msg)
            if date_match:
                date_str = date_match.group(1)
            
            result = check_free_time(date_str)
            return result.get("message", "빈시간 조회에 실패했습니다.")
        
        # 일정 추가 명령어 처리 (간단한 형태)
        elif "일정 추가" in msg:
            return "일정 추가 기능은 아직 웹훅에서 지원하지 않습니다. /api/calendar/events 엔드포인트를 사용해주세요."
        
        return "📅 사용 가능한 명령어:\n• '일정 보여줘' - 오늘 일정 조회\n• '빈시간 오늘/내일' - 빈 시간 확인"
        
    except Exception as e:
        logger.error(f"웹훅 처리 실패: {e}")
        return "서버 오류가 발생했습니다."

# ====== 서버 시작 ======

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 초기화"""
    logger.info("Google Calendar MCP 서버 시작됨")
    
    # 토큰 파일 확인
    if not os.path.exists(TOKEN_FILE):
        logger.warning("OAuth 토큰이 없습니다. 첫 API 호출 시 인증이 필요합니다.")
    
    # credentials.json 파일 확인
    if not os.path.exists(CREDENTIALS_FILE):
        logger.error(f"{CREDENTIALS_FILE} 파일이 없습니다!")
        logger.error("Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 다운로드하여 "
                    f"이 파일명으로 저장해주세요.")

@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료 시 정리"""
    logger.info("Google Calendar MCP 서버 종료됨")

if __name__ == "__main__":
    # 포트는 환경변수 또는 기본값 9000 사용
    port = int(os.getenv("PORT", 9000))
    
    logger.info(f"서버 시작: 포트 {port}")
    logger.info("API 문서: http://localhost:{port}/docs")
    
    uvicorn.run(
        "fastapi_server:app",  # 이 파일명이 fastapi_server.py라고 가정
        host="0.0.0.0",
        port=port,
        reload=True,  # 개발 중에는 True, 프로덕션에서는 False
        log_level="info"
    )

"""
====== 설치 및 실행 가이드 ======

1. 필요 패키지 설치:
   pip install fastapi uvicorn google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client python-dotenv

2. Google Cloud Console 설정:
   - Calendar API 활성화
   - OAuth 2.0 클라이언트 ID 생성
   - credentials.json 다운로드하여 이 파일과 같은 폴더에 저장

3. .env 파일 생성 (선택사항):
   PORT=9000

4. 서버 실행:
   python fastapi_server.py

5. 첫 실행 시 OAuth 인증:
   - 브라우저가 자동으로 열림
   - Google 계정으로 로그인
   - 캘린더 권한 승인
   - token.pickle 파일이 자동 생성됨

6. 테스트:
   - http://localhost:9000/docs 에서 API 문서 확인
   - http://localhost:9000/api/health 에서 헬스체크

====== 메신저봇과 연동 ======

1. 메신저봇 코드에서 SERVER_URL을 실제 서버 주소로 변경
2. 서버가 외부에서 접근 가능하도록 포트 개방 (방화벽 설정)
3. 메신저봇 컴파일 및 실행
4. 카톡방에서 테스트: "일정", "일정 추가 회의 내일 3시"

====== 주요 API 엔드포인트 ======

- GET /api/health : 서버 상태 확인
- POST /api/calendar/events : 일정 CRUD
- POST /api/calendar/free-busy : 빈시간 조회
- POST /webhook : 메신저봇 웹훅 (레거시)

====== 문제 해결 ======

- credentials.json 없음: Google Cloud Console에서 다운로드
- 권한 에러: OAuth 재인증 (token.pickle 삭제 후 재실행)
- 포트 에러: PORT 환경변수 변경
- 네트워크 에러: 방화벽/보안그룹 확인
"""