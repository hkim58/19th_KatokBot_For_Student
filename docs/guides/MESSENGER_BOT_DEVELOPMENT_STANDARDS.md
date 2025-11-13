# 📋 메신저봇 개발 표준 문서
**Version**: 1.0.0  
**Last Updated**: 2025-09-26  
**Author**: Claude Code & User  
**Status**: Active Development

---

## 📌 문서 소개

이 문서는 메신저봇 R 환경에서 JavaScript 봇을 개발할 때 적용해야 할 표준 포맷과 모범 사례를 정의합니다.  
모든 항목이 필수는 아니며, 상황에 맞게 선택적으로 적용합니다.

### 버전 히스토리
| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2025-09-26 | 초기 문서 생성 - 3가지 핵심 표준 정의 | Claude & User |

---

## 🎯 핵심 개발 표준

### 1️⃣ 글로벌 모듈 통합 표준

#### 문제 상황
- 여러 봇이 공통으로 사용하는 모듈을 각 봇 폴더에 중복 저장
- 업데이트 시 모든 복사본을 개별 수정해야 하는 비효율
- 메모리 낭비 및 버전 불일치 문제

#### ✅ 올바른 적용 방법

**1. 글로벌 모듈 저장 위치**
```
/storage/emulated/0/msgbot/Bots/
├── TriggerReceiverModule.js  // ✅ 글로벌 모듈은 Bots 루트에
├── CalendarBot/
│   └── CalendarBot.js        // ❌ TriggerReceiverModule.js 중복 금지
├── KapyBot/
│   └── KapyBot.js            // ❌ TriggerReceiverModule.js 중복 금지
```

**2. 모듈 로드 방법**
```javascript
// ❌ 잘못된 방법 - load() 함수는 지원 안됨
load("/storage/emulated/0/msgbot/Bots/TriggerReceiverModule.js");

// ✅ 올바른 방법 - 각 봇이 독립적으로 실행
// TriggerReceiverModule은 별도 봇으로 등록하여 실행
```

**3. 모듈 배포 명령어**
```bash
# 글로벌 모듈 배포
adb push Bots/TriggerReceiverModule.js /storage/emulated/0/msgbot/Bots/

# 중복 파일 제거
adb shell rm /storage/emulated/0/msgbot/Bots/*/TriggerReceiverModule.js
```

---

### 2️⃣ 외부 트리거 예약 메시지 표준

#### 사용 사례
- 매일 특정 시간에 "오늘 하루 계획 알려줘" 자동 발송
- 정기적인 리마인더나 알림
- 시간 기반 자동화 작업

#### ✅ 구현 방법

**1. TriggerSender에서 예약 메시지 설정**
```javascript
// TriggerSender.js
var SCHEDULED_TRIGGERS = [
    {
        time: "09:00",  // 매일 오전 9시
        message: "!오늘일정",
        rooms: ["테스트방", "업무방"],
        enabled: true
    },
    {
        time: "18:00",  // 매일 오후 6시  
        message: "!퇴근알림",
        rooms: ["업무방"],
        enabled: true
    }
];

// 스케줄 체크 함수
function checkScheduledTriggers() {
    var now = new Date();
    var currentTime = String(now.getHours()).padStart(2, "0") + ":" + 
                     String(now.getMinutes()).padStart(2, "0");
    
    for (var i = 0; i < SCHEDULED_TRIGGERS.length; i++) {
        var schedule = SCHEDULED_TRIGGERS[i];
        if (schedule.enabled && schedule.time === currentTime) {
            sendTriggerToRooms(schedule.message, schedule.rooms);
        }
    }
}
```

**2. 수신 봇에서 반응**
```javascript
// CalendarBot.js
function onMessage(msg) {
    // 예약된 트리거 메시지에 반응
    if (msg.content === "!오늘일정") {
        var todaySchedule = getTodaySchedule();
        msg.reply("📅 오늘의 일정:\n" + todaySchedule);
    }
}
```

---

### 3️⃣ 메신저봇 크래시 방지 표준

#### ⚠️ 반드시 피해야 할 패턴

**1. Thread.interrupt() 절대 금지**
```javascript
// ❌ 절대 금지 - 앱 크래시 원인
thread.interrupt();  // UnsupportedOperationException

// ✅ 올바른 방법 - 플래그 사용
var isRunning = true;
var thread = new java.lang.Thread(new java.lang.Runnable({
    run: function() {
        while (isRunning) {
            // 작업 수행
            java.lang.Thread.sleep(1000);
        }
    }
}));

// 종료 시
isRunning = false;  // 플래그로 종료
```

