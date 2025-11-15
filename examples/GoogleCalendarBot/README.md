# 🗓️ Google Calendar 메신저봇 예제

카카오톡에서 Google Calendar를 자연어로 제어할 수 있는 완전 실용 메신저봇입니다.

## 📱 **주요 기능**

### 🔍 **일정 조회**
- `일정` - 오늘 일정 보기
- `내일 일정` - 내일 일정 보기  
- `이번주 일정` - 주간 일정 보기

### ➕ **일정 추가**
- `일정 추가 회의 내일 3시`
- `일정 추가 점심 오늘 12시 친구와`

### 🗑️ **일정 삭제**
- `일정 삭제 1` (번호로 삭제)

### 🕐 **빈시간 확인**
- `빈시간 오늘`
- `빈시간 내일`

### ❓ **도움말**
- `캘린더 도움말` - 전체 사용법
- `서버 상태` - 연결 상태 확인

---

## 📂 **파일 구조**

```
GoogleCalendarBot/
├── GoogleCalendarBot.js     # 메신저봇 코드 (ES5)
├── fastapi_server.py        # FastAPI 서버 (Python)
├── requirements.txt         # Python 패키지 목록
├── .env.example            # 환경변수 템플릿
├── setup_guide.md          # 완전 설치 가이드
├── README.md               # 이 파일
└── credentials.json        # Google OAuth 파일 (직접 다운로드)
```

---

## 🚀 **빠른 시작**

### 1️⃣ **Google Cloud 설정**
```bash
1. console.cloud.google.com 접속
2. Calendar API 활성화
3. OAuth 2.0 클라이언트 ID 생성
4. credentials.json 다운로드
```

### 2️⃣ **서버 설치**
```bash
# 가상환경 생성
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt

# 서버 실행
python fastapi_server.py
```

### 3️⃣ **메신저봇 설정**
```javascript
// GoogleCalendarBot.js에서 수정
var CONFIG = {
    SERVER_URL: "http://localhost:9000",     # 서버 주소
    TARGET_ROOMS: ["테스트방"]              # 카톡방 이름
};
```

### 4️⃣ **테스트**
```bash
카톡방에서:
"서버 상태" → 연결 확인
"일정" → 오늘 일정 보기
"일정 추가 테스트 내일 3시" → 일정 등록
```

---

## 🛠️ **기술 스택**

### 📱 **메신저봇 (JavaScript/ES5)**
- MessengerBot R 호환
- Rhino Engine 기반
- HTTP API 호출

### 🐍 **서버 (Python)**
- FastAPI - 고성능 웹 프레임워워크
- Google Calendar API - 공식 Python 클라이언트
- OAuth 2.0 - 안전한 인증

### 🔗 **통신 방식**
- REST API (JSON)
- 비동기 처리
- 에러 핸들링

---

## 📋 **API 엔드포인트**

### 🏥 **헬스체크**
```
GET  /api/health
POST /api/health
```

### 📅 **일정 관리**
```
POST /api/calendar/events
{
  "action": "get_events|add_event|delete_event",
  "title": "회의",
  "datetime": "내일 3시",
  "period": "today|tomorrow|week"
}
```

### 🕐 **빈시간 조회**
```
POST /api/calendar/free-busy
{
  "action": "check_free_time",
  "date": "오늘"
}
```

---

## 🎯 **사용 예시**

### 💬 **일상적인 대화**
```
사용자: "일정"
봇: 📅 오늘 일정:
    1. 팀 회의 (14:00 - 15:00)
    2. 의사 예약 (16:30 - 17:00)

사용자: "일정 추가 저녁약속 내일 7시"
봇: ✅ 일정이 등록되었습니다!
    📌 제목: 저녁약속
    🕐 시간: 내일 7시

사용자: "빈시간 내일"
봇: 🕐 내일 빈 시간:
    ⭕ 09:00 - 12:00
    ⭕ 13:00 - 19:00
```

### 🤖 **고급 기능**
```
사용자: "일정 추가 중요한 회의 2024-01-15 14:00 프로젝트 킥오프"
봇: ✅ 일정이 등록되었습니다!
    ⚠️ 충돌하는 일정이 있습니다: 팀 미팅

사용자: "서버 상태"
봇: ✅ Google Calendar 서버가 정상 작동 중입니다.
```

