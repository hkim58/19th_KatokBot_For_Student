# 🚀 고급 기능 및 심화 확장 가이드

## 🎯 **이 가이드의 대상**

- **기본 설정을 완료한** 사용자
- **더 많은 기능**을 원하는 개발자  
- **프로덕션 환경**으로 확장하려는 팀

---

## 📊 **기본 기능 vs 고급 기능 비교**

### 🟢 **기본 기능** (BEGINNER_SIMPLE_GUIDE.md)
```
✅ 일정 조회 (오늘/내일)
✅ 일정 추가 (간단한 형태)
✅ 빈시간 조회 (기본 시간대)
✅ 로컬 서버 테스트
```

### 🔥 **고급 기능** (이 가이드)
```
🚀 반복 일정 등록
🚀 참석자 초대 및 알림
🚀 캘린더 간 일정 동기화
🚀 AI 기반 일정 최적화
🚀 외부 서비스 연동 (Slack, Notion, Gmail)
🚀 웹 대시보드 및 모니터링
🚀 프로덕션 서버 배포
🚀 다중 사용자 권한 관리
```

---

## 🔄 **1. 반복 일정 기능**

### 📝 **구현 방식**
Google Calendar의 **Recurring Events** 활용

### 💻 **코드 예시**
```python
def create_recurring_event(title, start_datetime, recurrence_rule):
    """반복 일정 생성"""
    event = {
        'summary': title,
        'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': 'Asia/Seoul',
        },
        'end': {
            'dateTime': (start_datetime + timedelta(hours=1)).isoformat(),
            'timeZone': 'Asia/Seoul',
        },
        'recurrence': [
            recurrence_rule  # 예: 'RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR'
        ],
    }
    
    return service.events().insert(calendarId='primary', body=event).execute()
```

### 📱 **메신저봇 명령어 확장**
```javascript
// 반복 일정 명령어 처리
if (content.includes("반복 일정 추가")) {
    // "반복 일정 추가 회의 매주 월수금 3시"
    // → RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR
}
```

### 🎯 **지원하는 반복 패턴**
```
매일        → FREQ=DAILY
매주 월수금  → FREQ=WEEKLY;BYDAY=MO,WE,FR  
매월 15일   → FREQ=MONTHLY;BYMONTHDAY=15
매년       → FREQ=YEARLY
```

---

## 👥 **2. 참석자 초대 및 알림**

### 📧 **이메일 초대 기능**
```python
def create_event_with_attendees(title, start_time, attendees_emails):
    """참석자와 함께 일정 생성"""
    attendees = [{'email': email} for email in attendees_emails]
    
    event = {
        'summary': title,
        'start': {'dateTime': start_time, 'timeZone': 'Asia/Seoul'},
        'end': {'dateTime': end_time, 'timeZone': 'Asia/Seoul'},
        'attendees': attendees,
        'sendNotifications': True,  # 자동 이메일 발송
        'guestsCanModify': False,   # 참석자 수정 권한
    }
    
    return service.events().insert(
        calendarId='primary', 
        body=event, 
        sendUpdates='all'  # 모든 참석자에게 알림
    ).execute()
```

### 📱 **메신저봇 명령어**
```
일정 추가 팀미팅 내일 3시 @kim@company.com @lee@company.com
```

### 🔔 **알림 설정 종류**
```python
'reminders': {
    'useDefault': False,
    'overrides': [
        {'method': 'email', 'minutes': 24 * 60},     # 24시간 전
        {'method': 'popup', 'minutes': 30},          # 30분 전
        {'method': 'sms', 'minutes': 10},            # 10분 전 (유료)
    ],
}
```

---

## 🔄 **3. 다중 캘린더 동기화**

### 📅 **여러 캘린더 관리**
```python
def get_all_calendars():
    """사용자의 모든 캘린더 조회"""
    calendars_result = service.calendarList().list().execute()
    calendars = calendars_result.get('items', [])
    
    return [
        {
            'id': cal['id'],
            'name': cal['summary'],
            'color': cal.get('backgroundColor', '#ffffff'),
            'primary': cal.get('primary', False)
        }
        for cal in calendars
    ]

def sync_calendars(source_calendar_id, target_calendar_id, sync_period_days=30):
    """캘린더 간 일정 동기화"""
    # 소스 캘린더에서 일정 가져오기
    events = get_events_from_calendar_id(source_calendar_id, sync_period_days)
    
    # 타겟 캘린더에 복사
    for event in events:
        create_event_in_calendar(target_calendar_id, event)
```

