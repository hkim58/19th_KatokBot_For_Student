# CLAUDE.md - 메신저봇 개발 가이드

이 파일은 Claude Code (claude.ai/code)가 메신저봇 프로젝트를 작업할 때 따라야 할 지침입니다.

## 🚨 **절대 규칙 - 반드시 읽고 시작하세요!**

### ⚠️ **메신저봇 컴파일 금지**
**Claude가 절대 직접 메신저봇 JS 파일을 컴파일하면 안됩니다!**
- 메신저봇 자체가 다운될 수 있습니다
- 파일 수정 후에는 **사용자가 직접** 실제폰의 메신저봇 앱에서 컴파일해야 합니다
- Claude는 파일 수정까지만, 컴파일은 사용자의 영역입니다

### 📱 **봇 배포 경로 엄수**
```bash
# ✅ 올바른 배포 경로
adb push Bots/StudentBot/StudentBot.js /storage/emulated/0/msgbot/Bots/StudentBot/

# ❌ 잘못된 경로들 (절대 사용 금지)
# /storage/emulated/0/msgbot/StudentBot/  (Bots 폴더 누락)
# /sdcard/msgbot/...  (sdcard는 사용하지 않음)
```

### 📚 참고 문서
- 로그를 해석하거나 모바일 디버깅을 돕기 위해 `docs/guides/LOG_JSON_READING_GUIDE.md`를 우선 참고하세요.
- 학생 온보딩용 체크리스트는 `docs/guides/STUDENT_CHECKLIST.md`에 있습니다.
- 메신저봇 공통 개발 표준과 금지 패턴은 `docs/guides/MESSENGER_BOT_DEVELOPMENT_STANDARDS.md`를 따르세요.

## 프로젝트 구조

```
19th_KatokBot_For_Student/
├── Bots/                    # 메신저봇 JS 코드
│   └── StudentBot/          # 봇별 폴더
│       └── StudentBot.js    # 봇 메인 파일
├── fastapi/                 # FastAPI 서버
│   ├── main.py             # 메인 앱
│   ├── requirements.txt    # Python 의존성
│   └── .env.example        # 환경변수 예시
└── docs/                    # 문서화
    ├── CLAUDE.md           # 이 파일
    ├── AGENTS.md           # 에이전트 워크플로
    └── README.md           # 프로젝트 소개
```

## 메신저봇 개발 표준

### 1. **API2 규격 엄수**
```javascript
// ✅ 올바른 예시 - API2 규격
function onMessage(msg) {
    var room = msg.room;
    var sender = msg.author.name;
    var content = msg.content;
    
    if (content === "!안녕") {
        msg.reply("안녕하세요!");
    }
}

// ❌ 잘못된 예시 - Legacy API (사용 금지)
function response(room, msg, sender, isGroupChat, replier) {
    // 이 형식은 구버전이므로 사용하지 마세요
}
```

### 2. **ES5 문법 사용**
```javascript
// ✅ 올바른 ES5 문법
var items = [1, 2, 3];
for (var i = 0; i < items.length; i++) {
    Log.d("Item: " + items[i]);
}

// ❌ ES6+ 문법 (메신저봇 미지원)
const items = [1, 2, 3];
items.forEach(item => {  // 화살표 함수 사용 불가
    console.log(`Item: ${item}`);  // 템플릿 리터럴 사용 불가
});
```

### 3. **로깅 규칙**
```javascript
// ✅ 올바른 로깅
Log.d("디버그 메시지");  // 디버깅용
Log.i("정보 메시지");    // 일반 정보
Log.e("에러 메시지");    // 에러 발생

// ❌ 사용 금지
Log.w("경고");          // Log.w는 메신저봇에서 미지원
console.log("메시지");   // console 객체 미지원
```

## 자주 하는 실수와 해결법

### 1. **세션 만료 처리**
```javascript
// ✅ 올바른 예시 - try-catch로 보호
function sendMessage(room, message) {
    try {
        bot.send(room, message);
        return true;
    } catch (e) {
        Log.e("메시지 전송 실패: " + e.message);
        // 세션 만료 시 재시도 로직
        return false;
    }
}
```

### 2. **API 호출 시 타임아웃 설정**
```javascript
// ✅ 올바른 예시 - 타임아웃 설정
var url = "http://your-server.com/api";
var result = org.jsoup.Jsoup.connect(url)
    .timeout(5000)  // 5초 타임아웃
    .ignoreContentType(true)
    .get()
    .text();
```

### 3. **JSON 파싱 에러 처리**
```javascript
// ✅ 올바른 예시 - 안전한 JSON 파싱
function parseJSON(text) {
    try {
        return JSON.parse(text);
    } catch (e) {
        Log.e("JSON 파싱 실패: " + e.message);
        return null;
    }
}
```

## FastAPI 서버 연동

### 로컬 개발
```bash
# 가상환경 생성 및 활성화
cd fastapi
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
uvicorn main:app --reload --port 9000
```

### 서버 배포
```bash
# 서버에 파일 복사
scp fastapi/main.py user@server:/path/to/project/

# 서버 재시작
ssh user@server
sudo systemctl restart fastapi-service
```

## 테스트 및 디버깅

### 1. **단계별 테스트**
1. 먼저 간단한 응답부터 테스트
2. API 연동은 별도로 테스트
3. 에러 처리 로직 확인
4. 실제 카톡방에서 최종 테스트

### 2. **로그 확인**
```javascript
// 봇 코드에 로그 추가
Log.d("[StudentBot] 명령어 수신: " + content);
Log.d("[StudentBot] API 응답: " + response);
```

### 3. **일반적인 디버깅 순서**
1. 메신저봇 앱에서 컴파일 에러 확인
2. Log 탭에서 런타임 에러 확인
3. bot.send() 실패 시 세션 문제 확인
4. API 호출 실패 시 네트워크/서버 상태 확인

## Git 워크플로

### 커밋 메시지 규칙
```bash
# .commit_message.txt 파일에 작성
✨ 기능: 새로운 기능 추가
🐛 버그: 버그 수정
📝 문서: 문서 업데이트
♻️ 리팩토링: 코드 개선
🎨 스타일: 코드 포맷팅
```

## 중요 주의사항

1. **절대 메신저봇을 직접 컴파일하지 마세요**
2. **파일 경로는 정확히 확인 후 사용하세요**
3. **ES5 문법만 사용하세요 (const, let, 화살표 함수 금지)**
4. **Log.w는 사용하지 마세요 (Log.d, Log.i, Log.e만 사용)**
5. **세션 만료에 대비한 try-catch 처리를 항상 하세요**
6. **API 호출 시 타임아웃을 설정하세요**
7. **실제폰 테스트 전에 문법 검사를 하세요**

## 도움이 필요할 때

- 메신저봇 공식 문서 참조
- 기존 봇 코드 참고 (Bots/ 폴더)
- 강사나 멘토에게 질문
- Claude Code에게 코드 리뷰 요청

## 버전 정보
- 프로젝트 시작: 2025년 1월
- 메신저봇 버전: API2 기준
- FastAPI 버전: 0.100+ 권장
