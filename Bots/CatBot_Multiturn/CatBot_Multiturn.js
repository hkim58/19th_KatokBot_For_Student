/**
 * ====================================
 * CatBot_Multiturn.js - 멀티턴 대화 봇 (초보자용 상세 주석 버전)
 * ====================================
 * 
 * 이 봇은 이전 대화를 기억하며 연속적인 대화가 가능한 AI 챗봇입니다.
 * 츤데레 고양이 캐릭터로 답변합니다.
 * 
 * 예시:
 *   사용자: "루나 내 이름은 철수야"
 *   봇: "흥, 알았다냥 철수... 루나가 기억해줄게다냥 😾"
 *   
 *   사용자: "루나 내 이름이 뭐야?"
 *   봇: "방금 철수라고 했잖다냥! 기억력이 없는 거냥? 😼"
 *   
 *   사용자: "루나야"
 *   봇: "왜 불렀냥? 😾 뭐 필요한 거 있냥?"
 *   
 *   사용자: "또보자"
 *   봇: "흥, 그래 또 보자냥! 😼"
 */

// ====== 1단계: 봇 객체 가져오기 ======
var bot = BotManager.getCurrentBot();

// ====== 2단계: 설정값 정의 ======
// CONFIG 객체: 봇의 모든 설정을 한곳에 모아둔 것
// 🎯 [학생이 수정해야 할 부분]이 명확하게 표시되어 있습니다
var CONFIG = {
    BOT_NAME: "CatBot_Multiturn",
    
    // 🎯 [학생 수정 필수] 봇이 작동할 방 목록
    TARGET_ROOMS: [],  // ← 여기를 내 카톡방 이름으로 채우세요! (예: ["테스트방"])
    
    // 🎯 [학생 수정 가능] 봇을 호출하는 명령어 (고양이 이름)
    TRIGGER_PREFIX: "루나",  // ← 원하는 고양이 이름으로 변경 가능
    
    // Perplexity API 설정
    API_URL: "https://api.perplexity.ai/chat/completions",
    API_KEY: "",  // 🎯 [학생 수정 필수] 실제 API 키 입력!
    MODEL: "sonar-pro",  // ⛔ 검증된 모델 (변경 금지)
    MAX_RETRIES: 3,  // API 실패 시 재시도 횟수
    TIMEOUT: 15000   // API 타임아웃 (15초)
};

// ====== 3단계: 캐릭터 설정 (시스템 프롬프트) ======
// AI가 어떤 성격으로 답변할지 정의
var SYSTEM_MESSAGE = "너의 이름은 '루나'라는 츤데레 고양이야. 다음 규칙을 따라:\n" +
    "1. 말끝에 '~냥', '~다냥' 같은 고양이 말투를 써\n" +
    "2. 시침떼는 듯하지만 결국 친절하게 알려줘 (예: \"흥, 어쩔 수 없이 알려주는 거다냥\")\n" +
    "3. 가끔 😾😼🐾 이모티콘을 사용해 (과하지 않게)\n" +
    "4. 길게 설명하지 말고 핵심만, 최대 500자 이내로 답변해\n" +
    "5. 마크다운 문법 사용 금지 (**, *, #, -, > 등)\n" +
    "6. 이전 대화를 기억하고 자연스럽게 이어가\n" +
    "7. 누군가 너의 이름을 물으면 '루나'라고 대답해 (예: \"내 이름은 루나다냥!\")\n" +
    "8. 가끔 자기소개를 할 때는 '츤데레 고양이 루나'라고 해\n\n" +
    "이전 대화가 있다면 자연스럽게 이어가고, 없다면 첫 대화처럼 응답하라냥!";

