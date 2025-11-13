# 🤖 19기 메신저봇 카톡봇 개발 프로젝트

## 📌 프로젝트 소개
메신저봇을 처음 배우는 학생들을 위한 카카오톡 봇 개발 학습 프로젝트입니다.
프로그래밍을 전혀 모르는 비개발자도 단계별로 따라하며 자신만의 카톡봇을 만들 수 있습니다.

## 🎯 학습 목표
1. 메신저봇의 기본 구조 이해
2. JavaScript ES5 문법 학습
3. 간단한 봇부터 AI 챗봇까지 단계별 구현
4. 실제 카톡방에서 작동하는 봇 만들기

## 📚 프로젝트 구조
```
19th_KatokBot_For_Student/
├── Bots/                    # 봇 소스코드
│   ├── EchoBot/            # 따라하기 봇 (입문)
│   ├── HelloBot/           # 인사 봇 (초급)
│   ├── CalcBot/            # 계산기 봇 (초급)
│   ├── CatBot_Singleturn/  # AI 챗봇 - 모카 (중급)
│   └── CatBot_Multiturn/   # AI 챗봇 - 루나 (고급)
├── docs/                    # 학습 가이드
│   └── guides/             # 각종 가이드 문서
├── fastapi/                # FastAPI 서버 (향후 확장용)
├── CLAUDE.md               # Claude Code 개발 가이드
└── AGENTS.md               # 개발 워크플로우 가이드
```

## 🚀 시작하기

### 1️⃣ 사전 준비
1. 안드로이드 폰 준비
2. [메신저봇R](https://play.google.com/store/apps/details?id=com.xfl.msgbot) 앱 설치
3. 알림 접근 권한 허용
4. 테스트용 카톡방 만들기

### 2️⃣ 첫 번째 봇 실행하기
1. EchoBot 코드를 메신저봇에 복사
2. `TARGET_ROOMS`에 자신의 카톡방 이름 입력
3. 컴파일 및 실행
4. "따라해 안녕" 메시지 테스트

### 3️⃣ 학습 순서
```
EchoBot (따라하기) → HelloBot (인사) → CalcBot (계산) 
→ CatBot_Singleturn (AI 단순) → CatBot_Multiturn (AI 대화)
```

## 📖 필수 학습 가이드

### 초보자 필수
- 📘 [메신저봇 완전 학습 가이드](docs/guides/MESSENGER_BOT_COMPLETE_LEARNING_GUIDE.md)
- 📗 [ES5 JavaScript 문법 가이드](docs/guides/MESSENGERBOT_ES5_SYNTAX.md)
- 📙 [자주 겪는 오류 해결법](docs/guides/BEGINNER_COMMON_ERRORS.md)

### 문제 해결
- 🔧 [메신저봇 크래시 해결](docs/guides/MESSENGER_BOT_CRASH_GUIDE.md)
- 📋 [log.json 분석 가이드](docs/guides/LOG_JSON_READING_GUIDE.md)

### API 참고서
- 📚 [메신저봇 API 레퍼런스](docs/guides/MESSENGER_BOT_API.md)

## 🤖 봇 소개

### 1. EchoBot (따라하기 봇)
- **난이도**: ⭐
- **명령어**: `따라해 [메시지]`
- **특징**: 입력한 메시지를 그대로 따라합니다

### 2. HelloBot (인사 봇)
- **난이도**: ⭐⭐
- **명령어**: `안녕`, `하이`, `굿모닝`
- **특징**: 시간대별로 다른 인사말을 합니다

### 3. CalcBot (계산기 봇)
- **난이도**: ⭐⭐
- **명령어**: `계산 [수식]`
- **특징**: 간단한 사칙연산을 계산합니다

### 4. CatBot_Singleturn (모카 - 느긋한 고양이)
- **난이도**: ⭐⭐⭐
- **명령어**: `모카 [질문]`, `모카 통계`
- **특징**: 매번 새로운 대화, 빠른 응답
- **API 필요**: Perplexity API 키 필요

### 5. CatBot_Multiturn (루나 - 츤데레 고양이)
- **난이도**: ⭐⭐⭐⭐
- **명령어**: `루나 [질문]`, `또보자`, `루나 기억해?`
- **특징**: 대화 기억, 연속 대화 가능
- **API 필요**: Perplexity API 키 필요

## ⚙️ 설정 방법

### API 키 설정 (AI 봇용)
1. [Perplexity](https://www.perplexity.ai/) 가입
2. API 키 발급
3. 봇 코드의 `API_KEY` 부분에 입력
```javascript
API_KEY: "pplx-실제API키입력",  // 여기에 본인 API 키
```

### 카톡방 설정
```javascript
TARGET_ROOMS: ["테스트방", "스터디방"],  // 본인 방 이름으로 변경
```

## 🎓 실습 과제

### 초급 과제
1. EchoBot 명령어를 "복사해"로 바꾸기
2. HelloBot에 "잘자" 인사 추가하기
3. CalcBot에 에러 메시지 꾸미기

### 중급 과제
1. 모카 봇의 성격을 친절한 강아지로 바꾸기
2. 루나 봇의 대화 기억을 20턴으로 늘리기
3. 새로운 명령어 추가하기

### 고급 과제
1. 날씨 봇 만들기
2. 투표 봇 만들기
3. 일정 관리 봇 만들기

## 🚨 주의사항
1. **ES5 문법만 사용** (const, let, 화살표 함수 사용 금지)
2. **API 키는 절대 공유하지 않기**
3. **봇 테스트는 테스트방에서만**
4. **무한 루프 조심** (Thread 사용시 주의)

## 📞 도움말
- 오류 발생시 먼저 [자주 겪는 오류 해결법](docs/guides/BEGINNER_COMMON_ERRORS.md) 확인
- log.json 파일 확인: `/sdcard/msgbot/log.json`
- 메신저봇 앱 재시작으로 대부분의 문제 해결

## 🌟 학습 팁
1. **작은 것부터 시작**: EchoBot부터 차근차근
2. **로그 활용**: `Log.d()`로 디버깅하기
3. **주석 읽기**: 코드의 주석을 꼼꼼히 읽기
4. **직접 수정**: 코드를 조금씩 바꿔보며 실험
5. **에러 두려워하지 않기**: 에러는 학습의 기회!

## 📝 라이선스
교육 목적으로 자유롭게 사용 가능합니다.

---

**Happy Coding! 🎉**
메신저봇으로 나만의 카톡봇을 만들어보세요!