/**
 * =============================================
 * Google Calendar 심플 메신저봇 (개선된 버전)
 * =============================================
 * 
 * 특징:
 * - 코덱스 접근법 채택: 명령어를 서버에 직접 전송
 * - 최소한의 클라이언트 파싱
 * - 간단한 설정 (2개 변수만 수정)
 * - 서비스 계정 기반으로 인증 과정 생략
 * 
 * 명령어:
 * - "캘린더 조회 2024-01-15"
 * - "캘린더 추가 2024-01-15 14:00 팀 회의"  
 * - "캘린더 삭제 <event_id>"
 * - "오늘 일정", "내일 일정" (간편 명령어)
 */

// ====== 설정 구간 ======
var CONFIG = {
    BOT_NAME: "GoogleCalendarBot_Simple",
    
    // 🎯 [필수 수정] FastAPI 서버 URL
    FASTAPI_WEBHOOK_URL: "http://localhost:9000/webhook",  // 실제 서버 IP로 변경!
    
    // 🎯 [필수 수정] 봇이 작동할 방 목록
    TARGET_ROOMS: ["테스트방"],  // 실제 카톡방 이름으로 변경!
    
    // API 설정
    TIMEOUT: 15000,
    MAX_RETRIES: 3,
    USER_AGENT: "MessengerBot-GoogleCalendar-Simple/1.0"
};

// ====== 봇 객체 가져오기 ======
var bot = BotManager.getCurrentBot();

// ====== 유틸리티 함수 ======

/**
 * 오늘/내일 날짜를 YYYY-MM-DD 형식으로 반환
 */
function getDateString(offset) {
    var date = new Date();
    if (offset) {
        date.setDate(date.getDate() + offset);
    }
    
    var year = date.getFullYear();
    var month = String(date.getMonth() + 1).padStart(2, '0');
    var day = String(date.getDate()).padStart(2, '0');
    
    return year + "-" + month + "-" + day;
}

// ====== API 호출 함수 ======

/**
 * FastAPI 서버에 명령어 직접 전송 (코덱스 방식)
 */
function sendCommandToServer(command, room, author, retryCount) {
    if (retryCount === undefined) retryCount = 0;
    
    try {
        Log.i("[" + CONFIG.BOT_NAME + "] 서버 요청: " + command);
        
        // 요청 데이터 구성
        var requestData = {
            command: command,
            room: room,
            author: author,
            timestamp: new Date().toISOString()
        };
        
        // HTTP POST 요청
        var response = org.jsoup.Jsoup.connect(CONFIG.FASTAPI_WEBHOOK_URL)
            .header("Content-Type", "application/json")
            .header("User-Agent", CONFIG.USER_AGENT)
            .requestBody(JSON.stringify(requestData))
            .ignoreContentType(true)
            .timeout(CONFIG.TIMEOUT)
            .method(org.jsoup.Connection.Method.POST)
            .execute();
        
        var statusCode = response.statusCode();
        var responseBody = response.body();
        
        if (statusCode === 200) {
            Log.i("[" + CONFIG.BOT_NAME + "] 서버 응답 성공");
            
            // JSON 응답인 경우 파싱, 아니면 텍스트 그대로 반환
            try {
                var jsonResponse = JSON.parse(responseBody);
                return jsonResponse.message || jsonResponse.response || responseBody;
            } catch (e) {
                return responseBody;
            }
        } else {
            Log.e("[" + CONFIG.BOT_NAME + "] HTTP 에러: " + statusCode);
            throw new Error("서버 응답 에러: " + statusCode);
        }
        
    } catch (e) {
        Log.e("[" + CONFIG.BOT_NAME + "] API 호출 실패: " + e.message);
        
        // 재시도 로직
        if (retryCount < CONFIG.MAX_RETRIES) {
            Log.i("[" + CONFIG.BOT_NAME + "] 재시도 " + (retryCount + 1) + "/" + CONFIG.MAX_RETRIES);
            java.lang.Thread.sleep(2000);  // 2초 대기
            return sendCommandToServer(command, room, author, retryCount + 1);
        }
        
        return "❌ 서버 연결 실패: " + e.message + "\n잠시 후 다시 시도해주세요.";
    }
}

/**
 * 비동기 명령 처리
 */
function processCommandAsync(command, room, author, msg) {
    new java.lang.Thread(function() {
        try {
            Log.i("[" + CONFIG.BOT_NAME + "] 명령 처리 시작: " + command);
            
            // 서버에 명령 전송
            var response = sendCommandToServer(command, room, author);
            
            // 응답 전송
            msg.reply(response);
            
        } catch (e) {
            Log.e("[" + CONFIG.BOT_NAME + "] 명령 처리 에러: " + e.message);
            msg.reply("❌ 처리 중 오류가 발생했습니다: " + e.message);
        }
    }).start();
}

// ====== 메인 메시지 처리 ======