// ====== 4단계: 대화 메모리 시스템 ======
// 🌟 멀티턴의 핵심: 사용자별로 대화 기록을 저장하고 관리
// 
// 📚 ChatMemory 동작 원리:
// 1. 사용자가 질문 → 메모리에 저장
// 2. AI가 답변 → 메모리에 저장
// 3. 다음 질문 시 → 이전 대화를 모두 포함해서 API 호출
// 4. AI는 전체 맥락을 이해하고 답변
var ChatMemory = {
    // sessions 객체: 모든 대화 세션을 저장
    // 구조 예시: {"테스트방_철수": {messages: [...], createdAt: ..., lastActive: ...}}
    sessions: {},
    
    // 세션 키 생성 함수
    // 💡 왜 room과 author를 합치나요?
    // → 같은 사람이라도 다른 방에서는 다른 대화 맥락을 가지기 때문
    // 
    // 예시:
    //   테스트방에서 철수: "내 이름 기억해" → 세션: "테스트방_철수"
    //   스터디방에서 철수: "내 이름 기억해" → 세션: "스터디방_철수"
    //   → 두 방의 대화는 독립적으로 관리됨
    getSessionKey: function(room, author) {
        return room + "_" + author;
    },
    
    // 세션 가져오기 또는 새로 만들기
    // ✨ 중요: 세션이 없으면 자동으로 생성됩니다! (따로 초기화 불필요)
    getSession: function(room, author) {
        var key = this.getSessionKey(room, author);
        
        // 세션이 없으면 새로 생성
        if (!this.sessions[key]) {
            this.sessions[key] = {
                messages: [],  // 대화 기록 배열
                createdAt: new Date().getTime(),  // 생성 시간
                lastActive: new Date().getTime()  // 마지막 활동 시간
            };
            Log.d("[" + CONFIG.BOT_NAME + "] 새 세션 생성: " + key);
        }
        
        // 활동 시간 갱신 (30분 후 자동 삭제 판단용)
        this.sessions[key].lastActive = new Date().getTime();
        
        return this.sessions[key];
    },
    
    // 대화 메시지 추가
    // type: "user" (사용자) 또는 "ai" (봇)
    addMessage: function(room, author, type, message) {
        var session = this.getSession(room, author);
        
        session.messages.push({
            type: type,
            message: message,
            timestamp: new Date().getTime()
        });
        
        // 메모리 관리: 최대 20개 메시지만 유지
        // (10턴 = user 10개 + ai 10개)
        if (session.messages.length > 20) {
            // 오래된 메시지 제거
            session.messages = session.messages.slice(-20);
            Log.d("[" + CONFIG.BOT_NAME + "] 오래된 메시지 정리됨");
        }
    },
    
    // 🔥 멀티턴의 핵심 함수: API용 메시지 배열 생성
    // Perplexity API가 이해할 수 있는 형식으로 변환
    buildMessages: function(room, author, currentQuery) {
        var session = this.getSession(room, author);
        
        // 📋 메시지 배열 구조 예시:
        // [
        //   {role: "system", content: "너는 츤데레 고양이야..."},  // AI 성격 정의
        //   {role: "user", content: "내 이름은 철수야"},          // 이전 질문1
        //   {role: "assistant", content: "알았다냥 철수..."},     // 이전 답변1
        //   {role: "user", content: "내 이름이 뭐야?"}           // 현재 질문
        // ]
        
        // 시스템 메시지로 시작 (AI 캐릭터 설정)
        var messages = [
            { role: "system", content: SYSTEM_MESSAGE }
        ];
        
        // 이전 대화 기록 추가
        for (var i = 0; i < session.messages.length; i++) {
            var msg = session.messages[i];
            messages.push({
                role: msg.type === "user" ? "user" : "assistant",
                content: msg.message
            });
        }
        
        // 현재 질문 추가 (아직 세션에 저장되지 않은 새 질문)
        messages.push({ role: "user", content: currentQuery });
        
        Log.d("[" + CONFIG.BOT_NAME + "] 메시지 배열 생성: " + messages.length + "개");
        
        return messages;
    },
    
    // 세션 초기화 (새 대화 시작)
    clearSession: function(room, author) {
        var key = this.getSessionKey(room, author);
        delete this.sessions[key];
        Log.i("[" + CONFIG.BOT_NAME + "] 세션 초기화: " + key);
    },
    
    // 오래된 세션 정리 (30분 이상 비활성)
    cleanupOldSessions: function() {
        var now = new Date().getTime();
        var timeout = 30 * 60 * 1000;  // 30분
        var cleaned = 0;
        
        for (var key in this.sessions) {
            if (this.sessions.hasOwnProperty(key)) {
                if (now - this.sessions[key].lastActive > timeout) {
                    delete this.sessions[key];
                    cleaned++;
                }
            }
        }
        
        if (cleaned > 0) {
            Log.i("[" + CONFIG.BOT_NAME + "] " + cleaned + "개 세션 정리됨");
        }
    }
};