---

## 🔧 **커스터마이징**

### 🎨 **명령어 변경**
```javascript
// GoogleCalendarBot.js에서
if (content === "일정") {
    // 원하는 명령어로 변경:
    // "스케줄", "오늘뭐해", "계획" 등
}
```

### ⏰ **시간 파싱 확장**
```javascript
function parseTime(timeStr) {
    // "오후 3시 30분", "15:30", "3시반" 등
    // 더 다양한 형식 지원 가능
}
```

### 🔔 **알림 기능 추가**
```python
# fastapi_server.py에서 확장 가능:
# - 이메일 알림
# - 슬랙 알림  
# - 푸시 알림
```

---

## 🚨 **문제 해결**

### ❌ **일반적인 오류**

#### "서버 연결 실패"
```bash
1. FastAPI 서버 실행 상태 확인
2. 포트 9000 사용 가능한지 확인
3. 방화벽 설정 확인
```

#### "OAuth 인증 실패" 
```bash
1. credentials.json 파일 확인
2. token.pickle 삭제 후 재인증
3. Google Calendar API 활성화 확인
```

#### "메신저봇 컴파일 에러"
```bash
1. ES5 문법 준수 확인 (const → var)
2. 문법 오류 확인
3. 로그 탭에서 상세 에러 확인
```

### 🔍 **디버깅**
```bash
# 서버 로그 확인
tail -f calendar_server.log

# API 테스트
curl http://localhost:9000/api/health

# 메신저봇 로그 확인 
# 메신저봇 앱 → Log 탭
```

---

## 🛡️ **보안 고려사항**

### 🔒 **OAuth 토큰**
- `token.pickle` 파일 안전하게 보관
- 정기적인 토큰 갱신
- 권한 범위 최소화

### 🌐 **네트워크 보안**
```bash
# 프로덕션 환경에서:
1. HTTPS 사용
2. API 키 환경변수 관리
3. 방화벽 설정
4. 접근 로그 모니터링
```

### 📱 **메신저봇 보안**
```javascript
// IP 화이트리스트 (선택사항)
var ALLOWED_IPS = ["your-server-ip"];

// 사용자 권한 확인
var ALLOWED_USERS = ["admin", "user1"];
```

---

## 🔄 **향후 개발 계획**

### 📈 **기능 확장**
- [ ] 반복 일정 등록
- [ ] 참석자 초대 기능
- [ ] 일정 수정 기능
- [ ] 위치 정보 추가
- [ ] 첨부파일 지원

### 🤖 **AI 통합**
- [ ] 자연어 처리 개선
- [ ] 일정 자동 분류
- [ ] 스마트 알림
- [ ] 회의록 자동 생성

### 🔗 **다른 서비스 연동**
- [ ] Slack 연동
- [ ] Notion 연동
- [ ] Gmail 연동
- [ ] Zoom 연동

---

## 📚 **참고 자료**

### 🔗 **공식 문서**
- [Google Calendar API](https://developers.google.com/calendar/api)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [MessengerBot R](https://github.com/nkh0830/MessengerBotR)

### 📖 **튜토리얼**
- [Google OAuth 2.0 설정](https://developers.google.com/identity/protocols/oauth2)
- [Python Calendar API 퀵스타트](https://developers.google.com/calendar/api/quickstart/python)

---

## 📞 **지원 및 기여**

### 🤝 **기여 방법**
1. 이슈 리포트
2. 기능 제안
3. 코드 개선
4. 문서 개선

### 💬 **문의 사항**
- 기술 문제: GitHub Issues
- 사용법 질문: 강의 게시판
- 버그 리포트: 상세한 에러 로그와 함께

---

## 📄 **라이선스**

이 프로젝트는 MIT 라이선스를 따릅니다. 자유롭게 사용, 수정, 배포할 수 있습니다.

---

**🎉 즐거운 개발 되세요! 궁금한 점이 있으면 언제든 물어보세요! 📱✨**