bot.on("message", function(msg) {
    // 설정된 방에서만 작동
    if (CONFIG.TARGET_ROOMS.indexOf(msg.room) === -1) {
        return;
    }
    
    var content = msg.content.trim();
    var room = msg.room;
    var author = msg.author.name;
    
    Log.i("[" + CONFIG.BOT_NAME + "] 메시지 수신: " + content);
    
    // ========== 캘린더 명령어 (서버에 직접 전송) ==========
    
    // 1. 정확한 캘린더 명령어
    if (content.startsWith("캘린더 조회") || 
        content.startsWith("캘린더 추가") || 
        content.startsWith("캘린더 삭제")) {
        
        processCommandAsync(content, room, author, msg);
        return;
    }
    
    // 2. 간편 명령어 → 표준 형식으로 변환
    if (content === "오늘 일정" || content === "오늘일정") {
        var todayCommand = "캘린더 조회 " + getDateString(0);
        processCommandAsync(todayCommand, room, author, msg);
        return;
    }
    
    if (content === "내일 일정" || content === "내일일정") {
        var tomorrowCommand = "캘린더 조회 " + getDateString(1);
        processCommandAsync(tomorrowCommand, room, author, msg);
        return;
    }
    
    if (content === "모레 일정" || content === "모레일정") {
        var dayAfterCommand = "캘린더 조회 " + getDateString(2);
        processCommandAsync(dayAfterCommand, room, author, msg);
        return;
    }
    
    // 3. 자연어 일정 추가 → 표준 형식으로 변환
    if (content.startsWith("일정 추가")) {
        // "일정 추가 내일 3시 회의" → "캘린더 추가 2024-01-16 15:00 회의"
        var parts = content.split(" ");
        if (parts.length >= 4) {
            var dateStr = parts[2];  // "내일"
            var timeStr = parts[3];  // "3시" 
            var title = parts.slice(4).join(" ") || "새 일정";
            
            // 날짜 변환
            var targetDate;
            if (dateStr === "오늘") {
                targetDate = getDateString(0);
            } else if (dateStr === "내일") {
                targetDate = getDateString(1);
            } else if (dateStr === "모레") {
                targetDate = getDateString(2);
            } else {
                targetDate = dateStr; // 이미 YYYY-MM-DD 형식인 경우
            }
            
            // 시간 변환 (간단한 파싱)
            var hour = parseInt(timeStr.replace(/[^0-9]/g, ""));
            if (timeStr.includes("오후") && hour !== 12) {
                hour += 12;
            } else if (timeStr.includes("오전") && hour === 12) {
                hour = 0;
            }
            var timeFormatted = String(hour).padStart(2, '0') + ":00";
            
            var standardCommand = "캘린더 추가 " + targetDate + " " + timeFormatted + " " + title;
            processCommandAsync(standardCommand, room, author, msg);
            return;
        }
    }
    
    // ========== 도움말 및 상태 ==========
    
    if (content === "캘린더 도움말" || content === "일정 도움말") {
        var helpMessage = "📅 Google Calendar 봇 사용법\n\n" +
                        "📋 정확한 명령어:\n" +
                        "• 캘린더 조회 2024-01-15\n" +
                        "• 캘린더 추가 2024-01-15 14:00 회의 제목\n" +
                        "• 캘린더 삭제 <event_id>\n\n" +
                        "📋 간편 명령어:\n" +
                        "• 오늘 일정\n" +
                        "• 내일 일정\n" +
                        "• 모레 일정\n\n" +
                        "📋 자연어 명령어:\n" +
                        "• 일정 추가 내일 3시 팀 회의\n" +
                        "• 일정 추가 오늘 오후 2시 점심약속\n\n" +
                        "❓ 기타:\n" +
                        "• 캘린더 도움말 (이 메시지)\n" +
                        "• 서버 테스트 (연결 확인)";
        
        msg.reply(helpMessage);
        return;
    }
    
    if (content === "서버 테스트" || content === "캘린더 상태") {
        processCommandAsync("health_check", room, author, msg);
        return;
    }
});

// ====== 봇 초기화 ======
Log.i("[" + CONFIG.BOT_NAME + "] Google Calendar 심플 봇 시작됨!");
Log.i("[" + CONFIG.BOT_NAME + "] 대상 방: " + CONFIG.TARGET_ROOMS.join(", "));
Log.i("[" + CONFIG.BOT_NAME + "] 서버 URL: " + CONFIG.FASTAPI_WEBHOOK_URL);

/**
 * ====== 사용법 요약 ======
 * 
 * 1. CONFIG에서 FASTAPI_WEBHOOK_URL과 TARGET_ROOMS 수정
 * 2. 메신저봇 앱에서 컴파일 및 실행
 * 3. 카톡방에서 명령어 테스트:
 *    - "오늘 일정" : 오늘 일정 보기
 *    - "캘린더 조회 2024-01-15" : 특정 날짜 일정
 *    - "일정 추가 내일 3시 회의" : 자연어로 일정 추가
 * 
 * ====== 코덱스 방식의 장점 ======
 * 
 * - 명령어 파싱을 서버에서 집중 처리
 * - 클라이언트는 단순한 전송 역할
 * - 서버 업데이트만으로 기능 확장 가능
 * - 에러 처리 로직 단순화
 * 
 * ====== 간편한 설정 ======
 * 
 * 1. 서버 URL 변경 (1줄)
 * 2. 카톡방 이름 변경 (1줄)
 * 3. 메신저봇 컴파일
 * 4. 완료!
 */