#!/usr/bin/env python3
"""
Google Calendar 서비스 계정 기반 FastAPI 서버 (개선된 버전)

특징:
- 코덱스 방식 채택: 서비스 계정으로 간단한 인증
- 명령어 파싱을 서버에서 집중 처리
- 환경변수 3개만 설정하면 바로 실행
- uvicorn 한 줄로 서버 시작

설치:
pip install fastapi uvicorn google-api-python-client google-auth python-dotenv

사용법:
1. .env 파일에 서비스 계정 정보 설정
2. uvicorn google_calendar_service:app --host 0.0.0.0 --port 9000
"""

import os
import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging

# Google Calendar API (서비스 계정 방식)
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# 환경 변수
from dotenv import load_dotenv
load_dotenv()

# ====== 설정 ======

# 환경 변수에서 설정 로드
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")  
CALENDAR_TIMEZONE = os.getenv("CALENDAR_TIMEZONE", "Asia/Seoul")

# Google Calendar API 스코프
SCOPES = ['https://www.googleapis.com/auth/calendar']

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('calendar_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# FastAPI 앱
app = FastAPI(
    title="Google Calendar Service (코덱스 방식)",
    description="서비스 계정 기반 Google Calendar API 서버",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====== 데이터 모델 ======

class WebhookRequest(BaseModel):
    command: str
    room: str
    author: str
    timestamp: str

# ====== Google Calendar 서비스 초기화 ======

def get_calendar_service():
    """서비스 계정을 사용하여 Google Calendar 서비스 객체 반환"""
    try:
        if not GOOGLE_SERVICE_ACCOUNT_JSON:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON 환경변수가 설정되지 않았습니다.")
        
        # 서비스 계정 JSON 파싱
        if os.path.isfile(GOOGLE_SERVICE_ACCOUNT_JSON):
            # 파일 경로인 경우
            credentials = service_account.Credentials.from_service_account_file(
                GOOGLE_SERVICE_ACCOUNT_JSON, scopes=SCOPES
            )
        else:
            # JSON 문자열인 경우
            service_account_info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
            credentials = service_account.Credentials.from_service_account_info(
                service_account_info, scopes=SCOPES
            )
        
        service = build('calendar', 'v3', credentials=credentials)
        logger.info("Google Calendar 서비스 연결 성공")
        return service
        
    except Exception as e:
        logger.error(f"Google Calendar 서비스 연결 실패: {e}")
        raise

# ====== 명령어 파싱 함수들 ======

def parse_date(date_str: str) -> str:
    """날짜 문자열을 ISO 형식으로 변환"""
    try:
        # YYYY-MM-DD 형식 확인
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return date_str
        
        # 상대적 날짜 처리
        today = datetime.now()
        if date_str == "오늘":
            return today.strftime("%Y-%m-%d")
        elif date_str == "내일":
            return (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif date_str == "모레":
            return (today + timedelta(days=2)).strftime("%Y-%m-%d")
        
        return date_str  # 기본값
        
    except Exception as e:
        logger.error(f"날짜 파싱 실패: {e}")
        return datetime.now().strftime("%Y-%m-%d")

def parse_datetime(date_str: str, time_str: str) -> datetime:
    """날짜와 시간을 datetime 객체로 변환"""
    try:
        date = parse_date(date_str)
        
        # 시간 파싱 (HH:MM 형식)
        if ':' in time_str:
            hour, minute = map(int, time_str.split(':'))
        else:
            # 시간만 있는 경우 (예: "14")
            hour = int(time_str.replace('시', ''))
            minute = 0
        
        dt = datetime.strptime(f"{date} {hour:02d}:{minute:02d}", "%Y-%m-%d %H:%M")
        return dt
        
    except Exception as e:
        logger.error(f"날짜/시간 파싱 실패: {e}")
        # 기본값: 1시간 후
        return datetime.now() + timedelta(hours=1)

# ====== Calendar API 함수들 ======

def get_events_for_date(date_str: str) -> List[Dict[str, Any]]:
    """특정 날짜의 일정 조회"""
    try:
        service = get_calendar_service()
        
        # 날짜 범위 설정
        target_date = parse_date(date_str)
        start_datetime = datetime.strptime(target_date, "%Y-%m-%d")
        end_datetime = start_datetime + timedelta(days=1)
        
        # Google Calendar API 호출
        events_result = service.events().list(
            calendarId=GOOGLE_CALENDAR_ID,
            timeMin=start_datetime.isoformat() + 'Z',
            timeMax=end_datetime.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return []
        
        # 이벤트 정보 정리
        event_list = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            # 시간 포맷팅
            if 'T' in start:  # datetime 형식
                start_time = datetime.fromisoformat(start.replace('Z', '+00:00')).strftime("%H:%M")
            else:  # date 형식 (종일 일정)
                start_time = "종일"
                
            event_info = {
                'id': event['id'],
                'title': event.get('summary', '제목 없음'),
                'start_time': start_time,
                'description': event.get('description', ''),
                'location': event.get('location', '')
            }
            event_list.append(event_info)
        
        logger.info(f"일정 조회 성공: {len(event_list)}개 ({date_str})")
        return event_list
        
    except HttpError as e:
        logger.error(f"Google API 에러: {e}")
        raise HTTPException(status_code=500, detail=f"Google Calendar API 에러: {e}")
    except Exception as e:
        logger.error(f"일정 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"일정 조회 실패: {e}")

def add_event(date_str: str, time_str: str, title: str) -> Dict[str, Any]:
    """새 일정 추가"""
    try:
        service = get_calendar_service()
        
        # 날짜/시간 파싱
        start_datetime = parse_datetime(date_str, time_str)
        end_datetime = start_datetime + timedelta(hours=1)  # 기본 1시간
        
        # 충돌 검사
        existing_events = service.events().list(
            calendarId=GOOGLE_CALENDAR_ID,
            timeMin=start_datetime.isoformat() + 'Z',
            timeMax=end_datetime.isoformat() + 'Z',
            singleEvents=True
        ).execute().get('items', [])
        
        # 이벤트 생성
        event = {
            'summary': title,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': CALENDAR_TIMEZONE,
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': CALENDAR_TIMEZONE,
            },
        }
        
        created_event = service.events().insert(
            calendarId=GOOGLE_CALENDAR_ID, 
            body=event
        ).execute()
        
        result = {
            'event_id': created_event['id'],
            'title': title,
            'datetime': start_datetime.strftime("%Y-%m-%d %H:%M"),
            'conflict_count': len(existing_events)
        }
        
        logger.info(f"일정 추가 성공: {title} at {start_datetime}")
        return result
        
    except HttpError as e:
        logger.error(f"Google API 에러: {e}")
        raise HTTPException(status_code=500, detail=f"Google Calendar API 에러: {e}")
    except Exception as e:
        logger.error(f"일정 추가 실패: {e}")
        raise HTTPException(status_code=500, detail=f"일정 추가 실패: {e}")

def delete_event(event_id: str) -> bool:
    """일정 삭제"""
    try:
        service = get_calendar_service()
        
        # 이벤트 삭제
        service.events().delete(
            calendarId=GOOGLE_CALENDAR_ID,
            eventId=event_id
        ).execute()
        
        logger.info(f"일정 삭제 성공: {event_id}")
        return True
        
    except HttpError as e:
        if e.resp.status == 404:
            logger.warning(f"삭제할 일정을 찾을 수 없음: {event_id}")
            raise HTTPException(status_code=404, detail="삭제할 일정을 찾을 수 없습니다.")
        else:
            logger.error(f"Google API 에러: {e}")
            raise HTTPException(status_code=500, detail=f"Google Calendar API 에러: {e}")
    except Exception as e:
        logger.error(f"일정 삭제 실패: {e}")
        raise HTTPException(status_code=500, detail=f"일정 삭제 실패: {e}")

# ====== 명령어 처리 함수 ======

def process_calendar_command(command: str) -> str:
    """캘린더 명령어 처리 (코덱스 방식의 핵심)"""
    try:
        command = command.strip()
        
        # 1. 캘린더 조회 [YYYY-MM-DD]
        if command.startswith("캘린더 조회"):
            match = re.match(r'캘린더 조회\s+(.+)', command)
            if match:
                date_str = match.group(1).strip()
                events = get_events_for_date(date_str)
                
                if events:
                    response = f"📅 {date_str} 일정:\n\n"
                    for i, event in enumerate(events, 1):
                        response += f"{i}. {event['title']} ({event['start_time']})\n"
                        if event['location']:
                            response += f"   📍 {event['location']}\n"
                        if event['description']:
                            response += f"   📝 {event['description'][:50]}...\n"
                        response += f"   🔗 ID: {event['id']}\n\n"
                    return response.strip()
                else:
                    return f"📅 {date_str}에는 일정이 없습니다."
            else:
                return "❌ 사용법: 캘린더 조회 2024-01-15"
        
        # 2. 캘린더 추가 YYYY-MM-DD HH:MM 제목
        elif command.startswith("캘린더 추가"):
            match = re.match(r'캘린더 추가\s+(\S+)\s+(\S+)\s+(.+)', command)
            if match:
                date_str = match.group(1)
                time_str = match.group(2)
                title = match.group(3)
                
                result = add_event(date_str, time_str, title)
                
                response = f"✅ 일정이 추가되었습니다!\n\n"
                response += f"📌 제목: {result['title']}\n"
                response += f"🕐 시간: {result['datetime']}\n"
                response += f"🔗 ID: {result['event_id']}\n"
                
                if result['conflict_count'] > 0:
                    response += f"\n⚠️ {result['conflict_count']}개의 기존 일정과 시간이 겹칩니다."
                
                return response
            else:
                return "❌ 사용법: 캘린더 추가 2024-01-15 14:00 회의 제목"
        
        # 3. 캘린더 삭제 <EVENT_ID>
        elif command.startswith("캘린더 삭제"):
            match = re.match(r'캘린더 삭제\s+(.+)', command)
            if match:
                event_id = match.group(1).strip()
                delete_event(event_id)
                return f"✅ 일정이 삭제되었습니다. (ID: {event_id})"
            else:
                return "❌ 사용법: 캘린더 삭제 <event_id>"
        
        # 4. 헬스체크
        elif command == "health_check":
            service = get_calendar_service()
            calendar_info = service.calendars().get(calendarId=GOOGLE_CALENDAR_ID).execute()
            return f"✅ 서버 정상 작동 중\n📅 연결된 캘린더: {calendar_info.get('summary', 'Primary')}"
        
        else:
            return "❌ 알 수 없는 명령어입니다.\n사용법: '캘린더 도움말' 입력"
            
    except HTTPException as e:
        return f"❌ {e.detail}"
    except Exception as e:
        logger.error(f"명령어 처리 실패: {e}")
        return f"❌ 서버 오류: {str(e)}"

# ====== FastAPI 엔드포인트 ======

@app.get("/")
async def root():
    """서버 상태 확인"""
    return {
        "message": "Google Calendar 서비스 (코덱스 방식)",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "calendar_id": GOOGLE_CALENDAR_ID,
        "timezone": CALENDAR_TIMEZONE
    }

@app.post("/webhook")
async def webhook_handler(request: WebhookRequest):
    """메신저봇 웹훅 처리 (코덱스 방식의 핵심)"""
    try:
        command = request.command
        room = request.room
        author = request.author
        
        logger.info(f"명령어 수신 - 방: {room}, 사용자: {author}, 명령: {command}")
        
        # 명령어 처리
        response = process_calendar_command(command)
        
        # 응답 반환 (메신저봇에서 직접 사용할 수 있는 문자열)
        return response
        
    except Exception as e:
        logger.error(f"웹훅 처리 실패: {e}")
        return f"❌ 서버 오류: {str(e)}"

@app.get("/health")
async def health_check():
    """헬스체크"""
    try:
        service = get_calendar_service()
        calendar_info = service.calendars().get(calendarId=GOOGLE_CALENDAR_ID).execute()
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "calendar_connected": True,
            "calendar_name": calendar_info.get('summary', 'Unknown'),
            "service_account": True
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "error": str(e),
                "calendar_connected": False
            }
        )

# ====== 서버 시작 ======

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 설정 검증"""
    logger.info("Google Calendar 서비스 서버 시작됨")
    
    # 필수 환경변수 확인
    if not GOOGLE_SERVICE_ACCOUNT_JSON:
        logger.error("GOOGLE_SERVICE_ACCOUNT_JSON 환경변수가 설정되지 않았습니다!")
        return
    
    if not GOOGLE_CALENDAR_ID:
        logger.error("GOOGLE_CALENDAR_ID 환경변수가 설정되지 않았습니다!")
        return
    
    # Google Calendar 연결 테스트
    try:
        service = get_calendar_service()
        calendar_info = service.calendars().get(calendarId=GOOGLE_CALENDAR_ID).execute()
        logger.info(f"Google Calendar 연결 성공: {calendar_info.get('summary', 'Unknown')}")
    except Exception as e:
        logger.error(f"Google Calendar 연결 실패: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """서버 종료"""
    logger.info("Google Calendar 서비스 서버 종료됨")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 9000))
    
    logger.info(f"서버 시작 - 포트: {port}")
    logger.info("API 문서: http://localhost:{port}/docs")
    
    uvicorn.run(
        "google_calendar_service:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )

"""
====== 코덱스 방식의 장점 요약 ======

1. 간단한 설정: 환경변수 3개만 설정
2. 서비스 계정: OAuth 인증 과정 생략
3. 명령어 파싱: 서버에서 집중 처리  
4. 한 줄 실행: uvicorn google_calendar_service:app --host 0.0.0.0 --port 9000
5. 확장성: 명령어 추가가 서버에서만 필요

====== 환경 설정 (.env 파일) ======

GOOGLE_SERVICE_ACCOUNT_JSON=/path/to/service-account.json
GOOGLE_CALENDAR_ID=primary
CALENDAR_TIMEZONE=Asia/Seoul
PORT=9000

====== 사용법 ======

1. Google Cloud Console에서 서비스 계정 생성
2. Calendar API 권한 부여  
3. 서비스 계정 JSON 키 다운로드
4. .env 파일에 경로 설정
5. uvicorn google_calendar_service:app --host 0.0.0.0 --port 9000
6. 메신저봇에서 테스트

명령어 예시:
- "캘린더 조회 2024-01-15"
- "캘린더 추가 2024-01-15 14:00 팀 회의"
- "캘린더 삭제 event_id_here"
"""