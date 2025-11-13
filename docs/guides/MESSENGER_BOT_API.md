# 📖 메신저봇 R API2 통합 가이드
> **클로드 코드를 위한 완전한 메신저봇 개발 레퍼런스**  
> 구조 가이드 + API 문서 + 실무 패턴을 하나로 통합

---

## 📋 목차

### 🚨 [1. 필수 구조 규칙](#1-필수-구조-규칙)
- [1.1 절대 지켜야 할 3가지 규칙](#11-절대-지켜야-할-3가지-규칙)
- [1.2 표준 코드 템플릿](#12-표준-코드-템플릿)
- [1.3 검증된 패턴들](#13-검증된-패턴들)

### 📚 [2. 핵심 API 객체](#2-핵심-api-객체)
- [2.1 Bot 객체](#21-bot-객체)
- [2.2 BotManager 객체](#22-botmanager-객체)
- [2.3 Event 객체](#23-event-객체)

### 🔗 [3. 데이터 & 통신 API](#3-데이터--통신-api)
- [3.1 HTTP 통신 (Jsoup 권장)](#31-http-통신-jsoup-권장)
- [3.2 Database 객체](#32-database-객체)
- [3.3 FileStream 객체](#33-filestream-객체)

### 🛠️ [4. 유틸리티 API](#4-유틸리티-api)
- [4.1 Console 객체](#41-console-객체)
- [4.2 Security 객체](#42-security-객체)
- [4.3 Broadcast 객체](#43-broadcast-객체)

### 💡 [5. 실무 예제 모음](#5-실무-예제-모음)
- [5.1 기본 자동응답 봇](#51-기본-자동응답-봇)
- [5.2 API 연동 봇](#52-api-연동-봇)
- [5.3 데이터 처리 봇](#53-데이터-처리-봇)

### 📌 [6. 버전별 호환성](#6-버전별-호환성)
### ⚠️ [7. 주요 주의사항](#7-주요-주의사항)

---

## 1. 필수 구조 규칙

### 1.1 절대 지켜야 할 3가지 규칙

#### 🔥 Rule 1: Bot 인스턴스 최상단 선언
```javascript
// ✅ 반드시 코드 첫 번째 줄!
var bot = BotManager.getCurrentBot();

// ❌ 다른 코드가 먼저 오면 순환 참조 오류
var CONFIG = {};
var bot = BotManager.getCurrentBot(); // 너무 늦음!
```

#### 🔥 Rule 2: 이벤트 리스너 최하단 등록
```javascript
// ✅ 모든 함수 정의 후 마지막에 등록
function onMessage(msg) { /* ... */ }
bot.addListener(Event.MESSAGE, onMessage);

// ❌ 함수 정의 전에 등록하면 오류
bot.addListener(Event.MESSAGE, onMessage); // 함수가 없음!
function onMessage(msg) { /* ... */ }
```

#### 🔥 Rule 3: ES5 문법만 사용
```javascript
// ✅ 메신저봇R 지원 문법
var config = { name: "봇" };
function handleMessage(msg) { }

// ❌ ES6+ 문법 (지원 안됨)
const config = { name: "봇" };
const handleMessage = (msg) => { };
```

### 1.2 표준 코드 템플릿

```javascript
// ===== 1. Bot 선언 (필수 - 최상단!) =====
var bot = BotManager.getCurrentBot();

// ===== 2. 설정 =====
var CONFIG = {
    BOT_NAME: "봇이름",
    VERSION: "1.0.0",
    TARGET_ROOMS: ["방이름1", "방이름2"],
    DEBUG_MODE: false
};

// ===== 3. 로깅 (권장) =====
var Log = {
    i: function(msg) { console.log("[INFO] " + msg); },
    d: function(msg) { console.log("[DEBUG] " + msg); },
    e: function(msg) { console.error("[ERROR] " + msg); }
};

// ===== 4. 유틸리티 함수들 =====
function safeAccess(obj, path, defaultValue) {
    try {
        return path.split('.').reduce(function(o, p) { return o[p]; }, obj) || defaultValue;
    } catch (e) {
        return defaultValue;
    }
}

// ===== 5. 비즈니스 로직 =====
function processCommand(content, msg) {
    if (content.startsWith("!도움말")) {
        return "사용 가능한 명령어:\n!도움말 - 이 메시지";
    }
    return null;
}

// ===== 6. 이벤트 핸들러 =====
function onMessage(msg) {
    try {
        // 방 필터링
        if (CONFIG.TARGET_ROOMS.indexOf(msg.room) === -1) {
            return;
        }
        
        // 안전한 데이터 추출
        var content = msg.content || "";
        var author = safeAccess(msg, 'author.name', 'Unknown');
        
        // 디버그 로그
        if (CONFIG.DEBUG_MODE) {
            Log.d("메시지: " + content + " from " + author);
        }
        
        // 명령어 처리
        var response = processCommand(content, msg);
        if (response) {
            msg.reply(response);
        }
        
    } catch (e) {
        Log.e("메시지 처리 오류: " + e.message);
    }
}

// ===== 7. 컴파일 이벤트 =====
function onStartCompile() {
    Log.i(CONFIG.BOT_NAME + " v" + CONFIG.VERSION + " 컴파일 시작");
}

// ===== 8. 이벤트 리스너 등록 (필수 - 최하단!) =====
bot.addListener(Event.MESSAGE, onMessage);
bot.addListener(Event.START_COMPILE, onStartCompile);

// ===== 9. 초기화 로그 (파일 끝에 직접 실행) =====
Log.i("================================");
Log.i(CONFIG.BOT_NAME + " v" + CONFIG.VERSION + " 로드 완료");
Log.i("대상 방: " + CONFIG.TARGET_ROOMS.join(", "));
Log.i("================================");
```

### 1.3 검증된 패턴들

#### 🛡️ 안전한 msg 객체 접근
```javascript
function safeMessageAccess(msg) {
    return {
        room: msg.room || "Unknown",
        content: msg.content || "",
        author: safeAccess(msg, 'author.name', 'Unknown'),
        hash: safeAccess(msg, 'author.hash', null),
        isGroup: msg.isGroupChat || false,
        packageName: msg.packageName || "com.kakao.talk"
    };
}
```

#### 🌐 HTTP 요청 패턴 (Jsoup 사용)
```javascript
function apiRequest(url, data, callback) {
    new java.lang.Thread(function() {
        try {
            var conn = org.jsoup.Jsoup.connect(url)
                .ignoreContentType(true)
                .header("Content-Type", "application/json")
                .timeout(30000);
            
            if (data) {
                conn.requestBody(JSON.stringify(data))
                    .method(org.jsoup.Connection.Method.POST);
            }
            
            var response = conn.execute();
            var statusCode = response.statusCode();
            
            if (statusCode === 200) {
                var result = JSON.parse(response.body());
                if (callback) callback(null, result);
            } else {
                Log.e("HTTP 오류: " + statusCode);
                if (callback) callback(new Error("HTTP " + statusCode), null);
            }
        } catch (e) {
            Log.e("API 요청 실패: " + e.message);
            if (callback) callback(e, null);
        }
    }).start();
}
```

---

## 2. 핵심 API 객체

### 2.1 Bot 객체

메신저봇의 핵심 기능을 담당하는 객체입니다.

#### 🔑 주요 메서드

##### `bot.addListener(eventName, listener)`
이벤트 리스너를 등록합니다.
```javascript
bot.addListener(Event.MESSAGE, function(msg) {
    console.log("메시지 수신: " + msg.content);
});
```

##### `bot.send(room, message, packageName)`
지정한 방에 메시지를 전송합니다.
```javascript
// 기본 사용
bot.send("테스트방", "안녕하세요!");

// 패키지 지정
bot.send("테스트방", "메시지", "com.kakao.talk");
```

##### `bot.setCommandPrefix(prefix)`
명령어 접두어를 설정합니다.
```javascript
bot.setCommandPrefix("!");
// 이제 "!도움말"은 COMMAND 이벤트로 처리됨

// COMMAND 이벤트 리스너
bot.addListener(Event.COMMAND, function(cmd) {
    console.log("명령어: " + cmd.command);        // "도움말"
    console.log("인자들: " + cmd.args.join(", ")); // 추가 인자들
    
    switch(cmd.command) {
        case "도움말":
            cmd.reply("사용 가능한 명령어를 표시합니다.");
            break;
        case "시간":
            cmd.reply("현재 시간: " + new Date().toLocaleString());
            break;
    }
});
```

##### `bot.canReply(room, packageName)`
해당 방에 메시지를 보낼 수 있는지 확인합니다.
```javascript
if (bot.canReply("테스트방")) {
    bot.send("테스트방", "메시지 전송 가능!");
}
```

#### 🎛️ 기타 메서드
- `bot.compile()` - 현재 봇 컴파일
- `bot.getName()` - 봇 이름 반환
- `bot.getPower()` - 봇 전원 상태
- `bot.setPower(power)` - 봇 전원 설정
- `bot.markAsRead(room, packageName)` - 읽음 표시

### 2.2 BotManager 객체

여러 봇을 관리하는 객체입니다.

#### 🔑 주요 메서드

##### `BotManager.getCurrentBot()`
현재 스크립트의 봇 인스턴스를 반환합니다.
```javascript
var bot = BotManager.getCurrentBot(); // 필수!
```

##### `BotManager.getBot(botName)`
특정 이름의 봇을 가져옵니다.
```javascript
var otherBot = BotManager.getBot("다른봇");
```

##### `BotManager.getRooms(packageName)`
수신한 메시지의 방 목록을 반환합니다.
```javascript
var rooms = BotManager.getRooms("com.kakao.talk");
console.log("카카오톡 방들: " + rooms.join(", "));
```

### 2.3 Event 객체

이벤트 상수를 제공합니다.

#### 📝 이벤트 타입
- `Event.MESSAGE` - 메시지 수신
- `Event.COMMAND` - 명령어 수신
- `Event.START_COMPILE` - 컴파일 시작
- `Event.NOTIFICATION_POSTED` - 알림 수신
- `Event.NOTIFICATION_REMOVED` - 알림 제거 (0.7.34a+)

#### 📋 MESSAGE 이벤트 객체 구조
```javascript
{
    room: "방이름",              // 문자열
    content: "메시지내용",
    author: {
        name: "발신자",
        hash: "해시값",          // 0.7.36a+
        avatar: {
            getBase64: function() { },  // 프로필 이미지 Base64
            getBitmap: function() { }   // 프로필 이미지 Bitmap
        }
    },
    isGroupChat: true,           // 단체방 여부
    isMultiChat: false,          // 듀얼 메신저 (0.7.36a+)
    isDebugRoom: false,          // 디버그룸 여부
    isMention: false,            // 멘션 포함 여부
    logId: "12345",              // 메시지 고유 ID (bigint)
    channelId: "67890",          // 방 고유 ID (bigint)
    packageName: "com.kakao.talk",
    reply: function(msg) { },    // 응답 함수
    markAsRead: function() { }   // 읽음 표시
}
```

#### 📋 COMMAND 이벤트 객체 구조
```javascript
{
    // MESSAGE 객체의 모든 속성 + 추가 속성
    command: "도움말",           // 명령어 이름
    args: ["인자1", "인자2"]     // 명령어 인자 배열
}
```

---

## 3. 데이터 & 통신 API

### 3.1 HTTP 통신 (Jsoup 권장)

#### ⚠️ 중요: Http.request vs Jsoup
```javascript
// ❌ Http.request - ConsString 오류 발생 가능
Http.request(url, options, callback);

// ✅ Jsoup - 안정적이고 권장
org.jsoup.Jsoup.connect(url).execute();
```

#### 🌐 Jsoup 사용법
```javascript
// GET 요청
function getRequest(url, callback) {
    new java.lang.Thread(function() {
        try {
            var response = org.jsoup.Jsoup.connect(url)
                .timeout(30000)
                .execute();
            
            var data = JSON.parse(response.body());
            callback(null, data);
        } catch (e) {
            callback(e, null);
        }
    }).start();
}

// POST 요청
function postRequest(url, data, callback) {
    new java.lang.Thread(function() {
        try {
            var response = org.jsoup.Jsoup.connect(url)
                .ignoreContentType(true)
                .header("Content-Type", "application/json")
                .requestBody(JSON.stringify(data))
                .method(org.jsoup.Connection.Method.POST)
                .timeout(30000)
                .execute();
            
            var result = JSON.parse(response.body());
            callback(null, result);
        } catch (e) {
            callback(e, null);
        }
    }).start();
}
```

### 3.2 Database 객체

봇 폴더 내 `/Database` 경로에 데이터를 저장합니다.

#### 💾 주요 메서드
```javascript
// JSON 객체 저장/읽기
var userData = { name: "홍길동", level: 5 };
Database.writeObject("user.json", userData);
var loaded = Database.readObject("user.json");

// 문자열 저장/읽기
Database.writeString("config.txt", "설정내용");
var config = Database.readString("config.txt");

// 파일 존재 확인
if (Database.exists("user.json")) {
    console.log("파일이 존재합니다");
}
```

### 3.3 FileStream 객체

파일 시스템 접근을 위한 API입니다.

#### 📁 주요 메서드 (0.7.39a+)
```javascript
// JSON 파일 처리
var data = FileStream.readJson("/storage/emulated/0/msgbot/data.json");
FileStream.writeJson("/storage/emulated/0/msgbot/output.json", data);

// 텍스트 파일 처리
FileStream.save("/storage/emulated/0/msgbot/log.txt", "로그내용\n", true); // 추가
FileStream.save("/storage/emulated/0/msgbot/data.txt", "내용", false); // 덮어쓰기

// 파일 관리
FileStream.copyFile("source.txt", "backup.txt");
FileStream.moveFile("old.txt", "new.txt");
FileStream.createDir("/storage/emulated/0/msgbot/newdir");
```

---

## 4. 유틸리티 API

### 4.1 Console 객체

로깅과 디버깅을 위한 API입니다.

#### 📝 기본 로깅
```javascript
console.log("일반 로그");
console.info("정보 메시지");
console.error("오류 메시지");
console.debug("디버그 메시지");
console.warn("경고 메시지"); // 0.7.39a+
```

#### 🔧 고급 로깅 패턴 (실무 권장)
```javascript
// DEBUG 모드 조건부 로깅
var Log = {
    i: function(msg) { console.log("[INFO] " + msg); },
    
    d: function(msg) {
        if (CONFIG.DEBUG_MODE) {
            console.log("[DEBUG] " + msg);
        }
    },
    
    e: function(msg) {
        console.error("[ERROR] " + msg);
    }
};

// 상세한 에러 로깅 (스택 트레이스 포함)
function handleError(e, context) {
    Log.e(context + " 오류: " + e.message);
    if (e.stack) {
        Log.e("스택 트레이스: " + e.stack);
    }
}

// 사용 예시
try {
    // 위험한 코드
} catch (e) {
    handleError(e, "API 호출");
}
```

#### ⏱️ 고급 기능 (0.7.39a+)
```javascript
// 시간 측정
console.time("작업");
// ... 작업 수행 ...
console.timeEnd("작업");

// 카운터
console.count("이벤트"); // 호출 횟수 계산
console.countReset("이벤트");

// 조건부 로깅
console.assert(user.level > 0, "레벨이 0 이하입니다");
```

### 4.2 Security 객체

암호화/해시 기능을 제공합니다.

#### 🔐 주요 메서드
```javascript
// 해시 함수
var hash = Security.md5("password");
var sha = Security.sha256("data");

// Base64 인코딩/디코딩
var encoded = Security.base64Encode("Hello");
var decoded = Security.base64Decode(encoded);

// UUID 생성 (0.7.39a+)
var uuid = Security.uuidv7();
var ulid = Security.ulid();
```

### 4.3 Broadcast 객체

봇 간 통신을 위한 API입니다.

#### 📡 사용법
```javascript
// 브로드캐스트 리스너 등록
Broadcast.register("dataUpdate", function(data) {
    console.log("데이터 업데이트: " + JSON.stringify(data));
});

// 다른 봇에서 브로드캐스트 전송
Broadcast.send("dataUpdate", { type: "user", action: "login" });
```

### 4.4 타이머 관리

메신저봇에서 타이머를 안전하게 사용하는 방법입니다.

#### ⏰ 타이머 API 사용법
```javascript
// 일회성 타이머 (전역 함수만 사용)
var timeoutId = setTimeout(function() {
    console.log("3초 후 실행");
}, 3000);
clearTimeout(timeoutId);

// 반복 타이머 (두 가지 방법)
// 방법 1: 전역 setInterval
var intervalId = setInterval(function() {
    console.log("매 5초마다 실행");
}, 5000);
clearInterval(intervalId);

// 방법 2: bot.setInterval (실제로 존재함)
var botIntervalId = bot.setInterval(function() {
    console.log("봇 타이머로 매 5초마다 실행");
}, 5000);
bot.clearInterval(botIntervalId);
```

#### 🔄 세션 관리 패턴 (세션 타임아웃)
```javascript
var activeSessions = {};
var SESSION_TIMEOUT = 30 * 60 * 1000; // 30분

function startSession(room) {
    activeSessions[room] = {
        startTime: new Date().getTime(),
        lastActivity: new Date().getTime()
    };
}

function checkSessionExpiry() {
    var currentTime = new Date().getTime();
    
    for (var room in activeSessions) {
        var session = activeSessions[room];
        if (currentTime - session.lastActivity >= SESSION_TIMEOUT) {
            // 세션 만료 처리
            delete activeSessions[room];
            bot.send(room, "⏰ 세션이 만료되었습니다.");
        }
    }
}

// 1분마다 세션 만료 체크
setInterval(checkSessionExpiry, 60000);
```

### 4.5 메모리 관리 패턴

대화형 봇을 위한 메모리 관리 방법입니다.

#### 🧠 세션 기반 메모리 관리
```javascript
var ChatMemory = {
    sessions: {}, // {room_author: {messages: []}}
    
    getSessionKey: function(room, author) {
        return room + "_" + author;
    },
    
    getSession: function(room, author) {
        var key = this.getSessionKey(room, author);
        if (!this.sessions[key]) {
            this.sessions[key] = { messages: [] };
        }
        return this.sessions[key];
    },
    
    addMessage: function(room, author, type, message) {
        var session = this.getSession(room, author);
        session.messages.push({
            type: type,    // "user" or "ai"
            message: message,
            timestamp: new Date().getTime()
        });
        
        // 컨텍스트 윈도우 관리 (최근 20개만 유지)
        if (session.messages.length > 20) {
            session.messages = session.messages.slice(-20);
        }
    },
    
    buildMessages: function(room, author, currentQuery) {
        var session = this.getSession(room, author);
        var messages = [];
        
        // 이전 대화 추가
        for (var i = 0; i < session.messages.length; i++) {
            var msg = session.messages[i];
            messages.push({
                role: msg.type === "user" ? "user" : "assistant",
                content: msg.message
            });
        }
        
        // 현재 질문 추가
        messages.push({ role: "user", content: currentQuery });
        return messages;
    }
};

// 사용 예시
function handleConversation(room, author, userMessage) {
    // 사용자 메시지 저장
    ChatMemory.addMessage(room, author, "user", userMessage);
    
    // AI 응답 생성 위한 메시지 배열 구성
    var messages = ChatMemory.buildMessages(room, author, userMessage);
    
    // API 호출 후 AI 응답도 저장
    callAI(messages, function(aiResponse) {
        ChatMemory.addMessage(room, author, "ai", aiResponse);
        bot.send(room, aiResponse);
    });
}
```

---

## 5. 실무 예제 모음

### 5.1 기본 자동응답 봇

```javascript
var bot = BotManager.getCurrentBot();

var CONFIG = {
    BOT_NAME: "AutoReply",
    TARGET_ROOMS: ["테스트방"],
    RESPONSES: {
        "안녕": ["안녕하세요!", "반가워요!", "하이!"],
        "뭐해": ["봇 일하는 중", "대기 중입니다"],
        "고마워": ["천만에요!", "도움이 되어 기뻐요"]
    }
};

function getRandomResponse(keyword) {
    var responses = CONFIG.RESPONSES[keyword];
    if (!responses) return null;
    var index = Math.floor(Math.random() * responses.length);
    return responses[index];
}

function onMessage(msg) {
    try {
        if (CONFIG.TARGET_ROOMS.indexOf(msg.room) === -1) return;
        
        var content = msg.content || "";
        
        for (var keyword in CONFIG.RESPONSES) {
            if (content.indexOf(keyword) !== -1) {
                var response = getRandomResponse(keyword);
                if (response) {
                    msg.reply(response);
                    return;
                }
            }
        }
    } catch (e) {
        console.error("오류: " + e.message);
    }
}

bot.addListener(Event.MESSAGE, onMessage);
console.log(CONFIG.BOT_NAME + " 준비 완료");
```

### 5.2 API 연동 봇

```javascript
var bot = BotManager.getCurrentBot();

var CONFIG = {
    BOT_NAME: "WeatherBot",
    API_URL: "https://api.weather.com/current",
    API_KEY: "YOUR_API_KEY"
};

function getWeather(city, callback) {
    var url = CONFIG.API_URL + "?city=" + encodeURIComponent(city) + "&key=" + CONFIG.API_KEY;
    
    new java.lang.Thread(function() {
        try {
            var response = org.jsoup.Jsoup.connect(url)
                .timeout(10000)
                .execute();
            
            if (response.statusCode() === 200) {
                var data = JSON.parse(response.body());
                var result = city + " 날씨\n";
                result += "온도: " + data.temp + "°C\n";
                result += "날씨: " + data.condition;
                callback(null, result);
            } else {
                callback(new Error("API 오류: " + response.statusCode()), null);
            }
        } catch (e) {
            callback(e, null);
        }
    }).start();
}

function onMessage(msg) {
    try {
        var content = msg.content || "";
        
        if (content.startsWith("!날씨 ")) {
            var city = content.substring(4).trim();
            if (city) {
                getWeather(city, function(error, result) {
                    if (error) {
                        msg.reply("날씨 정보를 가져올 수 없습니다: " + error.message);
                    } else {
                        msg.reply(result);
                    }
                });
            } else {
                msg.reply("사용법: !날씨 도시명");
            }
        }
    } catch (e) {
        console.error("오류: " + e.message);
    }
}

bot.addListener(Event.MESSAGE, onMessage);
console.log(CONFIG.BOT_NAME + " 준비 완료");
```

### 5.3 대화형 멀티턴 봇

```javascript
var bot = BotManager.getCurrentBot();

var CONFIG = {
    BOT_NAME: "멀티턴봇",
    TARGET_ROOMS: ["테스트방"],
    TRIGGER_PREFIX: "멀티턴톡",
    API_URL: "https://api.perplexity.ai/chat/completions",
    API_KEY: "your-api-key-here"
};

// 대화 메모리 관리
var ChatMemory = {
    sessions: {},
    
    getSessionKey: function(room, author) {
        return room + "_" + author;
    },
    
    addMessage: function(room, author, type, message) {
        var key = this.getSessionKey(room, author);
        if (!this.sessions[key]) {
            this.sessions[key] = { messages: [] };
        }
        
        this.sessions[key].messages.push({
            type: type,
            message: message
        });
        
        // 최근 10턴(20개 메시지)만 유지
        if (this.sessions[key].messages.length > 20) {
            this.sessions[key].messages = this.sessions[key].messages.slice(-20);
        }
    },
    
    buildMessages: function(room, author, query) {
        var key = this.getSessionKey(room, author);
        var messages = [
            { role: "system", content: "친근한 AI 어시스턴트로 답변해주세요." }
        ];
        
        if (this.sessions[key]) {
            for (var i = 0; i < this.sessions[key].messages.length; i++) {
                var msg = this.sessions[key].messages[i];
                messages.push({
                    role: msg.type === "user" ? "user" : "assistant",
                    content: msg.message
                });
            }
        }
        
        messages.push({ role: "user", content: query });
        return messages;
    }
};

function generateResponse(room, author, query) {
    new java.lang.Thread(function() {
        try {
            var messages = ChatMemory.buildMessages(room, author, query);
            
            var conn = org.jsoup.Jsoup.connect(CONFIG.API_URL)
                .header("Authorization", "Bearer " + CONFIG.API_KEY)
                .header("Content-Type", "application/json")
                .requestBody(JSON.stringify({
                    model: "sonar-pro",
                    messages: messages
                }))
                .ignoreContentType(true)
                .method(org.jsoup.Connection.Method.POST);
            
            var response = conn.execute();
            if (response.statusCode() === 200) {
                var result = JSON.parse(response.body());
                var aiResponse = result.choices[0].message.content;
                
                // 대화 저장
                ChatMemory.addMessage(room, author, "user", query);
                ChatMemory.addMessage(room, author, "ai", aiResponse);
                
                bot.send(room, aiResponse);
            }
        } catch (e) {
            bot.send(room, "오류가 발생했습니다: " + e.message);
        }
    }).start();
}

function onMessage(msg) {
    if (CONFIG.TARGET_ROOMS.indexOf(msg.room) === -1) return;
    
    var content = msg.content.trim();
    if (content.indexOf(CONFIG.TRIGGER_PREFIX + " ") === 0) {
        var query = content.substring(CONFIG.TRIGGER_PREFIX.length + 1).trim();
        if (query.length > 0) {
            generateResponse(msg.room, msg.author.name, query);
        }
    }
}

bot.addListener(Event.MESSAGE, onMessage);
console.log(CONFIG.BOT_NAME + " 준비 완료");
```

### 5.4 세션 기반 대화 봇 (호출어 제어)

```javascript
var bot = BotManager.getCurrentBot();

var CONFIG = {
    BOT_NAME: "SessionBot",
    TARGET_ROOMS: ["테스트방", "DEBUG ROOM"],
    WEBHOOK_URL: "http://your-server.com/webhook",
    SESSION_TIMEOUT: 30 * 60 * 1000,      // 30분 세션 타임아웃
    EXTENSION_THRESHOLD: 29 * 60 * 1000   // 29분에 연장
};

// 세션 관리 변수
var activeSessions = {};

// 세션 시작 함수
function startSession(room) {
    var currentTime = new Date().getTime();
    
    activeSessions[room] = {
        startTime: currentTime,
        lastActivity: currentTime
    };
    
    console.log("세션 시작: " + room);
    bot.send(room, "🔗 세션이 연결되었습니다. 이제 자유롭게 대화하세요!");
}

// 세션 종료 함수
function endSession(room) {
    delete activeSessions[room];
    
    console.log("세션 종료: " + room);
    bot.send(room, "🔌 세션이 종료되었습니다.");
}

// 세션 활성 상태 확인
function isSessionActive(room) {
    return activeSessions.hasOwnProperty(room);
}

// 세션 활동 시간 연장
function extendSession(room) {
    var currentTime = new Date().getTime();
    
    if (activeSessions[room]) {
        activeSessions[room].lastActivity = currentTime;
        console.log("세션 연장: " + room);
    }
}

// 세션 만료 체크 함수
function checkSessionExpiry() {
    var currentTime = new Date().getTime();
    
    for (var room in activeSessions) {
        var session = activeSessions[room];
        
        // 30분간 활동이 없으면 자동 종료
        if (currentTime - session.lastActivity >= CONFIG.SESSION_TIMEOUT) {
            console.log("세션 자동 만료: " + room);
            bot.send(room, "⏰ 30분간 활동이 없어 세션이 자동 종료되었습니다.");
            endSession(room);
        }
    }
}

// 서버로 메시지 전송 (세션이 활성일 때만)
function sendToServer(message, room) {
    if (!isSessionActive(room)) {
        bot.send(room, "❌ 활성 세션이 없습니다. '세션연결'을 먼저 해주세요.");
        return;
    }
    
    // 세션 활동 시간 연장
    extendSession(room);
    
    console.log("서버로 메시지 전송: " + message);
    
    new java.lang.Thread(function() {
        try {
            var conn = org.jsoup.Jsoup.connect(CONFIG.WEBHOOK_URL)
                .ignoreContentType(true)
                .header("Content-Type", "application/json")
                .timeout(30000)
                .requestBody(JSON.stringify({
                    query: message,
                    session: room
                }))
                .method(org.jsoup.Connection.Method.POST);
            
            var response = conn.execute();
            var statusCode = response.statusCode();
            
            if (statusCode === 200) {
                var result = JSON.parse(response.body());
                bot.send(room, result.answer);
            } else {
                bot.send(room, "❌ 서버 오류 발생 (HTTP " + statusCode + ")");
            }
        } catch (e) {
            console.error("서버 통신 오류: " + e.message);
            bot.send(room, "❌ 서버 연결 오류가 발생했습니다.");
        }
    }).start();
}

// 메시지 이벤트 핸들러
function onMessage(msg) {
    try {
        if (CONFIG.TARGET_ROOMS.indexOf(msg.room) === -1) {
            return;
        }
        
        var content = msg.content.trim();
        
        // '세션연결' 명령어 처리
        if (content === "세션연결") {
            if (isSessionActive(msg.room)) {
                bot.send(msg.room, "⚠️ 이미 활성 세션이 있습니다.");
            } else {
                startSession(msg.room);
            }
            return;
        }
        
        // '연결종료' 명령어 처리  
        if (content === "연결종료") {
            if (isSessionActive(msg.room)) {
                endSession(msg.room);
            } else {
                bot.send(msg.room, "⚠️ 활성 세션이 없습니다.");
            }
            return;
        }
        
        // 세션이 활성 상태라면 모든 메시지를 서버로 전송
        if (isSessionActive(msg.room)) {
            sendToServer(content, msg.room);
        }
        
    } catch (e) {
        console.error("메시지 처리 오류: " + e.message);
    }
}

// 이벤트 리스너 등록
bot.addListener(Event.MESSAGE, onMessage);

// 1분마다 세션 만료 체크
setInterval(checkSessionExpiry, 60000);

// 초기화 완료
console.log(CONFIG.BOT_NAME + " 준비 완료");
console.log("세션 타임아웃: " + (CONFIG.SESSION_TIMEOUT / 60000) + "분");
console.log("사용법:");
console.log("- '세션연결': 세션 시작");
console.log("- '연결종료': 세션 종료");
console.log("- 세션 중에는 모든 메시지가 서버로 전송됩니다.");
```

### 5.5 Activity 이벤트 처리 봇

```javascript
var bot = BotManager.getCurrentBot();

// UI 생성 함수
function onCreate(savedInstanceState, activity) {
    var textView = new android.widget.TextView(activity);
    textView.setText("메신저봇 UI가 생성되었습니다!");
    textView.setTextColor(android.graphics.Color.DKGRAY);
    activity.setContentView(textView);
    console.log("UI가 생성되었습니다.");
}

function onStart(activity) {
    console.log("액티비티가 시작되었습니다.");
}

function onResume(activity) {
    console.log("액티비티가 재개되었습니다.");
}

function onPause(activity) {
    console.log("액티비티가 일시정지되었습니다.");
}

function onBackPressed(activity) {
    console.log("뒤로 가기 버튼이 눌렸습니다.");
    return true; // true를 반환하면 기본 동작을 막음
}

// Activity 이벤트 리스너 등록
bot.addListener(Event.Activity.CREATE, onCreate);
bot.addListener(Event.Activity.START, onStart);
bot.addListener(Event.Activity.RESUME, onResume);
bot.addListener(Event.Activity.PAUSE, onPause);
bot.addListener(Event.Activity.BACK_PRESSED, onBackPressed);

console.log("Activity 이벤트 봇 준비 완료");
```

---

## 6. 버전별 호환성

### 📅 주요 버전별 차이점

| 기능 | 0.7.34a | 0.7.36a | 0.7.39a |
|------|---------|---------|---------|
| 작성자 해시 | `userHash` | `hash` | `hash` |
| 듀얼 메신저 | - | `isMultiChat` | `isMultiChat` |
| Console API | 기본 | 기본 | 가변인자 지원 |
| Security API | 기본 | 기본 | `ulid()`, `uuidv7()` |
| FileStream API | 기본 | 기본 | 확장 메서드 |
| Bot.send | 기본 | 기본 | 오류 수정 |

### 🔄 호환성 코드 예제

```javascript
// 작성자 해시 호환성
function getAuthorHash(msg) {
    if (!msg || !msg.author) return null;
    
    // 0.7.36a 이상
    if (typeof msg.author.hash !== 'undefined') {
        return msg.author.hash;
    }
    
    // 이전 버전
    if (typeof msg.author.userHash !== 'undefined') {
        return msg.author.userHash;
    }
    
    return null;
}

// 듀얼 메신저 호환성
function isMultiChat(msg) {
    return msg && typeof msg.isMultiChat !== 'undefined' ? 
           msg.isMultiChat : false;
}

// Console API 호환성
function safeLog(message) {
    try {
        console.log(message);
    } catch (e) {
        // 구버전 대체
        java.lang.System.out.println(message);
    }
}
```

---

## 7. 주요 주의사항

### ⚠️ 구조 관련 주의사항
1. **Bot 선언 순서**: 반드시 코드 최상단에 `var bot = BotManager.getCurrentBot();`
2. **이벤트 리스너**: 모든 함수 정의 후 최하단에서 등록
3. **ES5 문법**: const, let, 화살표함수, 템플릿리터럴 사용 금지
4. **초기화 로그**: 파일 끝에 직접 실행 (onStartCompile 이벤트만 사용하면 최초 로드 시 실행 안됨)

### ⚠️ API 사용 주의사항
1. **HTTP 통신**: Http.request 대신 Jsoup 사용 권장 (ConsString 오류 방지)
2. **msg 객체**: 안전한 접근을 위해 항상 null 체크
3. **파일 경로**: `/storage/emulated/0/msgbot/` 경로 사용
4. **Thread 사용**: 긴 작업은 반드시 Thread로 비동기 처리
5. **타이머 API**: `bot.setTimeout()` 존재하지 않음, `bot.setInterval()` 사용 가능

### ⚠️ 실무 보안 패턴
```javascript
// API 키 유효성 검사
function validateApiKey(apiKey) {
    if (!apiKey || apiKey.indexOf("여기에") !== -1 || apiKey.length < 10) {
        return false;
    }
    return true;
}

// Rate Limiting 패턴
var rateLimiter = {
    requests: {},
    limit: 5,        // 5회
    window: 60000,   // 1분
    
    canRequest: function(key) {
        var now = new Date().getTime();
        if (!this.requests[key]) {
            this.requests[key] = [];
        }
        
        // 시간 윈도우 밖의 요청들 제거
        this.requests[key] = this.requests[key].filter(function(time) {
            return now - time < this.window;
        });
        
        return this.requests[key].length < this.limit;
    },
    
    recordRequest: function(key) {
        this.requests[key].push(new Date().getTime());
    }
};

// 보호된 방 관리
var PROTECTED_ROOMS = ["관리자방", "중요방"];
function isProtectedRoom(room) {
    return PROTECTED_ROOMS.indexOf(room) !== -1;
}
```

### ⚠️ 디버깅 팁
```javascript
// 메시지 객체 완전 분석
function debugMessage(msg) {
    console.log("=== 메시지 객체 분석 ===");
    console.log("Room: " + msg.room);
    console.log("Content: " + msg.content);
    console.log("Author: " + JSON.stringify(msg.author));
    console.log("isGroupChat: " + msg.isGroupChat);
    console.log("isDebugRoom: " + msg.isDebugRoom);
    console.log("isMention: " + msg.isMention);
    console.log("logId: " + msg.logId);
    console.log("channelId: " + msg.channelId);
    console.log("Package: " + msg.packageName);
}

// 안전한 객체 접근
function safeAccess(obj, path, defaultValue) {
    try {
        return path.split('.').reduce(function(o, p) { return o[p]; }, obj) || defaultValue;
    } catch (e) {
        return defaultValue;
    }
}

// API 키 테스트 함수
function testApiKey(room) {
    if (!validateApiKey(CONFIG.API_KEY)) {
        bot.send(room, "❌ API 키가 설정되지 않았습니다.");
        return false;
    }
    bot.send(room, "🔍 API 키 테스트 중...");
    return true;
}
```

---

## 📝 빠른 체크리스트

코딩 후 반드시 확인:

- [ ] `var bot = BotManager.getCurrentBot();` 최상단 선언
- [ ] `bot.addListener()` 최하단 등록
- [ ] ES5 문법만 사용 (var, function)
- [ ] try-catch로 에러 처리
- [ ] msg 객체 안전 접근
- [ ] HTTP 통신 시 Jsoup 사용
- [ ] Thread로 비동기 처리
- [ ] 초기화 로그 파일 끝에 직접 실행

---

**🎯 이 가이드로 안전하고 효율적인 메신저봇 개발을 시작하세요!**