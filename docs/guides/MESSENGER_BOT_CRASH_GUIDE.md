# 🚨 메신저봇 크래시 & 좀비 프로세스 완벽 해결 가이드

> **최종 업데이트**: 2025-09-26 23:30  
> **대상**: 메신저봇 개발자 및 사용자 (비개발자도 OK!)  
> **목적**: 메신저봇 앱 크래시 원인 분석, 해결 및 좀비 프로세스 퇴치

---

## 📌 목차
1. [🆕 좀비 프로세스란?](#좀비-프로세스란)
2. [즉시 확인사항](#즉시-확인사항)
3. [주요 크래시 원인](#주요-크래시-원인)
4. [🆕 좀비 프로세스 완벽 퇴치법](#좀비-프로세스-완벽-퇴치법)
5. [긴급 응급처치](#긴급-응급처치)
6. [근본적 해결방법](#근본적-해결방법)
7. [예방 가이드](#예방-가이드)
8. [문제별 체크리스트](#문제별-체크리스트)

---

## 🧟 좀비 프로세스란?

### 쉬운 설명
> **좀비 프로세스 = 죽지 않는 과거 코드**

봇을 수정하고 컴파일했는데도 **이전 버전 코드가 계속 살아서 작동**하는 현상입니다.

### 실제 증상 예시
```
📱 당신: 봇 시간을 22:12에서 19:10으로 변경 → 컴파일
⏰ 19:10: 봇이 정상 작동 ✅
⏰ 22:12: 어? 봇이 또 작동? 🧟 (좀비!)
```

### 왜 발생하나요?
```
┌─────────────┐  컴파일  ┌─────────────┐
│  구 버전     │ ───X──→ │   죽어야 함   │
│  (22:12)    │         │              │
└─────────────┘         └─────────────┘
       ↓ 하지만...
┌─────────────┐         ┌─────────────┐
│  구 버전     │         │   신 버전    │
│  🧟 계속 살아있음 │      │   (19:10)   │
└─────────────┘         └─────────────┘
    둘 다 작동! 😱
```

---

## 🔥 즉시 확인사항

### 크래시 발생 시 1분 내 체크리스트
```bash
□ 메신저봇 앱이 완전히 멈췄는가? (앱 열림 여부)
□ 특정 봇 컴파일 후 발생했는가?
□ 최근 30분 내 새로운 봇을 추가했는가?
□ "Thread" 관련 코드를 수정했는가?
□ 메모리 사용량이 80% 이상인가?
□ 🆕 같은 작업이 여러 번 실행되는가? (좀비 징후!)
```

### 즉시 시도할 수 있는 복구 방법
1. **강제 종료**: 설정 → 앱 → 메신저봇 → 강제 종료
2. **캐시 삭제**: 설정 → 앱 → 메신저봇 → 저장공간 → 캐시 삭제
3. **문제 봇 비활성화**: 메신저봇 앱 → 가장 최근 수정한 봇 OFF
4. **재시작**: 휴대폰 재부팅

---

## 🚨 주요 크래시 원인

### 1. Thread.interrupt() 오류 ⚠️ 가장 흔함
**증상**
- 컴파일 직후 앱이 멈춤
- "앱이 반복해서 중단됨" 팝업
- `UnsupportedOperationException` 로그

**원인 코드 예시**
```javascript
// ❌ 위험한 코드
if (myThread) {
    myThread.interrupt();  // 크래시 원인!
}

// ✅ 안전한 코드
if (myThread) {
    isRunning = false;  // 플래그 사용
    myThread = null;
}
```

**해결책**
- `interrupt()` 호출 제거
- 플래그 변수로 대체
- try-catch로 감싸기

---

### 2. 메모리 누수 (무한 배열 증가)
**증상**
- 시간이 지날수록 느려짐
- 3-4시간 후 크래시
- 메모리 사용량 지속 증가

**원인 코드 예시**
```javascript
// ❌ 위험한 코드
var messages = [];
while (true) {
    messages.push({...});  // 무한 증가!
    Thread.sleep(1000);
}

// ✅ 안전한 코드
var messages = [];
while (true) {
    messages.push({...});
    if (messages.length > 100) {
        messages = messages.slice(-50);  // 크기 제한
    }
    Thread.sleep(1000);
}
```

---

### 3. 다중 Thread 생성
**증상**
- "Too many threads" 오류
- 봇 응답 없음
- 시스템 전체 느려짐

**원인 코드 예시**
```javascript
// ❌ 위험한 코드
function onMessage(msg) {
    new java.lang.Thread({
        run: function() { /*...*/ }
    }).start();  // 매번 새 Thread!
}

// ✅ 안전한 코드
var workerThread = null;
function onMessage(msg) {
    if (!workerThread) {
        workerThread = new java.lang.Thread({/*...*/});
        workerThread.start();
    }
}
```

---

### 4. 무한 루프 내 예외 처리 실패
**증상**
- 봇이 갑자기 작동 중지
- 재컴파일해도 작동 안 함
- 로그에 Exception 반복

**원인 코드 예시**
```javascript
// ❌ 위험한 코드
while (true) {
    var result = api.call();  // 예외 발생 가능
    Thread.sleep(1000);
}

// ✅ 안전한 코드
while (true) {
    try {
        var result = api.call();
    } catch (e) {
        Log.e("API 호출 실패: " + e);
    }
    Thread.sleep(1000);
}
```

---

## 🎯 좀비 프로세스 완벽 퇴치법

### 🔴 문제: 컴파일해도 이전 코드가 계속 실행됨

#### 실제 사례
```javascript
// 시간을 22:12 → 19:10으로 변경했는데
// 22:12에도 여전히 실행되는 문제!
```

### ✅ 해결책: 고유 ID로 좀비 감지 & 자동 퇴치

#### 1️⃣ 복붙해서 쓰는 완벽한 좀비 퇴치 코드

```javascript
/**
 * 🧟 좀비 프로세스 완벽 퇴치 시스템
 * 그대로 복사해서 봇 상단에 붙여넣기!
 */

// ===== 1. 고유 인스턴스 ID 생성 =====
var instanceId = new Date().getTime() + "_" + Math.random();
var SystemProps = java.lang.System;

// ===== 2. 전역 ID 관리 (좀비 감지용) =====
var ACTIVE_ID_KEY = "msgbot." + scriptName + ".activeId";

// ===== 3. 실행 플래그 =====
var isRunning = true;
var myThread = null;

// ===== 4. 좀비 체크 함수 =====
function amIZombie() {
    var activeId = SystemProps.getProperty(ACTIVE_ID_KEY);
    return activeId && activeId !== instanceId;
}

// ===== 5. 좀비 퇴치 Thread 패턴 =====
function startSafeThread() {
    // 기존 좀비 처리
    SystemProps.setProperty(ACTIVE_ID_KEY, instanceId);
    
    myThread = new java.lang.Thread(new java.lang.Runnable({
        run: function() {
            while (isRunning) {
                try {
                    // 좀비 체크 - 자동 종료!
                    if (amIZombie()) {
                        Log.i("🧟 좀비 감지! 자동 종료: " + instanceId);
                        break;
                    }
                    
                    // === 여기에 실제 작업 코드 ===
                    doWork();
                    
                    java.lang.Thread.sleep(1000);
                } catch(e) {
                    Log.e("오류: " + e);
                }
            }
            Log.i("Thread 정상 종료");
        }
    }));
    
    myThread.start();
}

// ===== 6. 컴파일 시 자동 정리 =====
function onStartCompile() {
    // 새 ID로 교체 → 기존 좀비 자동 종료
    var newId = new Date().getTime() + "_" + Math.random();
    SystemProps.setProperty(ACTIVE_ID_KEY, newId);
    
    isRunning = false;
    myThread = null;
    instanceId = newId;
    
    // 재시작
    isRunning = true;
    startSafeThread();
}
```

#### 2️⃣ 작동 원리 (그림으로 쉽게!)

```
컴파일 전:
┌──────────────────┐
│ Thread A (좀비)   │ ID: 12345_0.5
│ 계속 실행 중...   │ activeId: 12345_0.5
└──────────────────┘

↓ 컴파일!

컴파일 후:
┌──────────────────┐        ┌──────────────────┐
│ Thread A (좀비)   │        │ Thread B (신규)   │
│ ID: 12345_0.5    │        │ ID: 67890_0.8    │
│ activeId ≠ myId  │ ←체크→ │ activeId: 67890_0.8│
│ "난 좀비다!" 💀   │        │ "난 정상!" ✅      │
│ → 자동 종료       │        │ → 계속 실행       │
└──────────────────┘        └──────────────────┘
```

#### 3️⃣ 실제 적용 예시 (스케줄러)

```javascript
// TriggerSender 실제 코드
var schedulerInstanceId = new Date().getTime() + "_" + Math.random();

function runScheduler() {
    // 기존 좀비 알림
    var oldId = SystemProps.getProperty("msgbot.scheduler.activeId");
    if (oldId && oldId !== schedulerInstanceId) {
        Log.i("🧟 기존 스케줄러 감지, 교체 중...");
    }
    
    // 새 ID 등록
    SystemProps.setProperty("msgbot.scheduler.activeId", schedulerInstanceId);
    
    schedulerThread = new java.lang.Thread(new java.lang.Runnable({
        run: function() {
            while (true) {
                // 매번 체크!
                var activeId = SystemProps.getProperty("msgbot.scheduler.activeId");
                if (activeId !== schedulerInstanceId) {
                    Log.i("🧟→💀 좀비 자살: " + schedulerInstanceId);
                    break;  // 자동 종료!
                }
                
                // 정상 작업
                checkSchedule();
                Thread.sleep(30000);
            }
        }
    }));
    
    schedulerThread.start();
}
```

### 📊 적용 전후 비교

| 상황 | 적용 전 | 적용 후 |
|------|---------|---------|
| 컴파일 후 | 이전 Thread 계속 실행 🧟 | 이전 Thread 자동 종료 💀 |
| 중복 실행 | 여러 개 동시 실행 😱 | 항상 1개만 실행 ✅ |
| 수동 작업 | 앱 재시작 필요 😤 | 자동 처리 😎 |

### 🎮 즉시 적용 가능한 명령어

봇에 추가할 디버그 명령어:

```javascript
// 좀비 상태 확인 명령어
if (msg.content === "!좀비체크") {
    var activeId = SystemProps.getProperty(ACTIVE_ID_KEY);
    var status = "🔍 좀비 체크\n";
    status += "내 ID: " + instanceId + "\n";
    status += "활성 ID: " + activeId + "\n";
    status += "상태: " + (activeId === instanceId ? "✅ 정상" : "🧟 좀비") + "\n";
    msg.reply(status);
}

// 좀비 강제 퇴치 명령어
if (msg.content === "!좀비퇴치") {
    // 새 ID로 강제 교체
    var newId = new Date().getTime() + "_" + Math.random();
    SystemProps.setProperty(ACTIVE_ID_KEY, newId);
    msg.reply("💀 모든 좀비 프로세스 종료 명령 전달!\n3초 내 자동 정리됩니다.");
}
```

---

## 💊 긴급 응급처치

### Step 1: 앱 복구 (5분)
```
1. 메신저봇 강제 종료
2. 캐시 삭제
3. 휴대폰 재부팅
4. 메신저봇 재실행
```

### Step 2: 문제 봇 격리 (3분)
```
1. 모든 봇 비활성화
2. 하나씩 활성화하며 테스트
3. 크래시 유발 봇 확인
4. 해당 봇만 비활성화 유지
```

### Step 3: 임시 수정 (10분)
```
1. 문제 봇 코드 열기
2. Ctrl+F로 "interrupt" 검색
3. 해당 줄 주석 처리 (//)
4. 저장 후 재컴파일
```

---

## 🔧 근본적 해결방법

### 1. Thread 관리 개선
```javascript
// Thread 상태 관리 패턴
var ThreadManager = {
    threads: {},
    
    start: function(name, runnable) {
        if (this.threads[name]) {
            Log.w(name + " Thread 이미 실행 중");
            return;
        }
        
        this.threads[name] = new java.lang.Thread({
            run: function() {
                try {
                    runnable();
                } finally {
                    delete ThreadManager.threads[name];
                }
            }
        });
        this.threads[name].start();
    },
    
    stop: function(name) {
        if (this.threads[name]) {
            // interrupt 사용하지 않음
            delete this.threads[name];
        }
    }
};
```

### 2. 메모리 관리 자동화
```javascript
// 자동 메모리 정리
var MemoryManager = {
    init: function() {
        // 30분마다 정리
        setInterval(function() {
            this.cleanup();
        }.bind(this), 30 * 60 * 1000);
    },
    
    cleanup: function() {
        // 캐시 정리
        if (global.cache && global.cache.length > 100) {
            global.cache = global.cache.slice(-50);
        }
        
        // 가비지 컬렉션 요청
        java.lang.System.gc();
        
        Log.i("메모리 정리 완료");
    }
};
```

### 3. 안전한 파일 기반 Thread 관리
```javascript
// PID 파일 기반 관리 (BridgeBot 방식)
var SafeThreadManager = {
    STATE_FILE: "/storage/emulated/0/msgbot/thread_state.txt",
    
    isRunning: function() {
        var file = new java.io.File(this.STATE_FILE);
        if (!file.exists()) return false;
        
        // 파일 수정 시간 체크 (30초 이상 오래됨 = 죽음)
        var age = Date.now() - file.lastModified();
        return age < 30000;
    },
    
    updateState: function() {
        var file = new java.io.File(this.STATE_FILE);
        file.createNewFile();
        file.setLastModified(Date.now());
    }
};
```

---

## 🛡️ 예방 가이드

### 개발 시 필수 규칙
1. ✅ **절대 `interrupt()` 사용 금지**
2. ✅ **배열/객체 크기 제한 설정**
3. ✅ **Thread 수 최대 5개 제한**
4. ✅ **모든 while 루프에 try-catch**
5. ✅ **30분마다 메모리 정리**
6. ✅ **🆕 모든 Thread에 고유 ID 부여 (좀비 방지)**
7. ✅ **🆕 컴파일 시 ID 교체로 자동 정리**

### 코드 리뷰 체크리스트
```javascript
// 위험 패턴 검색 명령어
□ grep "interrupt()" *.js
□ grep "while.*true" *.js
□ grep "new.*Thread" *.js | wc -l  // 5개 이하 확인
□ grep "push(" *.js  // 배열 크기 체크 여부 확인
```

### 🆕 좀비 방지 기능이 포함된 안전한 봇 템플릿
```javascript
/**
 * 안전한 봇 템플릿 v2.0 - 좀비 프로세스 방지 기능 포함!
 * 이 템플릿을 기반으로 봇을 만들면 크래시 & 좀비 걱정 없음!
 */
var scriptName = "SafeBot_v2";
var bot = BotManager.getCurrentBot();

// ===== 좀비 방지 시스템 =====
var instanceId = new Date().getTime() + "_" + Math.random();
var SystemProps = java.lang.System;
var ACTIVE_ID_KEY = "msgbot." + scriptName + ".activeId";

// Thread 관리
var isRunning = true;
var workerThread = null;

// 메모리 관리
var messageCache = [];
var MAX_CACHE_SIZE = 100;

// 좀비 체크 함수
function amIZombie() {
    var activeId = SystemProps.getProperty(ACTIVE_ID_KEY);
    return activeId && activeId !== instanceId;
}

// 안전한 Thread 시작
function startWorkerThread() {
    // ID 등록
    SystemProps.setProperty(ACTIVE_ID_KEY, instanceId);
    
    workerThread = new java.lang.Thread(new java.lang.Runnable({
        run: function() {
            while (isRunning) {
                try {
                    // 좀비 체크 - 자동 종료!
                    if (amIZombie()) {
                        Log.i("🧟→💀 좀비 자동 종료");
                        break;
                    }
                    
                    // 실제 작업
                    doBackgroundWork();
                    
                    java.lang.Thread.sleep(1000);
                } catch(e) {
                    Log.e("Thread 오류: " + e);
                }
            }
        }
    }));
    workerThread.start();
}

function onStartCompile() {
    // 새 ID 생성 → 기존 좀비 자동 종료
    var newId = new Date().getTime() + "_" + Math.random();
    SystemProps.setProperty(ACTIVE_ID_KEY, newId);
    
    // 안전한 종료
    isRunning = false;
    workerThread = null;
    
    // 캐시 정리
    messageCache = [];
    
    // 새 인스턴스로 재시작
    instanceId = newId;
    isRunning = true;
    
    Log.i("✅ 봇 초기화 완료. ID: " + instanceId);
}

function onMessage(msg) {
    try {
        // 캐시 크기 관리
        messageCache.push(msg);
        if (messageCache.length > MAX_CACHE_SIZE) {
            messageCache = messageCache.slice(-50);
        }
        
        // 좀비 체크 명령어
        if (msg.content === "!상태") {
            var activeId = SystemProps.getProperty(ACTIVE_ID_KEY);
            msg.reply("🤖 봇 상태\n" +
                     "ID: " + instanceId.substring(0, 10) + "...\n" +
                     "활성: " + (activeId === instanceId ? "✅" : "🧟") + "\n" +
                     "캐시: " + messageCache.length + "/" + MAX_CACHE_SIZE);
            return;
        }
        
        // 메인 로직
        processMessage(msg);
        
    } catch (e) {
        Log.e("메시지 처리 오류: " + e);
    }
}

function processMessage(msg) {
    // 실제 봇 로직
}

function doBackgroundWork() {
    // 백그라운드 작업
}

// 30분마다 정리
setInterval(function() {
    if (!amIZombie()) {  // 좀비가 아닐 때만
        messageCache = [];
        java.lang.System.gc();
        Log.i("📊 메모리 정리 완료");
    }
}, 30 * 60 * 1000);

// Thread 시작 (필요한 경우)
// startWorkerThread();
```

---

## 📋 문제별 체크리스트

### 🔴 앱이 완전히 멈춤
```
□ Thread.interrupt() 검색 및 제거
□ 모든 봇 비활성화 후 하나씩 테스트
□ 메신저봇 앱 재설치
```

### 🟡 특정 봇만 작동 안 함
```
□ 해당 봇 로그 확인
□ try-catch 누락 확인
□ API 연결 상태 확인
□ 봇 재컴파일
```

### 🟢 가끔 느려짐
```
□ 메모리 사용량 확인
□ 배열 크기 제한 추가
□ 30분 자동 정리 코드 추가
□ 불필요한 로그 제거
```

### 🧟 중복 실행 / 좀비 프로세스
```
□ !좀비체크 명령어로 상태 확인
□ 고유 ID 시스템 적용 여부 확인
□ onStartCompile에서 ID 교체 코드 확인
□ Thread 내부에 좀비 체크 로직 추가
□ !좀비퇴치 명령어 실행
```

---

## 📚 추가 참고자료

- [메신저봇 공식 문서](https://violet.develope.kr)
- [Thread 관리 상세 가이드](./THREAD_MANAGEMENT_GUIDE.md)
- [메모리 최적화 가이드](./MEMORY_OPTIMIZATION_GUIDE.md)

---

## 🏆 좀비 프로세스 퇴치 성공 사례

### Case 1: TriggerSender 스케줄러
- **문제**: 시간 변경 후에도 이전 시간에 계속 실행
- **해결**: 고유 ID 시스템 적용
- **결과**: 중복 실행 완전 해결 ✅

### Case 2: TriggerReceiver 중앙 처리
- **문제**: 컴파일해도 이전 Thread가 큐 계속 처리
- **해결**: 인스턴스 ID로 자가 종료
- **결과**: 항상 최신 버전만 실행 ✅

## 🆘 도움 요청

해결되지 않는 경우:
1. 메신저봇 카카오톡 오픈채팅방
2. 디스코드 커뮤니티
3. GitHub Issues

---

**⚠️ 주의**: 이 문서는 지속적으로 업데이트됩니다. 새로운 크래시 패턴이 발견되면 추가될 예정입니다.

**🎉 좀비 프로세스 퇴치법 추가**: 2025-09-26 검증된 실전 코드로 업데이트!