### 📱 **메신저봇 명령어 확장**
```
캘린더 목록                    → 모든 캘린더 보기
캘린더 동기화 개인→업무         → 개인 캘린더를 업무 캘린더로 복사
캘린더 전환 업무               → 기본 캘린더를 업무용으로 변경
```

---

## 🤖 **4. AI 기반 일정 최적화**

### 🧠 **AI 분석 기능**
```python
from openai import OpenAI

def optimize_schedule_with_ai(events, preferences):
    """AI로 일정 최적화 제안"""
    
    prompt = f"""
    다음 일정들을 분석해서 최적화 방안을 제안해주세요:
    
    일정 목록: {events}
    사용자 선호: {preferences}
    
    고려사항:
    - 회의 시간 연속성
    - 점심시간 확보  
    - 집중 시간 블록
    - 이동 시간
    """
    
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content
```

### 📊 **일정 패턴 분석**
```python
def analyze_schedule_patterns(user_id, analysis_period_months=3):
    """사용자 일정 패턴 분석"""
    
    events = get_user_events_history(user_id, analysis_period_months)
    
    patterns = {
        'busiest_hours': analyze_peak_hours(events),
        'meeting_frequency': count_meeting_types(events),
        'free_time_distribution': analyze_free_time(events),
        'productivity_score': calculate_productivity_score(events),
        'recommendations': generate_recommendations(events)
    }
    
    return patterns
```

### 📱 **AI 명령어**
```
일정 분석                     → 내 일정 패턴 분석
일정 최적화 제안               → AI 기반 일정 개선 방안  
집중시간 추천                 → 방해받지 않을 시간대 추천
회의 최적화                   → 회의 시간 효율화 제안
```

---

## 🔗 **5. 외부 서비스 연동**

### 💬 **Slack 연동**
```python
from slack_sdk import WebClient

def send_to_slack(channel, message, event_data):
    """Slack으로 일정 알림 전송"""
    
    slack_client = WebClient(token=SLACK_BOT_TOKEN)
    
    blocks = [
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"📅 *일정 알림*\n{message}"}
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*시간:* {event_data['start_time']}"},
                {"type": "mrkdwn", "text": f"*장소:* {event_data.get('location', 'TBD')}"}
            ]
        },
        {
            "type": "actions",
            "elements": [
                {"type": "button", "text": {"type": "plain_text", "text": "참석"}, "action_id": "attend"},
                {"type": "button", "text": {"type": "plain_text", "text": "불참"}, "action_id": "decline"}
            ]
        }
    ]
    
    return slack_client.chat_postMessage(channel=channel, blocks=blocks)
```

### 📓 **Notion 연동**
```python
import requests

def create_notion_page_from_event(event_data):
    """일정을 Notion 페이지로 생성"""
    
    notion_headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    page_data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Title": {"title": [{"text": {"content": event_data['title']}}]},
            "Date": {"date": {"start": event_data['start_time']}},
            "Status": {"select": {"name": "Planned"}},
            "Attendees": {"multi_select": [{"name": attendee} for attendee in event_data.get('attendees', [])]}
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": event_data.get('description', '')}}]
                }
            }
        ]
    }
    
    return requests.post("https://api.notion.com/v1/pages", headers=notion_headers, json=page_data)
```

### 📧 **Gmail 연동**
```python
def create_gmail_draft_for_meeting(event_data):
    """회의 일정을 Gmail 임시 보관함에 저장"""
    
    gmail_service = build('gmail', 'v1', credentials=creds)
    
    message = MIMEText(f"""
    안녕하세요,
    
    다음 일정에 대한 회의 초대를 보내드립니다:
    
    제목: {event_data['title']}
    일시: {event_data['start_time']}
    장소: {event_data.get('location', 'TBD')}
    
    감사합니다.
    """)
    
    message['to'] = ', '.join(event_data.get('attendees', []))
    message['subject'] = f"회의 초대: {event_data['title']}"
    
    raw_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    
    return gmail_service.users().drafts().create(userId='me', body=raw_message).execute()
```

---

## 📊 **6. 웹 대시보드 및 모니터링**