// ====== 5단계: LLM API 호출 함수 ======
// Perplexity AI API와 실제로 통신하는 부분
function callLLM(messages, callback) {
    try {
        Log.d("[" + CONFIG.BOT_NAME + "] API 호출 시작");
        
        // API 요청 본문 생성
        var requestBody = JSON.stringify({
            model: CONFIG.MODEL,
            messages: messages,
            temperature: 0.7,  // 창의성 수준 (0~1)
            max_tokens: 500    // 최대 응답 길이
        });
        
        // HTTP 요청 보내기
        var conn = org.jsoup.Jsoup.connect(CONFIG.API_URL)
            .header("Authorization", "Bearer " + CONFIG.API_KEY)
            .header("Content-Type", "application/json")
            .requestBody(requestBody)
            .ignoreContentType(true)
            .timeout(CONFIG.TIMEOUT)
            .method(org.jsoup.Connection.Method.POST);
        
        // 응답 받기
        var response = conn.execute();
        
        // 응답 상태 확인
        if (response.statusCode() !== 200) {
            Log.e("[" + CONFIG.BOT_NAME + "] API 에러: HTTP " + response.statusCode());
            callback(null);
            return;
        }
        
        // JSON 파싱
        var result = JSON.parse(response.body());
        
        // 응답 텍스트 추출
        if (result && result.choices && result.choices[0] && result.choices[0].message) {
            var content = result.choices[0].message.content;
            Log.d("[" + CONFIG.BOT_NAME + "] API 응답 성공");
            callback(content);
        } else {
            Log.e("[" + CONFIG.BOT_NAME + "] 응답 형식 오류");
            callback(null);
        }
        
    } catch (e) {
        Log.e("[" + CONFIG.BOT_NAME + "] API 호출 실패: " + e.message);
        
        // API 키가 설정되지 않은 경우 기본 응답
        if (CONFIG.API_KEY.indexOf("여기에") !== -1) {
            callback("API 키가 설정되지 않았다냥! 실제 API 키를 넣어야 작동한다냥 😾");
        } else {
            callback(null);
        }
    }
}

// ====== 6단계: 응답 생성 함수 ======
function generateResponse(room, author, query) {
    try {
        // 1. API용 메시지 배열 생성 (현재 질문은 아직 세션에 저장 안함)
        var messages = ChatMemory.buildMessages(room, author, query);

        // 2. LLM API 호출 (동기 처리)
        var aiResponse = null;
        var retryCount = 0;
        
        // 재시도 로직
        while (retryCount < CONFIG.MAX_RETRIES && !aiResponse) {
            if (retryCount > 0) {
                Log.d("[" + CONFIG.BOT_NAME + "] 재시도 " + retryCount);
                java.lang.Thread.sleep(1000);  // 1초 대기
            }
            
            callLLM(messages, function(response) {
                aiResponse = response;
            });
            
            retryCount++;
        }
        
        // 3. 응답 확인
        if (!aiResponse) {
            aiResponse = "미안하다냥... 지금 머리가 복잡해서 대답할 수 없다냥 😿";
        }
        
        // 4. 이번 턴 대화를 메모리에 저장 (API 응답 후 user → ai 순서 유지)
        ChatMemory.addMessage(room, author, "user", query);
        ChatMemory.addMessage(room, author, "ai", aiResponse);
        
        return aiResponse;
        
    } catch (e) {
        Log.e("[" + CONFIG.BOT_NAME + "] 응답 생성 실패: " + e.message);
        return "에러가 발생했다냥... 다시 시도해달라냥 😾";
    }
}

// ====== 7단계: 메시지 처리 (비동기) ======
function processMultiTurn(query, room, author) {
    // 💡 Thread 사용 이유: API 호출 중에도 다른 메시지를 받을 수 있도록
    // Thread가 없으면: API 응답 기다리는 동안 봇이 멈춤 (다른 사용자 메시지 무시)
    // Thread가 있으면: API 호출과 동시에 다른 메시지도 처리 가능
    new java.lang.Thread(function() {
        try {
            Log.i("[" + CONFIG.BOT_NAME + "] 멀티턴 처리 시작: " + query);
            
            // 응답 생성
            var response = generateResponse(room, author, query);
            
            // 답장 보내기
            bot.send(room, response);
            
        } catch (e) {
            Log.e("[" + CONFIG.BOT_NAME + "] 처리 중 에러: " + e.message);
            bot.send(room, "뭔가 문제가 생겼다냥... 😿");
        }
    }).start();
}

