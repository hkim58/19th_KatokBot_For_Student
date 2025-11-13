# AGENTS.md - 메신저봇 개발 워크플로

이 문서는 메신저봇 개발 시 따라야 할 워크플로와 베스트 프랙티스를 정리합니다.

## 📋 프로젝트 개요

메신저봇 기반 카카오톡 자동응답 봇 개발 학습 프로젝트
- **대상**: 메신저봇을 처음 접하는 학생 개발자
- **목표**: 실무에서 사용 가능한 카톡봇 개발 능력 습득
- **구조**: 메신저봇(JS) + FastAPI(Python) + 문서화

## 🏗️ 프로젝트 구조

```
19th_KatokBot_For_Student/
├── Bots/                    # 메신저봇 스크립트
│   └── {봇이름}/           # 봇별 독립 폴더
│       └── {봇이름}.js     # 메인 봇 코드
├── fastapi/                 # 백엔드 서버
│   ├── main.py             # FastAPI 앱
│   ├── requirements.txt    # Python 패키지
│   └── .env                # 환경변수 (API 키 등)
└── docs/                    # 프로젝트 문서
    ├── CLAUDE.md           # 개발 지침
    ├── AGENTS.md           # 이 파일
    └── README.md           # 프로젝트 소개
```

## 🚀 개발 워크플로

### 1단계: 환경 구축
```bash
# 1. 프로젝트 클론 또는 생성
git clone [repository-url]
cd 19th_KatokBot_For_Student

# 2. FastAPI 환경 설정
cd fastapi
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn python-dotenv  # FastAPI 의존성 최초 1회 설치

# 3. 환경변수 설정
cp .env.example .env
# .env 파일에 필요한 API 키 입력
```

### 2단계: 봇 개발 사이클

#### 📝 코드 작성
1. `Bots/{봇이름}/{봇이름}.js` 파일 수정
2. ES5 문법 준수 확인
3. 로그 추가로 디버깅 준비

#### 📤 배포
```bash
# ADB로 실제폰에 전송
adb push Bots/StudentBot/StudentBot.js /storage/emulated/0/msgbot/Bots/StudentBot/
```

#### ✅ 컴파일 및 테스트
1. **실제폰**의 메신저봇 앱 열기
2. 해당 봇 찾아서 **컴파일** 버튼 클릭
3. 컴파일 성공 확인
4. 봇 **ON** 상태 확인
5. 카톡방에서 테스트
6. 실패 시: Log 탭에서 최근 에러(`Unexpected token`, `ReferenceError` 등)를 확인하고 코드의 ES5 준수 여부를 먼저 점검합니다. 그래도 해결되지 않으면 메신저봇 앱 캐시를 삭제하거나 앱/디바이스를 재시작한 뒤 다시 **컴파일 → ON**을 진행합니다. 테스트 로그는 `Bots/{봇이름}/README.md`에 남겨 재현 절차를 공유합니다.

#### 🐛 디버깅
- 메신저봇 앱의 **Log** 탭에서 에러 확인
- `Log.d()`, `Log.i()`, `Log.e()` 출력 확인
- 필요시 코드 수정 후 재배포

### 3단계: FastAPI 서버 개발

#### 로컬 개발
```bash
cd fastapi
uvicorn main:app --reload --port 9000
# http://localhost:9000/docs 에서 API 문서 확인
```

#### 서버 배포
```bash
# 서버에 코드 전송
scp main.py user@server:/path/to/fastapi/

# SSH 접속 후 재시작
ssh user@server
sudo systemctl restart fastapi-app
journalctl -u fastapi-app -f  # 로그 확인
```

## 💡 실무 팁 & 주의사항

- 자세한 디바이스 로그 분석법은 `docs/guides/LOG_JSON_READING_GUIDE.md`를 참고하세요. `log.json` 구조, `tail/jq/python` 사용법이 정리되어 있습니다.
- 프로젝트 준비 체크리스트가 필요하면 `docs/guides/STUDENT_CHECKLIST.md`를 따라 순서대로 환경을 구축하세요.
- 더 깊은 모범 사례와 금지 패턴은 `docs/guides/MESSENGER_BOT_DEVELOPMENT_STANDARDS.md`에서 확인할 수 있습니다.

### ⚠️ 자주 하는 실수들

#### 1. **컴파일 관련**
```javascript
// ❌ 절대 하지 말 것
// Claude나 다른 도구로 자동 컴파일 시도
// → 메신저봇이 다운될 수 있음!

// ✅ 올바른 방법
// 1. 코드 수정 → 2. ADB push → 3. 실제폰에서 수동 컴파일
```

#### 2. **경로 실수**
```bash
# ❌ 잘못된 경로들
/storage/emulated/0/msgbot/StudentBot/  # Bots 폴더 누락
/sdcard/msgbot/Bots/StudentBot/         # sdcard 사용 금지

# ✅ 올바른 경로
/storage/emulated/0/msgbot/Bots/StudentBot/StudentBot.js
```

#### 3. **문법 실수**
```javascript
// ❌ ES6+ 문법 (작동 안함)
const message = `Hello ${name}`;
const func = () => { };
let variable = 10;

// ✅ ES5 문법 (메신저봇 지원)
var message = "Hello " + name;
function func() { }
var variable = 10;
```