### 🌐 **FastAPI + React 대시보드**
```python
@app.get("/dashboard/stats")
async def get_dashboard_stats():
    """대시보드용 통계 데이터"""
    
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    
    stats = {
        'today_events': len(get_events_for_date(today)),
        'week_events': len(get_events_for_period(week_start, week_start + timedelta(days=7))),
        'busiest_day': find_busiest_day_this_week(),
        'average_meeting_duration': calculate_average_meeting_duration(),
        'productivity_score': calculate_weekly_productivity_score(),
        'upcoming_deadlines': get_upcoming_deadlines()
    }
    
    return stats

@app.get("/dashboard/calendar-heatmap")
async def get_calendar_heatmap():
    """캘린더 히트맵 데이터"""
    
    # 지난 1년간 일정 밀도 데이터 생성
    year_ago = datetime.now() - timedelta(days=365)
    daily_event_counts = {}
    
    for day in range(365):
        current_date = year_ago + timedelta(days=day)
        event_count = len(get_events_for_date(current_date))
        daily_event_counts[current_date.strftime('%Y-%m-%d')] = event_count
    
    return daily_event_counts
```

### 📈 **모니터링 메트릭스**
```python
from prometheus_client import Counter, Histogram, generate_latest

# 메트릭스 정의
calendar_requests = Counter('calendar_requests_total', 'Total calendar requests', ['operation'])
request_duration = Histogram('calendar_request_duration_seconds', 'Request duration')

@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    """요청 모니터링"""
    
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    # 메트릭스 업데이트
    operation = request.url.path.split('/')[-1]
    calendar_requests.labels(operation=operation).inc()
    request_duration.observe(duration)
    
    return response

@app.get("/metrics")
async def metrics():
    """Prometheus 메트릭스 노출"""
    return Response(generate_latest(), media_type="text/plain")
```

---

## 🚀 **7. 프로덕션 서버 배포**

### 🐳 **Docker 컨테이너화**
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 9000

CMD ["uvicorn", "fastapi_server:app", "--host", "0.0.0.0", "--port", "9000"]
```

### ⚙️ **Docker Compose 설정**
```yaml
# docker-compose.yml
version: '3.8'

services:
  calendar-bot:
    build: .
    ports:
      - "9000:9000"
    environment:
      - GOOGLE_CREDENTIALS_FILE=/app/credentials/credentials.json
      - ENVIRONMENT=production
    volumes:
      - ./credentials:/app/credentials
      - ./logs:/app/logs
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - calendar-bot
    restart: unless-stopped
      
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
```

### 🔒 **SSL/HTTPS 설정**
```nginx
# nginx.conf
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    location / {
        proxy_pass http://calendar-bot:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 👥 **8. 다중 사용자 권한 관리**

### 🔐 **JWT 기반 인증**
```python
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = None):
    """JWT 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """JWT 토큰 검증"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
        return None
```

### 👤 **사용자 권한 모델**
```python
class User(BaseModel):
    username: str
    email: str
    role: str  # 'admin', 'user', 'viewer'
    calendar_permissions: List[str]  # 접근 가능한 캘린더 ID들

class Permission(BaseModel):
    user_id: str
    calendar_id: str
    permission_level: str  # 'read', 'write', 'admin'

@app.middleware("http")
async def check_permissions(request: Request, call_next):
    """권한 확인 미들웨어"""
    
    # JWT 토큰에서 사용자 정보 추출
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    user = verify_token(token)
    
    if not user:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"})
    
    # 요청된 리소스에 대한 권한 확인
    if not has_permission(user, request.url.path, request.method):
        return JSONResponse(status_code=403, content={"detail": "Forbidden"})
    
    response = await call_next(request)
    return response
```

---

## 📊 **9. 성능 최적화 및 캐싱**

### ⚡ **Redis 캐싱**
```python
import redis
import json

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_events(calendar_id: str, date: str, events: List[dict], ttl: int = 300):
    """일정 데이터 캐싱"""
    cache_key = f"events:{calendar_id}:{date}"
    redis_client.setex(cache_key, ttl, json.dumps(events))

def get_cached_events(calendar_id: str, date: str) -> Optional[List[dict]]:
    """캐시된 일정 조회"""
    cache_key = f"events:{calendar_id}:{date}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        return json.loads(cached_data)
    return None

@lru_cache(maxsize=128)
def get_calendar_service_cached():
    """캐시된 Calendar 서비스 객체"""
    return get_calendar_service()
```

### 📈 **비동기 처리**
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)