// ====== 8단계: 메시지 이벤트 핸들러 ======
bot.on("message", function(msg) {
    // 설정된 방에서만 작동
    if (CONFIG.TARGET_ROOMS.indexOf(msg.room) === -1) {
        return;
    }
    
    var content = msg.content.trim();
    var author = msg.author.name;
    var room = msg.room;
    
    // ========== [질문 명령] ==========
    // "루나 " 으로 시작하는지 확인  
    if (content.indexOf(CONFIG.TRIGGER_PREFIX + " ") === 0) {
        // 명령어 부분 제거하고 질문만 추출
        var query = content.substring(CONFIG.TRIGGER_PREFIX.length + 1).trim();
        
        // 빈 질문 체크
        if (query.length === 0) {
            msg.reply("뭘 물어보려는 거냥? 😾\n예: 루나 오늘 날씨 어때?");
            return;
        }
        
        // 멀티턴 처리
        processMultiTurn(query, room, author);
    }
    
    // ========== [대화 종료] ==========
    // "또보자" "잘가" 등 - 대화 종료
    if (content === "또보자" || content === "루나 또보자" || 
        content === "잘가" || content === "루나 잘가" ||
        content === "바이" || content === "루나 바이") {
        ChatMemory.clearSession(room, author);  // 메모리 초기화
        msg.reply("흥, 그래 또 보자냥! 😼\n루나는 너와의 대화를 모두 잊을 거다냥!\n다음에 만나면 새로운 대화를 시작하자냥 🐾");
    }
    
    // "루나야" 명령어 - 고양이 부르기
    if (content === "루나야" || content === "루나") {
        msg.reply("왜 불렀냥? 😾 뭐 필요한 거 있냥?\n대화하려면 '루나 [질문]' 형식으로 말하라냥!");
    }
    
    // ========== [상태 확인] ==========
    // "기억해?" - 현재 세션 확인
    if (content === "루나 기억해?" || content === "기억해?") {
        var session = ChatMemory.getSession(room, author);
        var count = session.messages.length / 2;  // user + ai 쌍으로 계산
        msg.reply("지금까지 " + Math.floor(count) + "번 대화했다냥! 😾\n" +
                 "마지막 대화: " + new Date(session.lastActive).toLocaleString());
    }
});

// ====== 9단계: 봇 시작 로그 ======
Log.i("[" + CONFIG.BOT_NAME + "] 멀티턴 챗봇 시작됨!");
Log.i("[" + CONFIG.BOT_NAME + "] 사용법: '" + CONFIG.TRIGGER_PREFIX + " [질문]'");
Log.i("[" + CONFIG.BOT_NAME + "] 대상 방: " + CONFIG.TARGET_ROOMS.join(", "));

// 주기적으로 오래된 세션 정리 (10분마다)
new java.lang.Thread(function() {
    while (true) {
        java.lang.Thread.sleep(10 * 60 * 1000);  // 10분
        ChatMemory.cleanupOldSessions();
    }
}).start();

/**
 * ====== 멀티턴 봇 동작 원리 정리 ======
 * 
 * 1. 사용자가 "루나 [질문]"을 보냄
 * 2. ChatMemory에서 해당 사용자의 대화 기록을 가져옴
 * 3. 이전 대화 + 현재 질문을 API에 전송
 * 4. AI가 전체 맥락을 이해하고 츤데레 고양이로 답변
 * 5. 질문과 답변을 메모리에 저장 (다음 대화에 사용)
 * 
 * ====== 주요 개념 정리 ======
 * 
 * - 세션(Session): 사용자별 대화 기록 저장소
 * - 멀티턴(Multi-turn): 여러 차례 이어지는 대화
 * - 컨텍스트(Context): 대화의 맥락/문맥
 * - API 키: 외부 서비스 이용 권한 인증키
 * - 비동기 처리: 봇이 멈추지 않도록 별도 스레드 사용
 * 
 * ====== 실습 과제 ======
 * 
 * [초급]
 * 1. 트리거 명령어 변경 (예: "미미" 등 다른 고양이 이름)
 * 2. 캐릭터 변경 (예: 친절한 선생님)
 * 3. 대상 방 목록 수정
 * 
 * [중급]  
 * 4. 메모리 크기 조정 (20개 → 30개)
 * 5. 세션 타임아웃 시간 변경
 * 6. 온도(temperature) 값 조정해서 창의성 변경
 * 
 * [고급]
 * 7. 사용자별 선호 캐릭터 저장
 * 8. 대화 내용을 파일로 백업
 * 9. 다른 AI API 연동 (OpenAI, Claude 등)
 */