#### 4. **세션 처리**
```javascript
// ❌ 세션 만료 무시
bot.send(room, message);  // 실패 시 앱 정지 가능

// ✅ 안전한 처리
try {
    bot.send(room, message);
} catch (e) {
    Log.e("세션 만료: " + e.message);
    // 사용자에게 재시작 요청 메시지
}
```

### 🎯 개발 체크리스트

#### 새 기능 추가 시
- [ ] 기능 요구사항 명확히 정의
- [ ] 간단한 테스트 코드 먼저 작성
- [ ] 본 코드 구현
- [ ] 에러 처리 추가
- [ ] 로그 메시지 추가
- [ ] 로컬 테스트
- [ ] 실제 카톡방 테스트
- [ ] 문서 업데이트

#### 버그 수정 시
- [ ] 버그 재현 방법 확인
- [ ] 로그로 원인 파악
- [ ] 수정 코드 작성
- [ ] 부작용 확인
- [ ] 재발 방지 방안 추가
- [ ] 테스트 완료
- [ ] 수정 내용 문서화

#### 배포 전 확인
- [ ] ES5 문법 준수
- [ ] try-catch 처리 완료
- [ ] 불필요한 로그 제거
- [ ] API 키 하드코딩 없음
- [ ] 파일 경로 정확
- [ ] 버전 정보 업데이트

## 🔧 유용한 명령어 모음

### ADB 명령어
```bash
# 디바이스 연결 확인
adb devices

# 파일 전송
adb push [로컬파일] [디바이스경로]

# 파일 가져오기
adb pull [디바이스경로] [로컬경로]

# 로그 확인
adb logcat | grep MessengerBot
```

### Git 명령어
```bash
# 상태 확인
git status

# 변경사항 추가
git add .

# 커밋
git commit -m "✨ 기능: 새 명령어 추가"

# 푸시
git push origin main
```

### Python/FastAPI
```bash
# 가상환경 활성화
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate      # Windows

# 패키지 설치 (신규 패키지 추가 시)
pip install [package-name]

# 기존 의존성 동기화
pip install -r requirements.txt

# requirements.txt 업데이트 (신규 패키지 반영)
pip freeze > requirements.txt

# 서버 실행
uvicorn main:app --reload --port 9000
```

## 📚 학습 로드맵

### 초급 (1-2주차)
1. 메신저봇 설치 및 기본 설정
2. 간단한 응답 봇 만들기
3. 조건문으로 명령어 처리
4. 로그 사용법 익히기

### 중급 (3-4주차)
1. 외부 API 연동 (날씨, 뉴스 등)
2. JSON 데이터 처리
3. 에러 처리 구현
4. FastAPI 서버 연동

### 고급 (5-6주차)
1. 데이터베이스 연동
2. 스케줄링 기능
3. 멀티 룸 관리
4. 성능 최적화

## 🆘 문제 해결 가이드

### "컴파일 실패" 에러
1. 문법 에러 확인 (세미콜론, 괄호 등)
2. ES6 문법 사용 여부 확인
3. 파일 인코딩 확인 (UTF-8)

### "bot.send() 실패" 에러
1. 세션 만료 → 봇 재시작
2. 방 이름 오타 확인
3. 네트워크 상태 확인

### "API 호출 실패" 에러
1. 서버 상태 확인
2. 타임아웃 설정 확인
3. API 키 유효성 확인

### "undefined" 에러
1. 변수 초기화 확인
2. 함수 호출 순서 확인
3. require() 경로 확인

## 📝 커밋 메시지 규칙

```
✨ 기능: 새로운 기능 추가
🐛 버그: 버그 수정
📝 문서: 문서 수정
♻️ 리팩토링: 코드 개선
🎨 스타일: 코드 포맷팅
🔧 설정: 환경 설정 변경
✅ 테스트: 테스트 추가/수정
🚀 배포: 배포 관련 변경
```

### PR 템플릿 권장 항목
1. **변경 요약**: 주요 수정 사항을 bullet으로 정리.
2. **테스트 증빙**: `pytest` 결과, 디바이스 테스트 단계, 관련 스크린샷 첨부.
3. **체크리스트**: ES5 준수, 비밀정보 미포함, 문서 업데이트 여부.
4. **배포 단계**: ADB push 경로, FastAPI 재시작 명령 등 운영자가 따라야 할 절차.
5. **리뷰 포인트**: 검토가 필요한 위험 지점이나 추가 논의 사항을 명시.

## 🎓 추가 학습 자료

- 메신저봇 공식 문서
- JavaScript ES5 문법 가이드
- FastAPI 공식 튜토리얼
- 정규표현식 학습 사이트
- Git 기초 강의

## 💪 마지막 당부

1. **작은 것부터 시작하세요** - 복잡한 기능보다 간단하고 확실한 것부터
2. **로그를 적극 활용하세요** - 디버깅의 기본은 로그
3. **에러를 두려워하지 마세요** - 에러는 학습의 기회
4. **문서를 꼼꼼히 읽으세요** - 대부분의 답은 문서에 있음
5. **코드를 정리하세요** - 나중의 나를 위한 투자
6. **백업을 생활화하세요** - 코드는 언제든 날아갈 수 있음
7. **질문을 주저하지 마세요** - 모르는 것은 부끄러운 것이 아님

---
*이 문서는 메신저봇 개발을 시작하는 학생들을 위해 작성되었습니다.*
*지속적으로 업데이트되며, 피드백은 언제나 환영합니다.*