async def async_get_events(calendar_id: str, date: str):
    """비동기 일정 조회"""
    loop = asyncio.get_event_loop()
    
    # CPU 집약적 작업을 별도 스레드에서 실행
    events = await loop.run_in_executor(
        executor, 
        sync_get_events_from_calendar, 
        calendar_id, 
        date
    )
    
    return events

async def bulk_process_calendars(calendar_ids: List[str]):
    """여러 캘린더 동시 처리"""
    
    tasks = [async_get_events(cal_id, "today") for cal_id in calendar_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    return {cal_id: result for cal_id, result in zip(calendar_ids, results)}
```

---

## 🎯 **10. 고급 활용 시나리오**

### 🏢 **기업용 확장**
```python
# 팀 캘린더 관리
class TeamCalendarManager:
    def __init__(self, team_id: str):
        self.team_id = team_id
        self.members = self.get_team_members()
    
    def find_team_meeting_time(self, duration_minutes: int, preferred_days: List[str]):
        """팀 전체가 가능한 회의 시간 찾기"""
        
        all_busy_times = []
        for member in self.members:
            busy_times = self.get_member_busy_times(member.calendar_id)
            all_busy_times.extend(busy_times)
        
        return self.calculate_free_slots(all_busy_times, duration_minutes)
    
    def schedule_recurring_team_meeting(self, title: str, duration: int, frequency: str):
        """팀 정기 회의 자동 스케줄링"""
        
        optimal_time = self.find_team_meeting_time(duration, ["MON", "TUE", "WED", "THU"])
        
        for member in self.members:
            self.create_recurring_event_for_member(
                member.calendar_id, 
                title, 
                optimal_time, 
                frequency
            )
```

### 🤖 **AI 어시스턴트 통합**
```python
def natural_language_to_calendar_event(user_input: str):
    """자연어를 캘린더 이벤트로 변환"""
    
    # GPT-4를 사용한 자연어 처리
    prompt = f"""
    다음 자연어 요청을 JSON 형태의 캘린더 이벤트로 변환해주세요:
    
    요청: "{user_input}"
    
    응답 형식:
    {{
        "title": "회의 제목",
        "start_time": "2024-01-15T14:00:00",
        "duration_minutes": 60,
        "attendees": ["email1@example.com"],
        "location": "회의실 A",
        "description": "상세 내용"
    }}
    """
    
    # AI 응답 파싱 및 검증
    ai_response = query_openai(prompt)
    event_data = json.loads(ai_response)
    
    # 데이터 검증 및 보정
    validated_event = validate_and_correct_event_data(event_data)
    
    return validated_event
```

---

## 📚 **참고 자료 및 다음 단계**

### 🔗 **고급 개발 리소스**
- [Google Calendar API 고급 기능](https://developers.google.com/calendar/api/guides/overview)
- [FastAPI 성능 최적화](https://fastapi.tiangolo.com/advanced/)
- [Redis 캐싱 전략](https://redis.io/docs/manual/patterns/)
- [Docker 프로덕션 배포](https://docs.docker.com/engine/swarm/)

### 🎓 **학습 경로**
1. **기본 기능 마스터** → BEGINNER_SIMPLE_GUIDE.md 완료
2. **고급 기능 선택적 구현** → 이 가이드에서 필요한 부분만
3. **프로덕션 배포** → Docker + 실제 서버
4. **기업용 확장** → 다중 사용자 + 권한 관리
5. **AI 통합** → 자연어 처리 + 스마트 스케줄링

### 💡 **커스터마이징 아이디어**
- **음성 명령** 지원 (Speech-to-Text API)
- **지도 연동** (Google Maps API로 이동 시간 계산)
- **날씨 정보** 통합 (외부 미팅 시 날씨 고려)
- **할일 관리** 연동 (Todoist, Asana API)
- **시간 추적** 기능 (RescueTime API)

---

**🎉 여기까지 오셨다면 이제 정말 고급 개발자입니다! 
여러분만의 독창적인 기능을 추가해서 세상에 없던 캘린더 봇을 만들어보세요! 🚀**