**2. 무한 루프 안전 장치**
```javascript
// ❌ 위험한 무한 루프
while (true) {
    // 작업
}

// ✅ 안전한 루프
var MAX_ITERATIONS = 1000;
var iterations = 0;
while (isRunning && iterations < MAX_ITERATIONS) {
    // 작업
    iterations++;
    java.lang.Thread.sleep(100);
}
```

**3. try-catch 필수**
```javascript
// ✅ 모든 Thread에 try-catch 적용
var thread = new java.lang.Thread(new java.lang.Runnable({
    run: function() {
        try {
            while (isRunning) {
                // 작업
            }
        } catch (e) {
            Log.e("Thread 오류: " + e.message);
        }
    }
}));
```

---

### 4️⃣ 명령어 선언 표준화 (v1.0.0 신규)

#### 목적
- 봇이 지원하는 모든 명령어를 코드 상단에서 한눈에 파악
- 명령어 변경 시 한 곳만 수정
- 주석으로 각 명령어 설명 제공

#### ✅ 구현 방법

```javascript
/**
 * BotName v1.0
 * 명령어 정의 섹션
 */

// ============= 명령어 상수 정의 =============
// 기본 명령어
var CMD_HELP = "!도움말";           // 도움말 표시
var CMD_STATUS = "!상태";           // 봇 상태 확인
var CMD_VERSION = "!버전";          // 버전 정보

// 기능 명령어
var CMD_SCHEDULE = "!일정";         // 일정 조회
var CMD_ADD_SCHEDULE = "!일정추가";  // 일정 추가
var CMD_DEL_SCHEDULE = "!일정삭제";  // 일정 삭제
var CMD_REMINDER = "!알림설정";      // 알림 설정

// 관리자 명령어
var CMD_ADMIN_RELOAD = "!리로드";   // 설정 리로드
var CMD_ADMIN_RESET = "!초기화";     // 봇 초기화
var CMD_ADMIN_DEBUG = "!디버그";     // 디버그 모드

// ============= 명령어 처리 =============
function onMessage(msg) {
    var content = msg.content.trim();
    
    // switch-case로 명령어 처리
    switch(content.split(" ")[0]) {
        case CMD_HELP:
            showHelp(msg);
            break;
            
        case CMD_STATUS:
            showStatus(msg);
            break;
            
        case CMD_SCHEDULE:
            showSchedule(msg);
            break;
            
        case CMD_ADD_SCHEDULE:
            addSchedule(msg);
            break;
            
        default:
            // 명령어가 아닌 경우
            break;
    }
}

// 도움말 생성 시 명령어 상수 활용
function showHelp(msg) {
    var help = "📋 사용 가능한 명령어:\n";
    help += CMD_HELP + " - 도움말 표시\n";
    help += CMD_STATUS + " - 봇 상태 확인\n";
    help += CMD_SCHEDULE + " - 일정 조회\n";
    help += CMD_ADD_SCHEDULE + " [내용] - 일정 추가\n";
    
    msg.reply(help);
}
```

---

## 📋 체크리스트

### 새 봇 개발 시
- [ ] 명령어 상수를 코드 상단에 정의했는가?
- [ ] Thread 사용 시 interrupt() 대신 플래그를 사용하는가?
- [ ] 모든 Thread에 try-catch를 적용했는가?
- [ ] 글로벌 모듈은 Bots 루트에 배치했는가?

### 기존 봇 리팩토링 시
- [ ] 중복된 모듈 파일을 제거했는가?
- [ ] interrupt() 사용 부분을 플래그로 변경했는가?
- [ ] 명령어를 상단 상수로 추출했는가?
- [ ] 무한 루프에 안전 장치를 추가했는가?

---

## 🔄 향후 추가 예정 표준

### Version 1.1.0 (예정)
- [ ] 로깅 표준화 (Log Level, 포맷)
- [ ] 에러 메시지 표준화
- [ ] 설정 파일 구조 표준화

### Version 1.2.0 (예정)  
- [ ] 멀티턴 대화 상태 관리 표준
- [ ] API 호출 재시도 패턴
- [ ] 메모리 관리 모범 사례

---

## 📚 관련 문서

- [크래시 히스토리](../troubleshooting/18TH_GPTERS_CRASH_HISTORY.md)
- [봇 독립성 체크리스트](../principles/BOT_INDEPENDENCE_CHECKLIST.md)
- [Thread 관리 가이드](../education/THREAD_FILE_MANAGEMENT_EXPLAINED.md)

---

## 🏷️ 태그

`#standards` `#messenger-bot` `#javascript` `#es5` `#rhino` `#thread-safety` `#module-management` `#crash-prevention`

---

**📝 Note**: 이 문서는 지속적으로 업데이트됩니다. 새로운 패턴이나 문제 해결 방법이 발견되면 버전을 올리고 내용을 추가합니다.